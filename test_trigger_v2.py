import requests
import json
import os
import sys

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

headers = {
    "orbit-app-id": "Orbit Support Dashboard",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

# 1. Login
res = requests.post("https://api.orbitbhyve.com/v1/session", json={"session": {"email": BHYVE_EMAIL, "password": BHYVE_PASSWORD}}, headers=headers, timeout=20)
token = res.json().get("orbit_api_key")
headers["orbit-api-key"] = token

tests = [
    {
        "name": "Path 1: POST /v1/events (Global event router)",
        "method": "POST",
        "url": "https://api.orbitbhyve.com/v1/events",
        "body": {
            "event": "change_mode",
            "device_id": DEVICE_ID,
            "mode": "manual",
            "stations": [{"station": STATION, "run_time": 1}]
        }
    },
    {
        "name": "Path 2: POST /v1/devices/{id}/zones/{station}/start",
        "method": "POST",
        "url": f"https://api.orbitbhyve.com/v1/devices/{DEVICE_ID}/zones/{STATION}/start",
        "body": {"run_time": 1}
    },
    {
        "name": "Path 3: POST /v1/devices/{id}/zones/{station}/manual_run",
        "method": "POST",
        "url": f"https://api.orbitbhyve.com/v1/devices/{DEVICE_ID}/zones/{STATION}/manual_run",
        "body": {"run_time": 1}
    },
    {
        "name": "Path 4: POST /v1/devices/{id}/manual_override",
        "method": "POST",
        "url": f"https://api.orbitbhyve.com/v1/devices/{DEVICE_ID}/manual_override",
        "body": {
            "station": STATION,
            "run_time": 1
        }
    }
]

print(f"Testing 4 specific event endpoints for Device {DEVICE_ID} (Station {STATION})...\n")
for t in tests:
    print(f"Testing {t['name']}...")
    try:
        r = requests.post(t["url"], json=t["body"], headers=headers, timeout=15)
        print(f"   -> HTTP {r.status_code}: {r.text[:200]}\n")
    except Exception as e:
        print(f"   -> Error: {e}\n")
