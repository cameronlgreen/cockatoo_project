path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

# 1. Replace the slow trigger_spray with persistent socket burst + fallback
old_trigger = """    def trigger_spray(self, duration=2):
        def _burst():
            try:
                res = requests.post(
                    "https://api.orbitbhyve.com/v1/session",
                    json={"session": {"email": BHYVE_EMAIL, "password": BHYVE_PASSWORD}},
                    headers={"orbit-app-id": "Orbit Support Dashboard", "Content-Type": "application/json"},
                    timeout=8
                )
                if res.status_code != 200:
                    print(f"[B-HYVE ERROR] Auth failed: {res.status_code}", flush=True)
                    return
                token = res.json().get("orbit_api_key")

                ws = websocket.create_connection(f"wss://api.orbitbhyve.com/v1/events?token={token}", timeout=8)
                ws.send(json.dumps({"event": "app_connection", "orbit_session_token": token}))
                ws.send(json.dumps({"event": "subscribe", "devices": [DEVICE_ID]}))
                time.sleep(0.4)

                start_cmd = {
                    "event": "change_mode",
                    "mode": "manual",
                    "device_id": DEVICE_ID,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "stations": [{"station": STATION, "run_time": 1}]
                }
                ws.send(json.dumps(start_cmd))
                print(f"[B-HYVE] Spray ON (Station {STATION})! Bursting for {duration}s...", flush=True)

                time.sleep(duration)

                stop_cmd = {
                    "event": "change_mode",
                    "mode": "off",
                    "device_id": DEVICE_ID,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
                ws.send(json.dumps(stop_cmd))
                print(f"[B-HYVE] Spray OFF! Valve closed.", flush=True)
                time.sleep(0.4)
                ws.close()
            except Exception as e:
                print(f"[B-HYVE ERROR] Direct burst failed: {e}", flush=True)

        threading.Thread(target=_burst, daemon=True).start()
        return True"""

new_trigger = """    def trigger_spray(self, duration=2):
        def _burst():
            try:
                start_cmd = {
                    "event": "change_mode",
                    "mode": "manual",
                    "device_id": DEVICE_ID,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "stations": [{"station": STATION, "run_time": 1}]
                }
                stop_cmd = {
                    "event": "change_mode",
                    "mode": "off",
                    "device_id": DEVICE_ID,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }

                # Path 1: Fast direct send on persistent warm socket
                with self.lock:
                    if self.is_connected and self.ws:
                        self.ws.send(json.dumps(start_cmd))
                        print(f"[B-HYVE] Spray ON (Station {STATION}) via active WS! Bursting {duration}s...", flush=True)
                        time.sleep(duration)
                        self.ws.send(json.dumps(stop_cmd))
                        print(f"[B-HYVE] Spray OFF! Valve closed.", flush=True)
                        return

                # Path 2: Fallback on-demand connection if warm WS dropped
                print("[B-HYVE] Active WS unavailable, initiating fallback connection...", flush=True)
                res = requests.post(
                    "https://api.orbitbhyve.com/v1/session",
                    json={"session": {"email": BHYVE_EMAIL, "password": BHYVE_PASSWORD}},
                    headers={"orbit-app-id": "Orbit Support Dashboard", "Content-Type": "application/json"},
                    timeout=8
                )
                if res.status_code != 200:
                    print(f"[B-HYVE ERROR] Auth failed: {res.status_code}", flush=True)
                    return
                token = res.json().get("orbit_api_key")
                temp_ws = websocket.create_connection(f"wss://api.orbitbhyve.com/v1/events?token={token}", timeout=8)
                temp_ws.send(json.dumps({"event": "app_connection", "orbit_session_token": token}))
                temp_ws.send(json.dumps({"event": "subscribe", "devices": [DEVICE_ID]}))
                time.sleep(0.3)
                temp_ws.send(json.dumps(start_cmd))
                print(f"[B-HYVE] Spray ON (Station {STATION}) via fallback! Bursting {duration}s...", flush=True)
                time.sleep(duration)
                temp_ws.send(json.dumps(stop_cmd))
                print(f"[B-HYVE] Spray OFF! Valve closed.", flush=True)
                time.sleep(0.3)
                temp_ws.close()
            except Exception as e:
                print(f"[B-HYVE ERROR] Spray burst failed: {e}", flush=True)

        threading.Thread(target=_burst, daemon=True).start()
        return True"""

if old_trigger in code:
    code = code.replace(old_trigger, new_trigger)
    print("SUCCESS: Replaced trigger_spray with persistent socket burst.")
else:
    print("Warning: Exact match for old_trigger not found.")

# 2. Make trigger_alexa non-blocking so 429 quota errors don't delay the detection loop
old_call = "bhyve.trigger_spray()\n                trigger_alexa()"
new_call = "bhyve.trigger_spray()\n                threading.Thread(target=trigger_alexa, daemon=True).start()"

if old_call in code:
    code = code.replace(old_call, new_call)
    print("SUCCESS: Decoupled trigger_alexa into background thread.")

with open(path, "w") as f:
    f.write(code)
