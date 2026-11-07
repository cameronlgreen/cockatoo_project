path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

# 1. Ensure import subprocess exists at the top
if "import subprocess" not in code:
    code = "import subprocess\n" + code
    print("Fixed: Added missing 'import subprocess'.")

# 2. Remove 'bench' from detection classes
old_class_check = "if label in ['bird', 'bench']:"
new_class_check = "if label == 'bird':"
if old_class_check in code:
    code = code.replace(old_class_check, new_class_check)
    print("Fixed: Removed 'bench' class (now strictly 'bird').")
elif "if label in ['bird']:" in code:
    print("Class check already clean.")

# 3. Add aspect ratio sanity check so flat rectangular railings are discarded
old_append = """                        else:
                            candidate_crops.append((crop, conf, label, bw, bh))"""

new_append = """                        else:
                            # Reject static objects like horizontal rails/trays (extreme aspect ratios)
                            aspect_ratio = bw / max(1, bh)
                            if aspect_ratio > 2.2:
                                # Over 2.2x wider than tall is a ledge or tray, not a perched bird
                                pass
                            else:
                                candidate_crops.append((crop, conf, label, bw, bh))"""

if old_append in code:
    code = code.replace(old_append, new_append)
    print("Fixed: Added aspect ratio filter to reject horizontal railings/ledges.")

# 4. Require plumage verification along with bulk size so unpainted wood/plastic never triggers
old_bulk = "if box_area >= 7500 or bw >= 120 or bh >= 120:"
new_bulk = "if (box_area >= 7500 or bw >= 115 or bh >= 115) and (white_ratio >= 0.12 or pink_ratio >= 0.035):"

if old_bulk in code:
    code = code.replace(old_bulk, new_bulk)
    print("Fixed: Bulk bird trigger now requires white (Cockatoo) or pink (Galah) plumage.")

with open(path, "w") as f:
    f.write(code)
