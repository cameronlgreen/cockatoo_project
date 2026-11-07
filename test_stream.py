import os
import cv2

# Force FFmpeg backend to use TCP
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

RTSP_URL = "rtsp://cockatoo:cockatoo1234@192.168.1.147:554/stream2"

cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)

if not cap.isOpened():
    print("Failed to open stream.")
else:
    ret, frame = cap.read()
    if ret:
        print(f"Success! Captured frame with shape: {frame.shape}")
    else:
        print("Failed to read frame.")

cap.release()
