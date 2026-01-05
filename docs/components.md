# Workflow Components (V2.5)

The system is composed of **Specialized Agents** (Python Classes) and **Deterministic Hooks** (helper modules).

## 1. Specialized Agents (`backend/agents/`)

Unlike V1, which used generic agents, V2.5 involves specialized classes inheriting from `BaseAgent`.

| Agent Class | File | Responsibility | Schema |
| :--- | :--- | :--- | :--- |
| `GuardAgent` | `guard.py` | Input sanitization, PII check, prompt injection defense. | `GuardResult` |
| `AnalystAgent` | `analyst.py` | Data ingestion and preliminary analysis. | `AnalysisResult` |
| `ProfilerAgent` | `profiler.py` | User intent profiling and bias detection. | `ProfilerAnalysis` |
| `LogicianAgent` | `logician.py` | Toulmin argument mapping and logical structure audit. | `ArgumentaatioAnalyysi` |
| `FalsifierAgent` | `falsifier.py` | Stress-testing arguments (Devil's Advocate). | `FalsifiointiAuditointi` |
| `CausalAgent` | `causal.py` | Causal graph generation and DoWhy refutation. | `KausaalinenAuditointi` |
| `PanelAgent` | `panel.py` | Simulates a panel of experts (Logic + Causal + Ethics). | `PanelAudit` |
| `JudgeAgent` | `judge.py` | Final verdict and scoring. | `JudgeVerdict` |
| `CoachAgent` | `coach.py` | Feedback generation without judging. | `CoachFeedback` |
| `XAIReporter` | `xai.py` | Generates human-readable MD reports. | `XAIReport` |

## 2. Deterministic Hooks (`backend/hooks/`)

Hooks are pure Python functions invoked by agents to perform tasks outside the LLM's capabilities.

### `backend/hooks/security.py`
*   **PII Anonymization:** Uses **Microsoft Presidio** to detect and mask names, emails, and phone numbers.
*   **Input Sanitization:** Removes invisible characters and potential injection patterns.

### `backend/hooks/archival.py`
*   **RAG Interface:** Connects to the **Vector Database (ChromaDB)**.
*   **Similarity Search:** Retrieves relevant case laws or precedents based on semantic embeddings.

### `backend/hooks/causal.py`
*   **DoWhy Integration:** Performs formal causal inference.
*   **Refutation Tests:** Runs Placebo and Random Subset tests to validate causal claims.

### `backend/hooks/search.py`
*   **Google Search:** Real-time fact-checking via Custom Search API.

### `backend/hooks/metrics.py`
*   **Text Statistics:** Calculates lexical diversity, reading level (Flesch-Kincaid).
*   **Structure Audit:** Counts paragraph and sentence structures.

## 3. Worker Service (`backend/worker.py`)

The **Worker Service** (Execution Plane) is the heavy-lifting engine of Quorum V2.5.

*   **Technology**: Built on **Arq** (Async Redis Queue) and monitored via **Logfire**.
*   **Role**: Executes the `execute_workflow_task` function.
*   **Resilience**: Handles retries, timeout management, and graceful shutdowns.
*   **Scalability**: Multiple worker instances can consume from the same Redis queue (Horizontal Scaling).

## 4. Data Models (`backend/models/`)

All components communicate using **Pydantic V2** models.

*   **`WorkflowState`**: The monolithic state object passed between agents. Implements **Optimistic Locking** (`version` field) for safe concurrent updates.
*   **`Domain Models`**: Specialized schemas (e.g., `JudgeVerdict`, `PanelAudit`) used for LLM structured output.

## 5. LLM Provider (`backend/llm/`)

A centralized adapter pattern for model access.
*   **Supported Models:** Google Gemini 2.5 (Flash/Pro) via **Regional Discovery** (Hamina / europe-north1).
*   **Features:** **Strict JSON Mode** enforcement, **Reasoning Token** extraction ("Show Your Work"), and exponential backoff retries.