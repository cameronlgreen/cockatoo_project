import os, cv2
from ultralytics import YOLO

proj = "/home/cameronlgreen/cockatoo_project"
crop_path = os.path.join(proj, "king_parrot_visits", "cropped_for_training", "kp_2026-11-15_07-26-18_crop.jpg")
full_path = os.path.join(proj, "king_parrot_visits", "kp_2026-11-15_07-26-18_false_galah_fix.jpg")

cls_model = YOLO(os.path.join(proj, "runs/classify/bird_classifier_v1/weights/best.pt"))
det_model = YOLO(os.path.join(proj, "yolov8n.pt"))

crop = cv2.imread(crop_path)
res = cls_model(crop, imgsz=224, verbose=False)[0]
top5 = [(res.names[i], round(float(res.probs.data[i]) * 100, 1)) for i in res.probs.top5]
print("Stage 2 Classifier Top-5 on actual King Parrot crop:", top5)

img = cv2.imread(full_path)
h, w = img.shape[:2]
wider_roi = img[int(h*0.21):int(h*1.00), int(w*0.45):int(w*1.00)]
det = det_model(wider_roi, imgsz=480, conf=0.25, verbose=False)[0]
for b in (det.boxes or []):
    print(f"Wider ROI detection: {det.names[int(b.cls[0])]} conf={float(b.conf[0]):.2f}")
