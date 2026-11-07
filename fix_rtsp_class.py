path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    lines = f.readlines()

# Locate 'class RTSPStream:' and 'def trigger_alexa():'
start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if line.strip().startswith("class RTSPStream:"):
        start_idx = i
    if line.strip().startswith("def trigger_alexa():") and start_idx is not None:
        end_idx = i
        break

if start_idx is not None and end_idx is not None:
    clean_block = [
        "class RTSPStream:\n",
        "    def __init__(self, url):\n",
        "        self.url = url\n",
        "        self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)\n",
        "        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)\n",
        "        self.lock = threading.Lock()\n",
        "        self.running = True\n",
        "        self.frame = None\n",
        "        self.thread = threading.Thread(target=self._reader, daemon=True)\n",
        "        self.thread.start()\n",
        "\n",
        "    def _reader(self):\n",
        "        failed_count = 0\n",
        "        while self.running:\n",
        "            ret, frame = self.cap.read()\n",
        "            if not ret or frame is None:\n",
        "                failed_count += 1\n",
        "                time.sleep(0.05)\n",
        "                if failed_count > 40:\n",
        "                    print(\"[RTSP] Stream stalled, reconnecting...\", flush=True)\n",
        "                    self.cap.release()\n",
        "                    time.sleep(1.0)\n",
        "                    self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)\n",
        "                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)\n",
        "                    failed_count = 0\n",
        "                continue\n",
        "            failed_count = 0\n",
        "            with self.lock:\n",
        "                self.frame = frame\n",
        "\n",
        "    def read(self):\n",
        "        with self.lock:\n",
        "            return self.frame.copy() if self.frame is not None else None\n",
        "\n"
    ]
    lines = lines[:start_idx] + clean_block + lines[end_idx:]
    with open(path, "w") as f:
        f.writelines(lines)
    print("SUCCESS: RTSPStream cleanly reconstructed.")
else:
    print(f"FAILED: start_idx={start_idx}, end_idx={end_idx}")
