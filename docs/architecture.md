## Architecture: Cognitive Quorum v2

The **Cognitive Quorum v2** architecture is designed to be a fully **Generic Workflow Engine** with a **Cloud Native** focus. It decouples the frontend from the backend, allowing for asynchronous processing and scalable deployment.

## Core Concepts

### 1. Data-Driven Logic
All business logic is defined in the database (seeded from `seed_data.json`), not in code.
- **Rules**: Global constraints (e.g., "Chain of Trust").
- **Prompts**: Instructions for LLMs.
- **Steps**: Units of execution with defined Inputs, Outputs, and Hooks.
- **Workflows**: Ordered sequences of Steps.

### 2. REST API & Job Queue
The system exposes a REST API (FastAPI) to handle requests. Long-running workflows are executed asynchronously using a Job Queue pattern:
- **`POST /orchestrator/run`**: Accepts files and starts a background task. Returns a `job_id`.
- **`GET /orchestrator/status/{job_id}`**: Polling endpoint to check progress and retrieve results.

### 3. Generic Engine
The `Orchestrator` and `Executor` classes (`src/engine/`) are agnostic to the specific content of the workflow. They simply execute the sequence defined in the database.

### 4. Registry Pattern
To bridge the gap between static data (JSON) and dynamic code (Python), we use a Registry Pattern:
- **`SchemaRegistry`**: Maps string names (e.g., "AnalysisSummary") to Pydantic models.
- **`HookRegistry`**: Maps string names (e.g., "execute_google_search") to Python functions.

## Directory Structure

```
src/
├── api/                # FastAPI Application
│   ├── routers/        # API Endpoints
│   └── server.py       # Entry Point
├── components/         # Hybrid Components (Hooks & Templates)
│   ├── hooks/          # Python functions (Search, RAG, Parsing)
│   └── templates/      # Jinja2 templates for reporting
├── database/           # Database Client (Firestore/TinyDB)
├── engine/             # Orchestrator & Executor
└── models/             # Pydantic Schemas & Registry
```

## Execution Flow

1.  **Frontend** uploads files to `POST /orchestrator/run`.
2.  **API** saves files (Local/GCS), creates a `Job` record (PENDING), and triggers a background task.
3.  **Background Task**:
    *   Updates Job status to RUNNING.
    *   **Orchestrator** loads the Workflow definition.
    *   **Executor** runs each Step (Pre-Hooks -> LLM -> Post-Hooks).
    *   Updates Job status to COMPLETED and saves the result (JSON + Markdown).
4.  **Frontend** polls `GET /orchestrator/status` and displays the result when ready.

## 5. Prompt Engineering & SSOT Architecture

To ensure consistency and maintainability across all agents, the system employs a **Single Source of Truth (SSOT)** architecture for prompt engineering.

### 5.1 Data Fragments (`data/fragments/`)
Instead of monolithic prompt files, core logic is atomized into JSON fragments:
- **`rules.json`**: Global constraints (e.g., "SÄÄNTÖ 1: Haurauden Tunnustus").
- **`mandates.json`**: System-wide mandates (e.g., "Mandaatti 1.4: Performatiivisuuden Torjunta").
- **`protocols.json`**: Operational protocols (e.g., RFI, Schema Validation).
- **`methods.json`**: Methodological tools (e.g., Metodologinen Loki).
- **`criteria.json`**: BARS evaluation criteria.

### 5.2 Dynamic Assembly (Jinja2)
Prompts are dynamically assembled using **Jinja2 templates** (`data/templates/`) during the database seeding process.
- **Templates**: Define the structure of the prompt (e.g., `prompt_guard.j2`).
- **Injection**: Fragments are injected into templates (e.g., `{{ methods | selectattr('id', 'equalto', 'METHOD_LOG') ... }}`).

### 5.3 Seeding Process (`backend/seeder.py`)
The seeding script:
1.  Loads all JSON fragments.
2.  Loads Jinja2 templates.
3.  Renders the final prompt text for each agent.
4.  Upserts the rendered prompts into the `components` table in `data/db.json`.

This ensures that a change to a single rule in `rules.json` is automatically propagated to every agent that references it.

