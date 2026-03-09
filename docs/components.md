# System Components & Hooks (V5.1 / Phase 9 Hardening)

The Cognitive Quorum system is a hybrid architecture composed of **Specialized Agents** (Python Classes), **Deterministic Hooks** (Helper Modules), a **Configuration-Driven Registry** (SSOT Components), and a strictly typed **Server-Driven UI (SDUI)** platform.

> [!IMPORTANT]
> **Enterprise V2 Standard (Strict Pydantic V2 & Zero-Deploy)**
> Järjestelmä siirtää kaiken kognitiivisen liiketoimintalogiikan, datareitityksen, arvioinnin kalibroinnin ja käyttöliittymän piirtosäännöt tietokantaan (Zero-Deploy). All components must adhere to **RFC 7807 Fail Fast** principles. Defensive coding (e.g., `getattr(obj, "field", default)`) to hide missing data is strictly forbidden. Agents, Services, and Hooks must trust the Pydantic Schema and raise `AppException` immediately upon data violation.

---

## 1. Specialized Agents (`backend/agents/`)

Agents in V5.1 are specialized classes inheriting from `BaseAgent`, designed to be "Thin Wrappers" around configuration and specific Agent constraints. They are executed by the `GraphEngine`. All agents return strictly typed **Pydantic V2** models (`strict=True, extra="ignore"`).

| Agent Class | File | Responsibility | Output Schema (Domain) |
| :--- | :--- | :--- | :--- |
| `GuardAgent` | `guard.py` | Input sanitization, PII check, prompt injection defense. | `GuardOutput` |
| `AnalystAgent` | `analyst.py` | Data ingestion and preliminary context engineering audit. | `AnalystOutput` |
| `InteractionAgent`| `interaction.py`| Analyzes user dependency, strategy (Zero vs Few-Shot). | `InteractionAnalysis` |
| `ProfilerAgent` | `profiler.py` | User intent profiling and cognitive bias detection. | `ProfilerMetrics` |
| `LogicianAgent` | `logician.py` | Toulmin argument mapping and logical structure audit. | `LogicianOutput` |
| `FalsifierAgent` | `falsifier.py` | Stress-testing arguments (Devil's Advocate). | `FalsifierOutput` |
| `CausalAgent` | `causal.py` | Impact verification (Did user input *cause* improvement?).| `CausalAnalysis` |
| `OverseerAgent` | `overseer.py` | Protocol compliance and system logic monitoring. | `OverseerData` |
| `PanelAgent` | `panel.py` | **Unified Parallel Critic**: Orchestrates sub-critics in parallel. | `PanelOutput` |
| `JudgeAgent` | `judge.py` | **Polymorphic Scorer**: Final verdict using dynamic `matrix_id`, calibrated stricness (0-100), and forcing Theory-Grounded XAI justifications. | `JudgeOutput` |
| `CoachAgent` | `coach.py` | Feedback generation based on Judge's verdict. | `CoachingPlan` |
| `XAIReporterAgent`| `xai.py` | **Explanability Engine**: Final executive summary rendering. | `XAIFlatReportDTO` |

### 1.1 Python Authority Layer (`post_process`)
The system enforces the **Deterministic Python** rule. LLMs are never trusted with Math, Formatting, or Deduplication. The Agent's wrapper class MUST override `post_process()` to perform these actions deterministically before promoting the raw LLM output to a Domain Model.

---

## 2. SSOT Registry (`backend/seed/seed_data.json`)

The "Mind" of the system is decoupled from Python logic files. Reusable configuration blocks are stored and versioned in `seed_data.json`.

### Component Types (Zero-Deploy)
1. **`workflows`**: The Structural DAG (Directed Acyclic Graph) determining step sequences and Semantic Data Flow mapping.
2. **`steps`**: The execution instructions mapped to a specific `Agent`.
3. **`matrices`**: Scoring rubrics (e.g., `matrix_standard_v2`) containing heavily typed numerical constraints, **Strictness parameters (0-100)**, and Theory URL groundings.
4. **`components`**: Reusable generic text blocks like System Prompts.
5. **`output_configs`**: SDUI rendering maps dictating the structure of final views. The *only* place `ui_hints` are permitted.

---

## 3. Deterministic Hooks System (`backend/hooks/`)

**Hooks** are deterministic Python functions executed by the `GraphEngine` at specific points in a step's lifecycle. They provide a mechanism for:
1. **Input Pre-processing (Pre-hooks)**: executed before the Agent's LLM call.
2. **Output Post-processing (Post-hooks)**: executed after the Agent's handler returns.
3. **Deterministic Logic**: Pure code execution without LLM variance.
4. **External Integrations**: Google Search, Database Archival, etc.

> [!IMPORTANT]
> **Strict DTO Mandate (V5.1)**:
> 1. All hooks must output strict **Pydantic V2 Models** (`ConfigDict(strict=True, extra="ignore")`). Loose dictionaries (`aux_data`) are strictly forbidden.
> 2. All hooks must **Fail Fast** using `AppException` with a specific `ErrorCode` (RFC 7807 compliance). `try-except pass` is banned.

### 3.1 Hook Architecture

#### A. Blackboard Pattern (`context_variables`)
Hooks interact with the `WorkflowState` primarily through `context_variables`.
* **Read**: Hooks read input data from `state.context_variables`.
    * **Strict Access**: Use `state.get_context(ModelType)` or `inflate()` to ensure type safety. DO NOT access raw dicts.
* **Write**: Hooks return a **new** state with updated `context_variables` containing their Pydantic result model.
* **Immutability**: `WorkflowState` is frozen. Hooks use `state.model_copy(update=...)`.

#### B. Strict Pydantic Models (`backend/models/domain.py`)
Every hook typically has a corresponding result model:

| Hook | Result Model | Description |
| :--- | :--- | :--- |
| `sanitize_text` | `SanitizationResult` | Redacted inputs & threat logs |
| `detect_performative_patterns` | `LinguisticsResult` | Detected "AI-ese" patterns |
| `execute_google_search` | `SearchResult` | Structured search items |
| `verify_structure` | `ValidationResult` | Pass/Fail status & errors |
| `apply_scoring_logic` | `ScoringResult` | Calculated totals & penalties |
| `generate_report` | `ReportResult` | Final Markdown & metadata |

#### C. Zero-Fallback Principle (Fail Fast)
Hooks do **not** fail silently.
* If a configuration (`settings.SEARCH_ENGINE_ID`) is missing and required, they raise `AppException`.
* If a critical dependency is unavailable, they raise `ErrorCode.SERVICE_DEPENDENCY_MISSING`.

### 3.2 Hook Reference

#### 1. Security Hooks (`backend/hooks/security.py`)
* **`sanitize_text_hook` (Pre-hook)**
  * **Action**: Scans inputs for PII (SSN, Phone) and Banned Phrases.
  * **Inputs**: Accesses `WorkflowInputs` object strictly.
  * **Behavior**: Raises `AppException` (403) for critical threats.

#### 2. Search Hooks (`backend/hooks/search.py`)
* **`execute_google_search` (Post-hook for Analyst)**
  * **Action**: Executes Google Custom Search based on Analyst hypotheses.
  * **Gating**: Respects `enable_vertex_search` setting. Gracefully returns empty results ONLY if explicitly disabled by the user setting.
  * **Fail Fast**: If enabled but missing keys (`API_KEY`, `CX_ID`), it strictly raises an `AppException(SEARCH_CONFIG_ERROR)` to alert the user.
  * **Output**: `SearchResult` containing list of `SearchResultItem`.

#### 3. Scoring Hooks (`backend/hooks/scoring.py`)
* **`apply_scoring_logic` (Post-hook)**
  * **Action**: Aggregates scores from all judges and applies deterministic penalties (Security/Logic).
  * **Safety Clamp**: Ensures scores never drop below `scale_min` (e.g., 0.1) to prevent Pydantic validation errors (`>= 0.1`) that would crash the pipeline.
  * **Output**: `ScoringResult`. **Overwrites** `JudgeOutput` with authoritative scores.

#### 4. Reporting Hooks (`backend/hooks/reporting.py`)
* **`generate_report` (Post-hook)**
  * **Action**: Renders the final PDF/Markdown report using Jinja2 templates.
  * **Strict Context**: Instantiates `ReportContext` Pydantic model. Fails immediately if domain data is missing.
  * **Output**: `ReportResult` (wraps the generated Markdown).

#### 5. Integrity Hooks (`backend/hooks/integrity.py`)
* **`verify_citation_integrity` (Post-hook)**
  * **Action**: Verifies that quotes used by Analyst and Judges actually exist in the source texts.
  * **Fail Fast**: Raises `AppException` if the LLM hallucination rate > 50%.
  * **Output**: `CitationAudit` (logged in metadata).

### 3.3 Developer Guide: Creating a New Hook
1. **Define Model**: Create a result model in `backend/models/domain.py` with `strict=True`.
2. **Implement Hook**: Create a function in `backend/hooks/`.
    ```python
    def my_hook(state: WorkflowState) -> WorkflowState:
        # 1. Validate Input (Fail Fast)
        inputs = state.context_variables.get("inputs")
        if not inputs:
            raise AppException(message="Missing input data.", error_code=ErrorCodes.VALIDATION_FAILED)

        # 2. Logic (Deterministic)
        result = MyHookResult(value=100)

        # 3. Update State (Immutable)
        new_context = state.context_variables.copy()
        new_context["my_hook_result"] = result
        return state.model_copy(update={"context_variables": new_context})
    ```
3. **Register**: Add it to `HOOK_MAPPING` in `backend/core/engine.py`.

---

## 4. Execution Engine (`backend/core/` & `backend/api/`)

The Core execution path relies entirely on typed components.

* **API Layer**: `backend/api/routes/*.py`. Pure IO. Fast routing and dependency injection.
* **Service Layer**: Unites Domain constraints. The API calls the Service, the Service validates the constraints, and triggers the repo or queue.
* **GraphEngine**: The core orchestrator that executes `WorkflowDefinition` DAGs. Creates the immutable `WorkflowState` log.
* **Transformers (BFF)**: `backend/api/transformers/`. Responsible for extracting raw domain state from `GraphEngine` records and mapping it to lean `View Models` (SDUI Enums) for the frontend.

---

## 5. View Models (Frontend Mapping), I18N, & Late-Binding Omni-Channel

To adhere to the **No-String Mandate**, the backend strictly passes **Keys** rather than user-visible text. 
* The `profiler.py` and `logician.py` output heavy nested reasoning data.
* The `ReportTransformer` strips out internal LLM reasoning tokens and formats properties like `say_do_gap` into Enums like `GAP_NONE`.
* **Late-Binding Omni-Channel**: Datan prosessointi pidetään yhtenäisenä koneluettavana JSON-rakenteena läpi koko prosessin, ja se purkautuu vasta aivan viimeisessä adapterikerroksessa kolmeen eri muotoon (Flutter SDUI Compound Widgets, Backend Jinja2 PDF, ja litteä CSV/Flat-File vienti).
* **Flutter (`client_app`) SDUI** executes dynamic matching of these Enum labels against `app_fi.arb` dictionaries for robust UI presentation independent of backend deployments.