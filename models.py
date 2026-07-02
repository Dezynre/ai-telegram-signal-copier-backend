"""
Database models.

This module defines the database tables used by the backend.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import db


class Signal(db.Model):
    """
    Store one Telegram message and its trading signal information.

    A record begins with the original Telegram message. As the message
    moves through the workflow, the same record is updated with parsed
    trade details, processing status, and execution feedback.
    """

    __tablename__ = "signals"

    # Internal database identifier for each signal record.
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Optional Telegram message identifier used when the signal comes
    # from the Telegram listener.
    telegram_message_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    # Original text received from Telegram or submitted manually for testing.
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)

    # JSON text returned after the message has been analyzed.
    parsed_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Trading instrument extracted from the message, for example XAUUSD.
    symbol: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    # Trade direction extracted from the message, for example BUY or SELL.
    direction: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # High-level trading intent, for example BUY_MARKET or SELL_LIMIT.
    intent: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Final order type resolved later before MetaTrader 5 execution.
    order_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Optional entry price. Market orders may not require this value.
    entry_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Stop-loss price extracted from the trading signal.
    stop_loss: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Take-profit price extracted from the trading signal.
    take_profit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Confidence score returned by the parsing step.
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Current processing status of the signal.
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="NEW",
    )

    # MetaTrader 5 order or position ticket reported after execution.
    execution_ticket: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    # Execution result message reported by the Expert Advisor.
    execution_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Timestamp showing when the signal record was created.
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    # Timestamp updated whenever the signal record changes.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def to_dict(self):
        """
        Convert the signal record to a JSON-friendly dictionary.

        Flask uses this method later when returning signal records through
        REST API responses.
        """

        return {
            "id": self.id,
            "telegram_message_id": self.telegram_message_id,
            "raw_text": self.raw_text,
            "parsed_json": self.parsed_json,
            "symbol": self.symbol,
            "direction": self.direction,
            "intent": self.intent,
            "order_type": self.order_type,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "confidence": self.confidence,
            "status": self.status,
            "execution_ticket": self.execution_ticket,
            "execution_message": self.execution_message,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }