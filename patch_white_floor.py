path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

# Replace the entire Cockatoo detection block with a strict 15% white floor
old_cockatoo_block = """            # 1. Sulphur-Crested Cockatoo: Yellow crest, white body, or large shaded bird
            if yellow_pixels >= 40 and white_ratio >= 0.04:
                target_hit = True
                target_type = f"Cockatoo (Crest: {yellow_pixels}px, White: {white_ratio:.1%})"
            elif white_ratio >= 0.18 and (bw >= 100 or bh >= 100):
                target_hit = True
                target_type = f"Cockatoo ({bw}x{bh}px, White: {white_ratio:.1%})"
            elif (bw >= 120 or bh >= 80) and white_ratio >= 0.03 and pink_ratio < 0.02:
                target_hit = True
                target_type = f"Cockatoo Shaded ({bw}x{bh}px, White: {white_ratio:.1%})""""

new_cockatoo_block = """            # 1. Sulphur-Crested Cockatoo: Must be at least 15% white plumage
            if yellow_pixels >= 40 and white_ratio >= 0.15:
                target_hit = True
                target_type = f"Cockatoo (Crest: {yellow_pixels}px, White: {white_ratio:.1%})"
            elif white_ratio >= 0.15 and (bw >= 105 or bh >= 105):
                target_hit = True
                target_type = f"Cockatoo ({bw}x{bh}px, White: {white_ratio:.1%})""""

if old_cockatoo_block in code:
    code = code.replace(old_cockatoo_block, new_cockatoo_block)
    with open(path, "w") as f:
        f.write(code)
    print("SUCCESS: Cockatoo white threshold raised to 15% minimum.")
else:
    # If the file had variations from earlier edits, check lines 260-280
    print("Direct replace failed; checking file lines...")
