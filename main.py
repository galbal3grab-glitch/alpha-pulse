import requests
import time
from datetime import datetime, timezone
import os

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("❌ BOT_TOKEN or CHAT_ID is missing in Railway Variables")

SCAN_INTERVAL = 300  # 5 دقائق

EXCLUDED_SYMBOLS = ["BTC", "ETH", "SOL"]

MIN_VOLUME = 300_000
MIN_CHANGE = 3
MAX_CHANGE = 15

BINANCE_ALPHA_URL = "https://api.binance.com/api/v3/ticker/24hr"

# ================= TELEGRAM =================
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
        print("📨 Telegram status:", r.status_code)
    except Exception as e:
        print("❌ Telegram error:", e)

# ================= FILTER =================
def is_excluded(symbol):
    return any(symbol.startswith(ex) for ex in EXCLUDED_SYMBOLS)

# ================= SCAN =================
def scan_market():
    try:
        data = requests.get(BINANCE_ALPHA_URL, timeout=15).json()
    except Exception as e:
        print("❌ Binance error:", e)
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
        except:
            continue

        if volume >= MIN_VOLUME and MIN_CHANGE <= change <= MAX_CHANGE:
            signals.append({
                "symbol": symbol,
                "price": price,
                "volume": volume,
                "change": change
            })

    return signals

# ================= FORMAT =================
def format_signal(c):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    entry = round(c["price"], 6)
    target1 = round(entry * 1.01, 6)
    target2 = round(entry * 1.02, 6)
    stop = round(entry * 0.99, 6)

    return f"""
🚀 <b>ALPHA SIGNAL</b>

🪙 <b>{c['symbol']}</b>
💰 السعر: <b>{entry}</b>
📊 التغير: <b>{round(c['change'],2)}%</b>
💧 الفوليوم: <b>{round(c['volume'],0):,}$</b>

🎯 دخول: <b>{entry}</b>
🎯 هدف 1: <b>{target1}</b>
🎯 هدف 2: <b>{target2}</b>
🛑 وقف: <b>{stop}</b>

⏱ {now}
"""

# ================= MAIN LOOP =================
def main():
    send_telegram("🟢 <b>SmartScanner Bot بدأ العمل بنجاح</b>\n⏳ مراقبة السوق الآن...")

    while True:
        print("🔍 Scanning market...")
        signals = scan_market()

        if signals:
            for s in signals:
                send_telegram(format_signal(s))
        else:
            print("⚪ لا فرص حالياً")

        time.sleep(SCAN_INTERVAL)

# ================= RUN =================
if __name__ == "__main__":
    main()
