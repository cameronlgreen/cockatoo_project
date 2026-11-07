import os, requests, json, time, websocket

with open(os.path.expanduser("~/cockatoo_project/.env")) as f:
    creds = dict(line.strip().split("=", 1) for line in f if "=" in line and not line.startswith("#"))

email = creds["BHYVE_EMAIL"]
password = creds["BHYVE_PASSWORD"]
dev_id = creds["BHYVE_DEVICE_ID"]
station = int(creds.get("BHYVE_STATION", 3))

# Login
res = requests.post(
    "https://api.orbitbhyve.com/v1/session",
    json={"session": {"email": email, "password": password}},
    headers={"orbit-app-id": "Orbit Support Dashboard", "Content-Type": "application/json"},
    timeout=10
)
token = res.json()["orbit_api_key"]

# WebSocket connection
ws = websocket.create_connection(f"wss://api.orbitbhyve.com/v1/events?token={token}", timeout=10)
ws.send(json.dumps({"event": "app_connection", "orbit_session_token": token}))
ws.send(json.dumps({"event": "subscribe", "devices": [dev_id]}))
time.sleep(0.5)

# 1. Turn ON Station 3
print(f"--> [ON] Firing Station {station}...")
start_cmd = {
    "event": "change_mode",
    "mode": "manual",
    "device_id": dev_id,
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "stations": [{"station": station, "run_time": 1}]
}
ws.send(json.dumps(start_cmd))

# 2. Give the physical valve 8 seconds to open and spray
BURST_TIME = 8
print(f"--> Waiting {BURST_TIME} seconds for water burst...")
time.sleep(BURST_TIME)

# 3. Turn OFF Station 3
print("--> [OFF] Sending stop command...")
stop_cmd = {
    "event": "change_mode",
    "mode": "off",
    "device_id": dev_id,
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
}
ws.send(json.dumps(stop_cmd))
time.sleep(1.0)
ws.close()
print("--> Burst test complete. Valve shut.")
