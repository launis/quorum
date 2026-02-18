# System Components (V3.1)

The Cognitive Quorum system is a hybrid architecture composed of **Specialized Agents** (Python Classes), **Deterministic Hooks** (Helper Modules), a **Configuration-Driven Registry** (JSON Components), and a **Server-Driven UI (SDUI)** platform (Cognitive Studio).

> [!IMPORTANT]
> **V3.1 Standard (Strict Pydantic & Zero-Compromise)**
> All components must adhere to **RFC 7807 Fail Fast** principles. Defensive coding (e.g., `getattr(obj, "field", default)`) is forbidden. Agents and Hooks must trust the Schema and raise `AppException` immediately upon data violation.

---

## 1. Specialized Agents (`backend/agents/`)

Agents in V3.1 are specialized classes inheriting from `BaseAgent`, designed to be "Thin Wrappers" around configuration and logic. They are registered in the `TaskRegistry` and executed by the `GraphEngine`. All agents return strictly typed **Pydantic V2** models.

| Agent Class | File | Responsibility | Output Schema |
| :--- | :--- | :--- | :--- |
| `GuardAgent` | `guard.py` | Input sanitization, PII check, prompt injection defense. | `GuardOutput` |
| `AnalystAgent` | `analyst.py` | Data ingestion and preliminary context engineering audit. | `AnalystOutput` |
| `InteractionAnalystAgent` | `interaction.py` | Analyzes user dependency, strategy (Zero vs Few-Shot). | `InteractionAnalysis` |
| `ProfilerAgent` | `profiler.py` | User intent profiling and cognitive bias detection. | `ProfilerAnalysis` |
| `LogicianAgent` | `logician.py` | Toulmin argument mapping and logical structure audit. | `LogicianOutput` |
| `LogicalFalsifierAgent` | `critics.py` | Stress-testing arguments (Devil's Advocate) & Critical Loop audit. | `FalsifierOutput` |
| `CausalAnalystAgent` | `critics.py` | Impact verification (Did user input *cause* improvement?). | `CausalOutput` |
| `PerformativityDetectorAgent` | `critics.py` | Identifies "Illusion of Control" and performative language. | `PerformativityAnalysis` |
| `FactualOverseerAgent` | `critics.py` | Fact-checking (Google Search) and hallucination management. | `OverseerOutput` |
| `ArchivistAgent` | `archivist.py` | Best practices audit & precedent fetching. | `ArchivistOutput` |
| `RetrievalAgent` | `retrieval.py` | Organizational grounding and context retrieval (Precedents). | `ContextData` |
| `PanelAgent` | `panel.py` | **Unified Parallel Critic**: Orchestrates Falsifier, Causal, and Performativity agents in parallel. Aggregates capabilities with strict error handling. | `PanelOutput` |
| `JudgeAgent` | `judge.py` | **Polymorphic Scorer**: Final verdict using dynamic `matrix_id`. Supports Dual-Chain (Standard + Cognitive). | `JudgeOutput` |
| `CoachAgent` | `coach.py` | Feedback generation based on Judge's verdict. | `CoachingPlan` |
| `XAIReporterAgent` | `xai.py` | **Explanability Engine**: Aggregates Judge scores and critical findings into a final narrative. Enforces strict ScoreCard validation. | `XAIOutput` |

### 1.1 Architectural Patterns: Template vs. Stack vs. Fusion

The system employs distinct architectural patterns for agents to handle complexity and task volume.

| Feature | **Template Pattern** (e.g. Profiler) | **Stack Pattern** (e.g. Analyst) | **Fusion Pattern** (e.g. Panel) |
| :--- | :--- | :--- | :--- |
| **Logic Source** | **Injected Variable**. Task logic is injected into a placeholder. | **Stacked Module**. Logic is appended sequentially. | **Aggregated Directives**. Merges mandates from multiple sub-agents. |
| **Structure Source** | **Master Template**. Rigid forms. | **Global Headers**. General rules. | **Unified Schema**. A single complex schema (`PanelOutput`) that maps to multiple sub-domains. |
| **Capabilities** | **Single-Track**. Focuses on one specific output. | **Single-Track**. Focuses on one specific output. | **Multi-Track (Super-Set)**. Inherits capabilities from all sub-agents (e.g., *Google Search* from Overseer + *Citation Verification* from Falsifier). |
| **Use Case** | **Deep Dive**. When depth is required. | **Linear Analysis**. When order matters. | **Simultaneous Review**. When multiple perspectives are needed in parallel (e.g. 3-in-1 Audit). |

### 1.2 Resilience Patterns: Lazy Dictionary Inflation (`RetrievalAgent`)

While the system mandates strict Pydantic usage, historical database records may be stored as raw dictionaries (`dict[str, Any]`) to prevent schema-drift crashes.

> [!NOTE]
> **Just-In-Time Inflation**: Agents that interact with historical data (like `RetrievalAgent`) implement a defensive "Inflation Check" at the logic boundary.
> 1.  Check: `if isinstance(data, dict)`
> 2.  Action: Inflate to Pydantic Model (`WorkflowState.model_validate(data)`)
> 3.  Validation: If inflation fails -> **Fail Fast** with `AppException` (Integrity Error).

This pattern protects the database layer from rigidity while enforcing data integrity strictly at the logic layer.

---

## 2. Components Registry (`db.json` / `components`)

The "Mind" of the system is decoupled from Python code. Reusable blocks are stored in the `components` dictionary in `db.json` (or SQL database).

### Component Types
1.  **`evaluation_matrix`**: Defines the "Lens" the Judge uses (e.g., `matrix_standard_v1`).
    *   **Ontology Integration**: Dimensions are linked to the **Ontology Registry**.
    *   **Prompt Formatting**: Handled by `MatrixFormatter` service.
2.  **`mandate`**: Irrevocable system directives (e.g., "Slow Thinking").
3.  **`rule`**: Operational boundaries (e.g., "No Hallucination").
4.  **`instruction`**: Specific task capabilities (e.g., "Use Toulmin Model").
5.  **`protocol`**: Algorithm for analysis (e.g., "Negative Proof").
6.  **`system_config`**: Global system settings (e.g., `model_registry`).
7.  **`context`**: Dynamic context injection (e.g., Time/Location anchors).
8.  **`output_config`**: Defines schema hoisting rules for reports (e.g., which fields to show in the UI).

---

## 3. Deterministic Hooks (`backend/hooks/`)

Hooks are pure Python functions invoked by agents to perform tasks outside the LLM's capabilities. They are registered in `HOOK_MAPPING` and must adhere to **Strict Pydantic** input/output contracts.

### `backend/hooks/security.py`
*   **PII Anonymization:** Deterministic regex and heuristic cleaning.
*   **Input Sanitization:** Injection pattern removal.
*   **Fail Fast:** Raises `AppException(400)` if mandatory inputs (e.g., `history_text`) are missing.

### `backend/hooks/validation.py`
*   **Verify Structure:** Enforces minimum length requirements on input fields.
*   **Schema Enforcement:** Validates `WorkflowInputs` integrity before execution.

### `backend/hooks/archival.py`
*   **RAG Interface:** ChromaDB interface for `RetrievalAgent`.
*   **Similarity Search:** Semantic embedding retrieval.
*   **Strict Dependency:** Raises `500` if Repository is unavailable.

### `backend/hooks/reporting.py`
*   **XAI Report Generation:** Jinja2 template rendering using typed `ReportContext`.
*   **Composition:** Aggregates Agent outputs into a final artifacts payload.

### `backend/hooks/scoring.py`
*   **Score Normalization:** Standardizes 1-4 scales to 0-100% for radar charts.
*   **Relative Penalties:** Applies percentage-based deductions (Security, Post-Hoc) defined in `settings.py`.
*   **Passivity Detection:** Detecting min-score "lazy" judgments and applying multipliers.

### `backend/hooks/references.py`
*   **Citation Audit:** Scans text for references present in the Knowledge Base.
*   **Strict Context:** Requires `step_coach` or textual inputs to function.

### `backend/hooks/search.py`
*   **Vertex AI Search:** Grounding-based search integration (replaces legacy Custom Search API).
*   **Configuration Gate:** Controlled by `ENABLE_VERTEX_SEARCH` env var (Default: False).
    *   If enabled: Requires `VERTEX_SEARCH_MODEL` (Data Store ID).
    *   If disabled: Gracefully skips execution (returns empty results) to prevent crashes.
*   **Strict Inflation:** Uses `inflate(data, OverseerOutput)` to ensure type safety.
*   **Error Handling:** Maps API quotas (429) to specialized `ServiceUnavailableError`.

---

## 4. Execution Engine (`backend/worker.py` & `backend/core/`)

The **Execution Plane** has been modernized in V3.1.

*   **GraphEngine**: The core orchestrator that executes `WorkflowDefinition` DAGs. Handles state transitions via **Event Sourcing** (`TraceEvent`).
    *   **Strict Inputs**: Enforces `WorkflowInputs` model at entry.
*   **TaskRegistry**: A decorator-based registry that maps JSON task keys (e.g., `step_judge`) to Python functions.
*   **Worker Service**: Built on **Arq** (Async Redis Queue) for background processing.
    *   **Logfire Integration**: Full observability traces linked to `execution_id`.
    *   **Resilience**: Intelligent retries and phantom-job handling.
*   **LocalizationService**: Request-scoped (`ContextVar`) translation engine for error messages and UI hints.
*   **MatrixFormatter**: Service for strictly formatting Evaluation Matrices into LLM prompts.

---

## 5. Data Models (`backend/models/`)

All system communication relies on **Pydantic V2** models.

*   **`WorkflowState`**: The Event-Sourced State Container.
    *   **V3.1 Update**: Includes typed `inputs: WorkflowInputs` (via inflation).
*   **`WorkflowInputs`**: Strict schema for incoming requests (`history_text`, `product_text`, etc.).
*   **`JudgeOutput`**: Standardized scoring output containing `score_card`, `verdict`, and `dimensions`.
*   **`XAIOutput`**: Final report schema with `score_cards` list.
*   **`ReportContext`**: Typed context object for XAI report generation (passed to Jinja2).

---

## 6. Cognitive Studio (Frontend Architecture)

The **Cognitive Studio** is the specific Flutter-based administration interface for managing these components.

*   **Controller**: `StudioController` (Riverpod AsyncNotifier) manages optimistic UI state.
*   **Repository**: `StudioRepository` handles data fetching with "Loud Parsing" and high-fidelity error mapping.
*   **Domain Models**:
    *   `WorkflowDef`: The blueprint for execution chains.
    *   `ComponentDef`: Reusable configuration blocks.
    *   **Ontology Integration**: Dynamic fetching of analysis dimensions.
*   **Hub Architecture**: A dedicated "Studio Hub" separates configuration concerns from the general Admin Dashboard.