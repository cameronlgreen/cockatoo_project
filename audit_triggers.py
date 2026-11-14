import os, glob, cv2, numpy as np
from ultralytics import YOLO

proj = "/home/cameronlgreen/cockatoo_project"
trig_dir = os.path.join(proj, "trigger_photos")
det_model = YOLO(os.path.join(proj, "yolov8n.pt"))
cls_model = YOLO(os.path.join(proj, "runs/classify/bird_classifier_v2/weights/best.pt"))

files = sorted(glob.glob(os.path.join(trig_dir, "*.jpg")) + glob.glob(os.path.join(trig_dir, "*.png")))
print(f"Scanning {len(files)} images in {trig_dir}...\n")

suspects = []
for f in files:
    fname = os.path.basename(f)
    img = cv2.imread(f)
    if img is None:
        continue
    h, w = img.shape[:2]

    # 1. Check updated right-hand feeder_roi
    roi = img[int(h*0.21):int(h*1.00), int(w*0.53):int(w*1.00)]
    det = det_model(roi, imgsz=480, conf=0.35, verbose=False)[0]

    bird_boxes = [b for b in (det.boxes or []) if det.names[int(b.cls[0])] == "bird"]
    if not bird_boxes:
        # Fallback: check full frame in case bird perched outside ROI
        det_full = det_model(img, imgsz=640, conf=0.40, verbose=False)[0]
        full_birds = [b for b in (det_full.boxes or []) if det_full.names[int(b.cls[0])] == "bird"]
        if not full_birds:
            print(f"[NO BIRD / BLANK]   {fname}")
            suspects.append((fname, img, "NO BIRD"))
            continue
        src_img, box = img, max(full_birds, key=lambda b: float(b.conf[0]))
        loc = "outside_ROI"
    else:
        src_img, box = roi, max(bird_boxes, key=lambda b: float(b.conf[0]))
        loc = "in_ROI"

    x1, y1, x2, y2 = map(int, box.xyxy[0])
    crop = src_img[y1:y2, x1:x2]
    std_val = float(np.std(crop)) if crop.size > 0 else 0.0

    # 2. Classify bird crop with active v2 model
    res = cls_model(crop, imgsz=224, verbose=False)[0]
    top3 = [(res.names[i], round(float(res.probs.data[i]) * 100, 1)) for i in res.probs.top5[:3]]
    top1_lbl, top1_pct = top3[0]

    # 3. Check physical HSV vivid red/green (King Parrot / Rosella / Lorikeet indicator)
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    red1 = cv2.inRange(hsv, (0, 110, 70), (10, 255, 255))
    red2 = cv2.inRange(hsv, (170, 110, 70), (180, 255, 255))
    green = cv2.inRange(hsv, (35, 90, 60), (85, 255, 255))
    vivid_pct = ((np.count_nonzero(red1 | red2) + np.count_nonzero(green)) / max(1, crop.shape[0] * crop.shape[1])) * 100

    safe_in_top3 = any(lbl in ("king_parrot", "rosella", "lorikeet", "magpie", "miner") and pct >= 10.0 for lbl, pct in top3)
    is_suspect = (
        std_val < 20.0
        or top1_lbl not in ("cockatoo", "galah", "pigeon")
        or top1_pct < 75.0
        or safe_in_top3
        or vivid_pct > 4.0
    )

    tag = "SAFE / FALSE TRIGGER" if is_suspect else "TARGET OK"
    print(f"[{tag:20s}] {fname} | {loc} | std={std_val:.1f} | vivid={vivid_pct:.1f}% | Top3={top3}")
    if is_suspect:
        suspects.append((fname, crop, f"{top1_lbl} {top1_pct}%"))

print(f"\nFound {len(suspects)} likely false triggers out of {len(files)} trigger photos.")
