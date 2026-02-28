# Reference Manual & API (V5.1 - Phase 9 Hardening)

This document serves as the technical reference for **Cognitive Quorum V2026**. It covers the directory structure, CLI commands, and the Backend API.

---

## 1. Directory Structure (V5.1)

The project follows a **Modular Monolith** architecture with **Strict Pydantic V2** enforcement and **Prefixed Identifiers** for automated relation mapping.

```
quorum/
├── backend/                # Async Python 3.14+ Core
│   ├── agents/             # Specialized Agent Logic (Panel, Judge, Analyst)
│   ├── api/                # FastAPI Routers (The Control Plane)
│   │   ├── routes/
│   │   │   ├── config/     # CRUD for Rules, Matrices, Workflows
│   │   │   └── execution/  # Job Submission & Status
│   │   ├── transformers/   # Modular View Transformers (Unified SDUI Pipeline for UI & PDF)
│   ├── core/               # GraphEngine & WorkflowRunner
│   ├── database/           # Unified Repository (TinyDB / Firestore)
│   │   └── db_mock.json    # Test DB (Mock LLMs)
│   ├── hooks/              # Deterministic Logic (Security, Reporting)
│   ├── llm/                # AI Provider Adapters (Vertex, OpenAI)
│   ├── models/             # Pydantic V2 Schemas (SSOT)
│   │   ├── domain/         # Domain Models (System Authority, Rich)
│   │   ├── dtos/           # Data Transfer Objects (Pure LLM Output)
│   │   ├── view/           # View Models & SDUI Response Schemas
│   │   ├── enums.py        # Shared Enumerations
│   │   └── state.py        # Workflow State Defs
│   ├── services/           # Business Logic (Auth, Storage, PromptBuilder)
│   ├── seed/               # Data Seeding Logic (SSOT)
│   │   └── seed_data.json  # THE CONFIGURATION BLUEPRINT
│   ├── settings.py         # Environment Settings (Pydantic BaseSettings)
│   └── worker.py           # Arq Worker Entry Point
├── data/                   # Local Persistence
│   ├── db.json             # Local Production DB
│   └── files/              # Local File Storage
├── docs/                   # Documentation (MkDocs)
├── client_app/             # Flutter Client (Cognitive Studio)
├── scripts/                # CI/CD & Utility Scripts
├── run_local.bat           # Local Development Startup
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

Managed via `backend/seed/run_seed.py`. **Seeding is the Single Source of Truth.**

| Target | Command | Purpose |
| :--- | :--- | :--- |
| **Local** | `python backend/seed/run_seed.py local` | Resets `data/db.json` from `seed_data.json`. Use for local dev. |
| **Mock** | `python backend/seed/run_seed.py mock` | Resets `backend/database/db_mock.json`. Use for offline testing. |
| **Cloud** | `python backend/seed/run_seed.py firestore` | **DANGER**. Overwrites Production Firestore with Seed Data. |

### Backend Development (uv)

We use `uv` for dependency management.

*   **Sync Dependencies**: `uv sync`
*   **Run Linter**: `uv run ruff check .`
*   **Format Code**: `uv run ruff format .`

---

## 3. Configuration & Metadata

### System Configuration (`system_config`)
The system uses a database-driven configuration strategy to avoid hardcoding.

| Key | Description | Example |
| :--- | :--- | :--- |
| `model_registry` | Defines available LLMs and their strategies. | `{"google": {"deep": "gemini-2.0-pro"}}` |
| `AgentSystemConfig` | Configures individual agents. | `{"id": "PanelAgent", "model_strategy": "deep"}` |

### Model Strategies
*   **Fast**: High speed, lower cost (e.g., Flash). Used for routine tasks.
*   **Deep**: High reasoning, larger context (e.g., Pro). Used for Panel, Analyst.
*   **Strict**: Low temperature, deterministic. Used for Guard, Syntax Checks.
*   **Precise**: Creative but grounded. Used for Judge.

---

## 4. Environment Variables

Defined in `.env` and managed by `backend/settings.py`.

| Variable | Description | Valid Values | Default |
| :--- | :--- | :--- | :--- |
| `ENVIRONMENT` | Environment Mode. | `development` / `production` | `development` |
| `STORAGE_BACKEND` | Storage engine choice. | `LOCAL` / `MOCK` / `FIRESTORE` | `LOCAL` |
| `ENABLE_VERTEX_SEARCH` | Gate Google Search access. | `true` / `false` | `false` |
| `GOOGLE_API_KEY` | Key for Google AI Studio (Gemini). | String | - |
| `REDIS_HOST` | Redis connection for Arq. | Hostname / IP | `localhost` |

---

## 5. Error Codes (RFC 7807)

The API returns standard HTTP codes plus a detailed `error_code` in the JSON body.

### General & System
*   **500**: `INTERNAL_SERVER_ERROR` - Unhandled system exception.
*   **503**: `NETWORK_UNAVAILABLE` - Connectivity issues.

### Validation (400 / 422)
*   **422**: `VALIDATION_ERROR` - Pydantic V2 strictly failed to parse input/legacy data (Fail Fast).
*   `INVALID_JSON_PAYLOAD`: Input does not match Pydantic model structure.
*   `EMPTY_INPUT`: Required text field was empty.
*   `SECURITY_VIOLATION`: Banned phrase detected or PII rejected.

### Resources (404)
*   `EXECUTION_NOT_FOUND`: Job ID lookup failed.
*   `WORKFLOW_NOT_FOUND`: Workflow definition missing.

### Execution & Logic
*   `WORKFLOW_EXECUTION_FAILED`: Critical failure during workflow run.
*   `MODEL_OUTPUT_LIMIT_EXCEEDED`: LLM response too large.
*   `SECURITY_DB_ERROR`: Failed to fetch security rules (Fail Fast).