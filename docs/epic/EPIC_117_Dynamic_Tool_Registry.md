# EPIC 117: Dynamic Tool Registry & SRP Hardening

> [!NOTE]
> **Scientific & Industrial Validation (2025-2026)**
>
> The Model Context Protocol (MCP) has emerged as the de-facto industry standard for decoupled tool integration in LLM agent architectures (Anthropic, 2025). Research from Tampere University on **Clean Agent Architecture (CAA)** validates the separation of core agent workflow logic from volatile tool integrations, enabling tool swaps without refactoring the agent's orchestration brain. Production systems in 2026 universally adopt the **Strategy + Registry** pattern with **Progressive Tool Exposure** to prevent context window saturation. Quorum's existing `ToolDispatcher` partially implements this, but the `mcp_tool_loop.py` orchestrator retains 4 hardcoded `TAVILY_TOOL_ID` references that violate the Open/Closed Principle and prevent zero-config tool registration.
>
> **Key Sources:**
> - Anthropic MCP Specification (2025): Standardized transport layer for runtime tool discovery
> - Tampere University CAA Research (2025): Separation of reasoning engine from execution plugins
> - "Progressive Tool Exposure" pattern (Towards Data Science, 2025): Dynamic loading of task-relevant tool subsets to prevent context saturation
> - Gziolo (2026): Tool routing/filtering via lightweight estimators to reduce "tool space interference"

**Epic ID:** EPIC-117
**Status:** Ready for Implementation
**Priority:** P2 (Architectural Debt / Extensibility)
**Architecture:** Python 3.14+, FastAPI, Pydantic V2, MCP

---

## 1. Goal Description & Background (Objective & Problem Statement)

### Objective

Decouple `mcp_tool_loop.py` from its hardcoded `Tavily` dependency by completing the SRP (Single Responsibility Principle) based `ToolDispatcher` and `BaseTool` architecture. The system already has partial implementation of the Dynamic Tool Registry (Phase 1 complete), but the orchestrator loop still contains direct Tavily-specific control flow that violates the Open/Closed Principle. This Epic completes the decoupling so that new tools (database lookups, calculators, mock tools for testing) can be registered with zero code changes to the orchestrator.

### Problem Statement

The current `mcp_tool_loop.py` orchestrator in @[c:\src\quorum\backend_v2\services\mcp\mcp_tool_loop.py] has the following architectural violations:

1. **Direct Import Coupling** (Line 29): `from backend_v2.services.mcp.tools.tavily import TAVILY_TOOL_ID, TavilyTool` — the orchestrator directly imports a specific tool implementation.
2. **Hardcoded Source Sufficiency Gate** (Line 201): `if is_source_sufficient(source_context) and TAVILY_TOOL_ID not in allowed_tools:` — the gate logic is coupled to a specific tool ID rather than a tool category/capability.
3. **Hardcoded Citation Extraction Routing** (Line 232): `if TAVILY_TOOL_ID in allowed_tools:` — Phase 0 citation extraction is gated on a specific tool rather than a generic "search-capable tools" capability check.
4. **Hardcoded Dispatch** (Line 420): `tool_id=TAVILY_TOOL_ID` — the dispatch call uses a specific tool ID constant instead of routing dynamically from the citation's resolved tool.
5. **Eager Module-Level Instantiation** (Line 52): `DISPATCHER = ToolDispatcher(tools=[TavilyTool()])` — the global dispatcher is constructed with a hardcoded tool list at module import time, preventing DI and test isolation.

### Strategic Scope

This Epic targets the MCP tool execution subsystem exclusively. It does NOT modify the DAG executor, prompt compiler, or LLM client. The blast radius is contained to:
- `backend_v2/services/mcp/` (orchestrator + dispatcher)
- `backend_v2/models/domain/tools.py` (BaseTool abstraction)
- `backend_v2/models/enums.py` (new ToolCapability enum)

---

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (`What We Will REMOVE`)

| Item | Location | Reason |
|------|----------|--------|
| `TAVILY_TOOL_ID` import in orchestrator | @[c:\src\quorum\backend_v2\services\mcp\mcp_tool_loop.py#L29] | Violates Open/Closed Principle; orchestrator must be tool-agnostic |
| `TavilyTool` import in orchestrator | @[c:\src\quorum\backend_v2\services\mcp\mcp_tool_loop.py#L29] | Direct coupling to specific tool implementation |
| Module-level `DISPATCHER` constant | @[c:\src\quorum\backend_v2\services\mcp\mcp_tool_loop.py#L52] | Prevents DI, test isolation, and dynamic tool registration |
| All 4 `TAVILY_TOOL_ID` references in orchestrator | Lines 201, 232, 420 of `mcp_tool_loop.py` | Hardcoded tool routing bypasses the dispatcher pattern |

### Retained SSOT Invariants (`What We Will RETAIN`)

| Invariant | File | Validation |
|-----------|------|------------|
| `BaseTool` ABC contract | @[c:\src\quorum\backend_v2\models\domain\tools.py] | All tool implementations MUST extend `BaseTool` |
| `ToolDispatcher` registry pattern | @[c:\src\quorum\backend_v2\services\mcp\dispatcher.py] | Static eager-loaded dict registry — no change to dispatch API |
| `MCPAuditTrace` output contract | @[c:\src\quorum\backend_v2\models\v2_core.py] | Every tool execution MUST return a standard `MCPAuditTrace` |
| `TavilyTool` implementation | @[c:\src\quorum\backend_v2\services\mcp\tools\tavily.py] | Internal tool logic unchanged; only its registration moves to DI |
| `AliasEngine` opaque ID hydration | @[c:\src\quorum\backend_v2\utils\alias_engine.py] | Tool-returned evidence continues to use `AliasEngine.register()` |
| Phase 1 Dynamic Tool ID Validation | Resolved 2026-07-08 | `SchemaFactory` dynamically creates Pydantic Union types for MCP tools |

### Compliance & Modernity Gates

| # | Quorum 2026 Invariant | Compliance |
|---|----------------------|------------|
| 1 | Zero Legacy State Support | ✅ No backward compatibility required — clean slate |
| 2 | Central Config Sovereignty | ✅ Tool registration moves to DI/settings, not scattered configs |
| 3 | Pydantic Strictness | ✅ `BaseTool` contract enforces `MCPAuditTrace` return type |
| 4 | Cross-Domain DTO Parity | ⚪ N/A — no Flutter DTO changes required (MCP is backend-only) |
| 5 | Static-First Caching Topology | ✅ No prompt changes — tool declarations are runtime-dynamic by design |
| 6 | Python 3.14 Concurrency | ✅ `asyncio.TaskGroup` already used in Phase 0 ensemble extraction |
| 7 | Python-Injected Metadata | ✅ Tool IDs and capabilities are Python-enumerated, never LLM-generated |
| 8 | FinOps & Cache Lifecycle | ✅ No cache topology changes |
| 9 | RFC-7807 Dual-Reporting | ✅ `ToolDispatcher` already uses `logger.error` + `AppException` |
| 10 | Strategy + Registry Pattern | ✅ **This is the core pattern being completed** |
| 11 | Exact String Matching | ✅ `AnchorValidationService.strict_match()` unchanged |

### Producer-Consumer Integration Check

| Producer | Data | Consumer |
|----------|------|----------|
| `ToolDispatcher.execute_tool()` | `MCPAuditTrace` | `mcp_tool_loop.py` → `ScorecardAtomDTO` → Flutter/PDF |
| `BaseTool.declaration` | OpenAI JSON Schema | `ToolDispatcher.get_declarations()` → LLM probe phase |
| `ToolDispatcher.get_search_tools()` (NEW) | `list[str]` tool IDs | `mcp_tool_loop.py` source sufficiency gate |
| `BaseTool.capability` (NEW) | `ToolCapability` enum | `ToolDispatcher` capability-based routing |

---

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 0: Seed Data & Database Prerequisite / Migration

**No seed data or database changes required.** Tool registration is purely a Python-side architectural concern. The existing `seed_data.json` workflow configurations that reference `mcp_tavily_search` as an `allowed_tool` string remain unchanged — the dispatcher resolves these strings at runtime.

### Phase 1: Backend Domain Models & Service Engine Hardening

> **Status: ✅ COMPLETED (2026-07-08)**

Phase 1 has already been implemented and validated:
- `BaseTool` ABC created in @[c:\src\quorum\backend_v2\models\domain\tools.py] with `tool_id`, `declaration`, and `execute()` abstract interface
- `ToolDispatcher` registry created in @[c:\src\quorum\backend_v2\services\mcp\dispatcher.py] with `get_declarations()` and `execute_tool()`
- `TavilyTool(BaseTool)` concrete implementation created in @[c:\src\quorum\backend_v2\services\mcp\tools\tavily.py]
- `SchemaFactory` dynamically creates Pydantic Union types (Literal + Regex) for MCP tools
- Execution Monitor confirmed (exe_9b35a21d33b54b4dbb359d42fd96fb63): Vertex AI calls succeed, MCP loop fetches Tavily documents with dynamic IDs, no validation errors or Rate Limit 429 crashes (Pacing Lock protects 180s+ Semaphore queues)

### Phase 2: Orchestration, Registry & Prompt Compiler Updates

This is the remaining work to fully decouple the orchestrator:

#### 2.1: Add `ToolCapability` Enum

Add a `ToolCapability` enum to @[c:\src\quorum\backend_v2\models\enums.py]:
```python
class ToolCapability(StrEnum):
    """Capability categories for registered MCP tools."""
    WEB_SEARCH = "web_search"
    DATABASE_LOOKUP = "database_lookup"
    COMPUTATION = "computation"
```

#### 2.2: Extend `BaseTool` with Capability Property

Add `capability` abstract property to @[c:\src\quorum\backend_v2\models\domain\tools.py]:
```python
@property
@abstractmethod
def capability(self) -> ToolCapability:
    """The capability category of this tool."""
    pass
```

#### 2.3: Extend `ToolDispatcher` with Capability-Based Queries

Add to @[c:\src\quorum\backend_v2\services\mcp\dispatcher.py]:
```python
def get_tools_by_capability(self, capability: ToolCapability) -> list[str]:
    """Return tool IDs matching a capability category."""
    return [tid for tid, tool in self._registry.items() if tool.capability == capability]

def has_capability(self, capability: ToolCapability, allowed_tools: list[str]) -> bool:
    """Check if any allowed tool provides the specified capability."""
    return any(
        self._registry[tid].capability == capability
        for tid in allowed_tools
        if tid in self._registry
    )
```

#### 2.4: Decouple `mcp_tool_loop.py`

In @[c:\src\quorum\backend_v2\services\mcp\mcp_tool_loop.py]:

1. **Remove Tavily imports** (Line 29): Delete `from backend_v2.services.mcp.tools.tavily import TAVILY_TOOL_ID, TavilyTool`
2. **Remove module-level DISPATCHER** (Line 52): Delete `DISPATCHER = ToolDispatcher(tools=[TavilyTool()])`. Instead, accept `dispatcher: ToolDispatcher` as a function parameter to `execute_tool_loop()` via dependency injection.
3. **Replace source sufficiency gate** (Line 201): Change `TAVILY_TOOL_ID not in allowed_tools` → `not dispatcher.has_capability(ToolCapability.WEB_SEARCH, allowed_tools)`
4. **Replace citation extraction gate** (Line 232): Change `if TAVILY_TOOL_ID in allowed_tools:` → `if dispatcher.has_capability(ToolCapability.WEB_SEARCH, allowed_tools):`
5. **Replace hardcoded dispatch** (Line 420): Change `tool_id=TAVILY_TOOL_ID` → dynamically resolve the first available web search tool from the dispatcher based on the priority defined in `allowed_tools`:
   ```python
   search_tool_ids = set(dispatcher.get_tools_by_capability(ToolCapability.WEB_SEARCH))
   target_tool_id = next((tid for tid in allowed_tools if tid in search_tool_ids), None)
   if not target_tool_id:
       continue # Or handle missing tool gracefully
   
   audit = await dispatcher.execute_tool(tool_id=target_tool_id, ...)
   ```

#### 2.5: Create Dispatcher Factory

Create @[c:\src\quorum\backend_v2\services\mcp\dispatcher_factory.py]:
```python
def create_default_dispatcher() -> ToolDispatcher:
    """Create the default ToolDispatcher with all registered tools.

    Returns:
        ToolDispatcher: Eagerly loaded registry with all production tools.
    """
    from backend_v2.services.mcp.tools.tavily import TavilyTool
    return ToolDispatcher(tools=[TavilyTool()])
```

This factory is the ONLY place in the codebase that imports concrete tool implementations. The dispatcher instance is injected via FastAPI `Depends()` or passed directly in the DAG executor.

#### 2.6: Create `MockTool` for Testing

Create @[c:\src\quorum\backend_v2\services\mcp\tools\mock_tool.py]:
- Implements `BaseTool` with `tool_id = "mock_tool"`, `capability = ToolCapability.WEB_SEARCH`
- Returns a deterministic `MCPAuditTrace` with configurable response data
- Used in unit tests to verify dispatcher routing without network calls

### Phase 3: Frontend Flutter UI & Freezed DTO Synchronization

**No Flutter changes required.** The Dynamic Tool Registry is a backend-only architectural refactor. The `MCPAuditTrace` DTO contract remains unchanged, so the Flutter client continues to consume the same API payload shape. No `flutter_audit_loop.py --build` needed.

### Phase 4: Verification & E2E Integration Gate

See Definition of Done below.

---

## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)

1. **Zero Tavily References in Orchestrator:** The entire `mcp_tool_loop.py` file MUST NOT contain the string `"Tavily"` or `"TAVILY"`. Only `backend_v2/services/mcp/tools/tavily.py` and `backend_v2/services/mcp/dispatcher_factory.py` may reference Tavily.
2. **Forensic Continuity:** Tool dispatch changes MUST NOT alter the `MCPAuditTrace` or `ScorecardAtomDTO` structure. The `<external_evidence>` block format in LLM prompts MUST remain identical.
3. **Fail-Fast (DLQ):** Tool execution MUST NOT fail silently. `AppException` with `ErrorCodes.FETCH_FAILED` MUST be raised on tool errors, as currently implemented.
4. **Opaque ID Hardening:** Tool-returned evidence MUST continue to be injected through `AliasEngine` to produce safe `mcp0`, `mcp1` pseudonyms for the Flutter/PDF UI.
5. **Single-Line Registration:** Adding a new tool to the system MUST require modifying ONLY the `dispatcher_factory.py` file (adding one line to the tools list).
6. **Test Isolation:** Unit tests MUST use `MockTool` via DI injection, never the production `TavilyTool`.

### Automated Unit Tests

```
uv run python scripts/backend_audit_loop.py backend_v2/services/mcp --test
uv run python scripts/backend_audit_loop.py backend_v2/models/domain --test
```

- [x] **Phase 1 (Dynamic Tool ID Validation):** Resolved (2026-07-08). `AliasEngine` cleaned from tool logic. `SchemaFactory` dynamically creates Pydantic Union types (Literal + Regex) for MCP tools in loop. Execution Monitor confirmed (exe_9b35a21d33b54b4dbb359d42fd96fb63): Vertex AI calls succeed, MCP loop fetches Tavily documents with dynamic IDs without validation errors or Rate Limit 429 crashes (Pacing Lock mechanism protects 180s+ Semaphore queues).
- [ ] **Phase 2 (ToolDispatcher Decoupling):** Backend tests pass with the new dispatcher DI: `uv run python scripts/backend_audit_loop.py backend_v2 --test`
- [ ] **Phase 2 (Single-Line Registration):** Registering a new tool (e.g., `MockTool`) requires modifying ONLY `dispatcher_factory.py` — one line added.
- [ ] **Phase 2 (Zero Tavily in Orchestrator):** `grep_search` for "Tavily" in `mcp_tool_loop.py` returns zero results.
- [ ] **Phase 2 (MockTool Integration):** `MockTool` is used in all MCP-related unit tests, providing deterministic responses without network calls.

### Manual Verification Steps

- [ ] Database re-seed (`uv run python backend_v2/seed/run_seed.py local`) succeeds — existing `allowed_tools` references in workflow configs resolve correctly through the dispatcher.
- [ ] Full execution produces identical `MCPAuditTrace` entries and `<external_evidence>` blocks in `llm_debug_prompts.md`.

### MANDATORY Final E2E REST API Verification Gate

```powershell
$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
```

---

## Knowledge Item Mandate

If the `ToolCapability` enum and capability-based routing pattern prove successful, a new Knowledge Item should be created:
- **KI Name:** `dynamic_tool_registry`
- **Summary:** Documents the `BaseTool` → `ToolDispatcher` → `ToolCapability` pattern for registering and routing MCP tools dynamically via capability categories.
