# System Components (V2.9)

The Cognitive Quorum system is a hybrid architecture composed of **Specialized Agents** (Python Classes), **Deterministic Hooks** (Helper Modules), a **Configuration-Driven Registry** (JSON Components), and a **Server-Driven UI (SDUI)** platform (Cognitive Studio).

---

## 1. Specialized Agents (`backend/agents/`)

Agents in V2.9 are specialized classes inheriting from `BaseAgent`, designed to be "Thin Wrappers" around configuration and logic. They are registered in the `TaskRegistry` and executed by the `GraphEngine`.

| Agent Class | File | Responsibility | Output Schema |
| :--- | :--- | :--- | :--- |
| `GuardAgent` | `guard.py` | Input sanitization, PII check, prompt injection defense. | `GuardResult` |
| `AnalystAgent` | `analyst.py` | Data ingestion and preliminary context engineering audit. | `AnalysisResult` |
| `InteractionAnalystAgent` | `interaction.py` | **[New]** Analyzes user dependency, strategy (Zero/Few-Shot), and control ratio. | `InteractionMetrics` |
| `ProfilerAgent` | `profiler.py` | User intent profiling and cognitive bias detection. | `ProfilerAnalysis` |
| `LogicianAgent` | `logician.py` | Toulmin argument mapping and logical structure audit. | `ArgumentaatioAnalyysi` |
| `LogicalFalsifierAgent` | `critics.py` | Stress-testing arguments (Devil's Advocate) & Critical Loop audit. | `FalsifiointiAuditointi` |
| `CausalAnalystAgent` | `critics.py` | Impact verification (Did user input *cause* improvement?). | `KausaalinenAuditointi` |
| `PerformativityDetectorAgent` | `critics.py` | Identifies "Illusion of Control" and performative language. | `PerformatiivisuusAuditointi` |
| `FactualOverseerAgent` | `critics.py` | Fact-checking (Google Search) and hallucination management. | `EtiikkaJaFakta` |
| `ArchivistAgent` | `archivist.py` | **[New]** Best practices audit & precedent fetching. | `ArchivistResult` |
| `RetrievalAgent` | `retrieval.py` | **[New]** Organizational grounding and context retrieval (Precedents). | `ContextData` |
| `PanelAgent` | `panel.py` | **[Fused]** Simulates a parallel panel of experts (Critics fused). | `PanelAudit` |
| `JudgeAgent` | `judge.py` | **[Polymorphic]** Final verdict using dynamic `matrix_id` from config. | `EvaluationResult` |
| `CoachAgent` | `coach.py` | Feedback generation based on Judge's verdict (Driver's License model). | `CoachFeedback` |
| `XAIReporterAgent` | `xai.py` | Generates human-readable MD reports & Comparison Matrices. | `XAIReport` |

---

## 2. Components Registry (`db.json` / `components`)

The "Mind" of the system is decoupled from Python code. Reusable blocks are stored in the `components` dictionary in `db.json` (or SQL database).

### Component Types
1.  **`evaluation_matrix`**: Defines the "Lens" the Judge uses (e.g., `matrix_standard_v1`, `matrix_cognitive_v2`).
    *   **Ontology Integration**: Dimensions are now linked to the **Ontology Registry** for cross-matrix consistency.
2.  **`mandate`**: Irrevocable system directives (e.g., "Slow Thinking").
3.  **`rule`**: Operational boundaries (e.g., "No Hallucination").
4.  **`instruction`**: Specific task capabilities (e.g., "Use Toulmin Model").
5.  **`protocol`**: Algorithm for analysis (e.g., "Negative Proof").
6.  **`system_config`**: **[New]** Global system settings and toggles.
7.  **`context`**: **[New]** Dynamic context injection (e.g., Time/Location anchors).
8.  **`output_config`**: **[New]** Defines schema hoisting rules for reports.

---

## 3. Deterministic Hooks (`backend/hooks/`)

Hooks are pure Python functions invoked by agents to perform tasks outside the LLM's capabilities.

### `backend/hooks/security.py`
*   **PII Anonymization:** Microsoft Presidio integration.
*   **Input Sanitization:** Injection pattern removal.

### `backend/hooks/archival.py`
*   **RAG Interface:** ChromaDB vector search.
*   **Similarity Search:** Semantic embedding retrieval.

### `backend/hooks/reporting.py` **[New]**
*   **XAI Report Generation:** Jinja2 template rendering (`report_template.jinja2`).
*   **Comparison Matrix:** Logic for side-by-side evaluation diffs (Dual-Judge support).

### `backend/hooks/scoring.py` **[New]**
*   **Score Normalization:** Standardizes 1-4 scales to 0-100% for radar charts.
*   **Aggregation Logic:** Weighted averages for dimension groups.

### `backend/hooks/linguistics.py`
*   **Pattern Analysis:** Rhetorical device detection.

### `backend/hooks/search.py`
*   **Google Search:** Custom Search API integration for `FactualOverseer`.

### `backend/hooks/metrics.py`
*   **Text Statistics:** Lexical diversity, Flesch-Kincaid.

---

## 4. Execution Engine (`backend/worker.py` & `backend/core/`)

The **Execution Plane** has been modernized in V2.9.

*   **GraphEngine**: The core orchestrator that executes `WorkflowDefinition` DAGs. Handles state transitions (`WorkflowState`) and error propagation.
*   **TaskRegistry**: A decorator-based registry (`@TaskRegistry.register_task`) that maps JSON task keys (e.g., `step_judge`) to Python functions.
*   **Worker Service**: Built on **Arq** (Async Redis Queue) for background processing.
    *   **Logfire Integration**: Full observability traces linked to `execution_id`.
    *   **Resilience**: Intelligent retries and phantom-job handling.
*   **PDF Service**: Generates high-fidelity PDF reports from execution results.

---

## 5. Data Models (`backend/models/`)

All system communication relies on **Pydantic V2** models.

*   **`WorkflowState`**: The Monolithic State Object.
    *   **V2.9 Update**: Includes `audit_results` (Dict of Evaluations), `aux_data` (Hook outputs), and generic `step_*` dynamic fields.
*   **`EvaluationResult`**: Standardized scoring output containing `dimensions` and `critical_findings`.
*   **`ReportContext`**: **[New]** Typed context object for XAI report generation (passed to Jinja2).
*   **`ContextData`**: **[New]** Structure for Retrieval Agent results (Precedents).

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