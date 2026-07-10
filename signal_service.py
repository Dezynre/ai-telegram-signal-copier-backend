"""
Signal processing service.

This module coordinates the workflow that receives a raw message,
checks whether it looks like a trading signal, sends valid candidates
to OpenAI, and stores the final result in SQLite.
"""

import json

from database import db
from models import Signal
from openai_parser import parse_signal_with_openai
from signal_filter import is_signal_candidate


def process_raw_message(message, telegram_message_id=None):
    """
    Process a raw Telegram-style message.

    The function stores every received message, but the final status
    depends on how far the message moves through the processing workflow.

    Returns:
        dict: Processing result containing JSON-safe signal data.
    """

    # Step 1: Run a lightweight local filter before calling OpenAI.
    accepted, reasons = is_signal_candidate(message)

    if not accepted:
        # Obvious non-signal messages are stored for visibility, but they
        # are marked as IGNORED because they should not continue further.
        signal = Signal(
            telegram_message_id=telegram_message_id,
            raw_text=message,
            status="IGNORED",
        )

        db.session.add(signal)
        db.session.commit()

        return {
            "accepted": False,
            "message": "Message ignored. It does not look like a trading signal.",
            "reasons": reasons,
            "parsed_signal": None,
            "signal": signal.to_dict(),
        }

    # Step 2: Candidate messages are sent to OpenAI for structured parsing.
    parsed_signal = parse_signal_with_openai(message)

    if not parsed_signal.get("is_signal"):
        # OpenAI may still reject a message even if it passed the first
        # regex filter. In that case, store the parser response and stop.
        signal = Signal(
            telegram_message_id=telegram_message_id,
            raw_text=message,
            parsed_json=json.dumps(parsed_signal),
            status="IGNORED",
        )

        db.session.add(signal)
        db.session.commit()

        return {
            "accepted": False,
            "message": "OpenAI did not classify this message as a trading signal.",
            "reasons": [],
            "parsed_signal": parsed_signal,
            "signal": signal.to_dict(),
        }

    # Step 3: Valid parsed signals are stored with extracted trade fields.
    signal = Signal(
        telegram_message_id=telegram_message_id,
        raw_text=message,
        parsed_json=json.dumps(parsed_signal),
        symbol=parsed_signal.get("symbol"),
        direction=parsed_signal.get("direction"),
        intent=parsed_signal.get("intent"),
        order_type=None,
        entry_price=parsed_signal.get("entry_price"),
        stop_loss=parsed_signal.get("stop_loss"),
        take_profit=parsed_signal.get("take_profit"),
        confidence=parsed_signal.get("confidence"),
        status="PENDING",
    )

    db.session.add(signal)
    db.session.commit()

    return {
        "accepted": True,
        "message": "Message parsed and stored successfully.",
        "reasons": [],
        "parsed_signal": parsed_signal,
        "signal": signal.to_dict(),
    }