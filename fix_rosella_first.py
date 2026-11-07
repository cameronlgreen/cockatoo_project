path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

import re

# Replace the pipeline logic block to put Rosella Shield #1
pattern = r"# --- 5-BIRD DISCRIMINATION PIPELINE ---.*?(?=# 4\. PEST CHECK: COCKATOO)"

replacement = """# --- 5-BIRD DISCRIMINATION PIPELINE ---
            # ==========================================
            box_area = bw * bh

            # 1. IMMUNITY SHIELD: CRIMSON ROSELLA (Scarlet Red / Blue Accents)
            # Evaluated FIRST: Any bird showing genuine crimson red or blue is immune,
            # regardless of dark mantle feathers or tray grey.
            is_rosella = (red_ratio >= 0.025 or blue_ratio >= 0.012) and (red_ratio > pink_ratio or blue_ratio >= 0.012)
            if is_rosella:
                print(f"[{timestamp}] [SAFE BIRD - ROSELLA] (Red: {red_ratio:.1%}, Pink: {pink_ratio:.1%}, Grey: {grey_ratio:.1%}, Blue: {blue_ratio:.1%}, Size: {bw}x{bh}px) - Pass", flush=True)
                continue

            # 2. IMMUNITY SHIELD: LORIKEET (Green Wings/Back or Blue Head)
            if green_ratio >= 0.030 or blue_ratio >= 0.020:
                print(f"[{timestamp}] [SAFE BIRD - LORIKEET] (Green: {green_ratio:.1%}, Blue: {blue_ratio:.1%}, Size: {bw}x{bh}px) - Pass", flush=True)
                continue

            # 3. PEST CHECK: GALAH (Rose-Pink Breast + Silver Grey Body, ZERO Red/Blue)
            # Must have substantial pink and grey, but zero blue and zero crimson red.
            is_galah = (pink_ratio >= 0.040 and grey_ratio >= 0.15) and (blue_ratio < 0.010) and (red_ratio < 0.020)
            if is_galah and (bw >= 65 or bh >= 65):
                target_hit = True
                target_type = f"Galah ({bw}x{bh}px, Grey:{grey_ratio:.1%}, Pink:{pink_ratio:.1%})"
                cockatoo_candidate = (white_ratio, pink_ratio, target_type)
                break

            """

new_code, count = re.subn(pattern, replacement, code, flags=re.DOTALL)
if count > 0:
    with open(path, "w") as f:
        f.write(new_code)
    print("SUCCESS: Rosella shield moved to Priority #1 ahead of Galah!")
else:
    print("Failed to match pattern.")
