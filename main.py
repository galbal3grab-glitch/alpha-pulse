import requests
import time
from datetime import datetime
import os

# ================= CONFIG =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SCAN_INTERVAL = 300  # 5 دقائق
EXCLUDED_SYMBOLS = ["BTC", "ETH", "SOL"]

MIN_VOLUME = 300_000
MIN_CHANGE = 3  # %
MAX_CHANGE = 15  # %

BINANCE_ALPHA_URL = "https://api.binance.com/api/v3/ticker/24hr"

# ================= TELEGRAM =================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, json=payload)

# ================= FILTER =================
def is_excluded(symbol):
    for ex in EXCLUDED_SYMBOLS:
        if symbol.startswith(ex):
            return True
    return False

# ================= SCAN =================
def scan_market():
    res = requests.get(BINANCE_ALPHA_URL).json()
    signals = []

    for coin in res:
        symbol = coin["symbol"]

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
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    entry = round(c["price"], 6)
    target1 = round(entry * 1.01, 6)
    target2 = round(entry * 1.02, 6)
    stop = round(entry * 0.99, 6)

    msg = f"""
🚨 <b>Alpha Pulse | Spot Signal</b>

🪙 <b>العملة:</b> {c['symbol']}
💰 <b>السعر:</b> {entry}
📊 <b>الفوليوم:</b> {int(c['volume']):,}$
📈 <b>التغير:</b> {round(c['change'],2)}%

🎯 <b>الدخول:</b> {entry}
🎯 <b>هدف 1:</b> {target1}
🎯 <b>هدف 2:</b> {target2}
🛑 <b>ستوب:</b> {stop}

⏱ <b>الوقت:</b> {now}

⚠️ سبوت فقط – لا صفقة تلقائية
"""
    return msg

# ================= MAIN LOOP =================
def main():
    send_telegram("🟢 Alpha Pulse بدأ العمل بنجاح")

    sent = set()

    while True:
        try:
            signals = scan_market()
            for c in signals:
                key = c["symbol"]
                if key not in sent:
                    send_telegram(format_signal(c))
                    sent.add(key)

            time.sleep(SCAN_INTERVAL)

        except Exception as e:
            send_telegram(f"❌ خطأ: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
