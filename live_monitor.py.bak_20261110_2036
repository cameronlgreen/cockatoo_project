#!/usr/bin/env python3
import os, sys, time, json, asyncio, threading
from datetime import datetime
import cv2, requests, websockets
from ultralytics import YOLO

TAPO_USER = "cockatoo"
TAPO_PASS = "cockatoo1234"
TAPO_IP   = "192.168.1.147"
RTSP_URL  = f"rtsp://{TAPO_USER}:{TAPO_PASS}@{TAPO_IP}:554/stream2"

BHYVE_EMAIL = os.environ.get("BHYVE_EMAIL", "cameron@green.net.au")
BHYVE_PASSWORD = os.environ.get("BHYVE_PASSWORD", "Cockatoo1234!")
BHYVE_DEVICE_ID = "66f4ce315e9a4f66453d7122"
STATION = 3
BURST_SECONDS = 3.0
COOLDOWN_SECONDS = 35.0

TELEGRAM_TOKEN = "8542046011:AAGixULwPxZWBesqY2jjI7XndeKMbA67Avk"
TELEGRAM_CHAT_ID = "7087305671"
VM_TOKEN  = "7db97-fcb6c-b3baf-45713-910ce-9a234-0f-0d55d606-c50d-4921-a2f2-c524cc2d115b"
VM_DEVICE = "bad-bird-kitchen-echo-pyowk"

DETECTOR_MODEL_PATH = "yolov8n.pt"
CLASSIFIER_MODEL_PATH = "/home/cameronlgreen/cockatoo_project/runs/classify/bird_classifier_v2/weights/best.pt"

SAFE_SPECIES = ["rosella", "king_parrot", "lorikeet", "rainbow_lorikeet", "kookaburra", "magpie"]
TARGET_SPECIES = ["cockatoo", "galah", "pigeon"]

TARGET_CONF_THRESHOLD = 0.65
SAFE_RUNNER_THRESHOLD = 0.15
SAFE_LATCH_SECONDS = 6.0

TRIGGER_DIR = "/home/cameronlgreen/cockatoo_project/trigger_photos"
os.makedirs(TRIGGER_DIR, exist_ok=True)

class BHyveWS:
    def __init__(self):
        print("[B-HYVE] Direct on-demand trigger engine ready.", flush=True)

    def trigger_spray(self, duration=BURST_SECONDS):
        def _burst():
            try:
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

                # 1. Fresh session token
                res = requests.post(
                    "https://api.orbitbhyve.com/v1/session",
                    json={"session": {"email": email, "password": password}},
                    timeout=8
                )
                if res.status_code != 200:
                    print(f"[B-HYVE ERROR] Orbit login failed: {res.text}", flush=True)
                    return

                token = res.json().get("orbit_session_token")

                # 2. Open clean WebSocket
                import ssl, websocket
                sock = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
                sock.connect(f"wss://api.orbitbhyve.com/v1/events?token={token}", timeout=8)

                # 3. Required app_connection subscription
                sock.send(json.dumps({
                    "event": "app_connection",
                    "orbit_session_token": token,
                    "subscribe_device_id": device_id
                }))
                time.sleep(0.4)

                # 4. Open valve
                start_cmd = {
                    "event": "change_mode",
                    "mode": "manual",
                    "device_id": device_id,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "stations": [{"station": station, "run_time": 1}]
                }
                sock.send(json.dumps(start_cmd))
                print(f"[B-HYVE] Spray ON! Station {station} bursting {duration}s...", flush=True)

                time.sleep(duration)

                # 5. Shut valve with auto mode
                stop_cmd = {
                    "event": "change_mode",
                    "mode": "auto",
                    "device_id": device_id,
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

            except Exception as e:
                print(f"[B-HYVE ERROR] Direct trigger failed: {e}", flush=True)

        threading.Thread(target=_burst, daemon=True).start()
        return True
bhyve = BHyveWS()

def trigger_alexa():
    try:
        requests.get(f"https://api-v2.voicemonkey.io/trigger?token={VM_TOKEN}&device={VM_DEVICE}", timeout=5)
    except Exception:
        pass

def send_telegram_alert(img_path, caption):
    try:
        with open(img_path, "rb") as f:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto", data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption}, files={"photo": f}, timeout=10)
    except Exception:
        pass

def display_on_desktop(img_path):
    def _show():
        try:
            import subprocess
            cmd = ["/usr/bin/python3", "-c", f"import cv2; img=cv2.imread('{img_path}'); cv2.namedWindow('Cockatoo Alert', cv2.WINDOW_NORMAL); cv2.resizeWindow('Cockatoo Alert', 800, 600); cv2.imshow('Cockatoo Alert', img); cv2.waitKey(0); cv2.destroyAllWindows()"]
            subprocess.run(cmd, env={"DISPLAY": ":0", "XAUTHORITY": "/home/cameronlgreen/.Xauthority"})
        except Exception:
            pass
    threading.Thread(target=_show, daemon=True).start()

class RTSPStream:
    def __init__(self, url):
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
        self.cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        self.frame = None
        self.lock = threading.Lock()
        threading.Thread(target=self._update, daemon=True).start()

    def _update(self):
        while True:
            ret, f = self.cap.read()
            if ret and f is not None:
                with self.lock:
                    self.frame = f
            else:
                time.sleep(0.05)

    def read(self):
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

def main():
    detector = YOLO(DETECTOR_MODEL_PATH)
    classifier = YOLO(CLASSIFIER_MODEL_PATH)
    stream = RTSPStream(RTSP_URL)
    time.sleep(2.0)
    print("[INFO] Two-stage pipeline and shield active.", flush=True)

    last_trigger = 0.0
    last_safe_bird_time = 0.0

    while True:
        now_dt = datetime.now()
        # Sleep mode outside 06:00 to 20:30 (8:30 PM)
        if now_dt.hour < 6 or (now_dt.hour, now_dt.minute) >= (20, 30):
            print(f"[{now_dt.strftime('%H:%M:%S')}] [NIGHT MODE] Outside active hours (06:00-20:30). Sleeping 60s...", flush=True)
            time.sleep(60)
            continue

        frame = stream.read()
        if frame is None:
            time.sleep(0.04)
            continue

        now = time.time()
        ts = datetime.now().strftime("%H:%M:%S")

        h, w = frame.shape[:2]
        feeder_roi = frame[int(h*0.40):int(h*0.70), int(w*0.30):int(w*0.60)]
        if feeder_roi.size == 0:
            time.sleep(0.05)
            continue

        det = detector(feeder_roi, imgsz=320, verbose=False)[0]
        crops = []
        for box in det.boxes:
            lbl = detector.names[int(box.cls[0])]
            conf = float(box.conf[0])
            if lbl == "bird" and conf >= 0.35:
                bx1, by1, bx2, by2 = map(int, box.xyxy[0])
                bw, bh = bx2 - bx1, by2 - by1
                if bw >= 70 and bh >= 70 and (max(bw, bh) / max(1, min(bw, bh))) <= 2.2:
                    crop = feeder_roi[by1:by2, bx1:bx2]
                    if crop.size > 0:
                        crops.append((crop, bw, bh))

        if not crops:
            time.sleep(0.04)
            continue

        candidates = []
        frame_has_safe = False
        safe_msg = ""

        for b_crop, bw, bh in crops:
            res = classifier(b_crop, imgsz=224, verbose=False)[0]
            top1 = res.names[res.probs.top5[0]].lower()
            top1_c = float(res.probs.top1conf)
            top2, top2_c = "", 0.0
            if len(res.probs.top5) > 1:
                top2 = res.names[res.probs.top5[1]].lower()
                top2_c = float(res.probs.data[res.probs.top5[1]])

            if top1 in SAFE_SPECIES:
                frame_has_safe = True
                safe_msg = f"Primary is {top1.upper()} ({top1_c*100:.1f}%)"
            elif top2 in SAFE_SPECIES and top2_c >= SAFE_RUNNER_THRESHOLD and top1 not in TARGET_SPECIES:
                frame_has_safe = True
                safe_msg = f"Runner-up is {top2.upper()} ({top2_c*100:.1f}%)"

            candidates.append({"name": top1, "conf": top1_c, "dims": (bw, bh)})

        if frame_has_safe:
            last_safe_bird_time = now
            print(f"[{ts}] [SAFE BIRD VETO] {safe_msg} - Suppressed.", flush=True)
            time.sleep(0.1)
            continue

        if (now - last_safe_bird_time) < SAFE_LATCH_SECONDS:
            print(f"[{ts}] [SAFE BIRD VETO] Latch active ({now - last_safe_bird_time:.1f}s) - Suppressed.", flush=True)
            time.sleep(0.1)
            continue

        target = None
        for cand in candidates:
            if cand["name"] in TARGET_SPECIES and cand["conf"] >= TARGET_CONF_THRESHOLD:
                target = cand
                break

        if target:
            if (now - last_trigger) > COOLDOWN_SECONDS:
                last_trigger = now
                sp, cf = target["name"], target["conf"]
                print(f"[{ts}] [ALERT] TARGET: {sp.upper()} ({cf*100:.1f}%)! SPRAYING...", flush=True)
                bhyve.trigger_spray(duration=BURST_SECONDS)
                hit_path = os.path.join(TRIGGER_DIR, f"hit_{datetime.now().strftime('%d%b_%H-%M-%S')}_{sp}.jpg")
                cv2.imwrite(hit_path, feeder_roi)
                threading.Thread(target=trigger_alexa, daemon=True).start()
                threading.Thread(target=send_telegram_alert, args=(hit_path, f"🚨 Sprayed {sp.upper()} ({cf*100:.1f}%)"), daemon=True).start()
                display_on_desktop(hit_path)
            else:
                print(f"[{ts}] [COOLDOWN] Target present but valve cooling down ({COOLDOWN_SECONDS - (now - last_trigger):.1f}s left).", flush=True)

        time.sleep(0.04)

if __name__ == "__main__":
    main()
