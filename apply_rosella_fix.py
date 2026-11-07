path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

old_block = """            # 1. PRIORITY PEST CHECK: GALAH (Grey Wings/Back + Pink/Red Breast)
            # Evaluated first because Galah pink bleeds into red masks
            is_galah = (grey_ratio >= 0.08) and (pink_ratio >= 0.025 or red_ratio >= 0.035 or white_ratio >= 0.10)
            if is_galah and (bw >= 65 or bh >= 65):
                target_hit = True
                target_type = f"Galah ({bw}x{bh}px, Grey:{grey_ratio:.1%}, Pink:{pink_ratio:.1%})"
                cockatoo_candidate = (white_ratio, pink_ratio, target_type)
                break

            # 2. IMMUNITY SHIELD: ROSELLA (Red Plumage, White Cheeks, ZERO Grey)
            # Evaluated before Cockatoo checks so white cheeks and red bodies don't trigger bulk checks
            if (red_ratio >= 0.020 or pink_ratio >= 0.030) and grey_ratio < 0.18:
                print(f"[{timestamp}] [SAFE BIRD - ROSELLA] (Red: {red_ratio:.1%}, P: {pink_ratio:.1%}, Grey: {grey_ratio:.1%}, Size: {bw}x{bh}px) - Pass", flush=True)
                continue"""

new_block = """            # 1. PRIORITY PEST CHECK: GALAH (Silver-Grey Body + Pale Pink Breast, ZERO Blue/Red)
            # Galahs have heavy silver-grey plumage (>=18%) and pink breasts.
            # They never have crimson red or blue cheeks/wings.
            is_galah = (grey_ratio >= 0.18) and (pink_ratio >= 0.035 or white_ratio >= 0.12) and (blue_ratio < 0.015) and (red_ratio < 0.030)
            if is_galah and (bw >= 65 or bh >= 65):
                target_hit = True
                target_type = f"Galah ({bw}x{bh}px, Grey:{grey_ratio:.1%}, Pink:{pink_ratio:.1%})"
                cockatoo_candidate = (white_ratio, pink_ratio, target_type)
                break

            # 2. IMMUNITY SHIELD: CRIMSON ROSELLA (Vivid Red Plumage or Blue Cheeks, Tray Grey Tolerant)
            # Crimson Rosellas have saturated red bodies and blue accents; grey is just the feeder tray lip.
            is_rosella = (red_ratio >= 0.020 or pink_ratio >= 0.030 or blue_ratio >= 0.020) and (grey_ratio < 0.20)
            if is_rosella:
                print(f"[{timestamp}] [SAFE BIRD - ROSELLA] (Red: {red_ratio:.1%}, Pink: {pink_ratio:.1%}, Grey: {grey_ratio:.1%}, Blue: {blue_ratio:.1%}, Size: {bw}x{bh}px) - Pass", flush=True)
                continue"""

if old_block in code:
    code = code.replace(old_block, new_block)
    with open(path, "w") as f:
        f.write(code)
    print("Clean update applied: Galah red bleed eliminated, Rosella immunity updated.")
else:
    print("Could not find exact block match. Verifying lines...")
