import sys
import time
import threading
import subprocess
import os
import telebot
from telebot import types

BOT_TOKEN = "8542046011:AAGixULwPxZWBesqY2jjI7XndeKMbA67Avk"
AUTHORIZED_USER_ID = 7087305671
MUTE_FILE = "/home/cameronlgreen/cockatoo_project/alexa.disabled"

bot = telebot.TeleBot(BOT_TOKEN)

def log_to_journal(msg):
    # Print directly to systemd service journal
    print(f"[BOT ACTION] {msg}", flush=True)
    # Broadcast to the system syslog / journald
    subprocess.run(["logger", "-t", "cockatoo_bot", msg])

def get_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_status = types.KeyboardButton("📊 Status & Temp")
    
    # Dynamic Voice Alert button
    if os.path.exists(MUTE_FILE):
        btn_voice = types.KeyboardButton("🔊 Enable Voice")
    else:
        btn_voice = types.KeyboardButton("🔇 Mute Voice")

    btn_start = types.KeyboardButton("🟢 Start Monitor")
    btn_stop = types.KeyboardButton("🔴 Stop Monitor")
    btn_test = types.KeyboardButton("🧪 Test Alert")

    markup.row(btn_status, btn_voice)
    markup.row(btn_start, btn_stop)
    markup.row(btn_test)
    return markup

def is_authorized(message):
    return message.from_user.id == AUTHORIZED_USER_ID

@bot.message_handler(func=lambda message: message.text == "🧪 Test Alert")
def handle_test_alert(message):
    if not is_authorized(message):
        return
    bot.send_message(message.chat.id, "🧪 Starting end-to-end test (Valve + Desktop + Alexa + Photo)...")

    def _run_test():
        try:
            import cv2
            import numpy as np
            from datetime import datetime
            sys.path.append("/home/cameronlgreen/cockatoo_project")
            import live_monitor

            # 1. B-Hyve valve trigger (3.5s verified burst)
            try:
                if hasattr(live_monitor, "bhyve") and hasattr(live_monitor.bhyve, "trigger_spray"):
                    live_monitor.bhyve.trigger_spray(duration=3.5)
                else:
                    bhyve_cls = getattr(live_monitor, "BHyveWS", getattr(live_monitor, "BHyveClient", getattr(live_monitor, "BHyveController", None)))
                    if bhyve_cls:
                        client = bhyve_cls()
                        time.sleep(1.5)
                        client.trigger_spray(duration=3.5)
            except Exception as e:
                print(f"[TEST ERROR B-HYVE] {e}", flush=True)

            # 2. Write snapshot to trigger_photos
            folder = "/home/cameronlgreen/cockatoo_project/trigger_photos"
            os.makedirs(folder, exist_ok=True)
            ts = datetime.now().strftime("%d%b_%H-%M-%S")
            fname = f"{folder}/hit_test_{ts}.jpg"

            dummy = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.rectangle(dummy, (15, 15), (625, 465), (0, 200, 0), 3)
            cv2.putText(dummy, "TELEGRAM TEST ALERT", (45, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 255, 0), 2)
            cv2.putText(dummy, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), (45, 275), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200, 200, 200), 2)
            cv2.imwrite(fname, dummy)

            # 3. Pi Desktop popup
            try:
                live_monitor.display_on_desktop(fname)
            except Exception as e:
                print(f"[TEST ERROR DISPLAY] {e}", flush=True)

            # 4. Telegram alert dispatch
            try:
                live_monitor.send_telegram_alert(fname, f"🧪 Manual Test Completed ({ts})")
            except Exception as e:
                print(f"[TEST ERROR TELEGRAM] {e}", flush=True)

            # 5. Alexa trigger
            try:
                live_monitor.trigger_alexa()
            except Exception as e:
                print(f"[TEST ERROR ALEXA] {e}", flush=True)

        except Exception as err:
            bot.send_message(message.chat.id, f"❌ Test execution error: {err}")

    threading.Thread(target=_run_test, daemon=True).start()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if not is_authorized(message):
        return
    bot.send_message(
        message.chat.id,
        "Cockatoo Monitor Controller online.\nUse the buttons below to control the feeder system:",
        reply_markup=get_keyboard()
    )

@bot.message_handler(func=lambda msg: msg.text in ["🔇 Mute Voice", "🔊 Enable Voice"])
def handle_voice_toggle(message):
    if not is_authorized(message):
        return
    if os.path.exists(MUTE_FILE):
        os.remove(MUTE_FILE)
        log_msg = "Alexa voice notifications UNMUTED / ENABLED via Telegram."
        reply = "🔊 Voice Monkey alert ENABLED."
    else:
        with open(MUTE_FILE, "w") as f:
            f.write("disabled")
        log_msg = "Alexa voice notifications MUTED via Telegram (Water spray active)."
        reply = "🔇 Voice Monkey alert MUTED (water spray will still fire)."

    log_to_journal(log_msg)
    bot.send_message(message.chat.id, reply, reply_markup=get_keyboard())

@bot.message_handler(func=lambda msg: msg.text == "🟢 Start Monitor")
def handle_start(message):
    if not is_authorized(message):
        return
    log_to_journal("START command received via Telegram. Launching cockatoo_monitor.service.")
    bot.send_message(message.chat.id, "Starting cockatoo monitor service...")
    subprocess.run(["sudo", "systemctl", "start", "cockatoo_monitor.service"])
    check_status(message.chat.id)

@bot.message_handler(func=lambda msg: msg.text == "🔴 Stop Monitor")
def handle_stop(message):
    if not is_authorized(message):
        return
    log_to_journal("STOP command received via Telegram. Stopping cockatoo_monitor.service.")
    bot.send_message(message.chat.id, "Stopping cockatoo monitor service...")
    subprocess.run(["sudo", "systemctl", "stop", "cockatoo_monitor.service"])
    check_status(message.chat.id)

@bot.message_handler(func=lambda msg: msg.text == "📊 Status & Temp")
def handle_status(message):
    if not is_authorized(message):
        return
    check_status(message.chat.id)

def check_status(chat_id):
    res = subprocess.run(["systemctl", "is-active", "cockatoo_monitor.service"], capture_output=True, text=True)
    status = res.stdout.strip()
    status_icon = "🟢 RUNNING" if status == "active" else "🔴 STOPPED"

    voice_status = "🔴 MUTED" if os.path.exists(MUTE_FILE) else "🟢 ACTIVE"

    temp_res = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True, text=True)
    temp = temp_res.stdout.strip().replace("temp=", "") if temp_res.returncode == 0 else "Unknown"

    text = f"*Service Status*: {status_icon}\n*Voice Monkey Alert*: {voice_status}\n*Pi Temperature*: {temp}"
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=get_keyboard())

if __name__ == "__main__":
    print("[BOT] Feeder remote control bot listening...", flush=True)
    bot.infinity_polling()
