import requests

token = "7db97-fcb6c-b3baf-45713-910ce-9a234-0f-0d55d606-c50d-4921-a2f2-c524cc2d115b"
monkey = "bad-bird-kitchen-echo-pyowk"

tests = [
    ("POST", "https://api-v2.voicemonkey.io/trigger", {"Authorization": "Bearer " + token}, {"monkey": monkey, "announcement": "Alert"}),
    ("POST", "https://api.voicemonkey.io/trigger", {"Authorization": "Bearer " + token}, {"monkey": monkey, "announcement": "Alert"}),
    ("GET", "https://api.voicemonkey.io/trigger", {}, {"access_token": token, "monkey": monkey, "announcement": "Alert"}),
    ("GET", "https://api.voicemonkey.io/trigger", {}, {"token": token, "monkey": monkey, "announcement": "Alert"}),
    ("POST", "https://api.voicemonkey.io/trigger", {"Content-Type": "application/json"}, {"token": token, "monkey": monkey, "announcement": "Alert"}),
]

for idx, (method, url, headers, payload) in enumerate(tests, 1):
    try:
        if method == "POST":
            r = requests.post(url, headers=headers, json=payload, timeout=6)
        else:
            r = requests.get(url, headers=headers, params=payload, timeout=6)
        print(f"Test {idx} status: {r.status_code} | response: {r.text[:80]}")
    except Exception as e:
        print(f"Test {idx} failed: {e}")
