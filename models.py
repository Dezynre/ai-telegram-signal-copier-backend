"""
Database models.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import db


class Signal(db.Model):
    """
    Stores Telegram messages that were identified as possible trading signals.
    """

    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_message_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    symbol: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    direction: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    intent: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    order_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    entry_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    stop_loss: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    take_profit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="NEW")

    execution_ticket: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    execution_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def to_dict(self):
        """
        Convert the signal record to a JSON-friendly dictionary.
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