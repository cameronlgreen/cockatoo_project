import os, glob, random, shutil

DATASET = os.path.expanduser("~/cockatoo_project/dataset")
TRAIN_DIR = os.path.join(DATASET, "train")
VAL_DIR = os.path.join(DATASET, "val")

random.seed(42)

classes = [d for d in os.listdir(TRAIN_DIR) if os.path.isdir(os.path.join(TRAIN_DIR, d))]

print("Creating 80/20 train/val split...")
print("Class           | Train    | Val      | Total   ")
print("----------------|----------|----------|---------")

for c in sorted(classes):
    c_train = os.path.join(TRAIN_DIR, c)
    c_val = os.path.join(VAL_DIR, c)
    os.makedirs(c_val, exist_ok=True)
    
    files = sorted(glob.glob(os.path.join(c_train, "*.jpg")))
    random.shuffle(files)
    
    # 20% to validation
    val_count = max(1, int(len(files) * 0.20)) if len(files) > 1 else 0
    val_files = files[:val_count]
    
    for f in val_files:
        shutil.move(f, os.path.join(c_val, os.path.basename(f)))
        
    remaining_train = len(files) - val_count
    print(f"{c:<15} | {remaining_train:<8} | {val_count:<8} | {len(files):<8}")

print("----------------|----------|----------|---------")
print("Dataset split complete!")
