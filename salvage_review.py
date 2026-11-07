import os, glob, shutil, cv2, random
import numpy as np

REVIEW = os.path.expanduser("~/cockatoo_project/training_data/review")
DATASET = os.path.expanduser("~/cockatoo_project/dataset")

images = glob.glob(os.path.join(REVIEW, "*.jpg"))
print(f"Scanning {len(images)} images in review folder...")

salvaged = {'cockatoo': 0, 'galah': 0, 'rosella': 0, 'unresolved': 0}

for p in images:
    img = cv2.imread(p)
    if img is None:
        continue
    h, w = img.shape[:2]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    total_px = h * w

    m_white = cv2.inRange(hsv, np.array([0, 0, 110]), np.array([180, 80, 255]))
    m_pink = cv2.inRange(hsv, np.array([135, 30, 60]), np.array([180, 180, 255]))
    m_red = cv2.inRange(hsv, np.array([0, 70, 50]), np.array([12, 255, 255]))
    m_grey = cv2.inRange(hsv, np.array([0, 0, 45]), np.array([180, 55, 185]))
    m_blue = cv2.inRange(hsv, np.array([90, 60, 40]), np.array([130, 255, 255]))

    w_ratio = np.sum(m_white > 0) / total_px
    p_ratio = np.sum(m_pink > 0) / total_px
    r_ratio = np.sum(m_red > 0) / total_px
    g_ratio = np.sum(m_grey > 0) / total_px
    b_ratio = np.sum(m_blue > 0) / total_px

    assigned = None
    # Cockatoos: high white, minimal red/blue/pink
    if w_ratio >= 0.22 and r_ratio < 0.02 and b_ratio < 0.01 and p_ratio < 0.03:
        assigned = 'cockatoo'
    # Galahs: grey mantle + pink breast, zero blue
    elif b_ratio < 0.005 and ((p_ratio >= 0.03 and g_ratio >= 0.18) or (p_ratio >= 0.08)):
        assigned = 'galah'
    # Straggler Rosellas: any red with blue or strong red
    elif r_ratio >= 0.05 or b_ratio >= 0.01:
        assigned = 'rosella'

    fname = os.path.basename(p)
    if assigned:
        split = "val" if random.random() < 0.20 else "train"
        shutil.move(p, os.path.join(DATASET, split, assigned, fname))
        salvaged[assigned] += 1
    else:
        salvaged['unresolved'] += 1

print("\n--- Salvage Complete ---")
for k, v in salvaged.items():
    print(f"  {k}: {v}")
