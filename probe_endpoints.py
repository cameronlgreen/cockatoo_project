import requests
import json
import os
import sys

# Load config
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

LOGIN_URL = "https://api.orbitbhyve.com/v1/session"
headers = {
    "orbit-app-id": "Orbit Support Dashboard",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

print("1. Authenticating...")
res = requests.post(LOGIN_URL, json={"session": {"email": BHYVE_EMAIL, "password": BHYVE_PASSWORD}}, headers=headers, timeout=20)
if res.status_code != 200:
    print(f"Auth failed: {res.text}")
    sys.exit(1)

token = res.json().get("orbit_api_key")
headers["orbit-api-key"] = token

tests = [
    {
        "name": "Method A: POST /v1/devices/{id} with event payload",
        "method": "POST",
        "url": f"https://api.orbitbhyve.com/v1/devices/{DEVICE_ID}",
        "payload": {
            "event": "change_mode",
            "mode": "manual",
            "stations": [{"station": STATION, "run_time": 1}]
        }
    },
    {
        "name": "Method B: PUT /v1/devices/{id} with manual mode",
        "method": "PUT",
        "url": f"https://api.orbitbhyve.com/v1/devices/{DEVICE_ID}",
        "payload": {
            "mode": "manual",
            "stations": [{"station": STATION, "run_time": 1}]
        }
    },
    {
        "name": "Method C: POST /v1/sprinklers/{id}/start",
        "method": "POST",
        "url": f"https://api.orbitbhyve.com/v1/sprinklers/{DEVICE_ID}/start",
        "payload": {
            "station": STATION,
            "run_time": 1
        }
    },
    {
        "name": "Method D: POST /v1/devices/{id}/zone/{station}/start",
        "method": "POST",
        "url": f"https://api.orbitbhyve.com/v1/devices/{DEVICE_ID}/zone/{STATION}/start",
        "payload": {
            "run_time": 1
        }
    }
]

print(f"\n2. Testing trigger formats for Device {DEVICE_ID}, Station {STATION}...\n")
for t in tests:
    print(f"Testing {t['name']}...")
    try:
        if t["method"] == "POST":
            r = requests.post(t["url"], json=t["payload"], headers=headers, timeout=15)
        else:
            r = requests.put(t["url"], json=t["payload"], headers=headers, timeout=15)
        print(f"   -> Result: {r.status_code} | {r.text[:150]}")
    except Exception as e:
        print(f"   -> Error: {e}")
    print()
