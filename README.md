# Ping Tester

A web app for Raspberry Pi that pings a range of addresses on a local
`192.168.x.x` network. The range is entered as two pairs of hex octets
(the last two bytes of a MAC address), which are converted into the
last two octets of the IP address.

## Installation

Requires [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

## Running

```bash
uv run python app.py
```

The app runs on `http://<raspberry-pi-ip>:5000`.

## Usage

1. In the **Od** (From) and **Do** (To) fields, enter two hex octets of a
   MAC address, e.g. `AA:00` and `AA:10`. This generates the range
   `192.168.170.0` – `192.168.170.16`.
2. Click **Start** — the app repeatedly pings all addresses in the range
   in parallel until you click **Stop**.
3. The table shows the status (online/offline), average and last response
   time, and the number of successful/total pings for each address.
   The summary panel at the top shows the total number of pings sent and
   the elapsed time.

The maximum range size is 512 addresses.

## Running as a systemd service (optional)

```ini
[Unit]
Description=Ping Tester
After=network.target

[Service]
WorkingDirectory=/home/pi/Ping-tester
ExecStart=/home/pi/.local/bin/uv run python app.py
Restart=on-failure
User=pi

[Install]
WantedBy=multi-user.target
```

Save as `/etc/systemd/system/ping-tester.service` and run:

```bash
sudo systemctl enable --now ping-tester
```
