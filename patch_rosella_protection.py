path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

target_marker = "# --- 5-BIRD DISCRIMINATION PIPELINE ---"
exec_marker = "if target_hit:"

if target_marker in code and exec_marker in code:
    parts = code.split(target_marker)
    header = parts[0] + target_marker + "\n            # ==========================================\n"
    rest = parts[1]
    pipeline_code, post_code = rest.split(exec_marker, 1)

    new_pipeline = """
            box_area = bw * bh

            # [SHIELD 1: ROSELLA IMMUNITY]
            # Checked first so even a big, long-tailed Rosella never gets sprayed
            if red_ratio >= 0.035:
                print(f"[{timestamp}] [SAFE BIRD - ROSELLA] (Red: {red_ratio:.1%}, Size: {bw}x{bh}px, Area: {box_area}) - Pass", flush=True)
                continue

            # [SHIELD 2: LORIKEET IMMUNITY]
            # Requires genuine green plumage (ignores blue sky reflections)
            if green_ratio >= 0.050 or (blue_ratio >= 0.030 and green_ratio >= 0.025):
                print(f"[{timestamp}] [SAFE BIRD - LORIKEET] (Green: {green_ratio:.1%}, Size: {bw}x{bh}px) - Pass", flush=True)
                continue

            # [TRIGGER 1: HEAVY / BULKY BIRD (Cockatoos & Galahs)]
            # Cockatoo/Galah bulk typically exceeds 7,500px area (e.g. 100x75+)
            if box_area >= 7500 or bw >= 120 or bh >= 120:
                target_hit = True
                target_type = f"Large Pest ({bw}x{bh}px, Area: {box_area}, W:{white_ratio:.1%}, P:{pink_ratio:.1%})"

            # [TRIGGER 2: MEDIUM TARGET BY PLUMAGE]
            elif yellow_pixels >= 40 and white_ratio >= 0.14:
                target_hit = True
                target_type = f"Cockatoo Crest ({yellow_pixels}px, W:{white_ratio:.1%})"
            elif white_ratio >= 0.16 and (bw >= 90 or bh >= 90):
                target_hit = True
                target_type = f"Cockatoo ({bw}x{bh}px, W:{white_ratio:.1%})"
            elif pink_ratio >= 0.040 and (bw >= 85 or bh >= 85):
                target_hit = True
                target_type = f"Galah ({bw}x{bh}px, P:{pink_ratio:.1%})"
            else:
                continue

            """

    code = header + new_pipeline + "if target_hit:" + post_code
    with open(path, "w") as f:
        f.write(code)
    print("SUCCESS: Rosella shield + Bulk Size logic applied.")
else:
    print("ERROR: Markers not matched.")
