import os, glob, cv2, numpy as np
from datetime import datetime

inbox = os.path.expanduser("~/cockatoo_project/training_data/inbox")
files = glob.glob(os.path.join(inbox, "*.jpg"))

afternoon_files = []
for f in files:
    try:
        raw = float(os.path.basename(f).split("_")[1])
        s = raw / 100.0 if raw > 1e11 else raw
        dt = datetime.fromtimestamp(s)
        if "16:10" <= dt.strftime("%H:%M") <= "16:35":
            afternoon_files.append((f, dt.strftime("%H:%M:%S")))
    except:
        pass

print(f"Total crops captured in 16:10-16:35 window: {len(afternoon_files)}")
print(f"{'Time':<10} | {'Filename':<32} | {'WxH':<8} | Key Color Readouts")
print("-" * 75)

for f, t_str in sorted(afternoon_files)[::50][:15]:
    img = cv2.imread(f)
    if img is None: continue
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

    print(f"{t_str:<10} | {os.path.basename(f):<32} | {w}x{h:<6} | White:{w_px:.0%}, Grey:{grey_px:.0%}, Pink:{p_px:.0%}, Red:{r_px:.0%}, Blue:{b_px:.0%}, Green:{g_px:.0%}")
