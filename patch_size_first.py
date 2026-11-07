path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

# Locate the 5-bird discrimination section
target_marker = "# --- 5-BIRD DISCRIMINATION PIPELINE ---"

if target_marker in code:
    parts = code.split(target_marker)
    header = parts[0] + target_marker + "\n            # ==========================================\n"
    rest = parts[1]

    # Find where target_hit execution begins
    exec_marker = "if target_hit:"
    pipeline_code, post_code = rest.split(exec_marker, 1)

    new_pipeline = """
            # [PRIORITY 1: SIZE CHECK - INSTANT TARGET]
            # Cockatoos and Galahs are large; Rosellas and Lorikeets are small
            if bw >= 95 or bh >= 95:
                target_hit = True
                target_type = f"Large Bird ({bw}x{bh}px, White: {white_ratio:.1%}, Pink: {pink_ratio:.1%})"

            # [CATEGORY 3: ROSELLA] (Immunity for smaller birds)
            elif red_ratio >= 0.040:
                print(f"[{timestamp}] [SAFE BIRD - ROSELLA] (Red: {red_ratio:.1%}, Size: {bw}x{bh}px) - Pass", flush=True)
                continue

            # [CATEGORY 4: LORIKEET] (Immunity for smaller birds)
            elif green_ratio >= 0.050 or (blue_ratio >= 0.030 and green_ratio >= 0.025):
                print(f"[{timestamp}] [SAFE BIRD - LORIKEET] (Green: {green_ratio:.1%}, Blue: {blue_ratio:.1%}, Size: {bw}x{bh}px) - Pass", flush=True)
                continue

            # [CATEGORY 1 & 2: COLOR CONFIRMATION FOR MEDIUM BIRDS]
            elif yellow_pixels >= 40 and white_ratio >= 0.15:
                target_hit = True
                target_type = f"Cockatoo (Crest: {yellow_pixels}px, White: {white_ratio:.1%})"
            elif pink_ratio >= 0.040:
                target_hit = True
                target_type = f"Galah (Pink: {pink_ratio:.1%}, Size: {bw}x{bh}px)"
            elif white_ratio >= 0.18:
                target_hit = True
                target_type = f"Cockatoo (White: {white_ratio:.1%}, Size: {bw}x{bh}px)"
            else:
                continue

            """

    code = header + new_pipeline + "            " + exec_marker + post_code
    with open(path, "w") as f:
        f.write(code)
    print("SUCCESS: Size check promoted to Priority 1.")
else:
    print("ERROR: Pipeline marker not found.")
