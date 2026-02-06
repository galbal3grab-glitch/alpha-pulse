import time
import requests
from datetime import datetime, timezone

# ================== CONFIG ==================
BOT_TOKEN = "8319981273:AAFxxGWig3lHrVgi6FnK8hPkq3ume8HghSA"
CHAT_ID = "5837332461"
# ============================================

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def send_message(text):
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(TELEGRAM_URL, json=payload, timeout=10)
        print("Telegram response:", r.text)
    except Exception as e:
        print("Telegram ERROR:", e)

def main():
    start_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # 🔥 رسالة إجبارية عند التشغيل
    send_message(
        "🚀 <b>BOT STARTED SUCCESSFULLY</b>\n"
        f"🕒 {start_time}\n"
        "✅ Telegram connection OK\n"
        "🔁 Test message every 60 seconds"
    )

    counter = 1
    while True:
        now = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
        send_message(
            f"🧪 <b>Heartbeat Test</b>\n"
            f"⏱ Time: {now}\n"
            f"🔢 Count: {counter}"
        )
        counter += 1
        time.sleep(60)

if __name__ == "__main__":
    main()
