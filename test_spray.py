import os, requests, json, time, websocket

env_path = os.path.expanduser("~/cockatoo_project/.env")
creds = {}
with open(env_path) as f:
    for line in f:
        if "=" in line and not line.startswith("#"):
            k, v = line.strip().split("=", 1)
            creds[k] = v

email = creds.get("BHYVE_EMAIL")
password = creds.get("BHYVE_PASSWORD")
dev_id = creds.get("BHYVE_DEVICE_ID")
station = int(creds.get("BHYVE_STATION", 3))

print("1. Logging into B-hyve...")
res = requests.post(
    "https://api.orbitbhyve.com/v1/session",
    json={"session": {"email": email, "password": password}},
    headers={"orbit-app-id": "Orbit Support Dashboard", "Content-Type": "application/json"},
    timeout=10
)
if res.status_code != 200:
    print("Login failed:", res.status_code, res.text)
    exit(1)

data = res.json()
token = data.get("orbit_api_key")
print("Login OK!")

print("2. Checking controller zones...")
dev_res = requests.get(
    f"https://api.orbitbhyve.com/v1/devices/{dev_id}",
    headers={"orbit-api-key": token, "orbit-app-id": "Orbit Support Dashboard"},
    timeout=10
)
if dev_res.status_code == 200:
    d = dev_res.json()
    status = d.get("status", {}).get("status", "unknown")
    name = d.get("name", "Unknown Device")
    print(f"Controller: {name} (Online Status: {status})")
    zones = d.get("zones", [])
    for z in zones:
        st_num = z.get("station")
        z_name = z.get("name")
        print(f"  -> Station {st_num}: '{z_name}'")
else:
    print("Failed to fetch device details:", dev_res.status_code)

print(f"\n3. Sending manual spray command to Station {station}...")
ws_url = f"wss://api.orbitbhyve.com/v1/events?token={token}"
ws = websocket.create_connection(ws_url, timeout=10)
payload = {
    "event": "change_mode",
    "mode": "manual",
    "device_id": dev_id,
    "stations": [{"station": station, "run_time": 1}]
}
ws.send(json.dumps(payload))
print(f"Command sent to Station {station} for 1 minute run time.")
print("Waiting 5 seconds for B-hyve response...")
time.sleep(5)
ws.close()
print("Done test.")
