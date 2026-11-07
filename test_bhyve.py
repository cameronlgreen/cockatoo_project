import requests
import json
import sys
import time
import os

# --- Read credentials from .env ---
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

if not BHYVE_EMAIL or not BHYVE_PASSWORD:
    print("ERROR: Missing credentials in ~/cockatoo_project/.env")
    sys.exit(1)

LOGIN_URL = "https://api.orbitbhyve.com/v1/session"
headers = {
    "orbit-app-id": "Orbit Support Dashboard",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

payload = {
    "session": {
        "email": BHYVE_EMAIL,
        "password": BHYVE_PASSWORD
    }
}

print("1. Connecting to Orbit B-hyve API...")
sys.stdout.flush()

try:
    res = requests.post(LOGIN_URL, json=payload, headers=headers, timeout=25)
except Exception as e:
    print(f"Login connection failed: {e}")
    sys.exit(1)

if res.status_code != 200:
    print(f"Login failed (status {res.status_code}): {res.text}")
    sys.exit(1)

auth_data = res.json()
token = auth_data.get("orbit_api_key")
user_id = auth_data.get("user_id")

print(f"2. Logged in successfully! (User ID: {user_id})")
print("3. Querying paired devices (allowing up to 45s per attempt)...")
sys.stdout.flush()

headers["orbit-api-key"] = token

dev_res = None
for attempt in range(1, 4):
    try:
        print(f"   Attempt {attempt} of 3 to query devices...")
        sys.stdout.flush()
        dev_res = requests.get(f"https://api.orbitbhyve.com/v1/devices?user_id={user_id}", headers=headers, timeout=45)
        if dev_res.status_code == 200:
            break
        print(f"   Server replied with status {dev_res.status_code}")
    except requests.exceptions.Timeout:
        print("   Device query timed out. Retrying in 2 seconds...")
        time.sleep(2)
    except Exception as e:
        print(f"   Query error: {e}")
        time.sleep(2)

if not dev_res or dev_res.status_code != 200:
    print("ERROR: Could not retrieve device list from Orbit.")
    sys.exit(1)

devices = dev_res.json()

if not devices:
    print("No devices found on this account.")
    sys.exit(0)

print(f"\n================ B-HYVE DEVICES FOUND ================")
for d in devices:
    dev_id = d.get("id")
    name = d.get("name")
    dev_type = d.get("type")
    is_connected = d.get("status", {}).get("connected", False)
    zones = d.get("zones", [])
    
    print(f"Device Name : {name}")
    print(f"Device ID   : {dev_id}")
    print(f"Model/Type  : {dev_type}")
    print(f"Online      : {is_connected}")
    print("Zones / Stations:")
    for z in zones:
        print(f"   -> Station Number: {z.get('station')} | Zone Name: {z.get('name')}")
    print("=" * 54)
