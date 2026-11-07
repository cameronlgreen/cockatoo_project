path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

# Replace the connection loop with a dedicated heartbeat worker
old_loop = """                while self.running and self.is_connected:
                    try:
                        self.ws.settimeout(20.0)
                        msg = self.ws.recv()
                        if not msg:
                            break
                    except websocket.WebSocketTimeoutException:
                        try:
                            self.ws.ping()
                        except Exception:
                            break
                    except Exception:
                        break"""

new_loop = """                def _heartbeat():
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

if old_loop in code:
    code = code.replace(old_loop, new_loop)
    with open(path, "w") as f:
        f.write(code)
    print("Keepalive heartbeat patch applied successfully.")
else:
    print("Could not match old loop snippet.")
