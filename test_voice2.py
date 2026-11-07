import requests

token = "7db97-fcb6c-b3baf-45713-910ce-9a234-0f-0d55d606-c50d-4921-a2f2-c524cc2d115b"
target = "bad-bird-kitchen-echo-pyowk"
url = "https://api-v2.voicemonkey.io/trigger"
headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json"
}

payloads = [
    ("device + text", {"device": target, "text": "Warning! Cockatoos detected at the feeder!"}),
    ("device + announcement", {"device": target, "announcement": "Warning! Cockatoos detected at the feeder!"}),
    ("device as monkey ID", {"device": target})
]

for name, body in payloads:
    try:
        r = requests.post(url, headers=headers, json=body, timeout=6)
        print(f"[{name}] -> Status {r.status_code}: {r.text}")
    except Exception as e:
        print(f"[{name}] failed: {e}")
