path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

old_alexa_block = """def trigger_alexa():
    try:
        url = "https://api-v3.voicemonkey.io/announce"
        params = {
            "token": VM_TOKEN,
            "device": VM_DEVICE,
            "speech": "Kill the bad bird"
        }
        res = requests.get(url, params=params, timeout=6)
        if res.status_code == 200:
            print("[ALEXA] Voice warning announced successfully.", flush=True)
        else:
            print(f"[ALEXA] Voice Monkey responded: {res.status_code} {res.text}", flush=True)
    except Exception as e:
        print(f"[ALEXA ERROR] {e}", flush=True)"""

new_alexa_block = """alexa_enabled = True

def trigger_alexa():
    global alexa_enabled
    if not alexa_enabled:
        return

    try:
        url = "https://api-v3.voicemonkey.io/announce"
        params = {
            "token": VM_TOKEN,
            "device": VM_DEVICE,
            "speech": "Kill the bad bird"
        }
        res = requests.get(url, params=params, timeout=4)
        if res.status_code == 200:
            print("[ALEXA] Voice warning announced successfully.", flush=True)
        elif res.status_code in [401, 402, 403, 429] or "credit" in res.text.lower() or "token" in res.text.lower():
            alexa_enabled = False
            print(f"[ALEXA SUSPENDED] Voice Monkey quota exhausted or unauthorized ({res.status_code}). Disabling Alexa alerts and falling back to B-hyve water deterrent only.", flush=True)
        else:
            print(f"[ALEXA] Voice Monkey responded: {res.status_code} {res.text}", flush=True)
    except Exception as e:
        print(f"[ALEXA ERROR] {e}", flush=True)"""

if old_alexa_block in code:
    code = code.replace(old_alexa_block, new_alexa_block)
    with open(path, "w") as f:
        f.write(code)
    print("SUCCESS: Alexa auto-mute failover installed.")
else:
    print("ERROR: Could not locate original trigger_alexa block.")
