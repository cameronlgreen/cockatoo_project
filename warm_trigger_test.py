import requests
import json
import time
import os
import sys
import websocket

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

# 1. Login once
print("Connecting & authenticating...")
res = requests.post("https://api.orbitbhyve.com/v1/session", 
                    json={"session": {"email": BHYVE_EMAIL, "password": BHYVE_PASSWORD}}, 
                    headers={"orbit-app-id": "Orbit Support Dashboard", "Content-Type": "application/json"}, 
                    timeout=20)
token = res.json().get("orbit_api_key")

# 2. Open WebSocket once and keep it hot
ws_url = "wss://api.orbitbhyve.com/v1/events?binary=json"
ws_headers = [f"orbit-api-key: {token}", "orbit-app-id: Orbit Support Dashboard"]
ws = websocket.create_connection(ws_url, header=ws_headers, timeout=15)
ws.send(json.dumps({"event": "app_connection", "orbit_session_token": token}))

try:
    ws.recv()
except Exception:
    pass

print("\n" + "="*50)
print(">>> SOCKET IS WARM AND READY <<<")
print("Press ENTER at any moment to fire the valve...")
print("="*50 + "\n")

try:
    while True:
        input()
        t0 = time.time()
        print(f"[{time.strftime('%H:%M:%S')}] Trigger dispatched! Start timing the water...")
        
        fire_cmd = {
            "event": "change_mode",
            "mode": "manual",
            "device_id": DEVICE_ID,
            "stations": [{"station": STATION, "run_time": 1}]
        }
        ws.send(json.dumps(fire_cmd))
        
        time.sleep(BURST_SECONDS)
        
        stop_cmd = {
            "event": "change_mode",
            "mode": "auto",
            "device_id": DEVICE_ID
        }
        ws.send(json.dumps(stop_cmd))
        print("Valve shut command sent. Press ENTER to fire again, or Ctrl+C to quit.\n")
except KeyboardInterrupt:
    ws.close()
    print("\nExiting.")
