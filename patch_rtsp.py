path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

old_rtsp = """# --- TAPO RTSP STREAM ---
class RTSPStream:
    def __init__(self, url):
        self.url = url
        self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
        self.lock = threading.Lock()
        self.running = True
        self.frame = None
        self.thread = threading.Thread(target=self._reader, daemon=True)
        self.thread.start()

    def _reader(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                time.sleep(0.05)
                continue
            with self.lock:
                self.frame = frame"""

new_rtsp = """# --- TAPO RTSP STREAM ---
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

class RTSPStream:
    def __init__(self, url):
        self.url = url
        self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
        self.lock = threading.Lock()
        self.running = True
        self.frame = None
        self.thread = threading.Thread(target=self._reader, daemon=True)
        self.thread.start()

    def _reader(self):
        failed_count = 0
        while self.running:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                failed_count += 1
                time.sleep(0.05)
                if failed_count > 40:
                    print("[RTSP] Stream stalled, reconnecting...", flush=True)
                    self.cap.release()
                    time.sleep(1.0)
                    self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
                    failed_count = 0
                continue
            failed_count = 0
            with self.lock:
                self.frame = frame"""

if old_rtsp in code:
    code = code.replace(old_rtsp, new_rtsp)
    with open(path, "w") as f:
        f.write(code)
    print("SUCCESS: RTSP TCP transport and auto-reconnect patched.")
else:
    print("Pattern match failed. Checking exact indentation...")
