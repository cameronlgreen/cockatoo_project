import http.server
import socketserver
import cv2
import json
import re
import threading

RTSP = "rtsp://cockatoo:cockatoo1234@192.168.1.147:554/stream2"
cap = cv2.VideoCapture(RTSP, cv2.CAP_FFMPEG)
for _ in range(5):
    ret, frame = cap.read()
cap.release()

if not ret or frame is None:
    print("Failed to capture from Tapo camera.")
    exit(1)

cv2.imwrite("/home/cameronlgreen/cockatoo_project/align.jpg", frame)
h, w, _ = frame.shape
print(f"Captured live frame: {w}x{h}")

HTML_CONTENT = """<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Align Feeder Zone</title>
<style>
  body { font-family: sans-serif; text-align: center; background: #222; color: #eee; margin: 10px; }
  #container { position: relative; display: inline-block; cursor: crosshair; user-select: none; }
  img { max-width: 90vw; height: auto; display: block; border: 2px solid #555; }
  #box { position: absolute; border: 2px solid #00ff00; background: rgba(0, 255, 0, 0.2); display: none; pointer-events: none; }
  button { padding: 12px 24px; font-size: 16px; font-weight: bold; background: #28a745; color: white; border: none; border-radius: 6px; cursor: pointer; margin-top: 15px; }
  #status { margin-top: 10px; font-size: 18px; color: #ffeb3b; }
</style>
</head>
<body>
  <h2>Drag a Box Over the Feeder Area</h2>
  <div id="container">
    <img id="cam" src="/align.jpg" draggable="false" />
    <div id="box"></div>
  </div>
  <br>
  <button id="saveBtn" onclick="saveZone()">Save Feeder Zone</button>
  <div id="status">Click and drag to set alignment.</div>

<script>
  const img = document.getElementById("cam");
  const box = document.getElementById("box");
  let startX, startY, endX, endY, dragging = false;
  let coords = null;

  img.addEventListener("mousedown", (e) => {
    const r = img.getBoundingClientRect();
    startX = e.clientX - r.left;
    startY = e.clientY - r.top;
    dragging = true;
    box.style.display = "block";
    box.style.left = startX + "px";
    box.style.top = startY + "px";
    box.style.width = "0px";
    box.style.height = "0px";
  });

  window.addEventListener("mousemove", (e) => {
    if (!dragging) return;
    const r = img.getBoundingClientRect();
    let curX = Math.max(0, Math.min(e.clientX - r.left, r.width));
    let curY = Math.max(0, Math.min(e.clientY - r.top, r.height));
    let x = Math.min(startX, curX);
    let y = Math.min(startY, curY);
    let w = Math.abs(curX - startX);
    let h = Math.abs(curY - startY);
    box.style.left = x + "px";
    box.style.top = y + "px";
    box.style.width = w + "px";
    box.style.height = h + "px";
    coords = {
      x1: +(x / r.width).toFixed(2),
      y1: +(y / r.height).toFixed(2),
      x2: +((x + w) / r.width).toFixed(2),
      y2: +((y + h) / r.height).toFixed(2)
    };
    document.getElementById("status").innerText = "Selected: (" + coords.x1 + ", " + coords.y1 + ", " + coords.x2 + ", " + coords.y2 + ")";
  });

  window.addEventListener("mouseup", () => { dragging = false; });

  function saveZone() {
    if (!coords) { alert("Please draw a box first!"); return; }
    fetch("/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(coords)
    }).then(res => res.text()).then(txt => {
      document.getElementById("status").innerText = "SAVED! You can close this tab now.";
      alert("Saved successfully to live_monitor.py!");
    });
  }
</script>
</body>
</html>"""

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode())
        elif self.path == "/align.jpg":
            with open("/home/cameronlgreen/cockatoo_project/align.jpg", "rb") as f:
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.end_headers()
                self.wfile.write(f.read())
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/save":
            length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(length).decode()
            data = json.loads(raw_body)
            new_zone = f"FEEDER_ZONE      = ({data['x1']}, {data['y1']}, {data['x2']}, {data['y2']})"
            
            path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
            with open(path, "r") as f:
                code = f.read()
            code = re.sub(r"FEEDER_ZONE\s*=\s*\(.*?\)", new_zone, code)
            with open(path, "w") as f:
                f.write(code)
                
            print(f"\nSUCCESS! Updated live_monitor.py to: {new_zone}", flush=True)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
            threading.Thread(target=httpd.shutdown, daemon=True).start()

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", 8080), Handler) as httpd:
    print("\nAlignment Tool running at: http://localhost:8080 (or http://raspberrypi.local:8080)")
    print("Open the link in your browser, drag the box, and click Save.\n")
    httpd.serve_forever()
