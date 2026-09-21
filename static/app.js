const socket = io();

const form = document.getElementById("range-form");
const startBtn = document.getElementById("start-btn");
const stopBtn = document.getElementById("stop-btn");
const errorMessage = document.getElementById("error-message");
const totalPingsEl = document.getElementById("total-pings");
const elapsedTimeEl = document.getElementById("elapsed-time");
const onlineCountEl = document.getElementById("online-count");
const devicesBody = document.getElementById("devices-body");

let deviceRows = new Map();

function setRunning(running) {
  startBtn.disabled = running;
  stopBtn.disabled = !running;
  form.querySelectorAll("input").forEach((input) => (input.disabled = running));
}

function formatElapsed(seconds) {
  const total = Math.floor(seconds);
  const mm = String(Math.floor(total / 60)).padStart(2, "0");
  const ss = String(total % 60).padStart(2, "0");
  return `${mm}:${ss}`;
}

function renderDevices(ips) {
  devicesBody.innerHTML = "";
  deviceRows.clear();
  ips.forEach((ip) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${ip}</td>
      <td><span class="status-dot offline"></span><span class="status-text">čeká</span></td>
      <td class="avg">-</td>
      <td class="last">-</td>
      <td class="count">0 / 0</td>
    `;
    devicesBody.appendChild(row);
    deviceRows.set(ip, row);
  });
  onlineCountEl.textContent = `0 / ${ips.length}`;
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  errorMessage.textContent = "";
  socket.emit("start", {
    start_mac: document.getElementById("start_mac").value.trim(),
    end_mac: document.getElementById("end_mac").value.trim(),
    timeout: document.getElementById("timeout").value,
  });
});

stopBtn.addEventListener("click", () => {
  socket.emit("stop");
});

socket.on("started", (data) => {
  errorMessage.textContent = "";
  setRunning(true);
  totalPingsEl.textContent = "0";
  elapsedTimeEl.textContent = "00:00";
  renderDevices(data.ips);
});

socket.on("stopped", () => {
  setRunning(false);
});

socket.on("error", (data) => {
  errorMessage.textContent = data.message;
});

socket.on("stats_update", (data) => {
  totalPingsEl.textContent = data.total_pings;
  elapsedTimeEl.textContent = formatElapsed(data.elapsed);

  let onlineCount = 0;
  data.devices.forEach((device) => {
    const row = deviceRows.get(device.ip);
    if (!row) return;
    if (device.online) onlineCount += 1;

    const dot = row.querySelector(".status-dot");
    const statusText = row.querySelector(".status-text");
    dot.className = `status-dot ${device.online ? "online" : "offline"}`;
    statusText.textContent = device.online ? "online" : "offline";

    row.querySelector(".avg").textContent =
      device.avg_ms !== null ? device.avg_ms.toFixed(1) : "-";
    row.querySelector(".last").textContent =
      device.last_ms !== null ? device.last_ms.toFixed(1) : "-";
    row.querySelector(".count").textContent = `${device.success} / ${device.sent}`;
  });

  onlineCountEl.textContent = `${onlineCount} / ${data.devices.length}`;
});
