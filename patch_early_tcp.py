path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

# 1. Ensure TCP option is set right after 'import os'
if 'os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"' not in code[:200]:
    code = code.replace("import os\n", "import os\nos.environ[\"OPENCV_FFMPEG_CAPTURE_OPTIONS\"] = \"rtsp_transport;tcp\"\n", 1)

# 2. Configure buffer size = 1 in RTSPStream to eliminate lag and corrupted backlog frames
old_init = "self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)"
new_init = """self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)"""

if old_init in code and "self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)" not in code:
    code = code.replace(old_init, new_init)

with open(path, "w") as f:
    f.write(code)

print("SUCCESS: Early TCP capture option and low-latency buffer patched.")
