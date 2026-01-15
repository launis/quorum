# API Reference & Directory Structure

This document provides a reference for the application's V2.5 directory structure and the backend REST API.

---

## Directory Structure (V2.5)

```text
quorum/
├── backend/                # Modular Async Monolith Core (Python 3.14)
│   ├── agents/             # Specialized Agent Classes (BaseAgent implementations)
│   ├── api/                # FastAPI Routers (Control Plane)
│   ├── core/               # Workflow Engine & Pipeline Runner (Logic)
│   ├── database/           # Abstracted DB Wrapper (TinyDB / Firestore)
│   ├── hooks/              # [LEGACY] Deterministic Logic (Moving to lib/ tools/)
│   ├── llm/                # LLM Provider Adapters (Gemini 2.5, Vertex AI)
│   ├── models/             # Pydantic V2 Data Models (State, Domain)
│   ├── services/           # Business Logic Services (Auth, IAM, PromptBuilder)
│   ├── config.py           # Configuration (Settings, Env Vars)
│   ├── main.py             # FastAPI App Entry Point
│   └── worker.py           # Arq Worker Entry Point (Background Service)
├── data/                   # Data Persistence (Local)
│   ├── db.json             # Runtime Database (Production)
│   ├── db_mock.json        # Runtime Database (Mock/Dev)
│   ├── seed_data.json      # Configuration Source of Truth
│   └── uploads/            # User Uploads
├── docs/                   # MkDocs Documentation
├── client_app/             # Client App (Flutter / Native)
│   ├── lib/
│   │   ├── features/
│   │   │   ├── admin/      # Organization & User Management
│   │   │   ├── auth/       # Authentication & Guard
│   │   │   ├── settings/   # Localization & Theme
│   │   │   └── orchestration/ # Workflow Execution UI
│   │   └── router/         # GoRouter Config
├── scripts/                # Utility Scripts (Seeding, OpenAPI Gen)
├── pyproject.toml          # Project Metadata & Dependnecies
└── uv.lock                 # Strict Dependency Lockfile
```

---

## API Reference

The backend exposes a RESTful API for management and job submission.

**Interactive Documentation:**
*   **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Key Endpoints

#### Execution (Async)
*   `POST /workflows/{id}/run`: Enqueue a workflow execution job. Returns `job_id`.
*   `GET /executions/{id}/status`: Poll the status of a specific job (`queued`, `in_progress`, `completed`).

#### Management
*   `GET /prompts`: List all prompt templates.
*   `PUT /prompts/{id}`: Update a prompt template.
*   `POST /system/reset-db`: Reset runtime DB from `seed_data.json`.

#### Identity & Access
*   `POST /auth/token`: Exchange credentials for JWT.
*   `GET /users/me`: Get current user context.

---

## Observability

*   **Logfire**: Distributed tracing is enabled for all API requests and Worker tasks.
*   **Redis**: Job queue persistence.

---

## Configuration

The system is configured via environment variables (see `.env.example`).

*   `ENV`: `MOCK` or `PROD`
*   `REDIS_URL`: Connection string for the job queue.
*   `FIRESTORE_CREDENTIALS`: Path to GCP Service Account JSON (Prod only).

---

## Development Standards & CI/CD

### Dependency Management (uv)
This project uses **uv** for strict dependency management. `requirements.txt` is deprecated.

*   **Install Dependencies**: `uv sync`
*   **Add Package**: `uv add package_name`
*   **Run Commands**: `uv run cmd_name`

### CI Pipelines (GitHub Actions)
Pipelines are defined in `.github/workflows/` and use `uv` for consistent environments.

    *   Runs on every push.
    *   Generates `docs/swagger/openapi.json`.
    *   Fails if the generated file differs from git (ensures API specs are up-to-date).
    *   **Manual Trigger**: `uv run python scripts/generate_openapi.py`

2.  **Documentation Deploy (`docs.yml`)**:
    *   Runs on push to `main`.
    *   Installs dependencies via `uv`.
    *   Builds site with `mkdocs build`.
    *   Deploys to **GitHub Pages**.

### Code Quality
*   **Formatting**: `uv run ruff format .`
*   **Flutter**:
    *   **Analyze**: `flutter analyze`
    *   **Test**: `flutter test`
    *   **Localization**: `flutter gen-l10n`
    *   **Code Generation**: `dart run build_runner build --delete-conflicting-outputs`