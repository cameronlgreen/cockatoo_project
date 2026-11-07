import cv2
import os
import glob
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

# 1. Process the previous Rosella hit image to extract the exact bird bounding box
rosella_imgs = glob.glob(os.path.expanduser("~/cockatoo_project/detections/*1791665192*.jpg"))
if not rosella_imgs:
    rosella_imgs = glob.glob(os.path.expanduser("~/cockatoo_project/*1791665192*.jpg"))

if rosella_imgs:
    img_path = rosella_imgs[0]
    frame = cv2.imread(img_path)
    results = model(frame, verbose=False)
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            if model.names[cls_id] == "bird":
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                crop = frame[y1:y2, x1:x2]
                out_path = os.path.expanduser("~/cockatoo_project/yolo_crop_rosella.jpg")
                cv2.imwrite(out_path, crop)
                print(f"Saved exact YOLO bird crop ({x2-x1}x{y2-y1}px) to: {out_path}")

# 2. Check the fresh empty painted tray snapshot
fresh_path = os.path.expanduser("~/cockatoo_project/painted_tray.jpg")
if os.path.exists(fresh_path):
    frame = cv2.imread(fresh_path)
    results = model(frame, verbose=False)
    bird_found = False
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            if model.names[cls_id] == "bird":
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                crop = frame[y1:y2, x1:x2]
                out_path = os.path.expanduser("~/cockatoo_project/yolo_crop_live_bird.jpg")
                cv2.imwrite(out_path, crop)
                print(f"Bird detected! Saved live YOLO crop to: {out_path}")
                bird_found = True
    
    if not bird_found:
        print("No bird currently in painted_tray.jpg (feeder empty).")
        # Draw the feeder analysis region defined in live_monitor.py
        h, w = frame.shape[:2]
        # Tray region: bottom-center where feeder sits
        y1, y2 = int(h * 0.55), int(h * 0.88)
        x1, x2 = int(w * 0.15), int(w * 0.85)
        crop = frame[y1:y2, x1:x2]
        out_path = os.path.expanduser("~/cockatoo_project/tray_roi_crop.jpg")
        cv2.imwrite(out_path, crop)
        print(f"Saved tight tray region of interest ({x2-x1}x{y2-y1}px) to: {out_path}")

print("Done.")
