import time
import asyncio
from detect_cockatoo import evaluate_frame
from ultralytics import YOLO

# Placeholder function for B-hyve trigger
async def trigger_bhyve_spray(duration_seconds=5):
    print(f"\n[B-HYVE] >>> Sending command to open valve for {duration_seconds} seconds! <<<")
    # Here goes the WebSocket / API call to start watering
    await asyncio.sleep(1)
    print(f"[B-HYVE] Spray active... water firing.")
    # In real operation, B-hyve shuts off after duration_seconds automatically or via stop command
    print(f"[B-HYVE] Command successfully acknowledged.\n")

async def main():
    model = YOLO('yolov8n.pt')
    
    print("Testing pipeline with cockatoo image...")
    target_found = evaluate_frame('synthetic_cockatoo.jpg', model)
    
    if target_found:
        print("Positive match confirmed by vision system. Activating deterrent...")
        await trigger_bhyve_spray(duration_seconds=3)
    else:
        print("No target match; deterrent will remain idle.")

if __name__ == "__main__":
    asyncio.run(main())
