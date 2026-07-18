# Digital Twin

## Project overview

This repository implements a professional AI digital twin for representing a candidate during interviews, portfolio demos, or recruiter conversations. It is built as a deployable product with:

- a conversational web interface using `Chainlit`
- an LLM assistant that represents the candidate professionally
- resume-grounded retrieval with a semantic search vector store
- tool orchestration for safe, explainable answers
- a scoring/evaluation pipeline using Google Gemini
- optional Telegram logging for live notification and audit
- Docker support for deployment

This project is designed to help you show practical experience in AI system architecture, backend engineering, retrieval-augmented generation, and production deployment.

---

## Architecture and flow

### 1. Chat interface

- `main.py` starts the `Chainlit` app and registers conversation starters.
- When a user sends a message, `main.py` forwards it to `ask_digital_twin()`.

### 2. LLM orchestration

- `inference.py` constructs a system prompt from `context.py`.
- It calls OpenAI chat completions using `gpt-5.4-mini`.
- If the model returns a tool call instead of a final answer, the tool is executed and the result is fed back.
- This loop continues until the model produces a final answer.

### 3. Resume grounding and retrieval

- `rag/ingest.py` reads `resources/resume.pdf` and `resources/summary.txt`.
- Text is chunked, embedded with `SentenceTransformer`, and stored in `chroma_db`.
- `rag/retrieval.py` performs semantic similarity search to return relevant resume content.
- `tools.py` exposes `search_resume()` as a callable tool for the LLM.

### 4. Evaluation and scoring

- `evaluation/judge.py` reloads the resume and summary documents.
- It uses Google Gemini (`google-genai`) to score model answers for faithfulness, relevance, persona, and out-of-scope refusals.
- This is useful for quality assurance and improving answer accuracy.

### 5. Notification and audit

- `tools.py` includes Telegram integration.
- It can send messages for recorded professional conversations and unanswered questions.
- This enables simple observability and alerting in a deployed workflow.

---

## Component summary

### `main.py`

- Loads environment variables.
- Starts the Chainlit session.
- Sets starter prompts.
- Handles incoming chat messages.

### `context.py`

- Defines the AI persona for the digital twin.
- Controls scope, behavior, and answer style.
- Provides starter messages for the chat UI.

### `inference.py`

- Sends structured prompts to OpenAI.
- Supports tool-enabled conversation loops.
- Returns a final response once the LLM stops requesting tools.

### `tools.py`

- Defines tool schemas and tool handlers.
- Implements `search_resume()` for grounding.
- Implements Telegram notification helpers.
- Provides checklist tools for multi-step workflows.

### `rag/vectorstore.py`

- Configures ChromaDB persistence.
- Loads the embedding model `all-MiniLM-L6-v2`.

### `rag/retrieval.py`

- Queries the vector store for relevant text.
- Returns the top matching chunks for resume search.

### `rag/ingest.py`

- Reads and chunks the resume and summary.
- Builds embeddings and stores them in ChromaDB.
- Creates a fresh collection for retrieval.

### `evaluation/judge.py`

- Loads your summary and resume.
- Uses Gemini to score assistant responses.
- Returns structured JSON for evaluation.

---

## Required environment variables

Copy `.env.example` to `.env` and fill in secret values:

```dotenv
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY=your-google-genai-api-key
TELEGRAM_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id
```

### Meaning of each variable

- `OPENAI_API_KEY`: used by `inference.py` for the OpenAI chat API.
- `GEMINI_API_KEY`: used by `evaluation/judge.py` for Gemini evaluation.
- `TELEGRAM_TOKEN`: used by `tools.py` for optional Telegram notifications.
- `TELEGRAM_CHAT_ID`: target chat for Telegram notifications.

> If you want to run the assistant without notification support, `TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID` can be left blank, but `OPENAI_API_KEY` is required.

---

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Local run

```bash
chainlit run main.py
```

Then open the URL shown in the terminal.

## Running retrieval ingestion (RAG)

After updating `resources/resume.pdf` or `resources/summary.txt`, rebuild the vector database:

```bash
python rag/ingest.py
```

This creates or refreshes the `chroma_db` collection used by `rag/retrieval.py` and `tools.py`.

## Running evaluation

Use the evaluation pipeline to generate answers and score them against `evaluation/dataset.json`:

```bash
python evaluation/evaluate.py
```

Results are written to `evaluation/results.json`.

## Docker deployment

Build and run the container:

```bash
docker build -t digital-twin .
docker run -p 8000:8000 --env-file .env digital-twin
```

The app will be available on port `8000`.

---

## Customizing with your own profile data

To make this system represent your personal career profile:

1. Replace `resources/resume.pdf` with your resume.
2. Replace `resources/summary.txt` with your professional summary.
3. Rebuild the vector store:

```bash
python rag/ingest.py
```

This ensures search results and answer grounding reflect your real experience.

---

## Production readiness

This project is already structured with production best practices in mind:

- environment-driven configuration
- container-ready Dockerfile
- external service integration for LLMs and evaluation
- persistent semantic search storage
- tool-based orchestration for safer AI behavior

### Recommended improvements for a production release

- add authentication and access control for the web UI
- add health checks and readiness probes
- add retry/fallback logic for external APIs
- add unit tests and integration tests
- add logging and metrics/monitoring
- implement a proper prompt versioning strategy
- add CI/CD pipeline for automated builds and deployment

---

## Why this is strong for your job application

Use this repo to demonstrate that you can:

- build an end-to-end AI product, not just a proof-of-concept
- design a grounded retrieval-augmented generation system
- structure conversational workflows with tools
- create a deployment-ready Python service
- integrate LLM evaluation and observability
- deliver a professional portfolio assistant that can represent a candidate accurately

This is the sort of project that tells hiring managers you understand both product-level architecture and the engineering details needed for real deployment.
