import os, glob
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8080
INBOX = os.path.expanduser("~/cockatoo_project/training_data/inbox")
HTML_PATH = os.path.join(INBOX, "index.html")

files = sorted(glob.glob(os.path.join(INBOX, "*.jpg")), key=os.path.getmtime, reverse=True)[:160]

html = """<!DOCTYPE html>
<html>
<head><title>Inbox Image Review</title>
<style>
body { font-family: sans-serif; background: #181818; color: #fff; padding: 15px; }
.grid { display: flex; flex-wrap: wrap; gap: 8px; }
.card { background: #262626; padding: 4px; border-radius: 4px; text-align: center; }
img { max-width: 140px; max-height: 140px; display: block; margin: auto; }
p { font-size: 10px; margin: 4px 0 0; color: #aaa; }
</style>
</head>
<body>
<h2>Latest 160 Harvester Crops (Inbox)</h2>
<div class="grid">
"""

for f in files:
    fn = os.path.basename(f)
    html += f'<div class="card"><img src="{fn}"><p>{fn}</p></div>\n'

html += "</div></body></html>"

with open(HTML_PATH, "w") as out:
    out.write(html)

os.chdir(INBOX)
print(f"Server started: open http://<raspberrypi-ip>:{PORT}/ in your browser")
HTTPServer(("", PORT), SimpleHTTPRequestHandler).serve_forever()
