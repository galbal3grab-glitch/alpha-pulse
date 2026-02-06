import requests
import time
from datetime import datetime, timezone
import os

# ================== CONFIG ==================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("❌ BOT_TOKEN or CHAT_ID is missing in Railway Variables")

SCAN_INTERVAL = 300  # 5 دقائق

EXCLUDED_SYMBOLS = ["BTC", "ETH", "SOL"]

MIN_VOLUME = 300_000
MIN_CHANGE = 3      # %
MAX_CHANGE = 15     # %

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
        requests.post(url, json=payload, timeout=10)
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
    except Exception:
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
        except Exception:
            continue

        if volume >= MIN_VOLUME and MIN_CHANGE <= change <= MAX_CHANGE:
            signals.append({
                "symbol": symbol,
                "price": price,
                "volume": volume,
                "change": change
            })

    return signals

# ================== FORMAT ==================

def format_signal(c):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    entry = round(c["price"], 6)
    target1 = round(entry * 1.01, 6)
    target2 = round(entry * 1.02, 6)
    stop = round(entry * 0.99, 6)

    msg = (
        f"🚀 <b>Alpha Pulse Signal</b>\n\n"
        f"🪙 <b>{c['symbol']}</b>\n"
        f"📈 Change: <b>{c['change']}%</b>\n"
        f"💰 Volume: <b>{int(c['volume']):,}</b>\n\n"
        f"🎯 Entry: <code>{entry}</code>\n"
        f"🎯 Target 1: <code>{target1}</code>\n"
        f"🎯 Target 2: <code>{target2}</code>\n"
        f"🛑 Stop: <code>{stop}</code>\n\n"
        f"⏱ {now}"
    )
    return msg

# ================== MAIN ==================

if __name__ == "__main__":
    send_telegram("🟢 <b>Alpha Pulse</b> بدأ العمل بنجاح\n\n⏳ المراقبة شغالة 24/7")

    sent_cache = set()

    while True:
        signals = scan_market()

        for coin in signals:
            key = f"{coin['symbol']}_{int(time.time() / SCAN_INTERVAL)}"
            if key in sent_cache:
                continue

            sent_cache.add(key)
            send_telegram(format_signal(coin))
            time.sleep(2)

        time.sleep(SCAN_INTERVAL)
