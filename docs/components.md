# System Components (V2.9)

The Cognitive Quorum system is a hybrid architecture composed of **Specialized Agents** (Python Classes), **Deterministic Hooks** (Helper Modules), a **Configuration-Driven Registry** (JSON Components), and a **Server-Driven UI (SDUI)** platform (Cognitive Studio).

---

## 1. Specialized Agents (`backend/agents/`)

Agents in V2.9 are specialized classes inheriting from `BaseAgent`, designed to be "Thin Wrappers" around configuration and logic. They are registered in the `TaskRegistry` and executed by the `GraphEngine`. All agents return strictly typed **Pydantic V2** models.

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
| `PanelAgent` | `panel.py` | **Unified Parallel Critic**: Orchestrates Falsifier, Causal, and Performativity agents in parallel. | `PanelOutput` |
| `JudgeAgent` | `judge.py` | **Polymorphic Scorer**: Final verdict using dynamic `matrix_id`. | `JudgeOutput` |
| `CoachAgent` | `coach.py` | Feedback generation based on Judge's verdict. | `CoachingPlan` |
| `XAIReporterAgent` | `xai.py` | Generates human-readable MD reports & Comparison Matrices. | `XAIOutput` |

---

## 2. Components Registry (`db.json` / `components`)

The "Mind" of the system is decoupled from Python code. Reusable blocks are stored in the `components` dictionary in `db.json` (or SQL database).

### Component Types
1.  **`evaluation_matrix`**: Defines the "Lens" the Judge uses (e.g., `matrix_standard_v1`).
    *   **Ontology Integration**: Dimensions are linked to the **Ontology Registry**.
2.  **`mandate`**: Irrevocable system directives (e.g., "Slow Thinking").
3.  **`rule`**: Operational boundaries (e.g., "No Hallucination").
4.  **`instruction`**: Specific task capabilities (e.g., "Use Toulmin Model").
5.  **`protocol`**: Algorithm for analysis (e.g., "Negative Proof").
6.  **`system_config`**: Global system settings (e.g., `model_registry`).
7.  **`context`**: Dynamic context injection (e.g., Time/Location anchors).
8.  **`output_config`**: Defines schema hoisting rules for reports (e.g., which fields to show in the UI).

---

## 3. Deterministic Hooks (`backend/hooks/`)

Hooks are pure Python functions invoked by agents to perform tasks outside the LLM's capabilities. They are registered in `HOOK_MAPPING`.

### `backend/hooks/security.py`
*   **PII Anonymization:** Deterministic regex and heuristic cleaning.
*   **Input Sanitization:** Injection pattern removal.

### `backend/hooks/validation.py`
*   **Verify Structure:** Enforces minimum length requirements on input fields to prevent "Empty Box" analysis.

### `backend/hooks/archival.py`
*   **RAG Interface:** ChromaDB interface for `RetrievalAgent`.
*   **Similarity Search:** Semantic embedding retrieval.

### `backend/hooks/reporting.py`
*   **XAI Report Generation:** Jinja2 template rendering.
*   **Comparison Matrix:** Logic for side-by-side evaluation diffs.

### `backend/hooks/scoring.py`
*   **Score Normalization:** Standardizes 1-4 scales to 0-100% for radar charts.
*   **Aggregation Logic:** Weighted averages for dimension groups.

### `backend/hooks/linguistics.py`
*   **Pattern Analysis:** Rhetorical device detection.

### `backend/hooks/search.py`
*   **Google Search:** Custom Search API integration for `FactualOverseer`.

### `backend/hooks/metrics.py`
*   **Text Statistics:** Lexical diversity, Flesch-Kincaid scoring.

---

## 4. Execution Engine (`backend/worker.py` & `backend/core/`)

The **Execution Plane** has been modernized in V2.9.

*   **GraphEngine**: The core orchestrator that executes `WorkflowDefinition` DAGs. Handles state transitions via **Event Sourcing** (`TraceEvent`).
*   **TaskRegistry**: A decorator-based registry that maps JSON task keys (e.g., `step_judge`) to Python functions.
*   **Worker Service**: Built on **Arq** (Async Redis Queue) for background processing.
    *   **Logfire Integration**: Full observability traces linked to `execution_id`.
    *   **Resilience**: Intelligent retries and phantom-job handling.
*   **PDF Service**: Generates high-fidelity PDF reports from execution results.

---

## 5. Data Models (`backend/models/`)

All system communication relies on **Pydantic V2** models.

*   **`WorkflowState`**: The Event-Sourced State Container.
    *   **V2.9 Update**: Includes `execution_trace` (Immutable Log) and `context_variables` (Snapshots).
*   **`JudgeOutput`**: Standardized scoring output containing `score_card`, `verdict`, and `dimensions`.
*   **`ReportContext`**: Typed context object for XAI report generation (passed to Jinja2).
*   **`ContextData`**: Structure for Retrieval Agent results (Precedents).

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