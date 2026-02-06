import requests
import time
from datetime import datetime, timezone

# ================== CONFIG ==================
BOT_TOKEN = "8319981273:AAFxxGWig3lHrVgi6FnK8hPkq3ume8HghSA"
CHAT_ID = "5837332461"

SCAN_INTERVAL = 300  # 5 minutes

EXCLUDED_SYMBOLS = ["BTC", "ETH", "SOL"]
MIN_VOLUME = 300_000
MIN_CHANGE = 3
MAX_CHANGE = 15

BINANCE_URL = "https://api.binance.com/api/v3/ticker/24hr"

# ================== TELEGRAM ==================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    r = requests.post(url, json=payload, timeout=10)
    return r.status_code == 200

# ================== FILTER ==================
def is_excluded(symbol):
    return any(symbol.startswith(x) for x in EXCLUDED_SYMBOLS)

# ================== SCAN ==================
def scan_market():
    try:
        data = requests.get(BINANCE_URL, timeout=15).json()
    except Exception:
        return []

    signals = []

    for coin in data:
        symbol = coin.get("symbol", "")

        if not symbol.endswith("USDT"):
            continue
        if is_excluded(symbol):
            continue

        try:
            price = float(coin["lastPrice"])
            volume = float(coin["quoteVolume"])
            change = float(coin["priceChangePercent"])
        except Exception:
            continue

        if volume >= MIN_VOLUME and MIN_CHANGE <= change <= MAX_CHANGE:
            signals.append((symbol, price, volume, change))

    return signals

# ================== MAIN ==================
if __name__ == "__main__":
    send_telegram("🚀 <b>Bot is LIVE</b>\nScanning market now...")

    while True:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        results = scan_market()

        for s in results:
            msg = (
                f"🔥 <b>Alpha Signal</b>\n\n"
                f"🪙 <b>{s[0]}</b>\n"
                f"💰 Price: {s[1]}\n"
                f"📊 Volume: {int(s[2]):,}\n"
                f"📈 Change: {s[3]}%\n"
                f"⏱ {now}"
            )
            send_telegram(msg)
            time.sleep(2)

        time.sleep(SCAN_INTERVAL)
