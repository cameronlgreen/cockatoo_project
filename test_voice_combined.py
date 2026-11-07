import requests

access_token = "7db97-fcb6c-b3baf-45713-910ce-9a234-0f-0d55d606-c50d-4921-a2f2-c524cc2d115b"
secret_token = "7db97-fcb6c-b3baf-45713-910ce-9a234-0f-5314c001-6783-4a5d-a0ce-578596b2823b"
device = "bad-bird-kitchen-echo-pyowk"
text = "Warning! Cockatoos detected at the feeder!"

# Test 1: Standard /trigger GET with access_token + secret_token + device
url = "https://api.voicemonkey.io/trigger"
params1 = {
    "access_token": access_token,
    "secret_token": secret_token,
    "device": device,
    "text": text
}
try:
    r1 = requests.get(url, params=params1, timeout=8)
    print("Test 1 (GET device):", r1.status_code, r1.text)
except Exception as e:
    print("Test 1 error:", e)

# Test 2: Standard /trigger GET with monkey param
params2 = {
    "access_token": access_token,
    "secret_token": secret_token,
    "monkey": device,
    "announcement": text
}
try:
    r2 = requests.get(url, params=params2, timeout=8)
    print("Test 2 (GET monkey):", r2.status_code, r2.text)
except Exception as e:
    print("Test 2 error:", e)

# Test 3: v2 POST with bearer + secret payload
try:
    r3 = requests.post(
        "https://api-v2.voicemonkey.io/trigger",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        json={"device": device, "secret": secret_token, "text": text},
        timeout=8
    )
    print("Test 3 (v2 POST):", r3.status_code, r3.text)
except Exception as e:
    print("Test 3 error:", e)
