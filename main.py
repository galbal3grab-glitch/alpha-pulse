import requests
import time
import os
from datetime import datetime, timezone

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("❌ BOT_TOKEN or CHAT_ID is missing")

SCAN_INTERVAL = 300  # 5 minutes

EXCLUDED_SYMBOLS = ["BTC", "ETH", "SOL"]

MIN_VOLUME = 300_000
MIN_CHANGE = 3
MAX_CHANGE = 15

BINANCE_URL = "https://api.binance.com/api/v3/ticker/24hr"

# ================= TELEGRAM =================
def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print("Telegram error:", e)

# ================= HELPERS =================
def is_excluded(symbol):
    for ex in EXCLUDED_SYMBOLS:
        if symbol.startswith(ex):
            return True
    return False

def now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

# ================= SCAN =================
def scan_market():
    try:
        data = requests.get(BINANCE_URL, timeout=15).json()
    except Exception as e:
        print("Binance fetch error:", e)
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
def format_signal(s):
    entry = round(s["price"], 6)
    target1 = round(entry * 1.01, 6)
    target2 = round(entry * 1.02, 6)
    stop = round(entry * 0.99, 6)

    return f"""
🚨 <b>Alpha Signal Detected</b>

🪙 <b>{s['symbol']}</b>
🕒 {now_utc()}

💰 Entry: <b>{entry}</b>
🎯 TP1: {target1}
🎯 TP2: {target2}
🛑 SL: {stop}

📊 Volume: {int(s['volume']):,} $
📈 Change: {round(s['change'],2)} %

⚠️ Spot only – No financial advice
""".strip()

# ================= MAIN LOOP =================
send_telegram("✅ <b>SmartScanner Bot is LIVE</b>\nBot started successfully.")

print("Bot started...")

while True:
    signals = scan_market()

    if not signals:
        print(f"[{now_utc()}] No signals found")
    else:
        for s in signals:
            msg = format_signal(s)
            send_telegram(msg)
            time.sleep(2)

    time.sleep(SCAN_INTERVAL)
