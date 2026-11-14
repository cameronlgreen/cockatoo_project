#!/usr/bin/env python3
import csv, os
from collections import defaultdict

csv_path = "/home/cameronlgreen/cockatoo_project/feeder_visits.csv"
if not os.path.exists(csv_path):
    print("No feeder_visits.csv found yet.")
    exit(0)

hourly = defaultdict(lambda: {"rosella": 0, "king_parrot": 0})
totals = {"rosella": 0, "king_parrot": 0}
times = []

with open(csv_path, "r") as f:
    for row in csv.DictReader(f):
        sp, hr = row["species"], int(row["hour"])
        if sp in totals:
            hourly[hr][sp] += 1
            totals[sp] += 1
            times.append(row["time"])

print(f"\n=== NATIVE BIRD FEEDING SUMMARY ===")
print(f"Total Sessions : {sum(totals.values())} (Rosellas: {totals['rosella']} | King Parrots: {totals['king_parrot']})")
if times:
    print(f"Earliest Visit : {min(times)} | Latest Visit: { max(times) }")
print(f"\n{'Hour':<13} | {'Rosellas':<10} | {'King Parrots':<14} | Activity")
print("-" * 60)
for h in range(5, 22):
    r, kp = hourly[h]["rosella"], hourly[h]["king_parrot"]
    if r > 0 or kp > 0:
        print(f"{h:02d}:00 - {h:02d}:59 | {r:<10} | {kp:<14} | {'\u2588' * (r + kp)}")
