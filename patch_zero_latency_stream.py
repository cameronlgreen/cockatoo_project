path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

old_rtsp_block = """    def _reader(self):
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
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    failed_count = 0
                continue
            failed_count = 0
            with self.lock:
                self.frame = frame"""

new_rtsp_block = """    def _reader(self):
        failed_count = 0
        while self.running:
            # Rapidly flush stale frames from buffer
            if not self.cap.grab():
                failed_count += 1
                time.sleep(0.04)
                if failed_count > 50:
                    print("[RTSP] Stream stalled, reconnecting...", flush=True)
                    self.cap.release()
                    time.sleep(1.0)
                    self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    failed_count = 0
                continue

            failed_count = 0
            # Retrieve and decode only the latest frame
            ret, frame = self.cap.retrieve()
            if ret and frame is not None:
                with self.lock:
                    self.frame = frame"""

if old_rtsp_block in code:
    code = code.replace(old_rtsp_block, new_rtsp_block)
    with open(path, "w") as f:
        f.write(code)
    print("SUCCESS: Zero-latency RTSP frame flusher installed.")
else:
    print("ERROR: Could not match old _reader block.")
