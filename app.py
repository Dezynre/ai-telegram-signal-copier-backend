"""
Main Flask application.
"""

from flask import Flask, jsonify, request
from signal_filter import is_signal_candidate

from config import Config
from database import db
from models import Signal

from signal_service import (
    process_raw_message,
    get_next_pending_signal,
    update_signal_execution_status,
)


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


@app.get("/")
def index():
    return jsonify(
        {
            "message": "AI Telegram Signal Copier API is running.",
            "health_endpoint": "/api/v1/health",
        }
    ), 200


@app.get("/api/v1/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "service": Config.APP_NAME,
            "version": Config.APP_VERSION,
            "database": "configured",
        }
    ), 200


@app.get("/api/v1/signals")
def list_signals():
    signals = db.session.execute(
        db.select(Signal).order_by(Signal.id.desc())
    ).scalars().all()

    return jsonify(
        {
            "count": len(signals),
            "signals": [signal.to_dict() for signal in signals],
        }
    ), 200


@app.get("/api/v1/signals/pending")
def get_pending_signal():
    """
    Return one pending signal for the MQL5 EA.
    """

    signal = get_next_pending_signal()

    if signal is None:
        return jsonify(
            {
                "message": "No pending signals available.",
                "signal": None,
            }
        ), 200

    return jsonify(
        {
            "message": "Pending signal retrieved successfully.",
            "signal": {
                "id": signal.id,
                "symbol": signal.symbol,
                "direction": signal.direction,
                "intent": signal.intent,
                "order_type": signal.order_type,
                "entry_price": signal.entry_price,
                "stop_loss": signal.stop_loss,
                "take_profit": signal.take_profit,
                "confidence": signal.confidence,
            },
        }
    ), 200


@app.post("/api/v1/test-message")
def create_test_message():
    """
    Process a manually submitted test message.
    """

    data = request.get_json(silent=True)

    if data is None:
        return jsonify(
            {
                "error": "Invalid request.",
                "message": "Request body must be valid JSON.",
            }
        ), 400

    message = data.get("message")

    if message is None:
        return jsonify(
            {
                "error": "Missing field.",
                "message": "The 'message' field is required.",
            }
        ), 400

    message = message.strip()

    if message == "":
        return jsonify(
            {
                "error": "Empty message.",
                "message": "The 'message' field cannot be empty.",
            }
        ), 400

    try:
        result = process_raw_message(message)
    except Exception as error:
        return jsonify(
            {
                "error": "Signal processing failed.",
                "message": str(error),
            }
        ), 500

    status_code = 201 if result["accepted"] else 200

    return jsonify(
        {
            "message": result["message"],
            "reasons": result["reasons"],
            "parsed_signal": result["parsed_signal"],
            "signal": result["signal"].to_dict(),
        }
    ), status_code


@app.post("/api/v1/signals/<int:signal_id>/status")
def update_signal_status(signal_id):
    """
    Update signal status after the MQL5 EA attempts execution.
    """

    data = request.get_json(silent=True)

    if data is None:
        return jsonify(
            {
                "error": "Invalid request.",
                "message": "Request body must be valid JSON.",
            }
        ), 400

    status = data.get("status")
    ticket = data.get("ticket")
    message = data.get("message")

    if status is None:
        return jsonify(
            {
                "error": "Missing field.",
                "message": "The 'status' field is required.",
            }
        ), 400

    if ticket is None:
        return jsonify(
            {
                "error": "Missing field.",
                "message": "The 'ticket' field is required.",
            }
        ), 400

    if message is None:
        return jsonify(
            {
                "error": "Missing field.",
                "message": "The 'message' field is required.",
            }
        ), 400

    result = update_signal_execution_status(
        signal_id=signal_id,
        status=status,
        ticket=ticket,
        message=message,
    )

    if not result["success"]:
        return jsonify(
            {
                "error": "Status update failed.",
                "message": result["message"],
            }
        ), result["http_status"]

    return jsonify(
        {
            "message": result["message"],
            "signal": result["signal"].to_dict(),
        }
    ), result["http_status"]


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
    )