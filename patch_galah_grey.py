path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

# 1. Lower small-visitor bypass from 95 to 65 so perched Galahs are evaluated
old_size_filter = "if max(bw, bh) < 95:"
new_size_filter = "if max(bw, bh) < 65:"
if old_size_filter in code:
    code = code.replace(old_size_filter, new_size_filter)
    print("Fixed: Lowered small-visitor skip threshold to 65px.")

# 2. Update Rosella / Galah discrimination logic
old_block = """            # [SHIELD 1: ROSELLA IMMUNITY]
            # Checked first so even a big, long-tailed Rosella never gets sprayed
            if red_ratio >= 0.035:
                print(f"[{timestamp}] [SAFE BIRD - ROSELLA] (Red: {red_ratio:.1%}, Size: {bw}x{bh}px, Area: {box_area}) - Pass", flush=True)
                continue"""

new_block = """            # [PRIORITY CHECK: GALAH (Grey Back/Wings + Pink/Red Breast)]
            # Must be checked before Rosella immunity because Galah pink bleeds into red masks
            is_galah = (grey_ratio >= 0.08) and (pink_ratio >= 0.025 or red_ratio >= 0.035 or white_ratio >= 0.10)
            if is_galah and (bw >= 65 or bh >= 65):
                target_hit = True
                target_type = f"Galah ({bw}x{bh}px, Grey:{grey_ratio:.1%}, Pink:{pink_ratio:.1%}, Red:{red_ratio:.1%})"

            # [SHIELD 1: ROSELLA IMMUNITY]
            # True Rosellas have vibrant red but NO grey body/wings
            elif red_ratio >= 0.035 and grey_ratio < 0.08:
                print(f"[{timestamp}] [SAFE BIRD - ROSELLA] (Red: {red_ratio:.1%}, Grey: {grey_ratio:.1%}, Size: {bw}x{bh}px) - Pass", flush=True)
                continue"""

if old_block in code:
    code = code.replace(old_block, new_block)
    print("Fixed: Added Galah grey-feather intercept ahead of Rosella immunity.")
else:
    print("Warning: Could not match exact Shield 1 block to replace.")

with open(path, "w") as f:
    f.write(code)
