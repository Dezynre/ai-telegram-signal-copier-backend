"""
Telegram listener.

This script listens for new Telegram text messages and forwards them into
the existing signal processing pipeline.
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
    target_chat = Config.TELEGRAM_TARGET_CHAT.strip()

    client = TelegramClient(
        session_name,
        api_id,
        api_hash,
        sequential_updates=True,
    )

    if target_chat == "":
        event_filter = events.NewMessage()
        print("Listening to all incoming Telegram messages.")
    else:
        event_filter = events.NewMessage(chats=target_chat)
        print("Listening to Telegram chat:", target_chat)

    @client.on(event_filter)
    async def handle_new_message(event):
        """
        Handle incoming Telegram messages.
        """

        message_text = event.raw_text

        if message_text is None or message_text.strip() == "":
            return

        telegram_message_id = str(event.id)

        print("New Telegram message received:")
        print(message_text)

        try:
            result = process_telegram_text(
                message_text=message_text,
                telegram_message_id=telegram_message_id,
            )

            print("Processing result:", result["message"])

        except Exception as error:
            print("Failed to process Telegram message:", str(error))

    print("Starting Telegram listener...")

    client.start()
    client.run_until_disconnected()


if __name__ == "__main__":
    main()