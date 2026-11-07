import os, requests, json, time, websocket

with open(os.path.expanduser("~/cockatoo_project/.env")) as f:
    creds = dict(line.strip().split("=", 1) for line in f if "=" in line and not line.startswith("#"))

email = creds["BHYVE_EMAIL"]
password = creds["BHYVE_PASSWORD"]
dev_id = creds["BHYVE_DEVICE_ID"]

# 1. Login
res = requests.post(
    "https://api.orbitbhyve.com/v1/session",
    json={"session": {"email": email, "password": password}},
    headers={"orbit-app-id": "Orbit Support Dashboard", "Content-Type": "application/json"}
)
auth_data = res.json()
token = auth_data["orbit_api_key"]
user_id = auth_data.get("user_id")

print(f"Logged in. User ID: {user_id}")

# 2. Connect to WebSocket
ws = websocket.create_connection(f"wss://api.orbitbhyve.com/v1/events?token={token}", timeout=10)

# Step A: App presence handshake
handshake = {
    "event": "app_connection",
    "orbit_session_token": token
}
ws.send(json.dumps(handshake))

# Step B: Subscribe to device stream
subscribe = {
    "event": "subscribe",
    "devices": [dev_id]
}
ws.send(json.dumps(subscribe))
time.sleep(1)

# Step C: Send manual watering command (Station 3 for 1 min)
run_cmd = {
    "event": "change_mode",
    "mode": "manual",
    "device_id": dev_id,
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "stations": [
        {"station": 3, "run_time": 1}
    ]
}
ws.send(json.dumps(run_cmd))
print(f"Sent manual run command to Station 3. Listening for response...")

# Listen for 6 seconds to capture controller ACKs / state updates
deadline = time.time() + 6
while time.time() < deadline:
    try:
        ws.settimeout(2.0)
        msg = ws.recv()
        evt = json.loads(msg)
        print("<- Event:", evt.get("event"), "| Payload:", msg[:120])
    except Exception:
        pass

ws.close()
print("Done.")
