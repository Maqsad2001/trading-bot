import os
import asyncio
from telegram import Bot
from yahooquery import Ticker
import pandas as pd
import pandas_ta as ta

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TOKEN)

# === Asosiy tahlil funksiyasi ===
def check_stock(ticker):
    try:
        t = Ticker(ticker)
        df = t.history(period="10d", interval="1d")

        if df is None or len(df) < 5:
            return None

        if isinstance(df.index, pd.MultiIndex):
            df = df.reset_index(level=0, drop=True)

        df["RSI"] = ta.rsi(df["close"], length=14)
        price = df["close"].iloc[-1]
        prev_price = df["close"].iloc[-2]
        rsi = df["RSI"].iloc[-1]

        # Filtirlar:
        if (
            price < 5
            and price > prev_price  # bugungi narx kechagidan yuqori
            and rsi > 40             # RSI oversold emas
        ):
            return f"{ticker} ✅ | Price: ${price:.2f} | RSI: {rsi:.1f}"

    except Exception:
        return None
    return None

# === Skanner funksiyasi ===
async def scan_and_send():
    tickers = ["AAPL", "TSLA", "F", "NOK", "SIRI", "AMZN", "T", "INTC", "BAC", "VZ"]
    results = []
    for t in tickers:
        r = check_stock(t)
        if r:
            results.append(r)

    if results:
        msg = "📊 *Topilgan aksiyalar:*\n\n" + "\n".join(results)
    else:
        msg = "❌ Hozircha shartlarga mos aksiya topilmadi."

    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")

async def main():
    while True:
        await scan_and_send()
        await asyncio.sleep(3600)  # har soatda tekshiradi

if __name__ == "__main__":
    asyncio.run(main())
