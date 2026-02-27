import requests

from app.config import BOT_TOKEN


def send_otp(chat_id, otp_code):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": f"Your verification code: {otp_code}\nThis code expires in 5 minutes.",
    }
    response = requests.post(url, json=payload)
    return response.ok
