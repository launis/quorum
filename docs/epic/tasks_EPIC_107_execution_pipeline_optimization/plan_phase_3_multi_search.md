# EPIC 107 Phase 3: Fact Checker Multi-Search Architecture & Bounded Concurrency

## Source: Epic Phase 3

### 1. Objective
Replace the slow, sequential 1-by-1 Agentic Loop (via `mcp_tool_loop`) in the Fact Checker with a concurrent Batch Multi-Search. Implement `asyncio.TaskGroup` to safely parallelize `Tavily` network calls with native deduplication, while avoiding external API Thundering Herd scenarios.

### 2. Architectural Invariants
- **`00-antigravity-core.md` / `01-python-backend.md` Mandates**:
  - **Zero Legacy Support**: No fallback logic for legacy states.
  - **Central Config Sovereignty**: `tavily_max_concurrent_requests` MUST reside in `backend_v2/settings.py`.
  - **Python 3.14 Concurrency**: Must use `asyncio.TaskGroup`, NOT `asyncio.gather`.
  - **Fail-Fast Typing**: DTOs MUST enforce `ConfigDict(strict=True, extra='forbid')`.
  - **Feature Sovereignty**: Enums MUST reside in `models/enums.py`.
  - **Data Loss Prevention**: Worker tasks must append results to a thread-safe list outside the `TaskGroup` instead of yielding/returning inside it.
  - **Tripartite Architecture**: Business logic, networking, and schema MUST NOT intertwine.
  - **Transient Error Resilience (KI)**: Must classify errors as transient vs. structural before retrying. Structural errors must NOT be retried.
  - **Enum Boundary Parsing**: Any new `StrEnum` crossing boundaries must have a `Lax` alias defined in `enums.py`.

### 3. File Modifications & Sequence

#### A. Settings & Enums (Dependencies & Models)
**`TARGET (Modify)`**: `@[c:\src\quorum\backend_v2\settings.py]`
- Inject `tavily_max_concurrent_requests: Annotated[int, Field(description="Max parallel Tavily search requests")] = 5`.

**`TARGET (Modify)`**: `@[c:\src\quorum\backend_v2\models\enums.py]`
- Add `SearchStatus(StrEnum)` with values: `COMPLETED`, `DLQ_TIMEOUT`, `DLQ_ERROR`.
- Add `LaxSearchStatus = Annotated[SearchStatus, Field(strict=False)]` to the lax type aliases block for Pydantic boundary parsing.

#### B. DTO Boundaries (Models)
**`TARGET (Modify/Create)`**: `@[c:\src\quorum\backend_v2\models\dtos\retrieval.py]` (or equivalent Retrieval DTO module)
- Define `BatchSearchQueryDTO` to receive queries natively from `LLMTaskExecutor.execute_structured_task()`. Enforce `model_config = ConfigDict(strict=True, extra='forbid', frozen=True)`.
- Add `TavilySearchResultDTO` containing `status: LaxSearchStatus` for proper DLQ tracking. Enforce `model_config = ConfigDict(strict=True, extra='forbid', frozen=True)`.

#### C. Service Orchestration (API / Core Logic)
**`TARGET (Modify)`**: `@[c:\src\quorum\backend_v2\services\mcp\tavily_search_client.py]` or dedicated Multi-Search Orchestrator
- **Step 3.1**: Call `LLMTaskExecutor.execute_structured_task()` to extract required queries into `BatchSearchQueryDTO`.
- **Step 3.1b (Deduplication)**: Implement case-folded, whitespace-normalized 1-to-N hash mapping (`Normalized Hash -> List[Original Queries]`).
- **Step 3.2 (Floodgate)**: Create an `asyncio.TaskGroup` bound by a local `asyncio.Semaphore(settings.tavily_max_concurrent_requests)`.
- **Transient Error Routing (RFC7807 & KI)**: Implement Tenacity-based transient error trapping. You MUST classify the error type first. Only retry on transient network anomalies. Structural validation failures (`ValidationError`) must instantly break the retry loop. Append DLQ states (`status=SearchStatus.DLQ_TIMEOUT` or `DLQ_ERROR`) to an external thread-safe `results` list upon exhaustion, accompanied by an RFC7807 structured `logger.error`.
- **Fan-Out Mapping**: Fan out the search results back to all matching original strings for injection.

#### D. Prompt Assembly (Business Logic)
**`TARGET (Modify)`**: `@[c:\src\quorum\backend_v2\seed\seed_data.json]`
- Update the relevant Fact Checker PromptBlock `ai_description`.
- Follow the De-Generator Mandate: Do NOT use XML tags inside the JSON string. Add a Markdown header (e.g., `DLQ TIMEOUT PROTOCOL:`) and instruct explicitly: "If SearchStatus is DLQ_TIMEOUT, you MUST NOT invent or hallucinate the fact. You must explicitly state that the validation timed out."

### 4. Integration Checkpoint Plan
- Schedule an Integration Checkpoint to validate end-to-end extraction and network resilience via UI execution.

### 5. Destructive Operation Inventory
- Replacing recursive MCP Tool Calls inside Fact Checker. `mcp_tavily_search` iterations might be sunset for Fact Checker if completely replaced by batch extraction. (Evaluate and document dropped tools carefully).

### 6. Documentation & Knowledge Item Mandate
- **Docs**: Update `docs/architecture/` with the new Multi-Search Pipeline execution flow.
- **KI**: Create `ki_multi_search_concurrency.md` detailing the thread-safe `TaskGroup` aggregation pattern.

### 7. Testing & Quality Gate Plan
- **Coverage Prerequisite**: Baseline coverage must be recorded.
- **Unit Testing**: Run `uv run python scripts/backend_audit_loop.py backend_v2/ --test`.
- **Integration**: Verify concurrent Thundering Herd limitation using mocked Tenacity HTTP exceptions.

---
# Session Handover Context
Execute this plan as Phase 3 of Epic 107. Follow Tier 2 instructions.
