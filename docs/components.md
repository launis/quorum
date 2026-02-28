# System Components (V5.1 / Phase 9 Hardening)

The Cognitive Quorum system is a hybrid architecture composed of **Specialized Agents** (Python Classes), **Deterministic Hooks** (Helper Modules), a **Configuration-Driven Registry** (SSOT Components), and a strictly typed **Server-Driven UI (SDUI)** platform.

> [!IMPORTANT]
> **V5.1 Standard (Strict Pydantic V2 & Zero-Compromise)**
> All components must adhere to **RFC 7807 Fail Fast** principles. Defensive coding (e.g., `getattr(obj, "field", default)`) to hide missing data is strictly forbidden. Agents, Services, and Hooks must trust the Pydantic Schema and raise `AppException` immediately upon data violation.

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
| `JudgeAgent` | `judge.py` | **Polymorphic Scorer**: Final verdict using dynamic `matrix_id`. | `JudgeOutput` |
| `CoachAgent` | `coach.py` | Feedback generation based on Judge's verdict. | `CoachingPlan` |
| `XAIReporterAgent`| `xai.py` | **Explanability Engine**: Final executive summary rendering. | `XAIOutput` |

### 1.1 Python Authority Layer (`post_process`)
The system enforces the **Deterministic Python** rule. LLMs are never trusted with Math, Formatting, or Deduplication. The Agent's wrapper class MUST override `post_process()` to perform these actions deterministically before promoting the raw LLM output to a Domain Model.

---

## 2. SSOT Registry (`backend/seed/seed_data.json`)

The "Mind" of the system is decoupled from Python logic files. Reusable configuration blocks are stored and versioned in `seed_data.json`.

### Component Types
1. **`workflows`**: The Structural DAG (Directed Acyclic Graph) determining step sequences.
2. **`steps`**: The execution instructions mapped to a specific `Agent`.
3. **`matrices`**: Scoring rubrics (e.g., `matrix_standard_v2`) containing heavily typed numerical constraints.
4. **`components`**: Reusable generic text blocks like System Prompts.
5. **`output_configs`**: SDUI rendering maps dictating the structure of final views. The *only* place `ui_hints` are permitted.

---

## 3. Deterministic Hooks (`backend/hooks/`)

Hooks are pure Python functions executed before/after agents to perform tasks outside the LLM's capabilities (RAG, Math, Formatting).

### `backend/hooks/security.py`
* **Input Sanitization:** Injection pattern removal.
* **Fail Fast:** Raises `AppException(400)` if mandatory input text is missing or explicitly toxic.

### `backend/hooks/validation.py`
* **Schema Enforcement:** Validates `WorkflowInputs` integrity before deep execution.

### `backend/hooks/reporting.py`
* **XAI Report Generation:** Jinja2 PDF template rendering using strictly typed `ReportContext`.

### `backend/hooks/scoring.py`
* **Relative Penalties:** Applies percentage-based deductions (Security, Post-Hoc).
* **Safety Clamp**: Clamps negative scores to `scale_min` to prevent downstream Pydantic validation crashes.

### `backend/hooks/search.py`
* **Vertex AI Search:** Grounding-based search integration.
* **Fail Fast**: If enabled but missing keys (`API_KEY`, `CX_ID`), raises `AppException(SEARCH_CONFIG_ERROR)` to alert the user, rather than silently failing.

---

## 4. Execution Engine (`backend/core/` & `backend/api/`)

The Core execution path relies entirely on typed components.

* **API Layer**: `backend/api/routes/*.py`. Pure IO. Fast routing and dependency injection.
* **Service Layer**: Unites Domain constraints. The API calls the Service, the Service validates the constraints, and triggers the repo or queue.
* **GraphEngine**: The core orchestrator that executes `WorkflowDefinition` DAGs. Creates the immutable `WorkflowState` log.
* **Transformers (BFF)**: `backend/api/transformers/`. Responsible for extracting raw domain state from `GraphEngine` records and mapping it to lean `View Models` (SDUI Enums) for the frontend.

---

## 5. View Models (Frontend Mapping) & I18N

To adhere to the **No-String Mandate**, the backend strictly passes **Keys** rather than user-visible text. 
* The `profiler.py` and `logician.py` output heavy nested reasoning data.
* The `ReportTransformer` strips out internal LLM reasoning tokens and formats properties like `say_do_gap` into Enums like `GAP_NONE`.
* **Flutter (`client_app`)** executes dynamic matching of these Enum labels against `app_fi.arb` dictionaries for robust UI presentation independent of backend deployments.