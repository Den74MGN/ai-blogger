import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

class Config:
    # LLM
    LLM_API_KEY = os.getenv("LLM_API_KEY", "ollama")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
    LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")

    # TTS
    TTS_VOICE = os.getenv("TTS_VOICE", "ru-RU-SvetlanaNeural")

    # YouTube
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
    YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID", "")
    YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")
    YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN", "")

    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

    # Avatar
    AVATAR_SOURCE_IMAGE = BASE_DIR / os.getenv("AVATAR_SOURCE_IMAGE", "avatar/source/0.png")
    DRIVING_VIDEO = BASE_DIR / os.getenv("DRIVING_VIDEO", "avatar/driving/drive.mp4")

    # Paths
    SCRIPTS_DIR = BASE_DIR / "content" / "scripts"
    AUDIO_DIR = BASE_DIR / "content" / "audio"
    BACKGROUND_DIR = BASE_DIR / "content" / "background"
    FINAL_DIR = BASE_DIR / "content" / "final"
    AVATAR_OUTPUT = BASE_DIR / "avatar" / "output"

    # Schedule
    POST_INTERVAL_HOURS = int(os.getenv("POST_INTERVAL_HOURS", "24"))

    for p in [SCRIPTS_DIR, AUDIO_DIR, BACKGROUND_DIR, FINAL_DIR, AVATAR_OUTPUT]:
        p.mkdir(parents=True, exist_ok=True)
