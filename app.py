"""
Main Flask application.

This module creates the Flask backend, loads configuration values,
initializes the database extension, and exposes the first API endpoints.
"""

from flask import Flask, jsonify

from config import Config
from database import db
from models import Signal

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

with app.app_context():
    # Create database tables for all registered models.
    # At this stage no model has been added yet, but keeping this call here
    # prepares the application for the signal model introduced later.
    db.create_all()

if __name__ == "__main__":
    # Start the local Flask development server using values from config.py.
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
    )