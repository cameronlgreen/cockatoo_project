import requests
import json
import time
import os
import sys
import threading
import socket
import websocket

# Load environment configuration
env_path = os.path.expanduser("~/cockatoo_project/.env")
creds = {}
with open(env_path) as f:
    for line in f:
        if "=" in line and not line.startswith("#"):
            k, v = line.strip().split("=", 1)
            creds[k] = v

BHYVE_EMAIL = creds.get("BHYVE_EMAIL")
BHYVE_PASSWORD = creds.get("BHYVE_PASSWORD")
DEVICE_ID = creds.get("BHYVE_DEVICE_ID")
STATION = int(creds.get("BHYVE_STATION", 3))
BURST_SECONDS = float(creds.get("BURST_SECONDS", 3.0))

ws_conn = None
ws_lock = threading.Lock()
running = True

def get_session_token():
    try:
        res = requests.post("https://api.orbitbhyve.com/v1/session", 
                            json={"session": {"email": BHYVE_EMAIL, "password": BHYVE_PASSWORD}}, 
                            headers={"orbit-app-id": "Orbit Support Dashboard", "Content-Type": "application/json"}, 
                            timeout=15)
        if res.status_code == 200:
            return res.json().get("orbit_api_key")
    except Exception as e:
        print(f"[AUTH ERROR] {e}")
    return None

def socket_reader(ws):
    """Continuously drains incoming packets to keep the TCP pipe healthy."""
    while running:
        try:
            msg = ws.recv()
            if not msg:
                break
        except Exception:
            break

def maintain_websocket():
    global ws_conn
    while running:
        try:
            token = get_session_token()
            if not token:
                time.sleep(10)
                continue

            ws_url = "wss://api.orbitbhyve.com/v1/events?binary=json"
            ws_headers = [f"orbit-api-key: {token}", "orbit-app-id: Orbit Support Dashboard"]
            
            new_ws = websocket.create_connection(ws_url, header=ws_headers, timeout=15)
            # Authenticate the connection
            new_ws.send(json.dumps({"event": "app_connection", "orbit_session_token": token}))

            with ws_lock:
                ws_conn = new_ws

            print("[B-HYVE] Persistent WebSocket active and warm.")

            # Start background thread to consume incoming frames
            reader_thread = threading.Thread(target=socket_reader, args=(new_ws,), daemon=True)
            reader_thread.start()

            # Heartbeat loop: Orbit expects JSON ping every 20-25s
            while running and reader_thread.is_alive():
                time.sleep(20)
                with ws_lock:
                    if ws_conn:
                        ws_conn.send(json.dumps({"event": "ping"}))

        except Exception as e:
            print(f"[B-HYVE DISCONNECT] {e}. Reconnecting in 5s...")
            with ws_lock:
                if ws_conn:
                    try:
                        ws_conn.close()
                    except Exception:
                        pass
                ws_conn = None
            time.sleep(5)

def trigger_spray():
    with ws_lock:
        if not ws_conn:
            print("[TRIGGER ERROR] WebSocket is not connected.")
            return False

        print(f"[TRIGGER] >>> FIRING Station {STATION} for {BURST_SECONDS}s <<<")
        fire_cmd = {
            "event": "change_mode",
            "mode": "manual",
            "device_id": DEVICE_ID,
            "stations": [{"station": STATION, "run_time": 1}]
        }
        try:
            ws_conn.send(json.dumps(fire_cmd))
        except Exception as e:
            print(f"[TRIGGER SEND ERROR] {e}")
            return False

    # Burst duration
    time.sleep(BURST_SECONDS)

    # Robust Stop with verification & rapid-fire redundancy
    stop_cmd = json.dumps({
        "event": "change_mode",
        "mode": "auto",
        "device_id": DEVICE_ID
    })
    
    stopped = False
    for attempt in range(1, 4):
        with ws_lock:
            if ws_conn:
                try:
                    ws_conn.send(stop_cmd)
                    # Rapid duplicate 100ms later to survive Wi-Fi packet drops
                    time.sleep(0.1)
                    ws_conn.send(stop_cmd)
                    stopped = True
                    break
                except Exception as e:
                    print(f"[STOP SEND ERROR attempt {attempt}] {e}")
        time.sleep(0.3)

    if stopped:
        print("[TRIGGER] Valve closed successfully.")
        return True
    else:
        print("[TRIGGER CRITICAL ERROR] Failed to send valve shutoff command after 3 attempts!")
        return False

def listen_local_commands():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 9999))
    server.listen(5)
    print("[LISTENER] Listening for local triggers on 127.0.0.1:9999...")
    
    while running:
        try:
            client, _ = server.accept()
            msg = client.recv(1024).decode().strip()
            if msg == "FIRE":
                threading.Thread(target=trigger_spray).start()
                client.send(b"ACK_FIRED\n")
            client.close()
        except Exception as e:
            print(f"[LISTENER ERROR] {e}")

if __name__ == "__main__":
    t_ws = threading.Thread(target=maintain_websocket, daemon=True)
    t_ws.start()
    listen_local_commands()
