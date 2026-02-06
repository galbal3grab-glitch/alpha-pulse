import requests
import time
from datetime import datetime, timezone

# ===============================
# TELEGRAM CONFIG
# ===============================
BOT_TOKEN = "8319981273:AAFxxGWig3lHrVgi6FnK8hPkq3ume8HghSA"
CHAT_ID = "5837332461"

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
# STARTUP MESSAGE
# ===============================
now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
send_telegram(
    f"🚀 <b>Alpha Pulse LIVE</b>\n"
    f"✅ Bot started successfully\n"
    f"🕒 {now}"
)

# ===============================
# BINANCE API
# ===============================
BINANCE_24H = "https://api.binance.com/api/v3/ticker/24hr"

# ===============================
# FILTER SETTINGS (ذكية + مزعجة)
# ===============================
MIN_VOLUME = 1_000_000       # 1M USDT
MIN_CHANGE = 2.5             # % change
MIN_PRICE = 0.0001           # نتجنب الميمات الميتة
SLEEP_TIME = 90              # كل دقيقة ونص

sent_cache = {}

def scan_binance():
    try:
        r = requests.get(BINANCE_24H, timeout=15)
        return r.json()
    except Exception as e:
        print("Binance error:", e)
        return []

while True:
    coins = scan_binance()

    for coin in coins:
        symbol = coin.get("symbol", "")
        if not symbol.endswith("USDT"):
            continue

        try:
            price = float(coin["lastPrice"])
            volume = float(coin["quoteVolume"])
            change = float(coin["priceChangePercent"])
        except:
            continue

        # فلترة أولية
        if price < MIN_PRICE:
            continue
        if volume < MIN_VOLUME:
            continue
        if change < MIN_CHANGE:
            continue

        # فلترة الحركة الوهمية
        prev = sent_cache.get(symbol)
        if prev:
            if volume <= prev["volume"] and change <= prev["change"]:
                continue

        sent_cache[symbol] = {
            "price": price,
            "volume": volume,
            "change": change
        }

        msg = (
            f"🔥 <b>SPOT MOMENTUM DETECTED</b>\n\n"
            f"💎 <b>{symbol}</b>\n"
            f"💰 Price: <code>{price}</code>\n"
            f"📊 Change 24h: <b>{change}%</b>\n"
            f"💧 Volume: <b>{int(volume):,}$</b>\n\n"
            f"⚠️ زخم حقيقي + فوليوم داخل\n"
            f"👀 راقب قبل الدخول"
        )

        send_telegram(msg)
        time.sleep(2)

    time.sleep(SLEEP_TIME)
