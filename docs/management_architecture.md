# Management Architecture

The Management Architecture for Cognitive Quorum v2.5 is a decoupled system designed for dynamic, real-time configuration of the AI engine. It enables administrators to manage the system's core logic—workflows, prompts, and agent configurations—through a web interface, without deploying new code.

This architecture separates the system into four execution components: a user-facing **Frontend**, an Async **API Backend**, a distributed **Worker Service**, and a data-driven **Generic Engine**.

---

## System Components

The v2.5 architecture introduces asynchronous processing to handle long-running cognitive tasks (Deep Research, Causal Analysis) without blocking the management UI.

```mermaid
graph TD
    subgraph "User Interface"
        A["Management UI (Streamlit)"]
    end
    subgraph "Application Layer"
        B["API Service (FastAPI)"]
        W["Worker Service (Arq)"]
    end
    subgraph "Core Logic"
        C["Generic Engine"]
        D["Agents"]
    end
    subgraph "Data Layer"
        R[(Redis - Job Queue)]
        E["Database (TinyDB / Firestore)"]
    end

    A -- API Calls (HTTP) --> B
    B -- Manages Config --> E
    B -- Enqueue Job --> R
    R -- Pull Job --> W
    W -- Orchestrates --> C
    C -- Reads Config --> E
    C -- Executes --> D
    D -- Updates State --> E
```

### Frontend (Streamlit)
A web-based user interface (`pages/Management_Dashboard.py`) for system administrators. It provides tools to edit all system configurations. It communicates exclusively with the Backend via REST API calls and has no direct access to the database.

### Backend (FastAPI)
The Control Plane. It handles incoming HTTP requests, validates configuration changes via Pydantic V2 schemas, and serves as the gateway for enqueuing execution jobs.

### Worker Service (Arq + Redis)
The Execution Plane. A distributed background service that pulls jobs from Redis. This allows the system to scale horizontally and handle tasks that exceed standard HTTP timeout limits (e.g., 60s+ LLM reasoning chains). Monitoring and traces are exported to **Logfire**.

### Generic Engine
The core processing unit running inside the Worker. It reads the `WorkflowState` and `WorkflowDefinition` from the database, initializes the required Agents using Dependency Injection, and executes the pipeline.

### Database (JSON / Firestore)
The single source of truth. It stores:
*   **Definitions**: Prompts, Rules, Agent Configs.
*   **State**: Live execution data (`WorkflowState`).

---

## Management Data Flow

Configuration changes follow an API-driven, immediate consistency model.

1.  **Edit**: An administrator modifies a prompt in the Streamlit UI.
2.  **API Request**: Upon saving, the UI sends a `PUT /prompts/{id}` request to the FastAPI backend.
3.  **Persistence**: The backend validates the data (Pydantic) and updates the record in the active database.
4.  **Live Update**: The next job picked up by a Worker will immediately use the new configuration.

## UI Components (`pages/Management_Dashboard.py`)

The Management Dashboard is organized into task-oriented tabs:

### 1. Workflow Editor
The primary interface for defining behavior.
*   **Visualizer**: Displays the sequence of agent steps.
*   **Step Configuration**: Drag-and-drop interface to add/remove/reorder steps and assign Agents/Prompts.

### 2. Prompts & Rules Editor
Manages the content assets.
*   **Prompt Editor**: Jinja2-aware text editor.
*   **Rules Editor**: Managed list of Mandates and Protocols.
*   **Previewer**: Real-time rendering of prompts with sample data.

### 3. System Maintenance
*   **Database Seeding**: Reset the active database to `seed_data.json` baseline interactively via API.
*   **Environment Sync**: APIs to promote configurations from Mock to Prod (`Deploy Mock to Prod`) or clone Prod to Mock (`Sync Prod to Mock`).

## Environments & Data Synchronization

## Environments & Data Synchronization

The system maintains a **3-Tier Environment** model to ensure safe promotion of configuration:

| Environment | Database | Purpose | Seeding Command |
| :--- | :--- | :--- | :--- |
| **Local Mock** | `data/db_mock.json` | Sandbox for offline testing and development. | `tools/seed_mock.py` |
| **Local Prod** | `data/db.json` | Local testing with Live LLMs (Vertex AI). | `run_rebuild_prod_db.py` |
| **Cloud Prod** | Firestore (GCP) | Production traffic in `europe-north1`. | `scripts/seed_firestore.py` |

## Operational Management (Process Hygiene)

Managing the distributed components (API, Worker, Redis) requires strict process hygiene, especially in Windows development environments.

### Docker-Based Orchestration
The primary deployment interface is Docker Compose.
*   **Startup**: `run_full_docker.bat` performs a "Clean Build & Start". It forcefully rebuilds images to ensure `worker.py` code changes are propagated.
*   **Shutdown**: Standard `docker-compose down`.

### Process Hygiene & "Zombie Kill"
Due to the multi-process nature of the Worker and Python's behavior on Windows:
*   **The Problem**: Terminating a terminal often leaves orphan `python.exe` or `uv` processes running in the background, holding onto file locks (TinyDB) or ports (8000).
*   **The Protocol**: The **Nuclear Kill Mandate** is enforced via `kill_services.bat`, which aggressively terminates all related processes by name/port before restarting. This is standard operating procedure when switching environments or recovering from "Split-Brain" database states.