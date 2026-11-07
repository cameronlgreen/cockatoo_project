path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

# 1. Clean up mask overlap in HSV definitions
old_masks = """            # 3. Rose/Pink Plumage Mask (Galah Breast)
            mask_rose = cv2.inRange(hsv, np.array([150, 50, 70]), np.array([178, 255, 255]))
            pink_ratio = np.sum(mask_rose > 0) / total_pixels

            # 4. Grey Feather Mask (Galah Back/Wings: Low Saturation, Mid Value)
            mask_grey = cv2.inRange(hsv, np.array([0, 0, 60]), np.array([180, 45, 190]))
            grey_ratio = np.sum(mask_grey > 0) / total_pixels

            # 5. Crimson Red Mask (Rosella)
            mask_red1 = cv2.inRange(hsv, np.array([0, 120, 80]), np.array([10, 255, 255]))
            mask_red2 = cv2.inRange(hsv, np.array([170, 120, 80]), np.array([180, 255, 255]))
            red_ratio = (np.sum(mask_red1 > 0) + np.sum(mask_red2 > 0)) / total_pixels"""

new_masks = """            # 3. Rose/Pink Plumage Mask (Galah Breast: Hue 145-172)
            mask_rose = cv2.inRange(hsv, np.array([145, 40, 70]), np.array([172, 255, 255]))
            pink_ratio = np.sum(mask_rose > 0) / total_pixels

            # 4. Grey Feather Mask (Galah Back/Wings: Low Saturation, Mid Value)
            mask_grey = cv2.inRange(hsv, np.array([0, 0, 60]), np.array([180, 50, 190]))
            grey_ratio = np.sum(mask_grey > 0) / total_pixels

            # 5. Crimson Red Mask (Rosella: Hue 0-10 and 175-180 only, saturated)
            mask_red1 = cv2.inRange(hsv, np.array([0, 130, 80]), np.array([10, 255, 255]))
            mask_red2 = cv2.inRange(hsv, np.array([175, 130, 80]), np.array([180, 255, 255]))
            red_ratio = (np.sum(mask_red1 > 0) + np.sum(mask_red2 > 0)) / total_pixels"""

# 2. Re-tune the logic pipeline
old_pipeline = """            # 1. IMMUNITY SHIELD: CRIMSON ROSELLA (Vivid Red Plumage or Blue Cheeks)
            # Evaluated FIRST: Crimson Rosellas carry red/pink/blue and tolerate dusk/mantle shadow grey up to 24%.
            is_rosella = (red_ratio >= 0.018 or pink_ratio >= 0.025 or blue_ratio >= 0.015) and (grey_ratio < 0.25)
            if is_rosella:
                print(f"[{timestamp}] [SAFE BIRD - ROSELLA] (Red: {red_ratio:.1%}, Pink: {pink_ratio:.1%}, Grey: {grey_ratio:.1%}, Blue: {blue_ratio:.1%}, Size: {bw}x{bh}px) - Pass", flush=True)
                continue

            # 2. PRIORITY PEST CHECK: GALAH (Substantial Silver-Grey Body, ZERO Blue/Crimson)
            # True Galahs have silver-grey bodies (>=24%). Shadowed Rosellas are shielded above.
            is_galah = (grey_ratio >= 0.24) and (pink_ratio >= 0.035 or white_ratio >= 0.12) and (blue_ratio < 0.012) and (red_ratio < 0.020)
            if is_galah and (bw >= 65 or bh >= 65):
                target_hit = True
                target_type = f"Galah ({bw}x{bh}px, Grey:{grey_ratio:.1%}, Pink:{pink_ratio:.1%})"
                cockatoo_candidate = (white_ratio, pink_ratio, target_type)
                break"""

new_pipeline = """            # 1. PRIORITY PEST CHECK: GALAH (Pink Breast + Grey Body, ZERO Blue)
            # Checked before Rosella so pink breast does not mimic red.
            # Galah has strong pink breast (>=4.0%), noticeable grey (>=10%), and no blue (<1.2%).
            is_galah = (pink_ratio >= 0.040 and grey_ratio >= 0.09) and (blue_ratio < 0.012)
            if is_galah and (bw >= 65 or bh >= 65):
                target_hit = True
                target_type = f"Galah ({bw}x{bh}px, Grey:{grey_ratio:.1%}, Pink:{pink_ratio:.1%})"
                cockatoo_candidate = (white_ratio, pink_ratio, target_type)
                break

            # 2. IMMUNITY SHIELD: CRIMSON ROSELLA (Deep Red Plumage and/or Blue Cheek/Wings)
            # Rosellas must have genuine crimson red (>=3.0%) or distinct blue (>=1.5%).
            # Pink alone NEVER qualifies as a Rosella.
            is_rosella = (red_ratio >= 0.030 or blue_ratio >= 0.015) and (pink_ratio < 0.060 or red_ratio > pink_ratio)
            if is_rosella:
                print(f"[{timestamp}] [SAFE BIRD - ROSELLA] (Red: {red_ratio:.1%}, Pink: {pink_ratio:.1%}, Grey: {grey_ratio:.1%}, Blue: {blue_ratio:.1%}, Size: {bw}x{bh}px) - Pass", flush=True)
                continue"""

if old_masks in code:
    code = code.replace(old_masks, new_masks)
    print("HSV masks updated.")
else:
    print("Could not match old masks block cleanly.")

if old_pipeline in code:
    code = code.replace(old_pipeline, new_pipeline)
    print("Pipeline logic updated.")
else:
    print("Could not match old pipeline block cleanly.")

with open(path, "w") as f:
    f.write(code)
