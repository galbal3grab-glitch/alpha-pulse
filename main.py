import requests
import time
from datetime import datetime, timezone

# ================== CONFIG (HARD CODED) ==================

BOT_TOKEN = "8319981273:AAFxxGWig3lHrVgi6FnK8hPkq3ume8HghSA"
CHAT_ID = "5837332461"

SCAN_INTERVAL = 300  # 5 minutes

EXCLUDED_SYMBOLS = ["BTC", "ETH", "SOL"]

MIN_VOLUME = 300_000
MIN_CHANGE = 3
MAX_CHANGE = 15

BINANCE_ALPHA_URL = "https://api.binance.com/api/v3/ticker/24hr"

# ================== TELEGRAM ==================

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        print("Telegram status:", r.status_code, r.text)
    except Exception as e:
        print("Telegram error:", e)

# ================== FILTER ==================

def is_excluded(symbol):
    for ex in EXCLUDED_SYMBOLS:
        if symbol.startswith(ex):
            return True
    return False

# ================== SCAN ==================

def scan_market():
    try:
        res = requests.get(BINANCE_ALPHA_URL, timeout=15).json()
    except Exception as e:
        print("Binance error:", e)
        return []

    signals = []

    for coin in res:
        symbol = coin.get("symbol", "")

        if not symbol.endswith("USDT"):
            continue
        if is_excluded(symbol):
            continue

        try:
            price = float(coin["lastPrice"])
            volume = float(coin["quoteVolume"])
            change = float(coin["priceChangePercent"])
        except:
            continue

        if volume >= MIN_VOLUME and MIN_CHANGE <= change <= MAX_CHANGE:
            signals.append(
                f"🚀 <b>ALPHA SIGNAL</b>\n"
                f"🪙 <b>{symbol}</b>\n"
                f"💰 Price: {price}\n"
                f"📊 Volume: {int(volume):,}\n"
                f"📈 Change: {change}%\n"
                f"🕒 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
            )

    return signals

# ================== MAIN ==================

if __name__ == "__main__":
    print("Bot started...")
    send_telegram("✅ Bot is LIVE and scanning the market now.")

    while True:
        signals = scan_market()
        for msg in signals:
            send_telegram(msg)
            time.sleep(2)
        time.sleep(SCAN_INTERVAL)
