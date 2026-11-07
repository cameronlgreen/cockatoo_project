path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

import re

# 1. Accommodate smaller Galah bounding boxes (50px instead of 75px)
code = re.sub(r"MIN_BIRD_DIM\s*=\s*\d+", "MIN_BIRD_DIM   = 50", code)

# 2. Bird detection confidence floor to 0.32
code = re.sub(r"CONF_THRESHOLD\s*=\s*0\.\d+", "CONF_THRESHOLD = 0.32", code)

# 3. True rose-pink mask that catches shaded Galah feathers (Sat >= 45, Hue 150-178)
old_rose_mask = r"mask_rose = cv2\.inRange\(hsv, np\.array\(\[158, 70, 90\]\), np\.array\(\[176, 255, 255\]\)\)"
new_rose_mask = "mask_rose = cv2.inRange(hsv, np.array([150, 45, 75]), np.array([178, 255, 255]))"
code = re.sub(old_rose_mask, new_rose_mask, code)

# 4. Discrimination: Galah if Rose >= 2.5%, Cockatoo if White >= 18% & Rose < 1.5%
old_disc = r"# --- Galah Shield ---.*?elif label == 'bird':.*?print\(f\"\[\{timestamp\}\] Non-target bird.*?\)"
new_disc = """# --- Galah Shield & Species Discrimination ---
            if pink_ratio >= 0.025:
                print(f"[{timestamp}] Galah detected (Rose: {pink_ratio:.1%}, White: {white_ratio:.1%}, Conf: {conf:.2f}) -> Sparing friend.", flush=True)
                cockatoo_candidate = None
                break
            elif white_ratio >= 0.18 and pink_ratio < 0.015:
                cockatoo_candidate = (white_ratio, pink_ratio)
                break
            else:
                print(f"[{timestamp}] Non-target bird (Conf: {conf:.2f}, White: {white_ratio:.1%}, Rose: {pink_ratio:.1%})", flush=True)"""

code = re.sub(old_disc, new_disc, code, flags=re.DOTALL)

with open(path, "w") as f:
    f.write(code)

print("Galah visibility patch applied.")
