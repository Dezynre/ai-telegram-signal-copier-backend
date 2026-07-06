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

    The listener cannot connect to Telegram without the API ID, API hash,
    and target channel. Failing early gives a clear error before Telethon
    attempts to start.
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

    The user may enter the channel as a full link, an @username, or a plain
    username. Telethon can work cleanly with the plain username, so this
    function converts the configured value into that format.
    """

    target_chat = target_chat.strip()

    # Convert a full Telegram link into a channel username.
    if target_chat.startswith("https://t.me/"):
        target_chat = target_chat.replace("https://t.me/", "")

    # Convert @channelname into channelname.
    if target_chat.startswith("@"):
        target_chat = target_chat[1:]

    return target_chat


def process_telegram_text(message_text, telegram_message_id):
    """
    Process Telegram text inside a Flask application context.

    The signal service writes to the database through Flask-SQLAlchemy.
    Because this listener runs as a separate script, the Flask application
    context must be opened before calling process_raw_message().
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

    # Confirm that all required Telegram settings are available.
    validate_telegram_config()

    # Read Telegram connection settings from the centralized Config class.
    api_id = int(Config.TELEGRAM_API_ID)
    api_hash = Config.TELEGRAM_API_HASH
    session_name = Config.TELEGRAM_SESSION_NAME
    target_chat = normalize_target_chat(Config.TELEGRAM_TARGET_CHAT)

    # Create the Telethon client. The session name controls the local
    # session file created after the first successful login.
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

        # Ignore empty Telegram messages because there is nothing to process.
        if message_text is None or message_text.strip() == "":
            return

        # Store the Telegram message ID as text so it can be saved in SQLite.
        telegram_message_id = str(event.id)

        print("[TELEGRAM] New message received from target channel.")
        print("[TELEGRAM] Message ID:", telegram_message_id)
        print("[TELEGRAM] Text:", message_text)

        try:
            # Forward the message into the same processing workflow used by
            # the manual test endpoint.
            result = process_telegram_text(
                message_text=message_text,
                telegram_message_id=telegram_message_id,
            )

            print("[TELEGRAM] Processing result:", result["message"])
            print("[TELEGRAM] Stored signal ID:", result["signal"].id)
            print("[TELEGRAM] Stored signal status:", result["signal"].status)

        except Exception as error:
            # Keep the listener alive and print the error for debugging.
            print("[TELEGRAM] Failed to process message:", str(error))

    # Start the Telegram client and keep listening until the script is stopped.
    client.start()
    client.run_until_disconnected()


if __name__ == "__main__":
    main()