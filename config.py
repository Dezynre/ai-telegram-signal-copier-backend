"""
Application configuration.

This module loads environment variables from the .env file and exposes
them through a single Config class used by the rest of the backend.
"""

import os

from dotenv import load_dotenv

# Load values from the .env file into the process environment.
load_dotenv()

class Config:
    # Central configuration object used by the backend application.
    
    # Application metadata used by the API and project documentation.
    APP_NAME = "AI Telegram Signal Copier API"
    APP_VERSION = "1.0.0"

    # Flask development server settings.
    HOST = os.getenv("FLASK_HOST", "127.0.0.1")
    PORT = int(os.getenv("FLASK_PORT", "5000"))
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

    # SQLite database connection used by Flask-SQLAlchemy.
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "sqlite:///signals.db"
    )

    # Disable SQLAlchemy modification tracking because it is not needed here.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # OpenAI settings used later when parsing candidate trading signals.
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    # Telegram settings used later by the Telethon listener.
    TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID", "")
    TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")
    TELEGRAM_SESSION_NAME = os.getenv(
        "TELEGRAM_SESSION_NAME",
        "telegram_signal_session"
    )
    TELEGRAM_TARGET_CHAT = os.getenv("TELEGRAM_TARGET_CHAT", "")