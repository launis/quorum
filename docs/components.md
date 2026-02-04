# Workflow Components (V2.6)

The system is composed of **Specialized Agents** (Python Classes), **Deterministic Hooks** (helper modules), and a **Configuration-Driven Registry** (JSON Components).

## 1. Specialized Agents (`backend/agents/`)

Agents in V2.6 are specialized classes inheriting from `BaseAgent`, designed to be "Thin Wrappers" around configuration and logic.

| Agent Class | File | Responsibility | Schema |
| :--- | :--- | :--- | :--- |
| `GuardAgent` | `guard.py` | Input sanitization, PII check, prompt injection defense. | `GuardResult` |
| `AnalystAgent` | `analyst.py` | Data ingestion and preliminary analysis. | `AnalysisResult` |
| `ProfilerAgent` | `profiler.py` | User intent profiling and bias detection. | `ProfilerAnalysis` |
| `LogicianAgent` | `logician.py` | Toulmin argument mapping and logical structure audit. | `ArgumentaatioAnalyysi` |
| `LogicalFalsifierAgent` | `critics.py` | Stress-testing arguments (Devil's Advocate). | `FalsifiointiAuditointi` |
| `CausalAnalystAgent` | `critics.py` | Causal graph generation. | `KausaalinenAuditointi` |
| `PerformativityDetectorAgent` | `critics.py` | Identifies performativity and pretense. | `PerformatiivisuusAuditointi` |
| `FactualOverseerAgent` | `critics.py` | Fact-checking (Google Search) and ethical oversight. | `EtiikkaJaFakta` |
| `PanelAgent` | `panel.py` | **[Fused]** Simulates a parallel panel of experts. | `PanelAudit` |
| `JudgeAgent` | `judge.py` | **[Polymorphic]** Final verdict using dynamic `matrix_id` from config. | `EvaluationResult` |
| `CoachAgent` | `coach.py` | Feedback generation based on Judge's verdict. | `CoachFeedback` |
| `XAIReporter` | `xai.py` | Generates human-readable MD reports from `EvaluationResult`. | `XAIReport` |

---

## 2. Components Registry (`db.json` / `components`)

In V2.6, the "Mind" of the system is decoupled from Python code. Reusable blocks are stored in the `components` dictionary in `db.json`.

### Component Types
1.  **`evaluation_matrix`**: Defines the "Lens" the Judge uses (e.g., `matrix_standard_v1`, `matrix_cognitive_v2`). Contains:
    *   `role_description`: Persona for the Judge.
    *   `criteria`: List of dimensions (e.g., "Agency", "Synthesis").
    *   `scale`: Scoring range and anchors.
2.  **`mandate`**: Irrevocable system directives (e.g., "Slow Thinking").
3.  **`rule`**: Operational boundaries (e.g., "No Hallucination").
4.  **`instruction`**: Specific task capabilities (e.g., "Use Toulmin Model").
5.  **`protocol`**: Algorithm for analysis (e.g., "Negative Proof").

### Example Component (Matrix)
```json
"matrix_cognitive_v2": {
  "type": "evaluation_matrix",
  "content": {
    "name": "Cognitive Quorum Unified Matrix",
    "role_description": "You are the Chief Cognitive Judge.",
    "scale": {"min": 1, "max": 4},
    "criteria": [
      {
        "id": "agency",
        "label": "Strateginen Ohjaus",
        "anchors": {
            "1": "Passenger (Passive)",
            "4": "Architect (Strategic)"
        }
      }
    ]
  }
}
```

---

## 3. Deterministic Hooks (`backend/hooks/`)

Hooks are pure Python functions invoked by agents to perform tasks outside the LLM's capabilities.

### `backend/hooks/security.py`
*   **PII Anonymization:** Uses **Microsoft Presidio** to detect and mask names, emails, and phone numbers.
*   **Input Sanitization:** Removes invisible characters and potential injection patterns.

### `backend/hooks/archival.py`
*   **RAG Interface:** Connects to the **Vector Database (ChromaDB)**.
*   **Similarity Search:** Retrieves relevant case laws or precedents based on semantic embeddings.

### `backend/hooks/linguistics.py`
*   **Pattern Analysis:** Detects performative language and rhetorical devices.

### `backend/hooks/search.py`
*   **Google Search:** Real-time fact-checking via Custom Search API.

### `backend/hooks/metrics.py`
*   **Text Statistics:** Calculates lexical diversity, reading level (Flesch-Kincaid).
*   **Structure Audit:** Counts paragraph and sentence structures.

---

## 4. Worker Service (`backend/worker.py`)

The **Worker Service** (Execution Plane) is the heavy-lifting engine of Quorum.

*   **Technology**: Built on **Arq** (Async Redis Queue) and monitored via **Logfire**.
*   **Role**: Executes the `execute_workflow_task` function.
*   **Resilience**: Handles retries, timeout management, and graceful shutdowns.
*   **Scalability**: Multiple worker instances can consume from the same Redis queue (Horizontal Scaling).

---

## 5. Data Models (`backend/models/`)

All components communicate using **Pydantic V2** models.

*   **`WorkflowState`**: The MONOLITHIC state object passed between agents.
    *   **V2.6 Update:** Stores `audit_results` (Dictionary of EvaluationResults) instead of just single-step outputs, enabling multi-matrix audits.
*   **`EvaluationResult`**: The standardized output for any Judging process, containing `dimensions` (List[DimensionResultItem]) and `score`.

---

## 6. LLM Provider (`backend/llm/`)

A centralized adapter pattern for model access.
*   **Supported Models:** Google Gemini 1.5 (Flash/Pro) via **Regional Discovery** (Hamina / europe-north1).
*   **Features:** **Strict JSON Mode** enforcement, **Reasoning Token** extraction ("Show Your Work"), and exponential backoff retries.