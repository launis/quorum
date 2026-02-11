# System Architecture (V2.9 / 2026)

**Status:** V2.9 Production Standard (Feb 2026)
**Core Philosophy:** "Zero-Magic" Modular Async Monolith

Cognitive Quorum V2.9 is a deterministic, highly verifiable AI orchestration platform. It rejects the "black box" nature of standard agent frameworks in favor of a strictly typed, schema-driven architecture where every state transition is audited and persisted via **Event Sourcing**.

---

## 1. High-Level Architecture

The system follows a **Separated Execution Model**: the API accepts requests, but the actual intelligence runs in a detached Async Worker pool. This decouples the user experience from the latency of deep cognitive reasoning.

```mermaid
graph TD
    subgraph "Client Layer (Flutter)"
        App["Thick Client (Riverpod)"]
        Router["GoRouter"]
    end

    subgraph "Orchestration Layer (FastAPI)"
        API["Core API (Admin, Auth)"]
        DomainAPI["Domain API (Config, Execution)"]
        BFF["BFF Transformer"]
        Queue[(Redis / Arq)]
    end

    subgraph "Cognitive Layer (Async Workers)"
        Worker["Arq Worker Pool"]
        Engine["GraphEngine (Core)"]
        State[("WorkflowState (Event Log)")]
        
        Engine -->|Invoke| Agent["Agent Wrapper"]
        Agent -->|1. Reason| LLM["Gemini 1.5 Pro (Thinking)"]
        Agent -->|2. Verify| Hooks["Deterministic Hooks"]
    end

    subgraph "Persistence Layer"
        DB[("TinyDB / Firestore")]
        VectorDB[("ChromaDB")]
    end

    App -->|JSON/Multipart| API
    API -->|Enqueue Job| Queue
    Queue -->|Pull Job| Worker
    Worker --> Engine
    Engine <-->|Load/Save| DB
    Hooks <--> VectorDB
```

---

## 2. Core Components Analysis

### A. The "Spine" (Execution Engine)
*   **Location**: `backend/core/engine.py` (Class: `GraphEngine`)
*   **Role**: The deterministic runtime that loads definitions and executes steps.

### E. API Structure (Modular Routers)
*   **System Routers** (`backend/api/*.py`):
    *   `auth_router`: Login & Session Management.
    *   `admin_router`: System-wide configuration & User Management.
    *   `organization_router`: Multi-tenancy isolation.
*   **Domain Routes** (`backend/api/routes/`):
    *   `config/`: CRUD for `workflows`, `steps`, `components` (The "Brains").
    *   `execution/`: `lifecycle` (Run/Stop), `monitor` (Status), `views` (BFF).
*   **Pattern**: This separation ensures that high-volume execution logic is isolated from low-volume administrative tasks.
*   **Event Sourcing**:
    *   The Engine does not mutate a "Blackboard".
    *   Instead, it appends `TraceEvent` items to an immutable `execution_trace`.
    *   State is derived by replaying these events (or checking the latest snapshot `context_variables`).
*   **Key Feature: Strict Object Mode**:
    *   The Engine **never** passes raw dictionaries to Agents.
    *   It hydrates a `WorkflowState` Pydantic object before execution.
    *   If the DB data does not match the Schema, the Engine **crashes fast** rather than propagating corruption.

### B. The "Mind" (Agent Graph)
*   **Location**: `backend/agents/`
*   **Pattern**: Functional Wrapper.
*   **Behavior**: Agents are stateless logic units. They receive `WorkflowState`, perform **one** specific cognitive task, and return a structured Pydantic object (e.g., `AnalystOutput`).
*   **Reasoning Continuity**: To solve "Chain-of-Thought Amnesia", the engine extracts hidden "Thinking Tokens" from Gemini and passes them to the next agent via `ReasoningTrace`.

### C. The "Hand" (Async Worker)
*   **Location**: `backend/worker.py`
*   **Tech**: `arq` (Redis-based).
*   **Why**: Standard HTTP/WSGI servers timeout after 60s. Cognitive Workflows (e.g., Causal Analysis) take 5-15 minutes.
*   **Resilience**: Workers are stateless. If a worker dies, the job is re-queueable. The `WorkflowState.version` field prevents race conditions ("Optimistic Locking").

### D. The "Face" (Flutter Client)
*   **Location**: `client_app/`
*   **Architecture**: Feature-First, Riverpod-based.
*   **Modules**:
    *   `orchestration`: The flowchart UI and execution monitoring.
    *   `studio`: The Matrix Editor and Configuration tools.
    *   `admin`: User management and System settings.
*   **BFF Pattern**: The frontend does not parse raw Agent outputs. The Backend exposes a "BFF" (Backend for Frontend) view that transforms complex graphs into UI-ready view models.

---

## 3. Data & Persistence Strategy

The system supports a **Dual-Database** strategy for development velocity vs. production scale.

### Primary Store: AbstractWorkflowRepository
*   **Interface**: `backend/database/repository.py`
*   **Implementation A (Local)**: `TinyDBRepository` (JSON file). Zero-setup dev env.
*   **Implementation B (Cloud)**: `FirestoreRepository`. Production scale.

### Vector Store: KnowledgeBaseService
*   **Implementation**: `ChromaDB` (Local/Server).
*   **Use Case**: RAG (Retrieval Augmented Generation) for the Analyst Agent.

### Schema Enforcement
*   **Source of Truth**: `backend/models/state.py`.
*   **Migration Strategy**: "Field Addition Only". We never rename fields; we add new ones and deprecate old ones to maintain backward compatibility with serialized JSON blobs.

---

## 4. Security & Compliance

### Identity & Access Management (IAM)
*   **Scope**: `auth_router.py`.
*   **Model**: RBAC (Root, Admin, Manager, Member, Viewer).
*   **Multi-Tenancy**: All DB queries are scoped by `organization_id`.

### PII Protection
*   **Agent**: `GuardAgent`.
*   **Mechanism**: **Deterministic Cleaning Hooks** (`backend.hooks.security`).
*   **Flow**:
    1.  User submits raw text.
    2.  `GuardAgent` executes `sanitize_input` pre-hook.
    3.  Detected entities (Names, SSNs) are flagged/redacted via regex/heuristics.
    4.  Downstream agents **only** see the sanitized text.

---

## 5. Technology Stack (V2.9 Locked)

| Component | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Backend** | Python | 3.14.2 | Core Logic (Async) |
| **Web Framework** | FastAPI | 0.115+ | REST API |
| **Worker** | Arq | 0.26+ | Job Queue |
| **DB (Doc)** | TinyDB / Firestore | 4.7+ | State Persistence |
| **DB (Vector)** | ChromaDB | 0.4+ | Semantic Search |
| **Frontend** | Flutter | 3.27+ | UI / Client |
| **State Mgmt** | Riverpod | 2.6+ | Reactive State |
| **Routing** | GoRouter | 14.0+ | Navigation |
| **LLM** | Vertex AI | Gemini 1.5 | Cognitive Engine |

---

## 6. Deployment (Docker)

The system is deployed as a consolidated **Docker Compose** stack.

*   `backend`: Exposes Port 8000.
*   `execution-worker`: Runs the Arq process (scales horizontally).
*   `redis`: Message Broker.
*   `client`: Nginx serving the Flutter Web build (Port 8080).

> **Note**: In Development, the `backend` and `worker` bind-mount the local source code for hot-reloading. In Production, they use immutable builds.