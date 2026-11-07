path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

import re

# 1. Allow 'bench' ONLY if it shows cockatoo white plumage (>= 22%)
old_cand = """                if bw >= MIN_BIRD_DIM and bh >= MIN_BIRD_DIM:
                    if label == 'bird':
                        crop = frame[max(0, by1):min(h, by2), max(0, bx1):min(w, bx2)]
                        if crop.size > 0:
                            candidate_crops.append((crop, conf))"""

new_cand = """                if bw >= MIN_BIRD_DIM and bh >= MIN_BIRD_DIM:
                    # Catch both standard bird detections and large cockatoos misclassified as bench
                    if label in ['bird', 'bench']:
                        crop = frame[max(0, by1):min(h, by2), max(0, bx1):min(w, bx2)]
                        if crop.size > 0:
                            candidate_crops.append((crop, conf, label))"""

code = code.replace(old_cand, new_cand)

# 2. Update loop unpacking and discrimination logic
old_loop = """        for crop, conf in candidate_crops:"""
new_loop = """        for crop, conf, label in candidate_crops:"""
code = code.replace(old_loop, new_loop)

# 3. Update discrimination block
old_disc = r"# --- Galah Shield & Species Discrimination ---.*?(?=\n\s*# Verification:)"
new_disc = """# --- Galah Shield & Species Discrimination ---
            # If misclassified as 'bench', require White >= 22% so empty feeder glare (~12%) never triggers
            min_white_required = 0.22 if label == 'bench' else 0.18

            # Galah Shield: Solid rose breast
            if pink_ratio >= 0.050 or (pink_ratio >= 0.025 and white_ratio < (pink_ratio * 4.0)):
                print(f"[{timestamp}] Galah detected (Rose: {pink_ratio:.1%}, White: {white_ratio:.1%}, Conf: {conf:.2f}) -> Sparing friend.", flush=True)
                cockatoo_candidate = None
                break

            # Cockatoo Strike: Substantial white that dominates rose reflections
            elif white_ratio >= min_white_required and (pink_ratio < 0.015 or white_ratio >= (pink_ratio * 4.0)):
                cockatoo_candidate = (white_ratio, pink_ratio)
                break

            else:
                print(f"[{timestamp}] Non-target ({label}, Conf: {conf:.2f}, White: {white_ratio:.1%}, Rose: {pink_ratio:.1%})", flush=True)"""

code = re.sub(old_disc, new_disc, code, flags=re.DOTALL)

with open(path, "w") as f:
    f.write(code)

print("Bench-cockatoo patch applied.")
