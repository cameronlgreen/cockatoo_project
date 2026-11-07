import os, glob, shutil, cv2

INBOX = os.path.expanduser("~/cockatoo_project/training_data/inbox")
BASE = os.path.expanduser("~/cockatoo_project/dataset/train")

targets = {
    ord('c'): os.path.join(BASE, "cockatoo"),
    ord('g'): os.path.join(BASE, "galah"),
    ord('l'): os.path.join(BASE, "lorikeet"),
    ord('r'): os.path.join(BASE, "rosella"),
}

for p in targets.values():
    os.makedirs(p, exist_ok=True)

files = sorted(glob.glob(os.path.join(INBOX, "*.jpg")), key=os.path.getmtime)
print(f"Loaded {len(files)} files. Controls: [c]=Cockatoo, [g]=Galah, [l]=Lorikeet, [r]=Rosella, [d/space]=Skip/Trash, [q]=Quit")

for f in files:
    img = cv2.imread(f)
    if img is None: continue
    
    # Scale up for easy viewing
    display = cv2.resize(img, (250, 250), interpolation=cv2.INTER_NEAREST)
    cv2.imshow("Labeler (c/g/l/r/d/q)", display)
    key = cv2.waitKey(0) & 0xFF
    
    if key == ord('q'):
        break
    elif key in targets:
        shutil.move(f, os.path.join(targets[key], os.path.basename(f)))
    elif key in [ord('d'), 32]: # d or space bar to delete/skip
        os.remove(f)

cv2.destroyAllWindows()
