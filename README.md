# Property Discovery Chatbot

A Docker-ready, source-grounded chatbot for exploring an initial Saudi real-estate catalog from DarGlobal and Wasalt.

The app retrieves relevant records before responding. Every answer contains public source links and a reminder that price and availability may have changed.

## Features

- Filters by source, property type, bedrooms, and maximum price.
- Answers catalog questions such as "Tell me about Neptune in Riyadh."
- Shows public source links for every answer.
- Uses OpenRouter's free-model router when configured.
- Falls back to deterministic catalog answers when a model key is unavailable.

## Catalog scope

The initial dataset is a 20-record demo sample.

| Source | Records | Coverage |
| --- | ---: | --- |
| DarGlobal | 8 | Saudi projects in Riyadh and Jeddah |
| Wasalt | 12 | Riyadh listings for sale |

Records retain public source URLs but exclude contact names, phone numbers, WhatsApp links, and images. See [data/initial_catalog.json](data/initial_catalog.json) for exact records and capture metadata.

This is a discovery demo, not investment, legal, or financial advice.

## Run with Docker

Prerequisite: [Docker Desktop](https://www.docker.com/products/docker-desktop/) is installed and running.

```bash
git clone https://github.com/marshanabilah/real-estate-chatbot.git
cd real-estate-chatbot
docker compose up --build
```

Open <http://localhost:8000>.

To stop the app:

```bash
docker compose down
```

## Enable OpenRouter

The app works without a key, but uses structured catalog responses instead of model-written prose.

```bash
cp .env.example .env
```

Add these values to `.env`:

```text
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openrouter/free
```

Restart Docker after changing `.env`:

```bash
docker compose down
docker compose up --build
```

`openrouter/free` selects from OpenRouter's currently available free models. If that service is limited or unavailable, the app safely returns a retrieval-only answer. Never commit `.env` or expose the key in browser code.

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API

| Endpoint | Purpose |
| --- | --- |
| `GET /` | Web interface |
| `GET /api/health` | Health check |
| `GET /api/properties` | Catalog search |
| `POST /api/chat` | Grounded chatbot answer with citations |

Example property search:

```text
GET /api/properties?source=wasalt&city=Riyadh&propertyType=villa&minBedrooms=4&maxPrice=4000000
```

Example chat request:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"question":"Tell me about Neptune in Riyadh"}'
```

## Grounding and safety

1. The app scores records against the question and retains the best matches, prioritizing title matches.
2. When configured, only selected catalog facts are sent to OpenRouter.
3. The application, not the model, creates citation links.
4. Model output is rendered as safe text with a small Markdown allowlist for bold text and line breaks. Raw HTML is never rendered.

## Project structure

```text
app/          FastAPI routes, retrieval, OpenRouter adapter, and web UI
collector/    Normalization utilities for later data refreshes
data/         Initial source-linked catalog
tests/        Python and formatting tests
Dockerfile    Container image
compose.yaml  Local container configuration
```

## Verify

```bash
python3 -m unittest discover -s tests -v
node tests/test_format.mjs
docker compose build
```

## Deploy

Deploy the included Dockerfile to a Docker-capable host. Expose port `8000`, set `/api/health` as the health-check path, and configure `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` through the host's secret settings. A hosting account and deployment credentials are needed to create a public URL.
