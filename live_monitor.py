import subprocess
#!/usr/bin/env python3
import os, sys, time, json, asyncio, threading
from datetime import datetime
import cv2
import numpy as np, requests, websockets
from ultralytics import YOLO

TAPO_USER = "cockatoo"
TAPO_PASS = "cockatoo1234"
TAPO_IP   = "192.168.1.147"
RTSP_URL  = f"rtsp://{TAPO_USER}:{TAPO_PASS}@{TAPO_IP}:554/stream2"

BHYVE_EMAIL = os.environ.get("BHYVE_EMAIL", "cameron@green.net.au")
BHYVE_PASSWORD = os.environ.get("BHYVE_PASSWORD", "Cockatoo1234!")
BHYVE_DEVICE_ID = "66f4ce315e9a4f66453d7122"
STATION = 3
BURST_SECONDS = 3.5
COOLDOWN_SECONDS = 15.0

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
SAFE_LATCH_SECONDS = 3.5

TRIGGER_DIR = "/home/cameronlgreen/cockatoo_project/trigger_photos"
os.makedirs(TRIGGER_DIR, exist_ok=True)

class BHyveWS:
    def __init__(self):
        self.log_path = "/home/cameronlgreen/cockatoo_project/bhyve_debug.log"
        self.token = None
        self.token_time = 0.0
        self.lock = threading.Lock()
        self.email, self.password, self.device_id, self.station = self._load_creds()
        threading.Thread(target=self._keepalive_loop, daemon=True).start()
        print("[B-HYVE] Low-latency cached-token trigger engine active.", flush=True)

    def _load_creds(self):
        env = {}
        env_file = "/home/cameronlgreen/cockatoo_project/.env"
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        k, v = line.strip().split("=", 1)
                        env[k] = v
        return (
            env.get("BHYVE_EMAIL", "cameron.l.green@bigpond.com"),
            env.get("BHYVE_PASSWORD", "Cg31473147"),
            env.get("BHYVE_DEVICE_ID", "6764f0d0a29c4e52dccb9062"),
            int(env.get("BHYVE_STATION", 3)),
        )

    def _log(self, msg):
        line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
        print(line, flush=True)
        try:
            with open(self.log_path, "a") as lf:
                lf.write(line + "\n")
        except Exception:
            pass

    def _get_token(self, force_refresh=False):
        with self.lock:
            if not force_refresh and self.token and (time.time() - self.token_time) < 1200:
                return self.token
            res = requests.post(
                "https://api.orbitbhyve.com/v1/session",
                json={"session": {"email": self.email, "password": self.password}},
                timeout=5
            )
            if res.status_code == 200:
                self.token = res.json().get("orbit_session_token")
                self.token_time = time.time()
                return self.token
            self._log(f"[B-HYVE ERROR] Login failed ({res.status_code}): {res.text}")
            return None

    def _keepalive_loop(self):
        while True:
            try:
                now_h = datetime.now().hour
                if 5 <= now_h <= 21:
                    self._get_token(force_refresh=True)
            except Exception:
                pass
            time.sleep(900)

    def trigger_spray(self, duration=BURST_SECONDS):
        def _burst():
            import ssl, websocket
            for attempt in range(1, 3):
                sock = None
                try:
                    t0 = time.time()
                    token = self._get_token(force_refresh=(attempt > 1))
                    if not token:
                        continue

                    sock = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
                    sock.connect(f"wss://api.orbitbhyve.com/v1/events?token={token}", timeout=4)

                    sock.send(json.dumps({
                        "event": "app_connection",
                        "orbit_session_token": token,
                        "subscribe_device_id": self.device_id
                    }))
                    time.sleep(0.15)

                    start_cmd = {
                        "event": "change_mode",
                        "mode": "manual",
                        "device_id": self.device_id,
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "stations": [{"station": self.station, "run_time": 1}]
                    }
                    sock.send(json.dumps(start_cmd))
                    time.sleep(0.15)
                    sock.send(json.dumps(start_cmd))
                    self._log(f"[B-HYVE] Spray ON (attempt {attempt}, {time.time()-t0:.2f}s)! Station {self.station} bursting {duration}s...")

                    time.sleep(duration)

                    stop_cmd = {
                        "event": "change_mode",
                        "mode": "auto",
                        "device_id": self.device_id,
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    }
                    for _ in range(3):
                        try:
                            sock.send(json.dumps(stop_cmd))
                            time.sleep(0.08)
                        except Exception:
                            pass

                    sock.close()
                    self._log("[B-HYVE] Spray OFF! Valve closed cleanly.")
                    return
                except Exception as e:
                    self._log(f"[B-HYVE ERROR] Attempt {attempt} failed: {e}")
                    if sock:
                        try:
                            sock.close()
                        except Exception:
                            pass

        threading.Thread(target=_burst, daemon=True).start()
        return True

bhyve = BHyveWS()

def trigger_alexa():
    mute_file = "/home/cameronlgreen/cockatoo_project/alexa.disabled"
    if os.path.exists(mute_file):
        print("[ALEXA] Voice alerts muted via toggle.", flush=True)
        return
    try:
        url = "https://www.virtualsmarthome.xyz/url_routine_trigger/activate.php?trigger=213a4ffc-9a2b-4b50-af9d-59aa09899ff6&token=1727a699-41a9-4d85-9e4e-74fa1938e3c9&response=html"
        requests.get(url, timeout=5)
        print("[ALEXA] Free Virtual Smart Home trigger dispatched successfully.", flush=True)
    except Exception as e:
        print(f"[ALEXA ERROR] {e}", flush=True)


def send_telegram_alert(img_path, caption):
    try:
        with open(img_path, "rb") as f:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto", data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption}, files={"photo": f}, timeout=10)
    except Exception:
        pass

def display_on_desktop(img_path):
    def _show():
        try:
            env = os.environ.copy()
            env["DISPLAY"] = ":0"
            env["XAUTHORITY"] = "/home/cameronlgreen/.Xauthority"
            # Close any previous trigger photo window before opening the new one
            subprocess.run(["pkill", "-f", "Cockatoo Alert"], stderr=subprocess.DEVNULL)
            time.sleep(0.1)
            viewer_code = (
                "import cv2; "
                f"img = cv2.imread({img_path!r}); "
                "cv2.namedWindow('Cockatoo Alert', cv2.WINDOW_NORMAL); "
                "cv2.resizeWindow('Cockatoo Alert', 800, 600); "
                "cv2.imshow('Cockatoo Alert', img); "
                "cv2.waitKey(0)"
            )
            subprocess.Popen(["python3", "-c", viewer_code], env=env)
        except Exception as e:
            print(f"[DISPLAY ERROR] {e}", flush=True)

    threading.Thread(target=_show, daemon=True).start()

def trigger_tapo_siren(duration=2.5):
    try:
        from pytapo import Tapo
        cam = Tapo("192.168.1.147", "cameron.l.green@bigpond.com", "CgT31473147O#")
        cam.startManualAlarm()
        time.sleep(duration)
        cam.stopManualAlarm()
        print(f"[TAPO SIREN] Fired {duration}s local camera alarm.", flush=True)
    except Exception as e:
        if "Temporary Suspension" in str(e):
            print("[TAPO SIREN] Camera API locked out (rate limited). Skipping siren.", flush=True)
        else:
            print(f"[TAPO SIREN ERROR] {e}", flush=True)
class RTSPStream:
    def __init__(self, url):
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
                time.sleep(0.04)

    def read(self):
        with self.lock:
            return None if self.frame is None else self.frame.copy()

def main():
    detector = YOLO(DETECTOR_MODEL_PATH)
    classifier = YOLO(CLASSIFIER_MODEL_PATH)
    stream = RTSPStream(RTSP_URL)
    time.sleep(2.0)
    print("[INFO] Two-stage pipeline and shield active.", flush=True)

    last_trigger = 0.0
    last_safe_bird_time = 0.0
    last_species_log = {}
    consecutive_target_hits = 0
    target_first_seen_time = None
    last_bird_seen_time = 0.0
    interim_audio_fired = False

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
        feeder_roi = frame[int(h*0.15):int(h*1.00), int(w*0.00):int(w*1.00)]
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

        if (now - last_bird_seen_time) > 3.0:
            print(f"[{ts}] [ARRIVAL] Bird landed on feeder (box {crops[0][1]}x{crops[0][2]}px)", flush=True)
        last_bird_seen_time = now

        candidates = []
        frame_has_safe = False
        safe_msg = ""

        clahe = cv2.createCLAHE(clipLimit=1.8, tileGridSize=(4, 4))
        for b_crop, bw, bh in crops:
            lab = cv2.cvtColor(b_crop, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            norm_crop = cv2.cvtColor(cv2.merge((clahe.apply(l), a, b)), cv2.COLOR_LAB2BGR)
            res = classifier(norm_crop, imgsz=224, verbose=False)[0]
            top1 = res.names[res.probs.top5[0]].lower()
            top1_c = float(res.probs.top1conf)
            top2, top2_c = "", 0.0
            if len(res.probs.top5) > 1:
                top2 = res.names[res.probs.top5[1]].lower()
                top2_c = float(res.probs.data[res.probs.top5[1]])

            # Check if king_parrot appears anywhere in top5 with >= 3% confidence
            kp_in_top5 = any(
                res.names[idx].lower() == "king_parrot" and float(res.probs.data[idx]) >= 0.12
                for idx in res.probs.top5
            )

            # Physical HSV color guard: Galahs are pastel pink/grey, NEVER bright scarlet red or green
            hsv_crop = cv2.cvtColor(b_crop, cv2.COLOR_BGR2HSV)
            h_ch, s_ch, v_ch = cv2.split(hsv_crop)
            bright_red_mask = ((h_ch <= 4) | (h_ch >= 176)) & (s_ch >= 195) & (v_ch >= 70)
            green_mask = (h_ch >= 35) & (h_ch <= 85) & (s_ch >= 75) & (v_ch >= 45)
            has_vivid_red_or_green = (np.mean(bright_red_mask) > 0.14) or (np.mean(green_mask) > 0.10)

            if top1 == "galah" and top1_c < 0.95 and (kp_in_top5 or has_vivid_red_or_green):
                frame_has_safe = True
                safe_msg = f"Color/Top5 Guard blocked false GALAH ({top1_c*100:.1f}%) - Likely King Parrot"
                continue

            if top1 in ["rosella", "king_parrot"] and (now - last_species_log.get(top1, 0)) > 180.0:
                last_species_log[top1] = now
                dt_n = datetime.now()
                row = f"{dt_n:%Y-%m-%d %H:%M:%S},{dt_n:%Y-%m-%d},{dt_n:%H:%M:%S},{dt_n.hour},{top1},{top1_c:.3f}\n"
                open("/home/cameronlgreen/cockatoo_project/feeder_visits.csv", "a").write(row)
                if top1 == "king_parrot":
                    kp_img = f"/home/cameronlgreen/cockatoo_project/king_parrot_visits/kp_{dt_n:%Y-%m-%d_%H-%M-%S}_{top1_c*100:.0f}pct.jpg"
                    cv2.imwrite(kp_img, frame)
            if top1 in SAFE_SPECIES and (top1 != "rosella" or top1_c >= 0.78):
                frame_has_safe = True
                safe_msg = f"Primary is {top1.upper()} ({top1_c*100:.1f}%)"
            elif top2 in SAFE_SPECIES and top2_c >= SAFE_RUNNER_THRESHOLD and top1 not in TARGET_SPECIES:
                frame_has_safe = True
                safe_msg = f"Runner-up is {top2.upper()} ({top2_c*100:.1f}%)"

            candidates.append({"name": top1, "conf": top1_c, "dims": (bw, bh)})

        if len(candidates) > 0:
            last_bird_seen_time = now
            if target_first_seen_time is None:
                target_first_seen_time = now
        elif (now - last_bird_seen_time) > 2.0:
            target_first_seen_time = None

        if frame_has_safe:
            last_safe_bird_time = now
            consecutive_target_hits = 0
            print(f"[{ts}] [SAFE BIRD VETO] {safe_msg} - Suppressed.", flush=True)
            time.sleep(0.1)
            continue

        if (now - last_safe_bird_time) < SAFE_LATCH_SECONDS:
            print(f"[{ts}] [SAFE BIRD VETO] Latch active ({now - last_safe_bird_time:.1f}s) - Suppressed.", flush=True)
            time.sleep(0.1)
            continue

        target = None
        for cand in candidates:
            req_conf = 0.65 if cand["name"] == "cockatoo" else 0.85
            if cand["name"] in TARGET_SPECIES and cand["conf"] >= req_conf:
                target = cand
                break

        if not target:
            consecutive_target_hits = 0

        if target:
            consecutive_target_hits += 1
            if consecutive_target_hits < 2:
                time.sleep(0.04)
                continue
            if (now - last_trigger) > COOLDOWN_SECONDS:
                bhyve.trigger_spray(duration=BURST_SECONDS)
                last_trigger = time.time()
                consecutive_target_hits = 0
                sp, cf = target["name"], target["conf"]
                reaction_time = (now - target_first_seen_time) if target_first_seen_time else 0.0
                print(f"[{ts}] [BENCHMARK] Elapsed arrival-to-spray: {reaction_time:.2f}s", flush=True)
                print(f"[{ts}] [ALERT] TARGET: {sp.upper()} ({cf*100:.1f}%)! SPRAYING...", flush=True)
                target_first_seen_time = None
                interim_audio_fired = False
                hit_path = os.path.join(TRIGGER_DIR, f"hit_{datetime.now().strftime('%d%b_%H-%M-%S')}_{sp}.jpg")
                cv2.imwrite(hit_path, feeder_roi)
                threading.Thread(target=trigger_alexa, daemon=True).start()
                threading.Thread(target=send_telegram_alert, args=(hit_path, f"🚨 Sprayed {sp.upper()} ({cf*100:.1f}%) | Delay: {reaction_time:.2f}s"), daemon=True).start()
                display_on_desktop(hit_path)
            else:
                elapsed_since_spray = now - last_trigger
                remaining = COOLDOWN_SECONDS - elapsed_since_spray
                print(f"[{ts}] [SUSTAINED PRESENCE] Target lingering on tray ({remaining:.1f}s until next burst).", flush=True)
                if elapsed_since_spray > (BURST_SECONDS + 4.0) and not interim_audio_fired:
                    interim_audio_fired = True
                    print(f"[{ts}] [HARASSMENT] Bird stayed post-spray -> firing Tapo camera siren...", flush=True)
                    threading.Thread(target=trigger_tapo_siren, args=(2.0,), daemon=True).start()

        time.sleep(0.04)

if __name__ == "__main__":
    main()
