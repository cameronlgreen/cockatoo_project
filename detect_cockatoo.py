import cv2
import numpy as np
from ultralytics import YOLO

def evaluate_frame(image_path, model):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Unable to load image {image_path}")
        return False

    results = model(img, verbose=False)
    cockatoo_detected = False

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            label = model.names[cls_id]

            # Gate 1: Must be detected as a bird with reasonable confidence
            if label == 'bird' and conf >= 0.35:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # Ensure valid crop boundaries
                h, w, _ = img.shape
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                crop = img[y1:y2, x1:x2]

                if crop.size == 0:
                    continue

                # Gate 2: HSV Plumage Analysis (White Body)
                hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
                lower_white = np.array([0, 0, 140])
                upper_white = np.array([180, 60, 255])

                mask_white = cv2.inRange(hsv, lower_white, upper_white)
                white_ratio = np.sum(mask_white > 0) / (crop.shape[0] * crop.shape[1])

                print(f"Bird detected (conf: {conf:.2f}) | White plumage ratio: {white_ratio:.1%}")

                # Target cockatoos have substantial white surface area
                if white_ratio >= 0.30:
                    print(">>> TARGET CONFIRMED: Sulphur-crested Cockatoo! Triggering spray. <<<")
                    cockatoo_detected = True
                else:
                    print("--- NON-TARGET BIRD: Low white ratio, ignoring. ---")

    if not cockatoo_detected:
        print("No target birds to deter.")

    return cockatoo_detected

if __name__ == "__main__":
    yolo = YOLO('yolov8n.pt')
    
    print("--- Testing Synthetic Cockatoo ---")
    evaluate_frame('synthetic_cockatoo.jpg', yolo)
    
    print("\n--- Testing Non-Cockatoo Bird ---")
    evaluate_frame('test_cockatoo.jpg', yolo)
