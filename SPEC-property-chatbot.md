# Spec: Property Discovery Chatbot

## Objective

Build a public demo web app that answers questions about the locally collected DarGlobal projects and Wasalt listings. It must retrieve matching records before generating an answer, cite the source URL for every returned record, and state that price and availability may have changed since collection.

The initial audience is an evaluator looking for Saudi property options or DarGlobal project information. Success means they can search or ask a natural-language question, receive an answer grounded in the 20-record catalog, inspect citations, and run the app in Docker.

## Tech Stack

- Python 3.11, FastAPI, and server-rendered HTML/CSS/JavaScript.
- Local JSON catalog at `data/initial_catalog.json`; no database in the first release.
- OpenRouter's OpenAI-compatible chat-completions endpoint, configured with `OPENROUTER_API_KEY` and `OPENROUTER_MODEL=openrouter/free`. The model selector is configurable because free capacity and model availability change over time.
- Docker Compose for local container execution.

## Commands

```text
Test: python3 -m unittest discover -s tests -v
Dev:  uvicorn app.main:app --reload
Build: docker compose build
Run:   docker compose up
```

## Project Structure

```text
app/        HTTP routes, retrieval, OpenRouter adapter, and static UI
collector/  Normalization helpers for future dataset refreshes
data/       Source-linked catalog
tests/      Unit and HTTP integration tests
```

## Code Style

Use typed, small Python functions and explicit response models. Retrieval is deterministic and independent of the model.

```python
def search_records(query: str, records: list[Record]) -> list[Record]:
    tokens = set(query.lower().split())
    return [record for record in records if tokens & record.search_terms]
```

## Testing Strategy

- Unit test deterministic filtering, ranking, citation selection, and prompt-context construction.
- HTTP test search and chat endpoints with a fake model client.
- Browser smoke test the rendered page at mobile and desktop widths before handoff.
- Do not call OpenRouter from automated tests.

## Boundaries

- Always: show source links; include collection-date caveat; reject claims not supported by retrieved records; keep API keys out of source control.
- Ask first: replace the dataset, add user accounts, enable analytics, use a paid model, or deploy to an external account.
- Never: expose an OpenRouter API key to the browser; invent listings, prices, availability, or source links; use contact details from source websites.

## Success Criteria

1. Visitors can filter by source, property type, city/district, bedrooms, and maximum price.
2. Visitors can ask a question and receive a concise answer grounded in matching records, with linked citations.
3. When `OPENROUTER_API_KEY` is not configured or the free model is unavailable, the app returns a useful retrieval-only answer instead of failing.
4. The app runs with `docker compose up` and does not require a database.
5. Deployment instructions identify the environment variables and health-check endpoint required for a live URL.

## Open Questions

- Which deployment account/platform should host the final app? A working URL requires the user's authorization and credentials for a hosting provider.
- The initial catalog is a 20-record demo sample. A production recommendation feature requires a larger, approved, regularly refreshed dataset.
