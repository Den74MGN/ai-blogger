import requests
from pathlib import Path
from config import Config


def send_to_telegram(video_path: Path, caption: str = "") -> bool:
    """Отправляет видео в Telegram-канал/чат."""
    if not Config.TELEGRAM_BOT_TOKEN or not Config.TELEGRAM_CHAT_ID:
        print("[Telegram] Bot token или chat ID не настроены. Пропускаю.")
        return False

    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendVideo"

    with open(video_path, "rb") as f:
        files = {"video": f}
        data = {
            "chat_id": Config.TELEGRAM_CHAT_ID,
            "caption": caption[:1024] if caption else "",
            "parse_mode": "HTML",
            "supports_streaming": True,
        }
        response = requests.post(url, files=files, data=data, timeout=300)

    if response.ok:
        print("[Telegram] Video posted successfully")
        return True
    else:
        print(f"[Telegram] Error: {response.text}")
        return False


def send_text_message(text: str) -> bool:
    """Отправляет текстовое сообщение в Telegram."""
    if not Config.TELEGRAM_BOT_TOKEN or not Config.TELEGRAM_CHAT_ID:
        return False

    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": Config.TELEGRAM_CHAT_ID,
        "text": text[:4096],
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    response = requests.post(url, json=data, timeout=30)
    return response.ok
