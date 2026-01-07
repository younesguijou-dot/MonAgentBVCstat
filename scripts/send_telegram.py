import os
from telegram import Bot

async def send_telegram(message: str):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("❌ Secrets Telegram manquants")
        return
    
    bot = Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
