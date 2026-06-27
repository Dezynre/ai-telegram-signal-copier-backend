"""
Signal processing service.
"""

import json

from database import db
from models import Signal
from openai_parser import parse_signal_with_openai
from signal_filter import is_signal_candidate


def process_raw_message(message, telegram_message_id=None):
    """
    Process a raw Telegram-style message.
    """

    accepted, reasons = is_signal_candidate(message)

    if not accepted:
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
            "signal": signal,
        }

    parsed_signal = parse_signal_with_openai(message)

    if not parsed_signal.get("is_signal"):
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
            "signal": signal,
        }

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
        "signal": signal,
    }


def get_next_pending_signal():
    """
    Return the oldest pending signal waiting for EA execution.
    """

    signal = db.session.execute(
        db.select(Signal)
        .where(Signal.status == "PENDING")
        .order_by(Signal.id.asc())
    ).scalars().first()

    return signal


def update_signal_execution_status(signal_id, status, ticket, message):
    """
    Update a signal after the EA attempts execution.
    """

    allowed_statuses = ["EXECUTED", "FAILED"]

    if status not in allowed_statuses:
        return {
            "success": False,
            "http_status": 400,
            "message": "Invalid status. Allowed values are EXECUTED and FAILED.",
            "signal": None,
        }

    signal = db.session.get(Signal, signal_id)

    if signal is None:
        return {
            "success": False,
            "http_status": 404,
            "message": "Signal not found.",
            "signal": None,
        }

    signal.status = status
    signal.execution_ticket = ticket
    signal.execution_message = message

    db.session.commit()

    return {
        "success": True,
        "http_status": 200,
        "message": "Signal execution status updated successfully.",
        "signal": signal,
    }