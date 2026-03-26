import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import yfinance as yf
from datetime import datetime
from zoneinfo import ZoneInfo

TICKERS = ["NVDA", "SSABBH.HE", "NOKIA.HE", "KCR.HE", "MANTA.HE", "NESTE.HE", "NDA-FI.HE", "WRT1V.HE"]

def fetch(ticker):
    t = yf.Ticker(ticker)
    df = t.history(period="2d")

    if df.empty or len(df) < 2:
        return ticker, None, None, None

    last = df["Close"].iloc[-1]
    prev = df["Close"].iloc[-2]
    pct = (last - prev) / prev * 100
    currency = t.fast_info.get("currency")

    return ticker, last, pct, currency

def build_html(rows):
    now = datetime.now(ZoneInfo("Europe/Helsinki")).strftime("%Y-%m-%d %H:%M")
    html = f"<h2>Aamun osakeraportti ({now})</h2><ul>"
    for t, price, pct, cur in rows:
        if price is None:
            html += f"<li><b>{t}</b>: ei dataa</li>"
        else:
            sign = "▲" if pct >= 0 else "▼"
            html += f"<li><b>{t}</b>: {price:.2f} {cur} ({sign} {pct:.2f}%)</li>"
    html += "</ul>"
    return html

def send_email(html):
    gmail_user = os.getenv("GMAIL_USER")
    gmail_pass = os.getenv("GMAIL_APP_PASSWORD")
    to_email = os.getenv("TO_EMAIL")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Aamun markkinaraportti"
    msg["From"] = gmail_user
    msg["To"] = to_email

    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_pass)
        server.sendmail(gmail_user, to_email, msg.as_string())

if __name__ == "__main__":
    rows = [fetch(t) for t in TICKERS]
    html = build_html(rows)
    send_email(html)
