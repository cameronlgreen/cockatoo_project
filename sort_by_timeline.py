import os, glob, shutil, random
import cv2, numpy as np
from datetime import datetime

INBOX = os.path.expanduser("~/cockatoo_project/training_data/inbox")
BASE_DATASET = os.path.expanduser("~/cockatoo_project/dataset")
OTHER_DIR = os.path.expanduser("~/cockatoo_project/training_data/other")

os.makedirs(OTHER_DIR, exist_ok=True)
for split in ['train', 'val']:
    for cls in ['cockatoo', 'galah', 'lorikeet', 'rosella']:
        os.makedirs(os.path.join(BASE_DATASET, split, cls), exist_ok=True)

files = glob.glob(os.path.join(INBOX, "*.jpg"))
print(f"Sorting {len(files)} inbox images using confirmed visit timeline...")

counts = {'galah': 0, 'rosella': 0, 'lorikeet': 0, 'cockatoo': 0, 'other': 0, 'unassigned': 0}

for f in files:
    fn = os.path.basename(f)
    try:
        epoch_raw = float(fn.split("_")[1])
        epoch_s = epoch_raw / 100.0 if epoch_raw > 1e11 else epoch_raw
        dt = datetime.fromtimestamp(epoch_s)
        time_str = dt.strftime("%H:%M")
    except Exception:
        counts['unassigned'] += 1
        continue

    assigned = None

    # 1. Morning Rosella visit (09:35 - 09:55)
    if "09:35" <= time_str <= "09:55":
        assigned = 'rosella'

    # 2. Midday Galah visit (12:15 - 12:45)
    elif "12:15" <= time_str <= "12:45":
        assigned = 'galah'

    # 3. Afternoon Galah visit (13:25 - 13:45)
    elif "13:25" <= time_str <= "13:45":
        assigned = 'galah'

    # 4. Magpie visit (13:50 - 14:05) -> quarantine to "other"
    elif "13:50" <= time_str <= "14:05":
        shutil.move(f, os.path.join(OTHER_DIR, fn))
        counts['other'] += 1
        continue

    # 5. Afternoon Galah visit (14:08 - 14:35)
    elif "14:08" <= time_str <= "14:35":
        assigned = 'galah'

    # 6. Late Afternoon Mixed visit (16:05 - 16:35) -> Rosella + Lorikeet
    elif "16:05" <= time_str <= "16:35":
        # Check if green (Rainbow Lorikeet) or red/blue (Rosella)
        img = cv2.imread(f)
        if img is not None:
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            tot = img.shape[0] * img.shape[1]
            green_px = np.sum(cv2.inRange(hsv, (35, 60, 45), (85, 255, 255)) > 0)
            if (green_px / tot) >= 0.15:
                assigned = 'lorikeet'
            else:
                assigned = 'rosella'
        else:
            assigned = 'rosella'

    if assigned:
        split = "val" if random.random() < 0.20 else "train"
        shutil.move(f, os.path.join(BASE_DATASET, split, assigned, fn))
        counts[assigned] += 1
    else:
        counts['unassigned'] += 1

print("\n--- Timeline Sorting Complete ---")
for k, v in counts.items():
    print(f"  {k}: {v}")
