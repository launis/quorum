# Reference Manual & API (V2.9)

This document serves as the technical reference for **Cognitive Quorum V2026**. It covers the directory structure, CLI commands, and the Backend API.

---

## 1. Directory Structure (V2.9)

The project follows a **Modular Monolith** architecture.

quorum/
├── backend/                # Async Python 3.14+ Core
│   ├── agents/             # Specialized Agent Logic (Judge, Analyst)
│   ├── api/                # FastAPI Routers (The Control Plane)
│   │   ├── routes/
│   │   │   ├── config/     # CRUD for Rules, Matrices, Workflows
│   │   │   └── execution/  # Job Submission & Status
│   │   ├── transformers/   # Modular View Transformers (Assessment & Report)
│   ├── core/               # GraphEngine & WorkflowRunner
│   ├── database/           # AbstractRepository (TinyDB / Firestore)
│   │   └── db_mock.json    # Test DB (Mock LLMs)
│   ├── hooks/              # Deterministic Logic (Scoring, Searching)
│   ├── llm/                # AI Provider Adapters (Vertex, OpenAI)
│   ├── models/             # Pydantic V2 Schemas (SSOT)
│   │   ├── domain/         # Modular Domain Models (Guard, Analyst, etc.)
│   │   ├── enums.py        # Shared Enumerations
│   │   └── state.py        # Workflow State Defs
│   ├── services/           # Business Logic (Auth, Storage, PromptBuilder)
│   │   └── drivers/        # I/O Adapters (LocalFileDriver, GCSFileDriver)
│   ├── seed/               # Data Seeding Logic
│   │   └── seed_data.json  # THE BLUEPRINT (Source of Truth)
│   ├── scripts/            # Backend Utility Scripts
│   ├── settings.py         # Environment Settings (Pydantic BaseSettings)
│   └── worker.py           # Arq Worker Entry Point
├── data/                   # Local Persistence
│   ├── db.json             # Local Production DB
│   └── files/              # Local File Storage
├── docs/                   # Documentation (MkDocs)
├── client_app/             # Flutter Client (Cognitive Studio)
│   ├── lib/
│   │   ├── features/
│   │   │   ├── admin/      # System Administration
│   │   │   ├── auth/       # Login & Guard
│   │   │   ├── registry/   # Component Management
│   │   │   ├── studio/     # Workflow Editor & Designer
│   │   │   └── shell/      # Navigation & Layout
│   │   └── router/         # GoRouter Configuration
├── scripts/                # CI/CD & Utility Scripts (Python)
├── .env.example            # Environment Template
├── run_local.bat           # Local Development Startup (Recommended)
├── run_full_docker.bat     # Docker Startup Script
├── kill_services.bat       # Cleanup Script
└── pyproject.toml          # Python Dependencies (uv)
```

---

## 2. CLI Command Reference

### Operational Commands (Windows Root)

| Command | Description |
| :--- | :--- |
| `run_local.bat` | **Start Dev**. Launches Backend (Uvicorn), Worker (Arq), and Frontend (Flutter) locally. |
| `run_full_docker.bat` | **Start Docker**. Rebuilds and launches the full stack in containers. |
| `kill_services.bat` | **Stop System**. Aggressively terminates Python, Dart, Docker processes, and frees ports. |

### Data Management (Seeding)

Managed via `backend/seed/run_seed.py`.

| Target | Command | Purpose |
| :--- | :--- | :--- |
| **Local** | `python backend/seed/run_seed.py local` | Resets `data/db.json` from `seed_data.json`. Use for local dev. |
| **Mock** | `python backend/seed/run_seed.py mock` | Resets `backend/database/db_mock.json`. Use for offline testing. |
| **Cloud** | `python backend/seed/run_seed.py firestore` | **DANGER**. Overwrites Production Firestore with Seed Data. |

### Backend Development (uv)

We use `uv` for dependency management.

*   **Sync Dependencies**: `uv sync`
*   **Add Package**: `uv add <package>`
*   **Run Linter**: `uv run ruff check .`
*   **Format Code**: `uv run ruff format .`

### Frontend Development (Flutter)

*   **Run App**: `flutter run -d windows` (or `chrome`)
*   **Generate Code**: `dart run build_runner build --delete-conflicting-outputs`
*   **Update Localizations**: `flutter gen-l10n`

---

## 3. API Reference (FastAPI)

The API is accessible at `http://localhost:8000` (Local) or `https://api.quorum.com` (Prod).

**Documentation**:
*   **Swagger UI**: `/docs`
*   **ReDoc**: `/redoc`

### Execution API (`/execution`)
Manages the lifecycle of cognitive jobs.

*   `POST /execution/workflows/{id}/run`: Submit a job.
    *   **Input**: JSON payload matching the Workflow's input schema.
    *   **Output**: `job_id`.
*   `GET /execution/jobs/{job_id}`: Poll status.
    *   **Returns**: `status` (queued/running/completed/failed), `result` (if done).

### Configuration API (`/config`)
Manages the "Brains" of the system.

*   `GET /config/components`: List Registry items (Prompts, Matrices).
*   `GET /config/workflows`: List available Workflow definitions.
*   `PATCH /config/workflows/{id}`: Update specific workflow steps (Hot-Reload).
*   `POST /config/ontology/dimensions`: Add new evaluation criteria.

### System & Auth
*   `POST /auth/login`: Authenticate via Firebase/Email.
*   `POST /system/reset`: **Root Only**. Reset the database to factory settings.

---

## 4. Environment Variables

Defined in `.env` and managed by `backend/settings.py`.

| Variable | Description | Valid Values | Default |
| :--- | :--- | :--- | :--- |
| `ENVIRONMENT` | Environment Mode. | `development` / `production` | `development` |
| `STORAGE_BACKEND` | Storage engine choice. | `LOCAL` / `MOCK` / `FIRESTORE` | `LOCAL` |
| `STORAGE_BUCKET_NAME` | GCP Bucket for Files (Required if FIRESTORE). | String (e.g., `quorum-files`) | - |
| `USE_MOCK_LLM` | Force usage of Mock LLM service. | `true` / `false` | `false` |
| `USE_VERTEX_LLM` | Use Vertex AI (Google) vs OpenAI. | `true` / `false` | `false` |
| `VERTEX_LOCATION` | Google Cloud Region. | e.g., `europe-north1` | - |
| `GOOGLE_API_KEY` | Key for Google AI Studio (Gemini). | String | - |
| `REDIS_HOST` | Redis connection for Arq. | Hostname / IP | `localhost` |
| `PROJECT_ID` | GCP Project ID (Optional). | String | - |

---

## 5. Error Codes

The API returns standard HTTP codes plus a detailed `error_code` in the JSON body, defined in `backend/exceptions.py`.

### General & System
*   **500**: `INTERNAL_SERVER_ERROR` - Unhandled system exception.
*   **500**: `UNKNOWN_ERROR` - Fallback error code.
*   **503**: `NETWORK_UNAVAILABLE` - Connectivity issues.

### Validation (400)
*   `INVALID_JSON_PAYLOAD`: Input does not match Pydantic model.
*   `EMPTY_INPUT`: Required text field was empty.
*   `UNSUPPORTED_CONTENT_TYPE`: Invalid upload format.
*   `MISSING_WORKFLOW_ID`: Workflow ID not provided.

### Resources (404)
*   `EXECUTION_NOT_FOUND`: Job ID lookup failed.
*   `WORKFLOW_NOT_FOUND`: Workflow definition missing.
*   `STEP_NOT_FOUND`: Step reference invalid.

### Execution & Logic
*   `WORKFLOW_EXECUTION_FAILED`: Critical failure during workflow run.
*   `AGENT_EXECUTION_CRITICAL`: Logic failure within a specific agent.
*   `MODEL_OUTPUT_LIMIT_EXCEEDED`: LLM response too large.
*   `UPSTREAM_TIMEOUT`: External API (LLM/Search) timed out.

### Authentication & Auth (401/403)
*   `AUTH_TOKEN_EXPIRED`: Firebase ID token valid but expired.
*   `PERMISSION_DENIED`: Valid user but insufficient role scope.

### Reports & PDF
*   `PDF_GENERATION_FAILED`: Report rendering crashed.
*   `CHART_GENERATION_FAILED`: Visualization error.