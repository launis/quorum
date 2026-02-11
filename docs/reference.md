# Reference Manual & API (V2.9)

This document serves as the technical reference for **Cognitive Quorum V2026**. It covers the directory structure, CLI commands, and the Backend API.

---

## 1. Directory Structure (V2.9)

The project follows a **Modular Monolith** architecture.

```text
quorum/
├── backend/                # Async Python 3.14+ Core
│   ├── agents/             # Specialized Agent Logic (Judge, Analyst)
│   ├── api/                # FastAPI Routers (The Control Plane)
│   │   ├── routes/
│   │   │   ├── config/     # CRUD for Rules, Matrices, Workflows
│   │   │   └── execution/  # Job Submission & Status
│   ├── core/               # GraphEngine & WorkflowRunner
│   ├── database/           # AbstractRepository (TinyDB / Firestore)
│   ├── hooks/              # Deterministic Logic (Scoring, Searching)
│   ├── llm/                # AI Provider Adapters (Vertex, OpenAI)
│   ├── models/             # Pydantic V2 Schemas (SSOT)
│   ├── services/           # Business Logic (Auth, PromptBuilder)
│   ├── seed/               # Data Seeding Logic
│   ├── settings.py         # Environment Settings (Pydantic BaseSettings)
│   └── worker.py           # Arq Worker Entry Point
├── data/                   # Local Persistence
│   ├── db.json             # Local Production DB (GitIgnored)
│   ├── db_mock.json        # Test DB (Mock LLMs)
│   └── seed_data.json      # THE BLUEPRINT (Source of Truth)
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
├── run_full_docker.bat     # Windows Startup Script
├── kill_services.bat       # Windows Cleanup Script
└── pyproject.toml          # Python Dependencies (uv)
```

---

## 2. CLI Command Reference

### Operational Commands (Windows Root)

| Command | Description |
| :--- | :--- |
| `run_full_docker.bat` | **Start System**. Rebuilds Backend/Worker, starts Redis/Firestore, and launches the stack. |
| `kill_services.bat` | **Stop System**. Aggressively terminates Python, Docker processes, and frees ports. |

### Data Management (Seeding)

Managed via `backend/seed/run_seed.py`.

| Target | Command | Purpose |
| :--- | :--- | :--- |
| **Local** | `python backend/seed/run_seed.py local` | Resets `data/db.json` from `seed_data.json`. Use for local dev. |
| **Mock** | `python backend/seed/run_seed.py mock` | Resets `data/db_mock.json`. Use for offline testing. |
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