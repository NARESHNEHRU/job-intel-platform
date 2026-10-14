
# Job Intelligence Platform

An AI-powered job intelligence platform that collects job posts from Telegram channels, extracts structured job information using a local AI model, and displays jobs in a searchable web application with recommendations and a chatbot.

## How It Works

Telegram channels -> Raw messages (MongoDB) -> LangGraph agent -> LLM extraction -> Validation -> Normalization -> Deduplication -> Embeddings (ChromaDB) -> FastAPI -> React application

### Key Design Principles

- Original messages are preserved alongside AI-generated output so users can verify extracted information.
- The LLM extracts information from text. Validation, normalization, duplicate detection, and scoring are handled by Python code.
- AI-generated details that are not supported by the original message are removed.
- The chatbot only presents jobs that exist in the database.

## Tech Stack

- **Backend:** Python, FastAPI
- **AI orchestration:** LangGraph
- **Local LLM:** Ollama (`qwen2.5:3b`)
- **Embeddings:** `nomic-embed-text`
- **Database:** MongoDB
- **Vector database:** ChromaDB
- **Telegram integration:** Telethon
- **Frontend:** React, Vite, Tailwind CSS

## Setup

### Prerequisites

Install the following software:

- Python 3.12
- Node.js and npm
- MongoDB
- Ollama

### 1. Download the AI models

```bash
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
```

### 2. Set up the Python environment

From the project root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in the required values.

Required settings may include:

- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `TELEGRAM_CHANNEL_IDS`
- `MONGO_URI`
- `OLLAMA_MODEL`

Telegram API credentials can be obtained from [my.telegram.org](https://my.telegram.org).

Never commit `.env` or Telegram session files to GitHub.

### 4. Install frontend dependencies

```powershell
cd frontend
npm install
cd ..
```

## Run the Application

Make sure MongoDB and Ollama are running.

Start all application services using PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

Alternatively, start the services individually from the project root.

**Terminal 1 — ChromaDB**

```powershell
.\venv\Scripts\Activate.ps1
chroma run --path data/chroma --port 8001
```

**Terminal 2 — FastAPI**

```powershell
.\venv\Scripts\Activate.ps1
uvicorn backend.app.api.main:app --reload --reload-dir backend
```

**Terminal 3 — React frontend**

```powershell
cd frontend
npm run dev
```

**Terminal 4 — Job collection and processing**

```powershell
.\venv\Scripts\Activate.ps1
python -m backend.scripts.run_all
```

Use the frontend URL printed by Vite to open the application.

## Tests

Run the test suite from the project root:

```powershell
python -m pytest -q
```

## Responsible Use

- Only collect messages from Telegram channels you are authorized to access.
- Treat `.env` and Telegram session files as sensitive credentials.
- Only text posts are collected if image-only posters are not supported by the implementation.
- Verify job details on the company's official careers website before applying.
- Never pay money to obtain a job offer.

## Limitations

- Image-only job posters may be skipped.
- AI extraction can be imperfect. Review the original message and any validation warnings.
- A small local model may occasionally misinterpret job requirements.
- The current application is designed for local, single-user use and may not include authentication.
