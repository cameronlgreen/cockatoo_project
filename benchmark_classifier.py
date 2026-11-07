import time, os, glob
import numpy as np
from ultralytics import YOLO

model_path = os.path.expanduser("~/cockatoo_project/runs/classify/bird_classifier_v1/weights/best.pt")
val_images = glob.glob(os.path.expanduser("~/cockatoo_project/dataset/val/*/*.jpg"))

if not os.path.exists(model_path):
    print(f"Error: Model file not found at {model_path}")
    exit(1)

if not val_images:
    print("No validation images found to test.")
    exit(1)

print(f"Loading trained model: {model_path}")
model = YOLO(model_path)

sample_img = val_images[0]
print(f"Testing on sample: {os.path.basename(sample_img)}")

# Warm-up (allow torch/JIT to optimize execution paths)
for _ in range(5):
    _ = model(sample_img, imgsz=128, verbose=False)

# Timed run
latencies = []
for _ in range(50):
    t0 = time.perf_counter()
    res = model(sample_img, imgsz=128, verbose=False)
    latencies.append((time.perf_counter() - t0) * 1000)

avg_ms = np.mean(latencies)
p95_ms = np.percentile(latencies, 95)
fps = 1000.0 / avg_ms

top1_id = res[0].probs.top1
top1_conf = float(res[0].probs.top1conf)
top1_name = res[0].names[top1_id]

print("\n--- Latency Benchmark Results ---")
print(f"Average Latency : {avg_ms:.2f} ms")
print(f"95th Percentile : {p95_ms:.2f} ms")
print(f"Throughput      : {fps:.1f} crops/sec")
print(f"Sample Prediction: {top1_name} ({top1_conf*100:.1f}% confidence)")
