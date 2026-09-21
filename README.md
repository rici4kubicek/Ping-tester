# Ping Tester

Webová aplikace pro Raspberry Pi, která pinguje rozsah adres v lokální síti
`192.168.x.x`. Rozsah se zadává jako dva páry hex oktetů (poslední dva
bajty MAC adresy), které se převedou na poslední dva oktety IP adresy.

## Instalace

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Spuštění

```bash
python app.py
```

Aplikace poběží na `http://<ip-raspberry-pi>:5000`.

## Použití

1. Do polí **Od** a **Do** zadej dva hex oktety MAC adresy, např. `AA:00` a
   `AA:10`. Vygeneruje se rozsah `192.168.170.0` – `192.168.170.16`.
2. Klikni na **Start** – aplikace opakovaně pinguje všechny adresy v rozsahu
   paralelně, dokud nezmáčkneš **Stop**.
3. V tabulce se zobrazuje stav (online/offline), průměrný a poslední
   response time a počet úspěšných/celkových pingů pro každou adresu.
   V horním panelu je celkový počet provedených pingů a uběhlý čas.

Maximální velikost rozsahu je 512 adres.

## Spuštění jako systemd služba (volitelné)

```ini
[Unit]
Description=Ping Tester
After=network.target

[Service]
WorkingDirectory=/home/pi/Ping-tester
ExecStart=/home/pi/Ping-tester/venv/bin/python app.py
Restart=on-failure
User=pi

[Install]
WantedBy=multi-user.target
```

Ulož jako `/etc/systemd/system/ping-tester.service` a spusť:

```bash
sudo systemctl enable --now ping-tester
```
