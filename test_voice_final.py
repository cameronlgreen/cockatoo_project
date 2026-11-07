import requests

access_token = "7db97-fcb6c-b3baf-45713-910ce-9a234-0f-0d55d606-c50d-4921-a2f2-c524cc2d115b"
secret_token = "7db97-fcb6c-b3baf-45713-910ce-9a234-0f-5314c001-6783-4a5d-a0ce-578596b2823b"
monkey = "bad-bird-kitchen-echo-pyowk"
text = "Warning! Cockatoos detected at the feeder!"

url = "https://api.voicemonkey.io/trigger"
params = {
    "access_token": access_token,
    "secret_token": secret_token,
    "monkey": monkey,
    "announcement": text
}

r = requests.get(url, params=params, timeout=8)
print("Final Trigger Status:", r.status_code, r.text)
