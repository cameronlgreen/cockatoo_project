path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

# Define the start and end markers for replacement
old_section_start = "            # 1. White Plumage Mask (Cockatoos)"
old_section_end = "        if target_hit and cockatoo_candidate is not None:"

new_section = """            # 1. White Plumage Mask (Cockatoos)
            mask_white = cv2.inRange(hsv, np.array([0, 0, 115]), np.array([180, 75, 255]))
            white_ratio = np.sum(mask_white > 0) / total_pixels

            # 2. Yellow Crest Mask
            mask_yellow = cv2.inRange(hsv, np.array([20, 80, 100]), np.array([35, 255, 255]))
            yellow_pixels = int(np.sum(mask_yellow > 0))

            # 3. Rose/Pink Plumage Mask (Galah Breast)
            mask_rose = cv2.inRange(hsv, np.array([150, 50, 70]), np.array([178, 255, 255]))
            pink_ratio = np.sum(mask_rose > 0) / total_pixels

            # 4. Grey Feather Mask (Galah Back/Wings: Low Saturation, Mid Value)
            mask_grey = cv2.inRange(hsv, np.array([0, 0, 60]), np.array([180, 45, 190]))
            grey_ratio = np.sum(mask_grey > 0) / total_pixels

            # 5. Crimson Red Mask (Rosella)
            mask_red1 = cv2.inRange(hsv, np.array([0, 120, 80]), np.array([10, 255, 255]))
            mask_red2 = cv2.inRange(hsv, np.array([170, 120, 80]), np.array([180, 255, 255]))
            red_ratio = (np.sum(mask_red1 > 0) + np.sum(mask_red2 > 0)) / total_pixels

            # 6. Green Plumage Mask (Rainbow Lorikeet Back/Wings)
            mask_green = cv2.inRange(hsv, np.array([35, 80, 60]), np.array([85, 255, 255]))
            green_ratio = np.sum(mask_green > 0) / total_pixels

            # 7. Cobalt Blue Mask (Lorikeet Head / Rosella Cheeks)
            mask_blue = cv2.inRange(hsv, np.array([95, 100, 60]), np.array([130, 255, 255]))
            blue_ratio = np.sum(mask_blue > 0) / total_pixels

            # ==========================================
            # --- 5-BIRD DISCRIMINATION PIPELINE ---
            # ==========================================

            # [CATEGORY 3: ROSELLA] (Immunity)
            if red_ratio >= 0.040:
                print(f"[{timestamp}] [SAFE BIRD - ROSELLA] (Red: {red_ratio:.1%}, Blue: {blue_ratio:.1%}, Size: {bw}x{bh}px) - Pass", flush=True)
                continue

            # [CATEGORY 4: LORIKEET] (Immunity)
            if green_ratio >= 0.060 or (blue_ratio >= 0.020 and red_ratio < 0.030):
                print(f"[{timestamp}] [SAFE BIRD - LORIKEET] (Green: {green_ratio:.1%}, Blue: {blue_ratio:.1%}, Size: {bw}x{bh}px) - Pass", flush=True)
                continue

            # [CATEGORY 1: COCKATOO] (Deterrent Target)
            if yellow_pixels >= 40 and white_ratio >= 0.15:
                target_hit = True
                target_type = f"Cockatoo (Crest: {yellow_pixels}px, White: {white_ratio:.1%})"
            elif white_ratio >= 0.18 and (bw >= 95 or bh >= 95):
                target_hit = True
                target_type = f"Cockatoo ({bw}x{bh}px, White: {white_ratio:.1%})"
            elif (bw >= 110 and bh >= 110) and white_ratio >= 0.14 and pink_ratio < 0.02:
                target_hit = True
                target_type = f"Cockatoo Shaded ({bw}x{bh}px, White: {white_ratio:.1%})"

            # [CATEGORY 2: GALAH] (Deterrent Target: Pink > 4% + Grey > 2%)
            elif (pink_ratio >= 0.040 and grey_ratio > 0.020) or (pink_ratio >= 0.080 and (bw >= 95 or bh >= 95)):
                target_hit = True
                target_type = f"Galah ({bw}x{bh}px, Rose: {pink_ratio:.1%}, Grey: {grey_ratio:.1%})"

            # [CATEGORY 5: OTHER] (Mynas, Sparrows, Doves, Wattlebirds)
            else:
                print(f"[{timestamp}] [SAFE BIRD - OTHER] ({label}, Conf: {conf:.2f}, Size: {bw}x{bh}px, Grey: {grey_ratio:.1%}) - Pass", flush=True)

            if target_hit:
                cockatoo_candidate = (white_ratio, pink_ratio, target_type)
                break
"""

if old_section_start in code and old_section_end in code:
    idx1 = code.find(old_section_start)
    idx2 = code.find(old_section_end)
    code = code[:idx1] + new_section + code[idx2:]
    with open(path, "w") as f:
        f.write(code)
    print("SUCCESS: 5-Bird classification pipeline patched.")
else:
    print("ERROR: Could not locate markers in file.")
