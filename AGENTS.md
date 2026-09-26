# AGENTS.md

## Project overview

This repo is a local RAG application for answering questions about the Polars Python documentation. The main stack is:

- Litestar backend in [backend/app.py](backend/app.py)
- Shiny frontend in [frontend/ui.py](frontend/ui.py)
- Weaviate vector database and loader in [docker-compose.yml](docker-compose.yml), [weaviate_loader/load_weaviate.py](weaviate_loader/load_weaviate.py), and [weaviate/](weaviate/)
- Local LLM access through Ollama in [ollama/](ollama/)
- Guardrails and prompt-injection service in [guardrails/](guardrails/)

See the project overview in [README.md](README.md) for the architecture and local setup flow.

## Important workflows

### Local development

From the repo root, use Docker Compose to start the stack in this order:

- `docker compose up weaviate`
- `docker compose up ollama`
- `docker compose up server`
- `docker compose up ui`

The compose wiring and service dependencies live in [docker-compose.yml](docker-compose.yml).

### Formatting and linting

Project lint/format commands are defined in [justfile](justfile):

- `just lint`
- `just format`

The lint step includes `isort`, `pyupgrade`, `autoflake`, and `flake8`. Keep imports sorted and avoid unused code.

## Key code boundaries

- Backend: [backend/](backend/)
  - API route handlers and RAG chain logic in [backend/app.py](backend/app.py)
  - app configuration in [backend/appconfig.py](backend/appconfig.py)
  - shared request/response schemas in [backend/shared/api_models.py](backend/shared/api_models.py)
  - retrieval/vector-store wrappers in [backend/weaviatestore.py](backend/weaviatestore.py) and [backend/redistore.py](backend/redistore.py)

- Frontend: [frontend/](frontend/)
  - UI wiring in [frontend/ui.py](frontend/ui.py)
  - config in [frontend/appconfig.py](frontend/appconfig.py)
  - API schema alignment in [frontend/shared/api_models.py](frontend/shared/api_models.py)

- Data ingestion: [weaviate_loader/](weaviate_loader/)
  - Document loading and embedding pipeline in [weaviate_loader/load_weaviate.py](weaviate_loader/load_weaviate.py)

## Coding conventions

- Prefer small, service-local changes instead of broad rewrites.
- Keep backend and frontend API contracts consistent with the shared schema files in [backend/shared/api_models.py](backend/shared/api_models.py) and [frontend/shared/api_models.py](frontend/shared/api_models.py).
- Respect the existing `.env`-based configuration pattern; avoid hard-coding hostnames or ports in new code.
- Keep Docker service names and variable names aligned with [docker-compose.yml](docker-compose.yml) and the app config classes.
- Do not rename core integration pieces such as Weaviate collection names, embedding model settings, or Ollama model config without updating the corresponding code and environment configuration together.

## Validation expectations

There is no dedicated automated test suite in the repo at the moment. For changes, validate with the smallest relevant check:

1. Run the relevant Docker service or smoke flow if the change touches the stack.
2. Run `just lint` for Python hygiene and import cleanup.
3. Prefer targeted verification over broad repo-wide changes.

## Useful references

- [README.md](README.md)
- [justfile](justfile)
- [docker-compose.yml](docker-compose.yml)
- [backend/app.py](backend/app.py)
- [frontend/ui.py](frontend/ui.py)
- [weaviate_loader/load_weaviate.py](weaviate_loader/load_weaviate.py)
