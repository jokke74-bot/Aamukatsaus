import os
import requests
import yfinance as yf
from datetime import datetime
from zoneinfo import ZoneInfo

TICKERS = ["AAPL", "MSFT", "NVDA", "NOKIA.HE"]
WEBHOOK = os.getenv("TEAMS_WEBHOOK")

def fetch(ticker):
    t = yf.Ticker(ticker)
    info = t.fast_info

    price = info.get("last_price")
    prev = info.get("previous_close")
    currency = info.get("currency")

    if price and prev:
        chg = price - prev
        pct = (chg / prev) * 100
    else:
        chg = pct = None

    return {
        "ticker": ticker,
        "price": price,
        "pct": pct,
        "currency": currency,
    }

def format_msg(rows):
    now = datetime.now(ZoneInfo("Europe/Helsinki")).strftime("%Y-%m-%d %H:%M")
    lines = [f"**Aamun markkinakatsaus** ({now})\n"]

    for r in rows:
        if r["price"] is None:
            lines.append(f"- **{r['ticker']}**: ei dataa")
        else:
            arrow = "▲" if r["pct"] >= 0 else "▼"
            lines.append(
                f"- **{r['ticker']}**: {r['price']:.2f} {r['currency']} "
                f"({arrow} {r['pct']:.2f}%)"
            )
    return "\n".join(lines)

def send(msg):
    requests.post(WEBHOOK, json={"text": msg})

def main():
    rows = [fetch(t) for t in TICKERS]
    msg = format_msg(rows)
    send(msg)

if __name__ == "__main__":
    main()
