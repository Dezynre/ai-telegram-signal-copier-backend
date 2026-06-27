"""
OpenAI signal parser.
"""

import json

from openai import OpenAI

from config import Config


client = OpenAI(
    api_key=Config.OPENAI_API_KEY,
    base_url=Config.OPENAI_BASE_URL,
)


SYSTEM_PROMPT = """
You are a trading signal extraction assistant.

Your task is to analyze Telegram-style trading messages and extract structured
trade instructions from them.

General rules:
- Return only data that matches the provided JSON schema.
- Do not invent entry, stop loss, or take profit prices.
- Use null when a value is missing.
- If the message is not a trading signal, set is_signal to false.
- Extract only the first take-profit value if multiple targets are provided.

Symbol rules:
- Always return a symbol when the message is a trading signal and the traded asset can be identified.
- If the message mentions GOLD, XAU, or XAUUSD, return XAUUSD unless another quote currency is explicitly stated.
- If the message mentions SILVER, XAG, or XAGUSD, return XAGUSD unless another quote currency is explicitly stated.
- If the message mentions BITCOIN, BTC, or BTCUSD, return BTCUSD unless another quote currency is explicitly stated.
- If the message mentions ETHEREUM, ETH, or ETHUSD, return ETHUSD unless another quote currency is explicitly stated.
- If the message mentions a forex pair such as EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, or NZDUSD, return that exact pair in uppercase.
- If the asset is unclear, return null for symbol.

Direction and intent rules:
- BUY, LONG, BUY NOW, or LONG NOW means BUY_MARKET.
- SELL, SHORT, SELL NOW, or SHORT NOW means SELL_MARKET.
- BUY AT, LONG AT, BUY LIMIT, or BUY STOP means BUY_AT_PRICE.
- SELL AT, SHORT AT, SELL LIMIT, or SELL STOP means SELL_AT_PRICE.
- BUY ABOVE means BUY_ABOVE.
- SELL BELOW means SELL_BELOW.
"""


SIGNAL_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "is_signal": {"type": "boolean"},
        "symbol": {"type": ["string", "null"]},
        "direction": {"type": ["string", "null"], "enum": ["BUY", "SELL", None]},
        "intent": {
            "type": ["string", "null"],
            "enum": [
                "BUY_MARKET",
                "SELL_MARKET",
                "BUY_AT_PRICE",
                "SELL_AT_PRICE",
                "BUY_ABOVE",
                "SELL_BELOW",
                "UNKNOWN",
                None,
            ],
        },
        "entry_price": {"type": ["number", "null"]},
        "stop_loss": {"type": ["number", "null"]},
        "take_profit": {"type": ["number", "null"]},
        "confidence": {"type": "number"},
    },
    "required": [
        "is_signal",
        "symbol",
        "direction",
        "intent",
        "entry_price",
        "stop_loss",
        "take_profit",
        "confidence",
    ],
}


def parse_signal_with_openai(raw_text):
    """
    Extract structured signal information from raw Telegram text.
    """

    if Config.OPENAI_API_KEY == "":
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to your .env file.")

    response = client.responses.create(
        model=Config.OPENAI_MODEL,
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": raw_text,
            },
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "telegram_signal",
                "schema": SIGNAL_SCHEMA,
                "strict": True,
            }
        },
    )

    return json.loads(response.output_text)