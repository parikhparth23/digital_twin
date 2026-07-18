# Digital Twin

## Overview

This project runs a digital twin assistant using Chainlit and OpenAI, with additional judge and Telegram notification support.

## Required environment variables

Create a `.env` file in the project root with these values:

```dotenv
OPENAI_API_KEY=<your-openai-api-key>
GEMINI_API_KEY=<your-google-genai-api-key>
TELEGRAM_TOKEN=<your-telegram-bot-token>
TELEGRAM_CHAT_ID=<your-telegram-chat-id>
```

### Variable meanings

- `OPENAI_API_KEY`: API key for the `openai` Python client used by `inference.py`.
- `GEMINI_API_KEY`: API key for Google GenAI used by `evaluation/judge.py`.
- `TELEGRAM_TOKEN`: Telegram bot token used by `tools.py` to send notification messages.
- `TELEGRAM_CHAT_ID`: Chat ID where Telegram notifications are sent.

> Note: `TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID` are used for optional Telegram logging. Without them, Telegram notification functions will return an error if invoked.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the app

Start the Chainlit app:

```bash
chainlit run main.py
```

## Notes

- Replace `resources/summary.txt` and `resources/resume.pdf` with your own summary and resume data if you want the assistant and evaluator to use your personal information.
- `.env` values should not be committed to version control.
- Copy `.env.example` to `.env` and fill in your secrets.
- If you only want to run the assistant without Telegram notifications, you still need `OPENAI_API_KEY`.
