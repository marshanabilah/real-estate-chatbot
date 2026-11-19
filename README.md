# Property Discovery Chatbot

A source-grounded demo chatbot for the initial DarGlobal and Wasalt Saudi property catalog.

## What it does

- Filters the local catalog by source, property type, bedrooms, and maximum price.
- Answers property questions using only retrieved catalog records.
- Adds source links and a freshness disclaimer to every chat response.
- Uses `openrouter/free` when an `OPENROUTER_API_KEY` is present, with a deterministic retrieval-only fallback when it is not.

## Run locally

```bash
cp .env.example .env
docker compose up --build
```

Open `http://localhost:8000`. The health check is available at `GET /api/health`.

## Configure OpenRouter

Set `OPENROUTER_API_KEY` in `.env`; never expose this key in browser code or commit it. `OPENROUTER_MODEL` defaults to `openrouter/free`, which routes each request to an available free model. The app continues to work without a key, but replies use deterministic catalog retrieval rather than model-generated prose.

## Deploy

Deploy the repository to any Docker-capable host. Configure:

```text
OPENROUTER_API_KEY=<your key>
OPENROUTER_MODEL=openrouter/free
PORT=8000
```

Use `/api/health` as the health-check path. The provided `Dockerfile` listens on port `8000`; set the host's port mapping to that port. A hosting account and its credentials are required before a live URL can be created.

## Verify

```bash
python3 -m unittest discover -s tests -v
docker compose build
```
