import os, sys, time, json, requests, ssl, websocket

env = {}
env_file = "/home/cameronlgreen/cockatoo_project/.env"
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k] = v

email = env.get("BHYVE_EMAIL", "cameron.l.green@bigpond.com")
password = env.get("BHYVE_PASSWORD", "Cg31473147")
device_id = env.get("BHYVE_DEVICE_ID", "6764f0d0a29c4e52dccb9062")
station = int(env.get("BHYVE_STATION", 3))

def fire_test_burst(duration_seconds):
    print("\n" + "=" * 55)
    print(f">>> TARGET BURST DURATION: {duration_seconds}s")
    print(f">>> Ensure measuring container is empty and aligned under the nozzle.")
    input(">>> Press [ENTER] when ready to fire...")

    print(">>> 1. Authenticating with Orbit session...")
    res = requests.post(
        "https://api.orbitbhyve.com/v1/session",
        json={"session": {"email": email, "password": password}},
        timeout=10
    )
    if res.status_code != 200:
        print(f"❌ Orbit Login failed: {res.text}")
        return False
    token = res.json().get("orbit_session_token")

    print(">>> 2. Connecting to WebSocket...")
    ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
    ws.connect(f"wss://api.orbitbhyve.com/v1/events?token={token}", timeout=10)

    # Handshake registration
    ws.send(json.dumps({
        "event": "app_connection",
        "orbit_session_token": token,
        "subscribe_device_id": device_id
    }))
    time.sleep(0.5)

    # Open valve
    t_start = time.time()
    start_cmd = {
        "event": "change_mode",
        "mode": "manual",
        "device_id": device_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "stations": [{"station": station, "run_time": 1}]
    }
    ws.send(json.dumps(start_cmd))
    print(f"💧 [VALVE OPEN] Commanding Station {station} -> Sleeping {duration_seconds}s...")

    time.sleep(duration_seconds)

    # Redundant auto-shutoff
    stop_cmd = {
        "event": "change_mode",
        "mode": "auto",
        "device_id": device_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    for _ in range(3):
        try:
            ws.send(json.dumps(stop_cmd))
            time.sleep(0.08)
        except Exception:
            pass

    elapsed = time.time() - t_start
    ws.close()
    print(f"🛑 [VALVE SHUT] Total open-to-close loop elapsed: {elapsed:.2f}s")
    print(f">>> Measure and record water collected for {duration_seconds}s.")
    return True

# Testing target durations: 0.5s, 1.0s, and 3.0s
durations = [2.0]

print("=======================================================")
print(">>> B-HYVE BURST VOLUME BENCHMARK (0.5s vs 1.0s vs 3.0s)")
print("=======================================================")

for idx, d in enumerate(durations):
    success = fire_test_burst(d)
    if not success:
        break
    if idx < len(durations) - 1:
        print("\n>>> Waiting 20s for line pressure equalization and Orbit cloud reset...")
        time.sleep(20)

print("\n>>> All burst tests complete! Bring the monitor service back online.")
