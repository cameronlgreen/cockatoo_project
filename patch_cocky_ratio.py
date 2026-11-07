path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

import re

# Find and replace the discrimination block cleanly
pattern = r"# --- Galah Shield & Species Discrimination ---.*?(?=\n\s*# Verification:)"

replacement = """# --- Galah Shield & Species Discrimination ---
            # 1. COCKATOO TARGET: Dominant white plumage (overwhelms timber reflections >= 5:1 ratio)
            if white_ratio >= 0.22 and (pink_ratio < 0.015 or white_ratio >= (pink_ratio * 5.0)):
                cockatoo_candidate = (white_ratio, pink_ratio)
                break

            # 2. GALAH SHIELD: Genuine rose-magenta breast (at least 5% rose or balanced with white)
            elif pink_ratio >= 0.050 or (pink_ratio >= 0.025 and white_ratio < (pink_ratio * 4.0)):
                print(f"[{timestamp}] Galah detected (Rose: {pink_ratio:.1%}, White: {white_ratio:.1%}, Conf: {conf:.2f}) -> Sparing friend.", flush=True)
                cockatoo_candidate = None
                break

            # 3. OTHER COCKATOO POSTURES (Lower white, practically zero rose)
            elif white_ratio >= 0.17 and pink_ratio < 0.015:
                cockatoo_candidate = (white_ratio, pink_ratio)
                break

            else:
                print(f"[{timestamp}] Non-target bird (Conf: {conf:.2f}, White: {white_ratio:.1%}, Rose: {pink_ratio:.1%})", flush=True)"""

code = re.sub(pattern, replacement, code, flags=re.DOTALL)

with open(path, "w") as f:
    f.write(code)

print("Cockatoo 5:1 dominance ratio applied successfully.")
