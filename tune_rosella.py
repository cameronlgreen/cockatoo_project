path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

# 1. Broaden Rosella immunity to handle sun glare and background wood tones
old_rosella_block = """            # 2. IMMUNITY SHIELD: ROSELLA (Red Plumage, White Cheeks, ZERO Grey)
            # Evaluated before Cockatoo checks so white cheeks and red bodies don't trigger bulk checks
            if (red_ratio >= 0.030 or pink_ratio >= 0.050) and grey_ratio < 0.08:
                print(f"[{timestamp}] [SAFE BIRD - ROSELLA] (Red: {red_ratio:.1%}, P: {pink_ratio:.1%}, Grey: {grey_ratio:.1%}, Size: {bw}x{bh}px) - Pass", flush=True)
                continue"""

new_rosella_block = """            # 2. IMMUNITY SHIELD: ROSELLA (Red Plumage, ZERO Grey Wings)
            # Accommodates harsh sun specular glare and feeder timber shadows
            is_rosella = (red_ratio >= 0.015 or pink_ratio >= 0.030) and (grey_ratio < 0.20)
            if is_rosella:
                print(f"[{timestamp}] [SAFE BIRD - ROSELLA] (Red: {red_ratio:.1%}, P: {pink_ratio:.1%}, Grey: {grey_ratio:.1%}, Size: {bw}x{bh}px) - Pass", flush=True)
                continue"""

# 2. Add strict red/pink lockout to Cockatoo triggers
old_crest = "if yellow_pixels >= 45 and white_ratio >= 0.20:"
new_crest = "if yellow_pixels >= 45 and white_ratio >= 0.20 and red_ratio < 0.012 and pink_ratio < 0.020:"

old_cockatoo = "elif white_ratio >= 0.22 and (box_area >= 8000 or bw >= 95 or bh >= 95):"
new_cockatoo = "elif white_ratio >= 0.22 and (box_area >= 8000 or bw >= 95 or bh >= 95) and red_ratio < 0.012 and pink_ratio < 0.020:"

if old_rosella_block in code:
    code = code.replace(old_rosella_block, new_rosella_block)
    print("Updated: Rosella immunity shield tuned for direct sun glare.")
else:
    print("Notice: Rosella block already updated or structure differed slightly.")

if old_crest in code:
    code = code.replace(old_crest, new_crest)
if old_cockatoo in code:
    code = code.replace(old_cockatoo, new_cockatoo)
    print("Updated: Added red/pink lockout to Cockatoo checks.")

with open(path, "w") as f:
    f.write(code)
