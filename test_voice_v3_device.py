import requests

url = "https://api-v3.voicemonkey.io/announce"
device = "bad-bird-kitchen-echo-pyowk"
text = "Kill the bad bird"

tokens = [
    ("Old Token", "7db97-fcb6c-b3baf-45713-910ce-9a234-0f-0d55d606-c50d-4921-a2f2-c524cc2d115b"),
    ("New Token", "7db97-fcb6c-b3baf-45713-910ce-9a234-0f-5314c001-6783-4a5d-a0ce-578596b2823b")
]

for label, tok in tokens:
    try:
        r = requests.get(url, params={"token": tok, "device": device, "speech": text}, timeout=8)
        print(f"[{label}] Status: {r.status_code} -> {r.text}")
    except Exception as e:
        print(f"[{label}] Error: {e}")
