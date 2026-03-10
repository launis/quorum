# Reference Manual & API (V2.5)

This document serves as the technical reference for **Cognitive Quorum V2026**. It covers the directory structure, CLI commands, Data Lifecycle, and the Backend API.

---

## 1. Directory Structure (V2)

The project follows a **Modular Async Monolith** architecture with **Strict Pydantic V2** enforcement.

```
quorum/
├── backend_v2/             # Async Python 3.12+ Core
│   ├── api/                # FastAPI Routers (The Control Plane)
│   │   ├── routers/
│   │   │   ├── studio/     # CRUD for Rules, Matrices, Workflows
│   │   │   ├── execution/  # Job Submission & Status
│   │   │   └── iam/        # Tenant mapping and identity
│   ├── core/               # DAG Execution Engine
│   ├── database/           # Unified Repository (Firestore)
│   ├── models/             # Pydantic V2 Schemas (SSOT)
│   │   ├── execution.py    # Execution states
│   │   └── v2_core.py      # Core Models (Workflows, Blocks, SystemConfig)
│   ├── services/           # Business Logic (Auth, Studio, Execution)
│   ├── scripts/            # Database migration utilities
│   ├── seed/               # Data Seeding Logic (SSOT)
│   │   ├── run_seed.py     # Execution Script
│   │   └── seed_registry.py# Model to Collection mapping
│   ├── settings.py         # Environment Settings
│   └── main.py             # FastAPI App Entry
├── data/                   # Local Configuration
│   ├── db_v2.json          # Local V2 JSON Database
│   ├── seed_data.json      # V2 blueprint configuration
│   └── files/              # Local uploaded files
├── docs/                   # Documentation (MkDocs)
├── client_app_v2/          # Flutter Client (Cognitive Studio V2)
│   ├── lib/
│   │   ├── features/       # Feature-driven module architecture
│   │   ├── core/           # Routing and Networking
│   │   └── shared/         # Common DTOs and Logic
├── run_local.bat           # Local Development Startup
└── pyproject.toml          # Python Dependencies (uv)
```

---

## 2. CLI Command Reference

### Operational Commands (Windows)

| Command | Description |
| :--- | :--- |
| `run_local.bat` | Starts Uvicorn API (`8000`), Riverpod Dart server (`8001`), and Flutter UI. Handles mock vs production ENV variables automatically. |

### Data Management (Seeding)
Managed via `backend_v2/seed/run_seed.py`. **Seeding is the Single Source of Truth.**

| Target | Command | Purpose |
| :--- | :--- | :--- |
| **Local** | `uv run python backend_v2/seed/run_seed.py local` | Resets `data/db_v2.json` from `data/seed_data.json`. Use for offline development. |
| **Cloud** | `uv run python backend_v2/seed/run_seed.py firestore` | **DANGER**. Destructive operation. Overwrites Production Firestore with local rules. |

### Backend Development (uv)
We use `uv` for ultra-fast dependency management and virtual isolated Python environments.
*   **Sync Dependencies**: `uv sync`
*   **Run Backend Only**: `uv run uvicorn backend_v2.main:app --reload`
*   **Execute Script**: `uv run python backend_v2/scripts/[script_name].py`

---

## 3. Configuration & Metadata (`seed_data.json`)

`data/seed_data.json` is the **Immutable Source of Truth (SSOT)** for all configuration, logic, and structure.

### Schema Structure
1.  **`system_config`**: The Model Registry mapping logic (`fast`, `deep`) to actual cloud endpoints.
2.  **`prompt_blocks`**: Reusable Prompts, Instructions, and evaluation Matrices.
3.  **`steps`**: Reusable TaskBlueprints connecting a model strategy to a PromptBlock.
4.  **`workflows`**: Directed Acyclic Graph (DAG) flow tying steps together.

---

## 4. Environment Variables

Managed by `backend_v2/settings.py`.

| Variable | Description | Valid Values | Default |
| :--- | :--- | :--- | :--- |
| `ENVIRONMENT` | Environment Mode. | `development` / `production` | `development` |
| `USE_MOCK_DB` | Determines Storage Engine. | `true` (Local JSON) / `false` (Firestore) | `true` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Absolute path to Firebase Service Account if `USE_MOCK_DB=false`. | String | - |

---

## 5. Development Workflow (New Feature)
1. **Define Block**: Add a new `prompt_block` to `data/seed_data.json`.
2. **Bind Context**: Add a `step` referencing the block and defining input mappings (`$inputs.chat_log`).
3. **Route Workflow**: Create a `workflow` that places the step in a DAG sequence.
4. **Seed**: Run `uv run python backend_v2/seed/run_seed.py local`.
5. **Verify**: Open `http://localhost:8000/api/v2/studio/workflows` to verify the DB representation.