import requests
from bot.config import Config

def send_telegram_message(message: str):
    """ Отправляет сообщение в Telegram. """
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": Config.TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=data)
