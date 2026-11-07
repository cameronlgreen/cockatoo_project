import os, cv2, glob
from ultralytics import YOLO

weights = os.path.expanduser("~/cockatoo_project/runs/classify/bird_classifier_v2/weights/best.pt")
classifier = YOLO(weights)

crops = sorted(glob.glob(os.path.expanduser("~/cockatoo_project/dataset/train/rosella/179185933*.jpg")))
if not crops:
    crops = sorted(glob.glob(os.path.expanduser("~/cockatoo_project/debug_crops/179185933*.jpg")))

print(f"\nEvaluating {len(crops)} Rosella test crops against the Shield:\n" + "="*60)

for p in crops:
    img = cv2.imread(p)
    bh, bw, _ = img.shape
    fname = os.path.basename(p)

    res = classifier(img, imgsz=128, verbose=False)
    probs = res[0].probs
    species = res[0].names[probs.top1]
    conf = float(probs.top1conf)

    s2_name, s2_conf = "none", 0.0
    if len(probs.top5) > 1:
        s2_name = res[0].names[probs.top5[1]]
        s2_conf = float(probs.data[probs.top5[1]])

    # --- Strict Rosella Shield Logic ---
    safe_threat = False
    if len(probs.top5) > 1 and s2_name in {"rosella", "king_parrot"} and s2_conf > 0.01:
        safe_threat = True
    if species in {"rosella", "king_parrot"}:
        safe_threat = True

    eval_species = species
    reason = "Target"
    if safe_threat:
        eval_species = "protected_parrot"
        trace_sp = species if species in {"rosella", "king_parrot"} else s2_name
        trace_cf = conf if species in {"rosella", "king_parrot"} else s2_conf
        reason = f"VETO: trace of {trace_sp} ({trace_cf:.1%})"
    elif species == "galah":
        if conf < 0.95 or bw < 85 or bh < 85:
            eval_species = "uncertain_galah"
            reason = f"BLOCKED: galah needs >=95% & box>=85px (got {conf:.1%}, {bw}x{bh}px)"

    status = "SAFE (Valve Closed)" if eval_species in {"protected_parrot", "uncertain_galah"} else "TRIGGER (Spray)"
    print(f"File: {fname}")
    print(f"  Model Saw : 1st: {species} ({conf:.1%}) | 2nd: {s2_name} ({s2_conf:.1%}) | Box: {bw}x{bh}")
    print(f"  Shield    : {eval_species.upper()} -> {status}")
    print(f"  Reason    : {reason}\n")
