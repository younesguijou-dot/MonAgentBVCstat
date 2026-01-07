import os
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise RuntimeError("Missing TELEGRAM_TOKEN or TELEGRAM_CHAT_ID")

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
r = requests.post(url, json={"chat_id": CHAT_ID, "text": "✅ Test Telegram OK"})

print("Status:", r.status_code)
print("Response:", r.text)

if r.status_code != 200:
    raise RuntimeError("Telegram test failed")
