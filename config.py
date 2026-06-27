"""
Application configuration.
"""

import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    APP_NAME = "AI Telegram Signal Copier API"
    APP_VERSION = "1.0.0"

    HOST = os.getenv("FLASK_HOST", "127.0.0.1")
    PORT = int(os.getenv("FLASK_PORT", "5000"))
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "sqlite:///signals.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID", "")
    TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")
    TELEGRAM_SESSION_NAME = os.getenv("TELEGRAM_SESSION_NAME", "telegram_signal_session")
    TELEGRAM_TARGET_CHAT = os.getenv("TELEGRAM_TARGET_CHAT", "")

    