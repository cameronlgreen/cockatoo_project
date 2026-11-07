path = "/home/cameronlgreen/cockatoo_project/live_monitor.py"
with open(path, "r") as f:
    code = f.read()

# Define the display function
popup_func = """
def display_on_desktop(image_path):
    \"\"\"Displays the hit image directly on the Pi desktop GUI from systemd.\"\"\"
    def _show():
        try:
            # Kill previous feh popups to keep the screen clean
            subprocess.run(["pkill", "-f", "feh --geometry"], stderr=subprocess.DEVNULL)
            
            # Export X11 display environment variables for the desktop session
            env = os.environ.copy()
            env["DISPLAY"] = ":0"
            # Find the active user Xauthority cookie
            xauth_path = os.path.expanduser("~/.Xauthority")
            if os.path.exists(xauth_path):
                env["XAUTHORITY"] = xauth_path
            
            # Launch feh borderless, scaled, auto-closing after 15 seconds
            cmd = [
                "feh",
                "--geometry", "800x600",
                "--scale-down",
                "--auto-zoom",
                "--title", "BIRD ALERT",
                image_path
            ]
            subprocess.Popen(cmd, env=env)
        except Exception as err:
            print(f"[DISPLAY ERROR] Could not show desktop image: {err}", flush=True)

    threading.Thread(target=_show, daemon=True).start()
"""

# Inject before trigger handling
if "def display_on_desktop" not in code:
    code = popup_func + "\n" + code

# Inject the trigger call right after cv2.imwrite(hit_filename, feeder_crop)
old_save = "cv2.imwrite(hit_filename, feeder_crop)"
new_save = "cv2.imwrite(hit_filename, feeder_crop)\n                display_on_desktop(hit_filename)"

if old_save in code and "display_on_desktop(hit_filename)" not in code:
    code = code.replace(old_save, new_save)
    with open(path, "w") as f:
        f.write(code)
    print("SUCCESS: Desktop photo popup hooked into trigger sequence.")
else:
    print("Notice: Desktop hook already exists or save target could not be matched.")
