import requests
import time
from datetime import datetime, timezone

# ===============================
# CONFIG (غيرهم فقط)
# ===============================
BOT_TOKEN = "8319981273:AAFxxGWig3lHrVgi6FnK8hPkq3ume8HghSA"
CHAT_ID = "5837332461"

# ===============================
# TELEGRAM
# ===============================
def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code != 200:
            print("Telegram error:", r.text)
    except Exception as e:
        print("Telegram exception:", e)

# ===============================
# STARTUP CONFIRMATION (مهم جدًا)
# ===============================
now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
send_telegram(
    f"🚀 <b>Alpha Pulse LIVE</b>\n"
    f"✅ Bot started successfully\n"
    f"🕒 {now}"
)

# ===============================
# BINANCE SPOT SCAN
# ===============================
BINANCE_24H = "https://api.binance.com/api/v3/ticker/24hr"

def scan_binance():
    try:
        r = requests.get(BINANCE_24H, timeout=15)
        data = r.json()
    except Exception as e:
        print("Binance error:", e)
        return []

    results = []

    for coin in data:
        symbol = coin.get("symbol", "")
        if not symbol.endswith("USDT"):
            continue

        try:
            price = float(coin["lastPrice"])
            volume = float(coin["quoteVolume"])
            change = float(coin["priceChangePercent"])
        except:
            continue

        # فلترة خفيفة جدًا (اختبارية)
        if volume > 5_000_000 and change > 5:
            results.append({
                "symbol": symbol,
                "price": price,
                "change": change,
                "volume": volume
            })

    return results

# ===============================
# MAIN LOOP
# ===============================
sent_cache = set()

while True:
    coins = scan_binance()

    for c in coins:
        key = c["symbol"]
        if key in sent_cache:
            continue

        sent_cache.add(key)

        msg = (
            f"🔥 <b>SPOT MOMENTUM</b>\n\n"
            f"🪙 <b>{c['symbol']}</b>\n"
            f"💵 Price: <code>{c['price']}</code>\n"
            f"📈 Change 24h: <b>{c['change']}%</b>\n"
            f"💧 Volume: <b>{int(c['volume']):,}</b>\n\n"
            f"⚠️ مراقبة فقط — بدون دخول تلقائي"
        )

        send_telegram(msg)

    time.sleep(120)
