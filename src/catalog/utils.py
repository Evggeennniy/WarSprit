import requests
import os


def formater_text(text):
    return text.replace("<p>", "").replace("</p>", "").replace("<strong>", "").replace("</strong>", "")

def send_telegram_message(text, is_raise_error=False):
    try:
        bot_token = os.getenv("BOT_TOKEN")
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        print(os.getenv("TELEGRAM_USER_IDS"))
        for chat_id in os.getenv("TELEGRAM_USER_IDS").split(","):
            response = requests.get(url, params={"chat_id": chat_id, "text": formater_text(text)})
            if response.status_code != 200:
                print(f"Failed to send message: {response.status_code} {response.text}")
    except Exception:
        print(f"TELEGRAM_USER_IDS NOT FOUND")
        if is_raise_error:
            raise Exception("TELEGRAM_USER_IDS NOT FOUND")
