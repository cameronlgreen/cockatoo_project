path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

old_rose_block = """            # 3. Rose/Magenta Plumage Mask (Galah Breast - ignores woodwork)
            mask_rose = cv2.inRange(hsv, np.array([158, 70, 90]), np.array([176, 255, 255]))
            pink_ratio = np.sum(mask_rose > 0) / total_pixels"""

new_rose_block = """            # 3. Rose/Magenta Plumage Mask (Galah Breast - ignores woodwork)
            mask_rose = cv2.inRange(hsv, np.array([158, 70, 90]), np.array([176, 255, 255]))
            pink_ratio = np.sum(mask_rose > 0) / total_pixels

            # 4. Rosella / Lorikeet Signature: Vivid Red & Blue
            mask_red1 = cv2.inRange(hsv, np.array([0, 130, 90]), np.array([10, 255, 255]))
            mask_red2 = cv2.inRange(hsv, np.array([170, 130, 90]), np.array([180, 255, 255]))
            red_ratio = (np.sum(mask_red1 > 0) + np.sum(mask_red2 > 0)) / total_pixels

            mask_blue = cv2.inRange(hsv, np.array([95, 110, 70]), np.array([130, 255, 255]))
            blue_ratio = np.sum(mask_blue > 0) / total_pixels"""

old_target_start = """            # --- TARGET IDENTIFICATION (COCKATOOS & GALAHS) ---"""

new_target_start = """            # --- SAFE BIRD IMMUNITY (ROSELLAS & LORIKEETS) ---
            if red_ratio >= 0.035 or blue_ratio >= 0.025:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] [SAFE BIRD] Rosella/Lorikeet identified (Red: {red_ratio:.1%}, Blue: {blue_ratio:.1%}, Size: {bw}x{bh}px) - Pass", flush=True)
                continue

            # --- TARGET IDENTIFICATION (COCKATOOS & GALAHS) ---"""

if old_rose_block in code and old_target_start in code:
    code = code.replace(old_rose_block, new_rose_block)
    code = code.replace(old_target_start, new_target_start)
    with open(path, "w") as f:
        f.write(code)
    print("SUCCESS: Added Red & Blue color immunity for Rosellas.")
else:
    print("WARNING: Pattern not matched. Checking file contents...")
