# Reference Manual & API (V5.1 - Phase 9 Hardening)

This document serves as the technical reference for **Cognitive Quorum V2026**. It covers the directory structure, CLI commands, Data Lifecycle, and the Backend API.

---

## 1. Directory Structure (V5.1)

The project follows a **Modular Async Monolith** architecture with **Strict Pydantic V2** enforcement and **Prefixed Identifiers** for automated relation mapping.

```
quorum/
├── backend/                # Async Python 3.14+ Core
│   ├── agents/             # Specialized Agent Logic (Panel, Judge, Analyst)
│   ├── api/                # FastAPI Routers (The Control Plane)
│   │   ├── routes/
│   │   │   ├── config/     # CRUD for Rules, Matrices, Workflows
│   │   │   ├── usage/      # Token metrics & Aggregation (Root/Org/User scopes)
│   │   │   └── execution/  # Job Submission & Status
│   │   ├── transformers/   # Modular View Transformers (Unified SDUI Pipeline for UI & PDF)
│   ├── core/               # GraphEngine & WorkflowRunner
│   ├── database/           # Unified Repository (TinyDB / Firestore)
│   │   └── db_mock.json    # Test DB (Mock LLMs)
│   ├── hooks/              # Deterministic Logic (Security, Reporting, Search)
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
> **Note**: Seeding requires **Python 3.14.2+** to ensure consistent hashing and Pydantic V2 validation behavior.

| Target | Command | Purpose |
| :--- | :--- | :--- |
| **Local** | `uv run backend/seed/run_seed.py local` | Resets `data/db.json` from `seed_data.json`. Use for normal feature deployment. |
| **Mock** | `uv run backend/seed/run_seed.py mock` | Resets `backend/database/db_mock.json`. Use for offline testing or UI work. |
| **Cloud** | `uv run backend/seed/run_seed.py firestore` | **DANGER**. Destructive operation. Overwrites Production Firestore. |

### Backend Development (uv)
We use `uv` for dependency management.
*   **Sync Dependencies**: `uv sync`
*   **Run Linter**: `uv run ruff check .`
*   **Format Code**: `uv run ruff format .`
*   **Generate OpenAPI**: `uv run backend/scripts/generate_openapi.py` (Must be run after API schema changes).

---

## 3. Configuration & Metadata (`seed_data.json`)

`backend/seed/seed_data.json` is the **Immutable Source of Truth (SSOT)** for all configuration, logic, and structure. Unidirectional Data Flow applies: edit the JSON, then seed to the Database (GitOps pattern). The database is always a pure derivation of the code.

### Schema Structure
The file defines core domains:
1.  **`system_config`**: Global settings and **Model Registry** (maps Agents to Models like `gemini-2.5-pro` via `agent_mappings`).
2.  **`organizations` & `users`**: Multi-tenancy definitions and Seeded Identities (e.g., `root_master`).
3.  **`components`**: Reusable Prompts, Rules, and Matrices (BARS).
4.  **`workflows` & `steps`**: Execution Blueprints and Reusable step definitions.
5.  **`agents`**: Explicitly separated autonomous agent configurations.
6.  **`concepts`, `references`, `claims`**: Decoupled Knowledge Base items.

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
| `LOGFIRE_IGNORE_NO_CONFIG` | Suppress logfire warnings locally. | `1` | `0` |

---

## 5. System Seeding & Data Lifecycle Protocols

Because `seed_data.json` is the SSOT, making changes to data structures requires following specific protocols.

### 5.1. Schema-Agnostic Seeder
The seeder scripts are strictly "Schema-Agnostic", powered by a centralized **Universal Seed Registry** (`backend/seed/seed_registry.py`). You never need to modify the seeder scripts when adding new fields or collections to the database or models. The seeder dynamically invokes Pydantic validation via the Universal Registry mapping.

### 5.2. Derived Data (Ontology)
The Seeder performs **Intelligent Extraction**. For example, the `dimensions` collection in the database is NOT statically defined in `seed_data.json`. The Seeder scans all `evaluation_matrix` components, extracts every `criteria` and `scale` definition, and automatically populates the Ontology Store (`dimensions`) so the UI and MatrixFormatters can query them cleanly.

### 5.3. "Round-Trip" Testausprotokolla
To guarantee bit-for-bit data retention when using the integrator:
1. **Turva**: Keep a clean copy of `seed_data.json` (e.g. `seed_data_test_roundtrip.json`).
2. **Kantaan (Lataus)**: Run `uv run backend/seed/run_seed.py local`. Dumps JSON to database.
3. **Takaisin (Purku)**: Run `uv run backend/seed/migrate_to_seed.py`. Reads database back into `seed_data.json`.
4. **Varmennus**: Compare line counts (`wc -l`) and object limits. If differences are strictly 0 (except for intentional dead code purges), the integration is production-ready.

### 5.4. Legacy Field Strip (Data Extraction) Protocol
To safely amputate a "Dead Code" field from `seed_data.json` that is no longer supported by strict DTOs:
1. **Verify**: Grep the backend codebase to ensure the field is absolutely unused.
2. **Backup**: `cp seed_data.json seed_data.json.PRE_STRIP.bak`.
3. **Script the Purge**: Do NOT use regex. Write a targeted Python script that traverses the dictionary structure and executes `del item['config']['dead_key']`.
4. **Validate**: Perform the Round-Trip Protocol (Section 5.3) to establish system immunity.

### 5.5. Development Workflow (New Feature)
1. **Define Agent Strategy**: Add `ReviewerAgent` to `system_config` with strategy `precise`.
2. **Add Prompts**: Add instruction component to `components`.
3. **Create Step & Workflow**: Define in `steps` list and reference in `workflows`.
4. **Apply**: Run `uv run backend/seed/run_seed.py local`.
5. **Verify**: Open Cognitive Studio and test the workflow.

---

## 6. API Paradigms & Error Codes

### 6.1. Strict DTO & Identity
* **UUID vs ID:** Legacy `uid` payload keys are refactored to `id` uniformly across the API.
* **Slug Keys:** Definition models (`WorkflowConfigDefinition`, `StepDefinition`) support a `slug` field for legacy human-readable identification.
* **Executions (`ExecutionRequestDTO`):** Strictly require a `workflow_id`. Organization is validated internally. Accepts base64 robust inputs and `GuidedReflectionDTO` payloads.

### 6.2. Telemetry & Usage APIs
Usage metrics are tracked natively and exposed via:
* `/v1/usage/system` (Root only)
* `/v1/usage/organization/{org_id}`
* `/v1/usage/user/{user_id}`
* `/organizations/{org_id}/usage/detailed`

### 6.3. Error Codes (RFC 7807)
The API returns standard HTTP codes plus a detailed `error_code` in the JSON body.
* **500**: `INTERNAL_SERVER_ERROR` - Unhandled exception.
* **503**: `NETWORK_UNAVAILABLE` - Connectivity issues.
* **422**: `VALIDATION_ERROR` - Pydantic locally failed to parse data (**Fail Fast**).
* **422**: `INVALID_JSON_PAYLOAD` / `EMPTY_INPUT` / `SECURITY_VIOLATION`.
* **404**: `EXECUTION_NOT_FOUND` / `WORKFLOW_NOT_FOUND`.
* **400**: `WORKFLOW_EXECUTION_FAILED` / `MODEL_OUTPUT_LIMIT_EXCEEDED` / `SECURITY_DB_ERROR`.