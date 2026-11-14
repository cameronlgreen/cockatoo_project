import os
import glob
import cv2
import numpy as np

USB_PATH = "/media/cameronlgreen/900A-E2C3"

INPUT_DIR = os.path.join(USB_PATH, "Damaged")
OUTPUT_DIR = os.path.join(USB_PATH, "Repaired")
os.makedirs(OUTPUT_DIR, exist_ok=True)

extensions = ("*.jpg", "*.jpeg", "*.png", "*.tif", "*.tiff", "*.bmp")
image_files = []
for ext in extensions:
    image_files.extend(glob.glob(os.path.join(INPUT_DIR, ext)))
    image_files.extend(glob.glob(os.path.join(INPUT_DIR, ext.upper())))

print(f"Found {len(image_files)} images to process...")

for filepath in image_files:
    filename = os.path.basename(filepath)
    img = cv2.imread(filepath)
    if img is None:
        print(f"Skipping unreadable file: {filename}")
        continue

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

    kernel = np.ones((5, 5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print(f"No photo detected in {filename}, skipping.")
        continue

    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)

    cropped = img[y:y+h, x:x+w]
    cv2.imwrite(os.path.join(OUTPUT_DIR, filename), cropped)
    print(f"Saved cropped: {filename} ({w}x{h})")

print("Done!")
