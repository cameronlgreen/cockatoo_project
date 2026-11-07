path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

old_block = """            # 4. PEST CHECK: COCKATOO
            # Requires genuine Cockatoo white plumage and yellow crest without safe plumage
            if yellow_pixels >= 45 and white_ratio >= 0.20 and red_ratio < 0.012 and pink_ratio < 0.020:
                target_hit = True
                target_type = f"Cockatoo Crest ({yellow_pixels}px, W:{white_ratio:.1%})"
            elif white_ratio >= 0.22 and (box_area >= 8000 or bw >= 95 or bh >= 95) and red_ratio < 0.015 and pink_ratio < 0.020:
                target_hit = True
                target_type = f"Cockatoo ({bw}x{bh}px, W:{white_ratio:.1%})\""""

new_block = """            # 4. PEST CHECK: COCKATOO
            # Sulphur-crested Cockatoos NEVER have green wings or blue heads.
            # Strictly exclude any birds with green (>=2.0%) or blue (>=1.5%) to protect Lorikeets and Rosellas.
            cockatoo_color_valid = (green_ratio < 0.020 and blue_ratio < 0.015 and red_ratio < 0.015 and pink_ratio < 0.020)
            if yellow_pixels >= 45 and white_ratio >= 0.20 and cockatoo_color_valid:
                target_hit = True
                target_type = f"Cockatoo Crest ({yellow_pixels}px, W:{white_ratio:.1%})"
            elif white_ratio >= 0.22 and (box_area >= 8000 or bw >= 95 or bh >= 95) and cockatoo_color_valid:
                target_hit = True
                target_type = f"Cockatoo ({bw}x{bh}px, W:{white_ratio:.1%})\""""

if old_block in code:
    code = code.replace(old_block, new_block)
    with open(path, "w") as f:
        f.write(code)
    print("SUCCESS: Cockatoo check now strictly excludes green and blue!")
else:
    # Fallback line-by-line replacement if indentation differs slightly
    import re
    pattern = r"if yellow_pixels >= 45 and white_ratio >= 0\.20 and red_ratio < 0\.012 and pink_ratio < 0\.020:.*?" \
              r"target_type = f\"Cockatoo \(\{bw\}x\{bh\}px, W:\{white_ratio:\.1%\}\)\""
    replacement = """cockatoo_color_valid = (green_ratio < 0.020 and blue_ratio < 0.015 and red_ratio < 0.015 and pink_ratio < 0.020)
            if yellow_pixels >= 45 and white_ratio >= 0.20 and cockatoo_color_valid:
                target_hit = True
                target_type = f"Cockatoo Crest ({yellow_pixels}px, W:{white_ratio:.1%})"
            elif white_ratio >= 0.22 and (box_area >= 8000 or bw >= 95 or bh >= 95) and cockatoo_color_valid:
                target_hit = True
                target_type = f"Cockatoo ({bw}x{bh}px, W:{white_ratio:.1%})\""""
    new_code, n = re.subn(pattern, replacement, code, flags=re.DOTALL)
    if n > 0:
        with open(path, "w") as f:
            f.write(new_code)
        print("SUCCESS (regex): Cockatoo check now strictly excludes green and blue!")
    else:
        print("Pattern match failed.")
