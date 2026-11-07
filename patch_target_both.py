import re

path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

# Replace the discrimination block to hit BOTH Cockatoos and Galahs
old_pattern = r"# --- TARGET IDENTIFICATION ---.*?(?=\n\s*# Verification:)"
if not re.search(old_pattern, code, flags=re.DOTALL):
    old_pattern = r"# --- Galah Shield & Species Discrimination ---.*?(?=\n\s*# Verification:)"

new_logic = """# --- TARGET IDENTIFICATION (COCKATOOS & GALAHS) ---
            target_hit = False
            target_type = None

            # 1. Sulphur-Crested Cockatoo: Yellow crest OR heavy white body plumage
            if yellow_pixels >= 80 and white_ratio >= 0.15:
                target_hit = True
                target_type = f"Cockatoo (Crest: {yellow_pixels}px, White: {white_ratio:.1%})"
            elif white_ratio >= 0.28:
                target_hit = True
                target_type = f"Cockatoo (White Plumage: {white_ratio:.1%})"

            # 2. Galah: Rose/Magenta breast plumage
            elif pink_ratio >= 0.035:
                target_hit = True
                target_type = f"Galah (Rose Breast: {pink_ratio:.1%})"

            if target_hit:
                cockatoo_candidate = (white_ratio, pink_ratio, target_type)
                break
            else:
                print(f"[{timestamp}] Safe Visitor ({label}, Conf: {conf:.2f}, White: {white_ratio:.1%}, Rose: {pink_ratio:.1%})", flush=True)"""

code = re.sub(old_pattern, new_logic, code, flags=re.DOTALL)

with open(path, "w") as f:
    f.write(code)

print("Discrimination logic updated: Both Cockatoos & Galahs are now active targets.")
