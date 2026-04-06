import requests
from django.conf import settings

def send_telegram_message(text):
    """Sends a message to the Telegram chat using HTML parse mode."""
    if not hasattr(settings, 'TELEGRAM_BOT_TOKEN') or not hasattr(settings, 'TELEGRAM_CHAT_ID'):
        return False
        
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False
