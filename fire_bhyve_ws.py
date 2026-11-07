import requests
import json
import time
import os
import sys
import websocket

# Load environment configuration
env_path = os.path.expanduser("~/cockatoo_project/.env")
creds = {}
with open(env_path) as f:
    for line in f:
        if "=" in line and not line.startswith("#"):
            k, v = line.strip().split("=", 1)
            creds[k] = v

BHYVE_EMAIL = creds.get("BHYVE_EMAIL")
BHYVE_PASSWORD = creds.get("BHYVE_PASSWORD")
DEVICE_ID = creds.get("BHYVE_DEVICE_ID")
STATION = int(creds.get("BHYVE_STATION", 3))
BURST_SECONDS = float(creds.get("BURST_SECONDS", 3.0))

# 1. Obtain authenticated session token
print("1. Authenticating with Orbit session...")
login_payload = {
    "session": {
        "email": BHYVE_EMAIL,
        "password": BHYVE_PASSWORD
    }
}
headers = {
    "orbit-app-id": "Orbit Support Dashboard",
    "Content-Type": "application/json"
}

res = requests.post("https://api.orbitbhyve.com/v1/session", json=login_payload, headers=headers, timeout=20)
if res.status_code != 200:
    print(f"Login failed: {res.text}")
    sys.exit(1)

auth = res.json()
token = auth.get("orbit_api_key")
print("2. Authentication successful.")

# 2. Connect to the Orbit WebSocket on api.orbitbhyve.com
WS_URL = "wss://api.orbitbhyve.com/v1/events?binary=json"
print(f"3. Connecting to Orbit WebSocket broker at {WS_URL}...")

ws_headers = [
    f"orbit-api-key: {token}",
    f"orbit-app-id: Orbit Support Dashboard"
]

try:
    ws = websocket.create_connection(WS_URL, header=ws_headers, timeout=15)
except Exception as e:
    print(f"WebSocket connection failed: {e}")
    sys.exit(1)

# Handshake / Authenticate the socket stream
auth_msg = {
    "event": "app_connection",
    "orbit_session_token": token
}
ws.send(json.dumps(auth_msg))

try:
    init_resp = ws.recv()
    print(f"   -> Broker handshake established: {init_resp[:120]}")
except Exception:
    print("   -> Handshake sent (no reply payload needed)")

# 3. Fire the Station Valve (Manual Run)
print(f"4. >>> FIRING Station {STATION} for {BURST_SECONDS} seconds... <<<")
fire_cmd = {
    "event": "change_mode",
    "mode": "manual",
    "device_id": DEVICE_ID,
    "stations": [
        {
            "station": STATION,
            "run_time": 1
        }
    ]
}
ws.send(json.dumps(fire_cmd))

# Sleep for deterrence duration
time.sleep(BURST_SECONDS)

# 4. Shut the valve off immediately
print("5. Closing valve (returning to auto)...")
stop_cmd = {
    "event": "change_mode",
    "mode": "auto",
    "device_id": DEVICE_ID
}
ws.send(json.dumps(stop_cmd))

time.sleep(0.5)
ws.close()
print(f"\nSUCCESS: {BURST_SECONDS}-second deterrent sequence completed over WebSocket.")
