path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

# 1. Broaden Rosella shield so sun glare or subtle red/pink protects it
old_rosella = "if (red_ratio >= 0.030 or pink_ratio >= 0.050) and grey_ratio < 0.08:"
new_rosella = "if (red_ratio >= 0.020 or pink_ratio >= 0.030) and grey_ratio < 0.18:"

# 2. Prevent Cockatoo from triggering if ANY red, pink, or green is present
old_cockatoo = "elif white_ratio >= 0.22 and (box_area >= 8000 or bw >= 95 or bh >= 95):"
new_cockatoo = "elif white_ratio >= 0.22 and (box_area >= 8000 or bw >= 95 or bh >= 95) and red_ratio < 0.015 and pink_ratio < 0.020:"

if old_rosella in code and old_cockatoo in code:
    code = code.replace(old_rosella, new_rosella)
    code = code.replace(old_cockatoo, new_cockatoo)
    with open(path, "w") as f:
        f.write(code)
    print("Successfully patched Rosella shield and Cockatoo color lockout!")
else:
    print("Could not match exact target strings. Check manual sed.")
