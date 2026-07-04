"""
Regex-based signal candidate filter.

This module does not confirm whether a message is a valid trading signal.
It only decides whether the message looks important enough to send to the
OpenAI parser in the next phase.
"""

import re

# Direction words are the strongest early signal that the message may
# contain a trading instruction.
DIRECTION_PATTERN = re.compile(
    r"\b(buy|sell|long|short)\b",
    re.IGNORECASE,
)

# Execution words help detect whether the message describes how the trade
# should be entered, for example immediately, at a price, above a level,
# below a level, or using a pending order.
ORDER_TYPE_PATTERN = re.compile(
    r"\b("
    r"buy\s+limit|sell\s+limit|"
    r"buy\s+stop|sell\s+stop|"
    r"limit|stop|market|now|"
    r"above|below|breakout|entry|enter|at"
    r")\b",
    re.IGNORECASE,
)

# Risk and target words help detect whether the message contains trade
# management details such as stop-loss, take-profit, target, or risk-reward.
RISK_TARGET_PATTERN = re.compile(
    r"\b("
    r"sl|tp|tp1|tp2|tp3|"
    r"stop\s+loss|stop-loss|"
    r"take\s+profit|take-profit|"
    r"target|targets|risk|reward|rr"
    r")\b",
    re.IGNORECASE,
)

# Price levels and numeric values are common in trading signals.
NUMBER_PATTERN = re.compile(
    r"\d+(\.\d+)?"
)

def is_signal_candidate(text):
    """
    Check whether a text message looks like a possible trading signal.

    A message is accepted when:
    - It contains a direction word such as buy, sell, long, or short.
    - It also contains either a number, an execution keyword, or a risk/target keyword.

    Returns:
        tuple: (accepted: bool, reasons: list)
    """

    reasons = []

    # Reject missing input before running regex checks.
    if text is None:
        return False, ["Message text is missing."]

    cleaned_text = text.strip()

    # Reject empty messages after removing surrounding spaces.
    if cleaned_text == "":
        return False, ["Message text is empty."]

    # Run each lightweight check independently so that the response can
    # explain why a message was rejected.
    has_direction = DIRECTION_PATTERN.search(cleaned_text) is not None
    has_order_type = ORDER_TYPE_PATTERN.search(cleaned_text) is not None
    has_risk_target = RISK_TARGET_PATTERN.search(cleaned_text) is not None
    has_number = NUMBER_PATTERN.search(cleaned_text) is not None

    if not has_direction:
        reasons.append("No direction keyword found.")

    if not has_number and not has_order_type and not has_risk_target:
        reasons.append("No number, execution keyword, or risk/target keyword found.")

    # A candidate must contain a direction and at least one supporting clue.
    accepted = has_direction and (has_number or has_order_type or has_risk_target)

    return accepted, reasons