"""
Database extension setup.

This module creates the shared SQLAlchemy database object used by
the Flask application and the database models.
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.

    Flask-SQLAlchemy will use this class when creating model classes
    for the SQLite database.
    """

    pass

# Shared database extension.
# The Flask application will initialize this object in app.py.
db = SQLAlchemy(model_class=Base)