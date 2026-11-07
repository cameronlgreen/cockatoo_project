import cv2
import sys

TAPO_USER = "cockatoo"
TAPO_PASS = "cockatoo1234"
TAPO_IP   = "192.168.1.147"

# stream2 (lower res) is ideal for real-time processing
RTSP_URL = f"rtsp://{TAPO_USER}:{TAPO_PASS}@{TAPO_IP}:554/stream2"

print(f"Connecting to Tapo stream at {TAPO_IP}...")
cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("Error: Could not open RTSP video stream. Check camera network connection.")
    sys.exit(1)

ret, frame = cap.read()
if ret:
    cv2.imwrite("tapo_live_frame.jpg", frame)
    print("Success! Captured a live frame and saved to 'tapo_live_frame.jpg'.")
else:
    print("Error: Connected, but failed to retrieve a video frame.")

cap.release()
