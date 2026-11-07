import os
import glob
import shutil
import random
import cv2
import numpy as np

INBOX = os.path.expanduser("~/cockatoo_project/training_data/inbox")
BASE_DATASET = os.path.expanduser("~/cockatoo_project/dataset")
REVIEW_DIR = os.path.expanduser("~/cockatoo_project/training_data/review")

os.makedirs(REVIEW_DIR, exist_ok=True)
for split in ['train', 'val']:
    for cls in ['cockatoo', 'galah', 'lorikeet', 'rosella']:
        os.makedirs(os.path.join(BASE_DATASET, split, cls), exist_ok=True)

images = glob.glob(os.path.join(INBOX, "*.jpg"))
print(f"Analyzing and sorting {len(images)} images...")

counts = {'cockatoo': 0, 'galah': 0, 'lorikeet': 0, 'rosella': 0, 'review': 0, 'discard': 0}

for img_path in images:
    img = cv2.imread(img_path)
    if img is None:
        os.remove(img_path)
        counts['discard'] += 1
        continue

    h, w = img.shape[:2]
    if h < 45 or w < 45:
        os.remove(img_path)
        counts['discard'] += 1
        continue

    # Sample core
    pad_y, pad_x = int(h * 0.15), int(w * 0.15)
    core = img[pad_y:h - pad_y, pad_x:w - pad_x]
    if core.size == 0:
        core = img

    hsv = cv2.cvtColor(core, cv2.COLOR_BGR2HSV)
    total_px = core.shape[0] * core.shape[1]

    # Quick metric masks
    m_white = cv2.inRange(hsv, np.array([0, 0, 120]), np.array([180, 70, 255]))
    m_yellow = cv2.inRange(hsv, np.array([18, 90, 110]), np.array([36, 255, 255]))
    m_green = cv2.inRange(hsv, np.array([35, 60, 45]), np.array([85, 255, 255]))
    m_blue = cv2.inRange(hsv, np.array([92, 70, 45]), np.array([130, 255, 255]))
    m_red1 = cv2.inRange(hsv, np.array([0, 90, 60]), np.array([10, 255, 255]))
    m_red2 = cv2.inRange(hsv, np.array([168, 90, 60]), np.array([180, 255, 255]))
    m_pink = cv2.inRange(hsv, np.array([140, 35, 75]), np.array([178, 160, 255]))
    m_grey = cv2.inRange(hsv, np.array([0, 0, 50]), np.array([180, 45, 175]))

    w_ratio = np.sum(m_white > 0) / total_px
    y_px = np.sum(m_yellow > 0)
    g_ratio = np.sum(m_green > 0) / total_px
    b_ratio = np.sum(m_blue > 0) / total_px
    r_ratio = (np.sum(m_red1 > 0) + np.sum(m_red2 > 0)) / total_px
    p_ratio = np.sum(m_pink > 0) / total_px
    grey_ratio = np.sum(m_grey > 0) / total_px

    assigned = None

    # Lorikeet
    if g_ratio >= 0.18:
        assigned = 'lorikeet'
    # Crimson Rosella (Strong Red OR Distinct Blue)
    elif r_ratio >= 0.08 or (b_ratio >= 0.015 and (r_ratio >= 0.02 or p_ratio >= 0.02)):
        assigned = 'rosella'
    # Cockatoo (High White, Yellow Crest, NO Blue/Red)
    elif (w_ratio >= 0.25 or y_px >= 250) and r_ratio < 0.015 and b_ratio < 0.005 and p_ratio < 0.02:
        assigned = 'cockatoo'
    # Galah (Grey + Pink breast, NO Blue)
    elif b_ratio < 0.005 and ((p_ratio >= 0.05 and grey_ratio >= 0.20) or (p_ratio >= 0.15)):
        assigned = 'galah'

    fname = os.path.basename(img_path)
    if assigned:
        split = "val" if random.random() < 0.20 else "train"
        dest = os.path.join(BASE_DATASET, split, assigned, fname)
        shutil.move(img_path, dest)
        counts[assigned] += 1
    else:
        # Move unclassified crops to review for manual check
        dest = os.path.join(REVIEW_DIR, fname)
        shutil.move(img_path, dest)
        counts['review'] += 1

print("\n--- Auto-Sort Complete ---")
for k, v in counts.items():
    print(f"  {k}: {v}")
