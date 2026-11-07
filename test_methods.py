import os, requests, json, time, websocket

with open(os.path.expanduser("~/cockatoo_project/.env")) as f:
    creds = dict(line.strip().split("=", 1) for line in f if "=" in line and not line.startswith("#"))

email = creds["BHYVE_EMAIL"]
password = creds["BHYVE_PASSWORD"]
dev_id = creds["BHYVE_DEVICE_ID"]

# Login
s_res = requests.post(
    "https://api.orbitbhyve.com/v1/session",
    json={"session": {"email": email, "password": password}},
    headers={"orbit-app-id": "Orbit Support Dashboard", "Content-Type": "application/json"}
)
token = s_res.json()["orbit_api_key"]

print("Attempting Method A: REST API Direct Zone Run (Station 3)...")
r = requests.post(
    f"https://api.orbitbhyve.com/v1/devices/{dev_id}/zone_reports",
    headers={"orbit-api-key": token, "orbit-app-id": "Orbit Support Dashboard", "Content-Type": "application/json"},
    json={"station": 3, "run_time": 1},
    timeout=5
)
print("REST status:", r.status_code, r.text[:120])

print("\nAttempting Method B: WebSocket with event feedback...")
ws = websocket.create_connection(f"wss://api.orbitbhyve.com/v1/events?token={token}", timeout=10)
ws.settimeout(3.0)
try:
    print("WS Connected message:", ws.recv()[:80])
except Exception:
    pass

payload = {
    "event": "change_mode",
    "mode": "manual",
    "device_id": dev_id,
    "stations": [{"station": 3, "run_time": 1}]
}
ws.send(json.dumps(payload))
print("Payload sent. Listening for controller response...")

start_t = time.time()
while time.time() - start_t < 6:
    try:
        msg = ws.recv()
        data = json.loads(msg)
        evt = data.get("event")
        print(f"Controller Event: {evt} -> {msg[:100]}")
    except Exception:
        break
ws.close()
print("Test completed.")
