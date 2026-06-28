"""
Telegram listener.

This script listens only to the configured Telegram channel and forwards
new text messages into the existing signal processing pipeline.
"""

from telethon import TelegramClient, events

from app import app
from config import Config
from signal_service import process_raw_message


def validate_telegram_config():
    """
    Validate required Telegram configuration values.
    """

    if Config.TELEGRAM_API_ID == "":
        raise RuntimeError("TELEGRAM_API_ID is missing in the .env file.")

    if Config.TELEGRAM_API_HASH == "":
        raise RuntimeError("TELEGRAM_API_HASH is missing in the .env file.")

    if Config.TELEGRAM_TARGET_CHAT.strip() == "":
        raise RuntimeError("TELEGRAM_TARGET_CHAT is missing in the .env file.")


def normalize_target_chat(target_chat):
    """
    Normalize the configured Telegram channel value.
    """

    target_chat = target_chat.strip()

    if target_chat.startswith("https://t.me/"):
        target_chat = target_chat.replace("https://t.me/", "")

    if target_chat.startswith("@"):
        target_chat = target_chat[1:]

    return target_chat


def process_telegram_text(message_text, telegram_message_id):
    """
    Process Telegram text inside a Flask application context.
    """

    with app.app_context():
        return process_raw_message(
            message=message_text,
            telegram_message_id=telegram_message_id,
        )


def main():
    """
    Start the Telegram listener.
    """

    validate_telegram_config()

    api_id = int(Config.TELEGRAM_API_ID)
    api_hash = Config.TELEGRAM_API_HASH
    session_name = Config.TELEGRAM_SESSION_NAME
    target_chat = normalize_target_chat(Config.TELEGRAM_TARGET_CHAT)

    client = TelegramClient(
        session_name,
        api_id,
        api_hash,
        sequential_updates=True,
    )

    print("Starting Telegram listener...")
    print("Listening only to Telegram channel:", target_chat)

    @client.on(events.NewMessage(chats=target_chat))
    async def handle_new_message(event):
        """
        Handle new text messages from the configured Telegram channel.
        """

        message_text = event.raw_text

        if message_text is None or message_text.strip() == "":
            return

        telegram_message_id = str(event.id)

        print("[TELEGRAM] New message received from target channel.")
        print("[TELEGRAM] Message ID:", telegram_message_id)
        print("[TELEGRAM] Text:", message_text)

        try:
            result = process_telegram_text(
                message_text=message_text,
                telegram_message_id=telegram_message_id,
            )

            print("[TELEGRAM] Processing result:", result["message"])

        except Exception as error:
            print("[TELEGRAM] Failed to process message:", str(error))

    client.start()
    client.run_until_disconnected()


if __name__ == "__main__":
    main()