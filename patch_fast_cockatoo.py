path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

# Replace the Cockatoo threshold: 18% white is plenty when pink is virtually zero
old_logic = "elif white_ratio >= 0.28 and pink_ratio < 0.020:"
new_logic = "elif white_ratio >= 0.18 and pink_ratio < 0.015:"

if old_logic in code:
    code = code.replace(old_logic, new_logic)
    print("Lowered white threshold to 18% with tight pink exclusion.")
else:
    # Fallback pattern if whitespace or formatting differs
    import re
    code = re.sub(
        r"elif white_ratio >= 0\.\d+ and pink_ratio < 0\.\d+:",
        "elif white_ratio >= 0.18 and pink_ratio < 0.015:",
        code
    )
    print("Replaced white threshold using regex pattern.")

# Ensure verification is set to 2 consecutive frames
code = re.sub(r"if consecutive_target_frames >= \d+:", "if consecutive_target_frames >= 2:", code)

with open(path, "w") as f:
    f.write(code)

print("Fast-strike configuration ready.")
