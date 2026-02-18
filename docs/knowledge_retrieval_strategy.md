# Knowledge Base, Search & Retrieval Strategy (V3.2)

## 1. Core Concepts

The Cognitive Quorum uses a **Hybrid Information Architecture** that combines internal long-term memory (Knowledge Base) with real-time external intelligence (Google Search).

### Knowledge Base
The **Knowledge Base** is the system's long-term memory. Unlike a traditional database (SQL) which stores structured rows, the Knowledge Base stores **Unstructured Data** (documents, PDFs, chat logs) converted into mathematical vectors.

-   **Vector Store**: The underlying engine (e.g., ChromaDB, PGVector) that allows searching by *meaning* rather than exact keywords.
-   **Embeddings (Future Roadmap)**: The process of converting text into a vector (e.g., `[0.1, -0.5, ...]`) representing semantic meaning. We plan to use high-fidelity models (e.g., OpenAI `text-embedding-3-small` or Vertex `gecko`) in Phase 3. Currently, the system relies on standard ingestion without vectorization.

### External Search
**External Search** provides real-time validation and fact-checking using the Google Search API. This is critical for verify claims against current events or data not present in the static Knowledge Base.

---

## 2. Architecture & Implementation

The system is built on a **Service-Oriented Architecture (SOA)** ensuring separation of concerns between ingestion, storage, and retrieval.

### A. Ingestion Pipeline (Non-Blocking)
Data ingestion is a CPU-intensive process handled asynchronously to keep the API responsive.

1.  **Job Creation**: The API (`POST /ingest`) creates a `job_id` and immediately returns it. The actual work happens in a `BackgroundTasks` runner.
2.  **Threadpool Offloading**: Heavy parsing (DOCX extraction, Regex matching) is offloaded to a threadpool (`run_in_threadpool`) to avoid blocking the main asyncio event loop.
3.  **Progress Tracking**: A `SimpleTracker` updates job status (`stage`, `percent`) in real-time.

### B. Dynamic Model Strategy
The Knowledge Base uses the **Agent Registry** to resolve models at runtime.

*   **Strategy-Based**: Users select a strategy (e.g., `fast`, `deep`).
*   **Fail Fast**: If the Registry is unavailable, the system raises `ServiceUnavailableError` (Error Code: `SERVICE_DEPENDENCY_MISSING`) rather than silently falling back.

### C. The Sidebar Pattern
To prevent hallucinations, we strictly enforce the **Sidebar Pattern** for Information Retrieval.

*   **Rule**: The `AnalystAgent` (who structures the argument) does **NOT** perform searches itself.
*   **Mechanism**: The `RetrievalAgent` (Knowledge) and `Overseer` (Role/Hook) run **parallel** to the Analyst or as pre-computation steps.
*   **Rationale**: If the Analyst searches for "Why is X true?", it will find confirmation bias. By keeping the Analyst "blind" to the "Correct Answer", we force it to rely on the user's input, which the **Falsifier** and **Overseer** then attack with independent evidence.

### D. Architectural Resilience (Lazy Inflation)
To handle evolving schemas while maintaining seamless access to historical data, the `RetrievalAgent` implements the **Lazy Inflation Pattern**.
*   **Storage**: Historical data (`db.json`) may contain older schema versions or raw dictionaries.
*   **Mechanism**: When the agent reads `results` (union type), it actively checks type. If raw `dict` is found, it attempts Just-In-Time inflation to `WorkflowState`.
*   **Benefit**: This prevents "Brittle Model" crashes on legacy data while enforcing strict typing for new execution.

---

## 3. Google Search Integration (V3.2)

The `Overseer` functionality is now implemented as a **Role** (in `PanelAgent`) and a **Hook** (`execute_google_search`).

### Configuration Gating (`enable_vertex_search`)
To support diverse deployment environments (e.g., Local Dev vs. Cloud Prod), access to external Google Search is strictly gated via `backend.settings`.
*   **Flag**: `enable_vertex_search` (Boolean).
*   **Disabled (Default)**: If `False`, the search hook gracefully returns an empty `SearchResult` list.
*   **Enabled (True)**: If `True`, the hook *must* have valid credentials (Project ID, Model ID).
    *   **Fail Fast**: If enabled but misconfigured, the hook raises `ConfigurationError`.

### Workflow Integration
1.  **Trigger**: The Analyst or Panel requests external verification.
2.  **Query Generation**: The LLM generates targeted search queries (e.g., "Finland GDP 2024 official interpretation").
3.  **Execution (Hook)**: Calls `VertexAISearchTool` via `backend/hooks/search.py`.
4.  **JSON Safety**: Results are sanitized into a strict `SearchResultItem` Pydantic model (`{"title": "...", "snippet": "...", "link": "..."}`) to prevent prompt injection.
5.  **Injection**: The results are injected into the context via the `{{SEARCH_RESULT}}` variable.

### Grounding Rules
To prevent "hallucination laundering" (where the AI invents a search result), we enforce strict grounding:

*   **Citation Mandate**: Every claim made by the Overseer must validly cite a specific search result or Knowledge Base chunk.
*   **URL Verification**: The system checks if the cited URL actually exists in the search payload.

---

## 4. Implementation in Workflow

### A. The Retrieval Agent (`step_retrieval`)
1.  **User Input**: "What was said about the Q3 strategy?"
2.  **Retrieval Step**: queries Vector Store -> returns top 5 chunks.
3.  **Context Injection**: Injects chunks into the prompt variable `{{ knowledge_context }}`.

### B. The Bibliography Problem
**Challenge**: Citations like `[1]` are meaningless if the Reference List is in a different chunk.
**Solution**: `BibliographyParser` scans for reference lists during ingestion and **injects** the full reference (`[1] Author, 2024`) into the metadata of every chunk that cites `[1]`.

---

## 5. API Interfaces

### Ingestion
-   **Endpoint**: `POST /api/v1/config/knowledge/ingest`
-   **Payload**: `file`, `language` ("fi"|"en"), `model_strategy`.
-   **Response**: `{"job_id": "uuid"}`.

### Management
-   **Endpoint**: `DELETE /api/v1/config/knowledge/reset`
-   **Description**: Resets the entire Knowledge Base.

### Config Tools
-   **Concept Extraction**: `POST /api/v1/tools/extract-concepts`
-   **Citation Lookup**: `POST /api/v1/tools/citation-lookup`
