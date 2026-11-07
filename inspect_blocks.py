import os, glob, cv2, numpy as np
from datetime import datetime

inbox = os.path.expanduser("~/cockatoo_project/training_data/inbox")
files = sorted(glob.glob(os.path.join(inbox, "*.jpg")), key=os.path.getmtime)

blocks = {
    "09:40s": [],
    "12:20s": [],
    "13:40s": [],
    "14:10s": [],
    "16:20s": []
}

for f in files:
    t = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%H:%M")[:-1] + "0s"
    if t in blocks and len(blocks[t]) < 4:
        blocks[t].append(f)

header_b = "Block"
header_fn = "Filename"
header_sz = "Size"
print(f"{header_b:<10} | {header_fn:<32} | {header_sz:<10} | Dominant Traits")
print("-" * 75)

for b_name, b_files in blocks.items():
    for f in b_files:
        img = cv2.imread(f)
        if img is None:
            continue
        h, w = img.shape[:2]
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        tot = h * w

        w_px = np.sum(cv2.inRange(hsv, (0, 0, 140), (180, 50, 255)) > 0) / tot
        g_px = np.sum(cv2.inRange(hsv, (35, 60, 45), (85, 255, 255)) > 0) / tot
        b_px = np.sum(cv2.inRange(hsv, (92, 70, 45), (130, 255, 255)) > 0) / tot
        r_px = (np.sum(cv2.inRange(hsv, (0, 90, 60), (10, 255, 255)) > 0) + 
                np.sum(cv2.inRange(hsv, (168, 90, 60), (180, 255, 255)) > 0)) / tot
        p_px = np.sum(cv2.inRange(hsv, (140, 35, 75), (178, 160, 255)) > 0) / tot
        grey_px = np.sum(cv2.inRange(hsv, (0, 0, 50), (180, 45, 175)) > 0) / tot

        traits = []
        if w_px > 0.25: traits.append(f"White:{w_px:.0%}")
        if g_px > 0.15: traits.append(f"Green:{g_px:.0%}")
        if b_px > 0.01: traits.append(f"Blue:{b_px:.0%}")
        if r_px > 0.05: traits.append(f"Red:{r_px:.0%}")
        if p_px > 0.05: traits.append(f"Pink:{p_px:.0%}")
        if grey_px > 0.20: traits.append(f"Grey:{grey_px:.0%}")

        trait_str = ", ".join(traits) if traits else "Indeterminate"
        print(f"{b_name:<10} | {os.path.basename(f):<32} | {w}x{h:<7} | {trait_str}")
