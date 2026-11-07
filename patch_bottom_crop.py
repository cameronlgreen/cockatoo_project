path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

old_crop = "crop = feeder_crop[max(0, by1):min(feeder_crop.shape[0], by2), max(0, bx1):min(feeder_crop.shape[1], bx2)]"
new_crop = """# Exclude bottom 18% to remove feet and grey feeder tray rim from color analysis
                    effective_by2 = min(feeder_crop.shape[0], by1 + int(bh * 0.82))
                    crop = feeder_crop[max(0, by1):effective_by2, max(0, bx1):min(feeder_crop.shape[1], bx2)]"""

if old_crop in code:
    code = code.replace(old_crop, new_crop)
    with open(path, "w") as f:
        f.write(code)
    print("Successfully patched bird crop to exclude feeder tray rim!")
else:
    print("Could not match exact crop line. Checking existing code...")
