import time
import subprocess

def display_on_desktop(img_path):
    def _show():
        try:
            import subprocess
            cmd = [
                "/usr/bin/python3", "-c",
                f"import cv2; "
                f"img = cv2.imread('{img_path}'); "
                f"cv2.namedWindow('Cockatoo Trigger Alert', cv2.WINDOW_NORMAL); "
                f"cv2.resizeWindow('Cockatoo Trigger Alert', 800, 600); "
                f"cv2.imshow('Cockatoo Trigger Alert', img); "
                f"cv2.waitKey(0); "
                f"cv2.destroyAllWindows()"
            ]
            subprocess.run(
                cmd,
                env={"DISPLAY": ":0", "XAUTHORITY": "/home/cameronlgreen/.Xauthority"}
            )
        except Exception as e:
            print(f"[DISPLAY ERROR] {e}", flush=True)

    threading.Thread(target=_show, daemon=True).start()


# --- LOAD CREDENTIALS (.env) ---
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
STATION = int(creds.get("BHYVE_STATION", 3))
BURST_SECONDS = float(creds.get("BURST_SECONDS", 3.0))

TAPO_USER = creds.get("TAPO_USER", "cockatoo")
TAPO_PASS = creds.get("TAPO_PASS", "cockatoo1234")
TAPO_IP   = creds.get("TAPO_IP", "192.168.1.147")
RTSP_URL  = f"rtsp://{TAPO_USER}:{TAPO_PASS}@{TAPO_IP}:554/stream2"

VM_TOKEN  = creds.get("VM_TOKEN", "7db97-fcb6c-b3baf-45713-910ce-9a234-0f-0d55d606-c50d-4921-a2f2-c524cc2d115b")
VM_DEVICE = creds.get("VM_DEVICE", "bad-bird-kitchen-echo-pyowk")

# --- DETECTION THRESHOLDS ---
CONF_THRESHOLD   = 0.42
MIN_BIRD_DIM     = 35   # Catch small birds for safe logging
TARGET_MIN_DIM   = 95
COOLDOWN_SECONDS = 15
FEEDER_ZONE      = (0.31, 0.42, 0.68, 0.78)

# --- B-HYVE WEBSOCKET CLIENT ---
class BHyveController:
    def __init__(self):
        print("[B-HYVE] Direct controller initialized (October engine).", flush=True)

    def trigger_spray(self, duration=3, on_complete=None):
        def _burst():
            try:
                res = requests.post(
                    "https://api.orbitbhyve.com/v1/session",
                    json={"session": {"email": BHYVE_EMAIL, "password": BHYVE_PASSWORD}},
                    timeout=10
                )
                if res.status_code != 200:
                    print(f"[B-HYVE ERROR] Auth failed: {res.text}", flush=True)
                    return
                token = res.json().get("orbit_session_token")

                sock = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
                sock.connect(f"wss://api.orbitbhyve.com/v1/events?token={token}", timeout=10)

                handshake = {
                    "event": "app_connection",
                    "orbit_session_token": token,
                    "subscribe_device_id": BHYVE_DEVICE_ID
                }
                sock.send(json.dumps(handshake))
                time.sleep(0.5)

                start_cmd = {
                    "event": "change_mode",
                    "mode": "manual",
                    "device_id": BHYVE_DEVICE_ID,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "stations": [{"station": BHYVE_STATION, "run_time": 1}]
                }
                sock.send(json.dumps(start_cmd))
                print(f"[B-HYVE] Spray ON! Bursting {duration}s...", flush=True)

                time.sleep(duration)

                stop_cmd = {
                    "event": "change_mode",
                    "mode": "auto",
                    "device_id": BHYVE_DEVICE_ID,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
                for _ in range(3):
                    try:
                        sock.send(json.dumps(stop_cmd))
                        time.sleep(0.08)
                    except Exception:
                        pass
                sock.close()
                print("[B-HYVE] Spray OFF! Valve closed cleanly.", flush=True)

                if on_complete:
                    try:
                        on_complete()
                    except Exception as e:
                        print(f"[ALEXA ERROR] {e}", flush=True)

            except Exception as e:
                print(f"[B-HYVE ERROR] Direct valve trigger failed: {e}", flush=True)

        threading.Thread(target=_burst, daemon=True).start()


if __name__ == "__main__":
    main()
