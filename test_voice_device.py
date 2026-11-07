import requests

token = "7db97-fcb6c-b3baf-45713-910ce-9a234-0f-5314c001-6783-4a5d-a0ce-578596b2823b"
device_id = "bad-bird-kitchen-echo-pyowk"

# Test 1: v2 /trigger with device parameter
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
body = {
    "device": device_id,
    "text": "Warning! Cockatoos detected at the feeder!"
}

try:
    r = requests.post("https://api-v2.voicemonkey.io/trigger", headers=headers, json=body, timeout=6)
    print(f"Trigger Test 1 (v2 JSON): {r.status_code} -> {r.text}")
except Exception as e:
    print("Test 1 error:", e)

# Test 2: Standard v1 trigger
try:
    r2 = requests.get(
        "https://api.voicemonkey.io/trigger",
        params={"token": token, "device": device_id, "text": "Warning! Cockatoos detected!"},
        timeout=6
    )
    print(f"Trigger Test 2 (v1 GET): {r2.status_code} -> {r2.text}")
except Exception as e:
    print("Test 2 error:", e)
