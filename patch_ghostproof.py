path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

import re

# 1. Strictly 'bird' only - reject bench, timber, furniture
code = re.sub(r"if label in \['bird'.*?\]:", "if label == 'bird':", code)

# 2. Real cockatoos are large; reject small background noise
code = re.sub(r"MIN_BIRD_DIM\s*=\s*\d+", "MIN_BIRD_DIM   = 75", code)

# 3. Confidence threshold: 0.42 ignores empty timber (which scored 0.29), catches birds immediately
code = re.sub(r"CONF_THRESHOLD\s*=\s*0\.\d+", "CONF_THRESHOLD = 0.42", code)

# 4. Cockatoo threshold: 18% white, < 1.5% rose
code = re.sub(
    r"if white_ratio >= 0\.\d+ and pink_ratio < 0\.\d+:",
    "if white_ratio >= 0.18 and pink_ratio < 0.015:",
    code
)

with open(path, "w") as f:
    f.write(code)

print("Ghost-proof patch applied successfully.")
