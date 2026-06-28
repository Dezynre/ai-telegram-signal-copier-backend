# AI Telegram Signal Copier Backend

This is the Python backend for the AI Telegram Signal Copier project. It listens to Telegram channel messages, filters likely trading signals, uses the OpenAI API to extract structured trading instructions, stores the parsed signals in SQLite, and exposes REST API endpoints for a MetaTrader 5 Expert Advisor.

The MetaTrader 5 Expert Advisor is hosted separately on MQL5 Algo Forge:

https://forge.mql5.io/CHACHAIAN/AITelegramSignalCopier

## Project Overview

Telegram trading signals are often written in natural language. For example:

```text
BUY GOLD NOW SL 2330 TP 2360
```

This backend converts such messages into structured JSON that can be consumed by a MetaTrader 5 Expert Advisor.

Example parsed output:

```json
{
  "is_signal": true,
  "symbol": "XAUUSD",
  "direction": "BUY",
  "intent": "BUY_MARKET",
  "entry_price": null,
  "stop_loss": 2330.0,
  "take_profit": 2360.0,
  "confidence": 0.99
}
```

## Main Features

* Flask REST API backend.
* SQLite signal storage using Flask-SQLAlchemy.
* Regex-based pre-filter for likely trading signals.
* OpenAI-powered signal extraction.
* Telegram channel listener using Telethon.
* Pending signal endpoint for the MQL5 Expert Advisor.
* Execution status endpoint for updating signal results.
* Supports manual API testing using Thunder Client, Postman, Insomnia, curl, or any REST client.

## Project Structure

```text
ai_telegram_signal_copier/
├── app.py
├── config.py
├── database.py
├── models.py
├── openai_parser.py
├── signal_filter.py
├── signal_service.py
├── telegram_listener.py
├── requirements.txt
├── README.md
└── .env
```

## Requirements

* Python 3.8 or later
* OpenAI API key
* Telegram API ID and API hash
* MetaTrader 5 running the companion Expert Advisor

## Installation

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-5.5
OPENAI_BASE_URL=https://api.openai.com/v1

TELEGRAM_API_ID=your_telegram_api_id
TELEGRAM_API_HASH=your_telegram_api_hash
TELEGRAM_SESSION_NAME=telegram_signal_session
TELEGRAM_TARGET_CHAT=mql5academyofficial

FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=True
```

Do not commit the `.env` file to GitHub.

## Running the Flask API

Start the backend:

```bash
python app.py
```

Default API URL:

```text
http://127.0.0.1:5000
```

Health check endpoint:

```text
GET /api/v1/health
```

## Running the Telegram Listener

Start the Telegram listener in a separate terminal:

```bash
python telegram_listener.py
```

The first time you run it, Telethon may ask for your Telegram phone number, login code, and two-factor authentication password if enabled.

After successful login, a local session file is created and reused for future runs.

## API Endpoints

### Health Check

```text
GET /api/v1/health
```

Confirms that the backend is running.

### List Signals

```text
GET /api/v1/signals
```

Returns all stored signals.

### Manual Test Message

```text
POST /api/v1/test-message
```

Example request body:

```json
{
  "message": "BUY GOLD NOW SL 2330 TP 2360"
}
```

This endpoint is useful for testing the backend with Thunder Client or any REST client before connecting Telegram.

### Fetch Pending Signal

```text
GET /api/v1/signals/pending
```

Returns one pending signal for the MetaTrader 5 Expert Advisor.

### Update Execution Status

```text
POST /api/v1/signals/<id>/status
```

Example request body:

```json
{
  "status": "EXECUTED",
  "ticket": 123456789,
  "message": "Trade opened successfully"
}
```

The Expert Advisor uses this endpoint to report whether a trade was executed or failed.

## Testing Workflow

1. Start the Flask backend.

```bash
python app.py
```

2. Start the Telegram listener.

```bash
python telegram_listener.py
```

3. Post a test signal in the configured Telegram channel.

```text
BUY BITCOIN NOW SL 59000 TP 64000
```

4. Confirm that the signal appears in SQLite using:

```text
GET http://127.0.0.1:5000/api/v1/signals
```

5. Run the companion MetaTrader 5 Expert Advisor.

6. Confirm that the signal status changes from `PENDING` to `EXECUTED` or `FAILED`.

## Companion Expert Advisor

The backend is designed to work with the MetaTrader 5 Expert Advisor hosted here:

https://forge.mql5.io/CHACHAIAN/AITelegramSignalCopier

The EA polls this backend, retrieves pending signals, resolves broker-specific symbols, executes trades, sends notifications, and reports execution status back to the API.

## Current Limitations

This project is an educational reference implementation. It does not currently include:

* Advanced risk-based position sizing.
* Spread filtering.
* Trading session filtering.
* Signal deduplication across all edge cases.
* Complex provider-specific signal normalization.
* Production-grade deployment configuration.
* Advanced retry logic.

These features can be added later without changing the core architecture.

## Disclaimer

This software is provided for educational purposes. Always test thoroughly on a demo account before using any automated trading system on a live account.
