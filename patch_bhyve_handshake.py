path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

old_bhyve_block = """            ws_url = f"wss://api.orbitbhyve.com/v1/events?token={token}"
            try:
                with self.lock:
                    self.ws = websocket.create_connection(ws_url, timeout=10)
                    self.is_connected = True
                    print("[B-HYVE] WebSocket connected and ready.", flush=True)

                def _heartbeat():
                    while self.running and self.is_connected:
                        time.sleep(15)
                        try:
                            with self.lock:
                                if self.is_connected and self.ws:
                                    self.ws.send(json.dumps({"event": "ping"}))
                        except Exception:
                            break

                threading.Thread(target=_heartbeat, daemon=True).start()

                while self.running and self.is_connected:
                    try:
                        self.ws.settimeout(30.0)
                        msg = self.ws.recv()
                        if not msg:
                            break
                    except websocket.WebSocketTimeoutException:
                        continue
                    except Exception:
                        break"""

new_bhyve_block = """            ws_url = f"wss://api.orbitbhyve.com/v1/events?token={token}"
            try:
                with self.lock:
                    self.ws = websocket.create_connection(ws_url, timeout=10)
                    # Complete mandatory Orbit app handshake
                    handshake = {"event": "app_connection", "orbit_session_token": token}
                    self.ws.send(json.dumps(handshake))
                    if hasattr(self, 'device_id') and self.device_id:
                        self.ws.send(json.dumps({"event": "subscribe", "devices": [self.device_id]}))
                    self.is_connected = True
                    print("[B-HYVE] WebSocket connected, handshaked, and ready.", flush=True)

                def _heartbeat():
                    while self.running and self.is_connected:
                        time.sleep(20)
                        try:
                            with self.lock:
                                if self.is_connected and self.ws:
                                    self.ws.send(json.dumps({"event": "ping"}))
                        except Exception:
                            break

                threading.Thread(target=_heartbeat, daemon=True).start()

                while self.running and self.is_connected:
                    try:
                        self.ws.settimeout(30.0)
                        msg = self.ws.recv()
                        if not msg:
                            break
                    except (websocket.WebSocketTimeoutException, socket.timeout):
                        continue
                    except Exception:
                        break"""

if old_bhyve_block in code:
    code = code.replace(old_bhyve_block, new_bhyve_block)
    with open(path, "w") as f:
        f.write(code)
    print("SUCCESS: B-hyve WebSocket handshake patched.")
else:
    print("ERROR: Could not locate original B-hyve block.")
