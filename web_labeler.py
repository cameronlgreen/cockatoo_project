import os, glob, shutil
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

INBOX = os.path.expanduser("~/cockatoo_project/training_data/inbox")
BASE = os.path.expanduser("~/cockatoo_project/dataset/train")

CLASSES = ['cockatoo', 'galah', 'lorikeet', 'rosella', 'miner', 'magpie']

for c in CLASSES:
    os.makedirs(os.path.join(BASE, c), exist_ok=True)

class LabelHandler(BaseHTTPRequestHandler):
    def get_files(self):
        return sorted(glob.glob(os.path.join(INBOX, "*.jpg")), key=os.path.getmtime)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)

        if parsed.path.startswith('/img/'):
            fn = os.path.basename(parsed.path)
            fpath = os.path.join(INBOX, fn)
            if os.path.exists(fpath):
                self.send_response(200)
                self.send_header('Content-Type', 'image/jpeg')
                self.end_headers()
                with open(fpath, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404)
            return

        # Action handling
        if 'action' in qs and 'file' in qs:
            action = qs['action'][0]
            fn = os.path.basename(qs['file'][0])
            src = os.path.join(INBOX, fn)
            if os.path.exists(src):
                if action in CLASSES:
                    shutil.move(src, os.path.join(BASE, action, fn))
                elif action == 'trash':
                    os.remove(src)

            # Redirect back to home
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
            return

        files = self.get_files()
        cur_file = os.path.basename(files[0]) if files else None
        remaining = len(files)

        counts = {c: len(glob.glob(os.path.join(BASE, c, "*.jpg"))) for c in CLASSES}

        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Bird Crop Labeler</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #161616; color: #eee; text-align: center; padding: 20px; }}
  .counts {{ margin-bottom: 20px; font-size: 15px; display: flex; justify-content: center; flex-wrap: wrap; gap: 8px; align-items: center; }}
  .badge {{ display: inline-block; padding: 6px 12px; border-radius: 6px; background: #262626; font-weight: 500; border: 1px solid #333; }}
  .preview {{ max-width: 340px; max-height: 340px; border-radius: 8px; border: 2px solid #444; margin: 15px auto; display: block; }}
  .buttons {{ margin-top: 15px; display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; max-width: 750px; margin-left: auto; margin-right: auto; }}
  .btn {{ font-size: 16px; font-weight: 600; padding: 12px 18px; border: none; border-radius: 6px; cursor: pointer; color: white; text-decoration: none; transition: transform 0.05s ease; }}
  .btn:active {{ transform: scale(0.97); }}
  .btn-c {{ background: #d4a017; }}
  .btn-g {{ background: #d94b76; }}
  .btn-l {{ background: #2e8b57; }}
  .btn-r {{ background: #b22222; }}
  .btn-m {{ background: #708090; }}
  .btn-p {{ background: #2f4f4f; border: 1px solid #777; }}
  .btn-t {{ background: #444; }}
  .hint {{ margin-top: 18px; font-size: 13px; color: #888; }}
</style>
</head>
<body>
  <h2>Bird Training Data Labeler</h2>
  <div class="counts">
    <span class="badge" style="background:#111; border-color:#555;">Remaining: <b>{remaining}</b></span>
    <span class="badge" style="color:#ffd700">Cockatoo: {counts['cockatoo']}</span>
    <span class="badge" style="color:#ff69b4">Galah: {counts['galah']}</span>
    <span class="badge" style="color:#32cd32">Lorikeet: {counts['lorikeet']}</span>
    <span class="badge" style="color:#ff4500">Rosella: {counts['rosella']}</span>
    <span class="badge" style="color:#b0c4de">Miner: {counts['miner']}</span>
    <span class="badge" style="color:#ffffff">Magpie: {counts['magpie']}</span>
  </div>
"""
        if cur_file:
            html += f"""
  <img src="/img/{cur_file}" class="preview">
  <div style="font-family: monospace; font-size: 12px; color: #888;">{cur_file}</div>
  <div class="buttons">
    <a href="/?action=cockatoo&file={cur_file}" class="btn btn-c" id="key-c">[C] Cockatoo</a>
    <a href="/?action=galah&file={cur_file}" class="btn btn-g" id="key-g">[G] Galah</a>
    <a href="/?action=lorikeet&file={cur_file}" class="btn btn-l" id="key-l">[L] Lorikeet</a>
    <a href="/?action=rosella&file={cur_file}" class="btn btn-r" id="key-r">[R] Rosella</a>
    <a href="/?action=miner&file={cur_file}" class="btn btn-m" id="key-m">[M] Miner</a>
    <a href="/?action=magpie&file={cur_file}" class="btn btn-p" id="key-p">[P] Magpie</a>
    <a href="/?action=trash&file={cur_file}" class="btn btn-t" id="key-space">[Space / D] Trash</a>
  </div>
  <div class="hint">Keyboard shortcuts: <b>C</b>, <b>G</b>, <b>L</b>, <b>R</b>, <b>M</b>, <b>P</b> | <b>Space / D</b> to trash</div>
  <script>
    window.addEventListener('keydown', function(e) {{
      const key = e.key.toLowerCase();
      if (key === 'c') window.location.href = document.getElementById('key-c').href;
      else if (key === 'g') window.location.href = document.getElementById('key-g').href;
      else if (key === 'l') window.location.href = document.getElementById('key-l').href;
      else if (key === 'r') window.location.href = document.getElementById('key-r').href;
      else if (key === 'm') window.location.href = document.getElementById('key-m').href;
      else if (key === 'p') window.location.href = document.getElementById('key-p').href;
      else if (key === ' ' || key === 'd') window.location.href = document.getElementById('key-space').href;
    }});
  </script>
"""
        else:
            html += "<h3>Inbox is clear! All crops categorized.</h3>"

        html += "</body></html>"
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

# Allow immediate socket reuse to prevent [Errno 98]
class ReusableServer(HTTPServer):
    allow_reuse_address = True

print("Starting Web Labeler on port 8080 (Miner [M] and Magpie [P] enabled)...")
ReusableServer(("", 8080), LabelHandler).serve_forever()
