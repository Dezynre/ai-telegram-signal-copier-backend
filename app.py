"""
Main Flask application.

This module creates the Flask backend, loads configuration values,
initializes the database extension, and exposes the API endpoints
implemented in this part of the article.
"""

from flask import Flask, jsonify, request

from config import Config
from database import db
from models import Signal
from signal_service import process_raw_message


# Create the Flask application instance.
app = Flask(__name__)

# Load backend configuration from the Config class.
app.config.from_object(Config)

# Connect the SQLAlchemy extension to this Flask application.
db.init_app(app)


@app.get("/")
def index():
    """
    Return basic API information.

    This endpoint is useful when the root URL is opened in the browser.
    It confirms that the backend is running and points the user to the
    health endpoint.
    """

    return jsonify(
        {
            "message": "AI Telegram Signal Copier API is running.",
            "health_endpoint": "/api/v1/health",
        }
    ), 200


@app.get("/api/v1/health")
def health():
    """
    Return the current health status of the backend.

    This endpoint gives immediate feedback that Flask is running,
    configuration values are available, and the API can return JSON.
    """

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
    """
    Return all signal records stored in the database.

    Newer records are returned first so that the most recent test
    messages are easier to see during development.
    """

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
    Return the oldest pending signal waiting for MetaTrader 5.

    The EA polls this endpoint on a timer. If no pending signal exists,
    the endpoint returns signal: null so the EA can wait for the next
    polling cycle without treating the response as an error.
    """

    signal = db.session.execute(
        db.select(Signal)
        .where(Signal.status == "PENDING")
        .order_by(Signal.id.asc())
        .limit(1)
    ).scalars().first()

    if signal is None:
        return jsonify(
            {
                "message": "No pending signals available.",
                "signal": None,
            }
        ), 200

    return jsonify(
        {
            "message": "Pending signal found.",
            "signal": signal.to_dict(),
        }
    ), 200
    

@app.post("/api/v1/test-message")
def create_test_message():
    """
    Process a manually submitted test message.

    The endpoint expects a JSON body containing a message field.
    It passes the message to the signal service and returns the full
    processing result to the client.
    """

    # Read the JSON request body without raising an exception if the
    # request body is missing or invalid.
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

    # Remove unnecessary surrounding spaces before processing the message.
    message = message.strip()

    if message == "":
        return jsonify(
            {
                "error": "Empty message.",
                "message": "The 'message' field cannot be empty.",
            }
        ), 400

    try:
        # The service handles filtering, OpenAI parsing, database storage,
        # and final status assignment.
        result = process_raw_message(message)
    except Exception as error:
        return jsonify(
            {
                "error": "Signal processing failed.",
                "message": str(error),
            }
        ), 500

    # Accepted trading signals create a parsed PENDING record.
    # Ignored messages are still stored, but the request itself is valid.
    status_code = 201 if result["accepted"] else 200

    return jsonify(
        {
            "message": result["message"],
            "reasons": result["reasons"],
            "parsed_signal": result["parsed_signal"],
            "signal": result["signal"],
        }
    ), status_code


with app.app_context():
    # Create database tables for all registered models.
    db.create_all()


if __name__ == "__main__":
    # Start the local Flask development server using values from config.py.
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
    )