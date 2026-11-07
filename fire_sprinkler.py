import requests
import json
import time
import os
import sys

# Load credentials and configuration
env_path = os.path.expanduser("~/cockatoo_project/.env")
creds = {}
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                creds[k] = v

BHYVE_EMAIL = creds.get("BHYVE_EMAIL")
BHYVE_PASSWORD = creds.get("BHYVE_PASSWORD")
DEVICE_ID = creds.get("BHYVE_DEVICE_ID")
STATION = int(creds.get("BHYVE_STATION", 1))

BURST_SECONDS = 2

LOGIN_URL = "https://api.orbitbhyve.com/v1/session"
headers = {
    "orbit-app-id": "Orbit Support Dashboard",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

print("1. Authenticating with B-hyve...")
sys.stdout.flush()
res = requests.post(LOGIN_URL, json={"session": {"email": BHYVE_EMAIL, "password": BHYVE_PASSWORD}}, headers=headers, timeout=20)
if res.status_code != 200:
    print(f"Authentication failed: {res.text}")
    sys.exit(1)

token = res.json().get("orbit_api_key")
headers["orbit-api-key"] = token

command_url = f"https://api.orbitbhyve.com/v1/sprinklers/{DEVICE_ID}"

# Step 1: Open valve
print(f"2. OPENING Station {STATION}...")
sys.stdout.flush()
start_payload = {
    "event": "change_mode",
    "mode": "manual",
    "stations": [
        {
            "station": STATION,
            "run_time": 1
        }
    ]
}
res_start = requests.post(command_url, json=start_payload, headers=headers, timeout=15)

if res_start.status_code not in [200, 204]:
    print(f"Start command rejected: {res_start.status_code} - {res_start.text}")
    sys.exit(1)

# Step 2: Wait 2 seconds
print(f"3. Spraying for {BURST_SECONDS} seconds...")
sys.stdout.flush()
time.sleep(BURST_SECONDS)

# Step 3: Close valve immediately
print("4. CLOSING valve (returning to auto)...")
sys.stdout.flush()
stop_payload = {
    "event": "change_mode",
    "mode": "auto"
}
res_stop = requests.post(command_url, json=stop_payload, headers=headers, timeout=15)

if res_stop.status_code in [200, 204]:
    print("\nSUCCESS: 2-second deterrent burst complete!")
else:
    print(f"Stop command response: {res_stop.status_code} - {res_stop.text}")
