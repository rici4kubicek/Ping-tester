import os
import threading

from flask import Flask, render_template
from flask_socketio import SocketIO

from mac_convert import MacRangeError, generate_ip_range
from pinger import PingWorker

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", os.urandom(24).hex())
socketio = SocketIO(app, async_mode="threading")

worker = None
worker_lock = threading.Lock()


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("start")
def handle_start(data):
    global worker
    data = data or {}
    with worker_lock:
        if worker is not None:
            socketio.emit("error", {"message": "Ping už běží."})
            return

        try:
            timeout = float(data.get("timeout", 1))
        except (TypeError, ValueError):
            socketio.emit("error", {"message": "Neplatný timeout."})
            return
        if not 0.1 <= timeout <= 10:
            socketio.emit("error", {"message": "Timeout musí být mezi 0.1 a 10 sekundami."})
            return

        try:
            ip_list = generate_ip_range(data.get("start_mac", ""), data.get("end_mac", ""))
        except MacRangeError as exc:
            socketio.emit("error", {"message": str(exc)})
            return

        worker = PingWorker(ip_list, socketio, timeout=timeout)
        worker.start()
    socketio.emit("started", {"ips": ip_list})


@socketio.on("stop")
def handle_stop():
    global worker
    with worker_lock:
        if worker is None:
            return
        worker.stop()
        worker = None
    socketio.emit("stopped", {})


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
