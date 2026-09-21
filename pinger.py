"""Background worker that repeatedly pings a list of IP addresses."""

import re
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

RTT_RE = re.compile(r"time[=<]([\d.]+)")


class PingWorker:
    def __init__(self, ip_list, socketio, timeout=1.0):
        self.ip_list = ip_list
        self.socketio = socketio
        self.timeout = timeout
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._thread = None
        self.start_time = None
        self.total_pings = 0
        self.stats = {
            ip: {"sent": 0, "success": 0, "avg_ms": None, "last_ms": None, "online": False}
            for ip in ip_list
        }

    def start(self):
        self.start_time = time.time()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=self.timeout + 5)

    def _ping_once(self, ip):
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", str(self.timeout), ip],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=self.timeout + 2,
            )
        except subprocess.TimeoutExpired:
            return ip, False, None

        if result.returncode != 0:
            return ip, False, None

        match = RTT_RE.search(result.stdout)
        rtt = float(match.group(1)) if match else None
        return ip, True, rtt

    def _run(self):
        max_workers = min(32, len(self.ip_list)) or 1
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            while not self._stop_event.is_set():
                futures = [executor.submit(self._ping_once, ip) for ip in self.ip_list]
                for future in as_completed(futures):
                    ip, success, rtt = future.result()
                    self._record_result(ip, success, rtt)
                    if self._stop_event.is_set():
                        break
                self._emit_update()
        self._emit_update()

    def _record_result(self, ip, success, rtt):
        with self._lock:
            stats = self.stats[ip]
            stats["sent"] += 1
            self.total_pings += 1
            if success:
                stats["success"] += 1
                stats["online"] = True
                stats["last_ms"] = rtt
                if rtt is not None:
                    n = stats["success"]
                    prev_avg = stats["avg_ms"] or rtt
                    stats["avg_ms"] = ((prev_avg * (n - 1)) + rtt) / n
            else:
                stats["online"] = False
                stats["last_ms"] = None

    def _emit_update(self):
        with self._lock:
            elapsed = time.time() - self.start_time if self.start_time else 0
            devices = [{"ip": ip, **values} for ip, values in self.stats.items()]
            total_pings = self.total_pings
        devices.sort(key=lambda d: tuple(int(part) for part in d["ip"].split(".")))
        payload = {
            "elapsed": round(elapsed, 1),
            "total_pings": total_pings,
            "devices": devices,
        }
        self.socketio.emit("stats_update", payload)
