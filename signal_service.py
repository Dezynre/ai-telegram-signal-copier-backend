"""
Signal processing service.

This module contains helper functions that work with signal records.
At this stage, the service stores manually submitted messages so that
the API and database workflow can be tested before Telegram is connected.
"""

from database import db
from models import Signal


def process_raw_message(message, telegram_message_id=None):
    """
    Store a raw Telegram-style message in the database.

    The message is saved with status NEW because AI parsing and signal
    filtering will be introduced in the next part of the series.
    """

    signal = Signal(
        telegram_message_id=telegram_message_id,
        raw_text=message,
        status="NEW",
    )

    db.session.add(signal)
    db.session.commit()

    return {
        "message": "Test message stored successfully.",
        "signal": signal,
    }