path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

# Replace the pink mask definition with pure magenta/rose
old_masks = """                    # 2. Pink Plumage Mask (Galah Protection)
                    mask_pink1 = cv2.inRange(hsv, np.array([155, 45, 100]), np.array([180, 255, 255]))
                    mask_pink2 = cv2.inRange(hsv, np.array([0, 45, 100]), np.array([12, 255, 255]))
                    pink_ratio = (np.sum(mask_pink1 > 0) + np.sum(mask_pink2 > 0)) / total_pixels"""

new_masks = """                    # 2. Rose/Magenta Plumage Mask (Strictly Galah Breast - Excludes Wood/Timber)
                    # Wood/stain is Hue 0-15; Galah breast is pure magenta/rose Hue 158-176, Sat >= 70
                    mask_rose = cv2.inRange(hsv, np.array([158, 70, 90]), np.array([176, 255, 255]))
                    pink_ratio = np.sum(mask_rose > 0) / total_pixels"""

# Replace the decision logic
old_logic = """                    # --- RATIO-BASED DISCRIMINATION ---
                    # Galah: Strong pink breast, OR pink is a large fraction of the white area
                    if pink_ratio >= 0.07 or (pink_ratio >= 0.030 and white_ratio <= (pink_ratio * 3.0)):
                        print(f"[{timestamp}] Galah detected (Pink: {pink_ratio:.1%}, White: {white_ratio:.1%}) -> Sparing friend.", flush=True)
                    # Cockatoo: Massive white plumage that overwhelms any faint reflection (4:1 ratio)
                    elif white_ratio >= 0.30 and white_ratio > (pink_ratio * 4.0):
                        cockatoo_candidate = (white_ratio, pink_ratio)"""

new_logic = """                    # --- DISCRIMINATION ---
                    # Galah: Has true rose-magenta breast plumage
                    if pink_ratio >= 0.045:
                        print(f"[{timestamp}] Galah detected (Rose: {pink_ratio:.1%}, White: {white_ratio:.1%}) -> Sparing friend.", flush=True)
                    # Cockatoo: Large white body, no rose plumage
                    elif white_ratio >= 0.25 and pink_ratio < 0.030:
                        cockatoo_candidate = (white_ratio, pink_ratio)"""

if old_masks in code:
    code = code.replace(old_masks, new_masks)
else:
    print("Warning: old_masks pattern not found cleanly.")

if old_logic in code:
    code = code.replace(old_logic, new_logic)
else:
    print("Warning: old_logic pattern not found cleanly.")

with open(path, "w") as f:
    f.write(code)

print("Patch applied.")
