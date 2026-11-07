import os, glob
from datetime import datetime

inbox = os.path.expanduser("~/cockatoo_project/training_data/inbox")
files = glob.glob(os.path.join(inbox, "bird_1791686*.jpg"))

print(f"Found {len(files)} files matching the prefix.")
print("Sample files and their epoch timestamps:")

fmt = "%Y-%m-%d %H:%M:%S"
for f in sorted(files)[:10]:
    fn = os.path.basename(f)
    try:
        epoch_val = float(fn.split("_")[1])
        # Auto-detect whether it is milliseconds or centiseconds/seconds
        if epoch_val > 1e11:
            epoch_s = epoch_val / 1000.0
        elif epoch_val > 1e9:
            epoch_s = epoch_val / 100.0 if epoch_val > 5e9 else epoch_val
        else:
            epoch_s = epoch_val
        dt_local = datetime.fromtimestamp(epoch_s)
        print(f"  {fn} -> {dt_local.strftime(fmt)}")
    except Exception as e:
        print(f"  {fn} -> (parse error: {e})")
