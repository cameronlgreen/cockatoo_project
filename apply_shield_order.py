path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    content = f.read()

# Target the start of the 5-bird discrimination pipeline
marker = "# --- 5-BIRD DISCRIMINATION PIPELINE ---"

if marker in content:
    pre = content.split(marker)[0]
    
    new_logic = """# --- 5-BIRD DISCRIMINATION PIPELINE ---
            # ==========================================
            box_area = bw * bh

            # 1. PRIORITY PEST CHECK: GALAH (Grey Wings/Back + Pink/Red Breast)
            # Evaluated first because Galah pink bleeds into red masks
            is_galah = (grey_ratio >= 0.08) and (pink_ratio >= 0.025 or red_ratio >= 0.035 or white_ratio >= 0.10)
            if is_galah and (bw >= 65 or bh >= 65):
                target_hit = True
                target_type = f"Galah ({bw}x{bh}px, Grey:{grey_ratio:.1%}, Pink:{pink_ratio:.1%})"
                cockatoo_candidate = (white_ratio, pink_ratio, target_type)
                break

            # 2. IMMUNITY SHIELD: ROSELLA (Red Plumage, White Cheeks, ZERO Grey)
            # Evaluated before Cockatoo checks so white cheeks and red bodies don't trigger bulk checks
            if (red_ratio >= 0.030 or pink_ratio >= 0.050) and grey_ratio < 0.08:
                print(f"[{timestamp}] [SAFE BIRD - ROSELLA] (Red: {red_ratio:.1%}, P: {pink_ratio:.1%}, Grey: {grey_ratio:.1%}, Size: {bw}x{bh}px) - Pass", flush=True)
                continue

            # 3. IMMUNITY SHIELD: LORIKEET (Green Back/Wings or Blue Head)
            # Evaluated before Cockatoo crest checks so neck yellow doesn't trigger
            if green_ratio >= 0.035 or blue_ratio >= 0.025:
                print(f"[{timestamp}] [SAFE BIRD - LORIKEET] (Green: {green_ratio:.1%}, Blue: {blue_ratio:.1%}, Size: {bw}x{bh}px) - Pass", flush=True)
                continue

            # 4. PEST CHECK: COCKATOO
            # Requires genuine Cockatoo white plumage and yellow crest without safe plumage
            if yellow_pixels >= 45 and white_ratio >= 0.20:
                target_hit = True
                target_type = f"Cockatoo Crest ({yellow_pixels}px, W:{white_ratio:.1%})"
            elif white_ratio >= 0.22 and (box_area >= 8000 or bw >= 95 or bh >= 95):
                target_hit = True
                target_type = f"Cockatoo ({bw}x{bh}px, W:{white_ratio:.1%})"
            else:
                continue

            if target_hit:
                cockatoo_candidate = (white_ratio, pink_ratio, target_type)
                break
"""
    # Replace from marker up to the hit confirmation block
    post_marker = "if target_hit and cockatoo_candidate is not None:"
    post = post_marker + content.split(post_marker)[1]
    
    with open(path, "w") as f:
        f.write(pre + new_logic + "\n        " + post)
    print("Successfully updated discrimination logic order!")
else:
    print("Could not find pipeline marker. Please verify file structure.")
