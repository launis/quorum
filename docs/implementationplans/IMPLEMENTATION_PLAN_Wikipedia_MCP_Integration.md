> **STATUS: PENDING / ODOTTAA TOTEUTUSTA (EPIC 89 Phase B)**

# Wikipedia MCP Integration & Tool Protocol Standardization (Phase B)

> **Implementation Plan for Phase B of MCP Standardization**
> **Follows Tier 8 Feature Audit for Wikipedia Integration**
> **Parent Epic**: EPIC 89 Phase 2 Follow-On: MCP Gateway Standardization

<required_context_rules>
- @[.agents/rules/00-antigravity-core.md]
- @[.agents/rules/01-python-backend.md]
- @[.agents/rules/02_flutter_desktop.md]
- @[.agents/rules/03_seed_vault.md]
- @[.agents/rules/04_directory_reference.md]
- @[.agents/rules/05_llm_architecture.md]
- @[ki_god_code_prevention.md]
- @[ki_global_config_sovereignty.md]
- @[ki_tripartite_pipeline_architecture.md]
</required_context_rules>

<anti_targets>
- Do NOT use third-party synchronous wikipedia PyPI package (`blocking_the_fastapi_thread`). Use native async `httpx.AsyncClient`.
- Do NOT create external Node.js / stdio MCP processes (prohibited by Sovereign Python Async Gateway principle).
- Do NOT hardcode Wikipedia API URLs, timeouts, or character truncation limits inside service logic (`ki_global_config_sovereignty.md`).
- Do NOT modify @[backend_v2/services/orchestrator/prompt_compiler.py] (frozen architectural cornerstone).
- Do NOT use `.get()` duck typing or unstructured kwargs in tool execution (`the_zero_compromise_pledge`).
- Do NOT bypass `seed_data.json` bounded mutation protocol (`03_seed_vault.md`).
</anti_targets>

## Problem Statement & Architectural Context

Following the activation of the `source_verification_hook` and `ToolDispatcher` pipeline in Phase A, Quorum's MCP tool loop supports live internet research. However, the MCP tool registry is currently limited to a single tool provider (`mcp_tavily_search`).

To provide specialized encyclopedic research and peer-reviewed factual anchoring without commercial API costs or search noise, Quorum requires native **Wikipedia MCP Tools**:
1. `mcp_wikipedia_search`: Rapid, low-token search querying Wikipedia Action API (OpenSearch / search) returning page titles, snippets, and Wikipedia canonical URLs.
2. `mcp_wikipedia_read`: Detailed, bounded content retrieval querying the Wikimedia REST API (page summary / lead section extract) protected by a strict character truncation shield (`mcp_wikipedia_max_chars = 8000` in `backend_v2/settings.py`) to prevent context window explosion and preserve prompt caching.

Because the core SDUI and audit pipeline established in Phase A (`TraceEvent` -> `dag_executor.py` -> `frozen_context.mcp_tool_audit` -> `PrintableSourcesAdapter`) is 100% tool-agnostic, registering Wikipedia tools requires **zero changes to the execution engine or SDUI presentation adapters**.

Furthermore, Studio V2's `MCP-yhdyskäytävät` view and `StepBuilderView` already dynamically read `SystemConfigMCPGateways` from `seed_data.json`, meaning registering Wikipedia in seed data instantly surfaces it for visual toggle on any specialist step in the Flutter UI.

---

## User Review Required

> [!IMPORTANT]
> **Wikimedia API User-Agent Mandate**: Wikimedia requires an explicit, descriptive `User-Agent` header (specifically: `Quorum-Engine/2.0 (contact@cognitivequorum.com)`). Requests without a custom User-Agent are rejected with HTTP 403 Forbidden. The client must configure this header from `mcp_wikipedia_user_agent` in `backend_v2/settings.py`.

> [!IMPORTANT]
> **Multi-Language Wikipedia Resolution**: Wikipedia operates across language subdomains (`fi.wikipedia.org`, `en.wikipedia.org`, `de.wikipedia.org`). The `WikipediaClient` must dynamically format the API endpoint based on the execution's `target_language` / `locale` (defaulting to `fi` or `en` with fallback to `en`).

---

## Proposed Changes

Grouped logically by architectural layer:

### Phase 1: Pre-Implementation Technical Debt Cleanups & Settings SSOT

#### [MODIFY] @[backend_v2/settings.py]

Add centralized configuration settings for Wikipedia MCP:
```python
# --- MCP Wikipedia Configuration ---
mcp_wikipedia_max_chars: Annotated[int, Field(description="Max characters returned by Wikipedia read tool to prevent context explosion")] = 8000
mcp_wikipedia_timeout_seconds: Annotated[int, Field(description="Timeout for Wikipedia HTTP requests")] = 10
mcp_wikipedia_user_agent: Annotated[str, Field(description="User-Agent header required by Wikimedia API policy")] = "Quorum-Engine/2.0 (contact@cognitivequorum.com)"
mcp_wikipedia_max_search_results: Annotated[int, Field(description="Max search results returned by Wikipedia search")] = 5
```

#### [MODIFY] @[backend_v2/models/domain/tools.py]

Clean up `BaseTool` typing to enforce strict type hints:
```python
from abc import ABC, abstractmethod
from typing import Any
from backend_v2.models.v2_core import MCPAuditTrace

class BaseTool(ABC):
    """Abstract interface for all MCP tools."""

    @property
    @abstractmethod
    def tool_id(self) -> str:
        """The strictly defined unique identifier for the tool."""
        pass

    @property
    @abstractmethod
    def declaration(self) -> dict[str, Any]:
        """The tool declaration in OpenAI JSON schema format."""
        pass

    @abstractmethod
    async def execute(self, **kwargs: Any) -> MCPAuditTrace:
        """Execute the tool logic and return a standard audit trace."""
        pass
```

---

### Phase 2: Async Wikipedia Client & Tool Implementations

#### [NEW] @[backend_v2/services/mcp/wikipedia_client.py]

A dedicated, isolated, 100% asynchronous Wikimedia API client using `httpx.AsyncClient` (`anti_god_file_dumping`, `private_helper_bloat_ban` < 150 lines):
- `search_articles(query: str, target_lang: str = "fi", limit: int = 5) -> list[WikipediaSearchResultItem]`: Queries `https://{lang}.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json`.
- `read_page_summary(title: str, target_lang: str = "fi") -> WikipediaPageSummaryResult`: Queries Wikimedia REST API `https://{lang}.wikipedia.org/api/rest_v1/page/summary/{encoded_title}` for extracts and canonical URL, truncating extract to `get_settings().mcp_wikipedia_max_chars`.
- Implements RFC 7807 dual-reporting and Fail-Fast on network failures with explicit `AppException(ErrorCodes.FETCH_FAILED)`.

#### [NEW] @[backend_v2/models/domain/wikipedia.py]

New domain models for Wikipedia data structures:
- `WikipediaSearchResultItem(V2CoreBase)`: `title: str`, `snippet: str`, `page_id: int`, `url: str`.
- `WikipediaPageSummaryResult(V2CoreBase)`: `title: str`, `extract: str`, `canonical_url: str`, `description: str | None`.

#### [NEW] @[backend_v2/services/mcp/tools/wikipedia.py]

Implements the two discrete tools adhering to `BaseTool`:
1. `WikipediaSearchTool(BaseTool)`:
   - `tool_id = "mcp_wikipedia_search"`
   - OpenAI JSON schema declaration for `query: str`, `reasoning: str`.
   - Executes `WikipediaClient.search_articles`, formats search results into `MCPAuditTrace.response_summary`, and collects `source_urls`.
2. `WikipediaReadTool(BaseTool)`:
   - `tool_id = "mcp_wikipedia_read"`
   - OpenAI JSON schema declaration for `title: str`, `reasoning: str`.
   - Executes `WikipediaClient.read_page_summary`, returns extract in `MCPAuditTrace.response_summary`, and sets canonical URL in `MCPAuditTrace.source_urls`.

---

### Phase 3: Tool Dispatcher Registration

#### [MODIFY] @[backend_v2/services/mcp/mcp_tool_loop.py]

Register the new Wikipedia tools in the global `DISPATCHER`:
```diff
+from backend_v2.services.mcp.tools.wikipedia import (
+    WIKIPEDIA_READ_TOOL_ID,
+    WIKIPEDIA_SEARCH_TOOL_ID,
+    WikipediaReadTool,
+    WikipediaSearchTool,
+)

 # Global Dispatcher Instance
-DISPATCHER = ToolDispatcher(tools=[TavilyTool()])
+DISPATCHER = ToolDispatcher(
+    tools=[
+        TavilyTool(),
+        WikipediaSearchTool(),
+        WikipediaReadTool(),
+    ]
+)
```

---

### Phase 4: Seed Data Vault Update (`mcp_gateways`)

#### [MODIFY] @[backend_v2/seed/seed_data.json#L106-L132]

Update `sys_8172bda70c8641c5` (`mcp_gateways`) to include `mcp_wikipedia_search` and `mcp_wikipedia_read` with full `I18nText` descriptions and input schemas:

```json
{
    "tool_id": "mcp_wikipedia_search",
    "name": {
        "default_locale": "en",
        "translations": {
            "en": "Wikipedia Search",
            "fi": "Wikipedia-haku"
        }
    },
    "description": "Search Wikipedia encyclopedic articles for factual definitions and historical data.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string"
            }
        },
        "required": [
            "query"
        ]
    }
},
{
    "tool_id": "mcp_wikipedia_read",
    "name": {
        "default_locale": "en",
        "translations": {
            "en": "Wikipedia Article Reader",
            "fi": "Wikipedia-artikkelin lukija"
        }
    },
    "description": "Read a Wikipedia article extract and summary by title.",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string"
            }
        },
        "required": [
            "title"
        ]
    }
}
```

---

### Phase 5: Verification & Tests (Positive & Negative ISTQB Partition Coverage)

#### [NEW] @[backend_v2/tests/unit/services/mcp/test_wikipedia_client.py]
Unit tests for `WikipediaClient`:
1. **Positive 1 (Search Success)**: Mock Wikimedia API response -> verify `WikipediaSearchResultItem` parsing and canonical URL formation.
2. **Positive 2 (Read Summary Success)**: Mock REST summary API -> verify extract and canonical URL.
3. **Negative 1 (API 404 / Page Not Found)**: Mock 404 response -> verify graceful Fail-Fast with `AppException(ErrorCodes.NOT_FOUND)` or structured empty fallback.
4. **Negative 2 (Network Timeout / HTTP 500)**: Mock HTTP error -> verify RFC 7807 dual-reporting and `AppException(ErrorCodes.FETCH_FAILED)`.
5. **Boundary 1 (Character Limit Truncation)**: Article exceeding 8000 chars -> verify truncation to `get_settings().mcp_wikipedia_max_chars`.
6. **Boundary 2 (Language Subdomain Resolution)**: Test locale resolution for `fi`, `en`, `de`, with fallback to `en`.

#### [NEW] @[backend_v2/tests/unit/services/mcp/tools/test_wikipedia_tools.py]
Unit tests for `WikipediaSearchTool` and `WikipediaReadTool`:
1. **Positive 1**: Execute search tool -> verify `MCPAuditTrace` contains `tool_id="mcp_wikipedia_search"` and `source_urls`.
2. **Positive 2**: Execute read tool -> verify `MCPAuditTrace` contains `tool_id="mcp_wikipedia_read"` and canonical article URL.
3. **Negative 1**: Missing required query/title parameter -> raises `AppException(ErrorCodes.VALIDATION_FAILED)`.

---

```xml
<execution_protocol>
  <phase id="1" name="SETTINGS &amp; DOMAIN MODELS">
    <step id="1.1" name="Add Wikipedia settings to settings.py">
      <file>@[backend_v2/settings.py]</file>
      <action>Add mcp_wikipedia_max_chars, mcp_wikipedia_timeout_seconds, mcp_wikipedia_user_agent, mcp_wikipedia_max_search_results Annotated fields.</action>
      <constraint invariant="ki_global_config_sovereignty.md">All thresholds must be centrally defined in settings.py.</constraint>
    </step>
    <step id="1.2" name="Create Wikipedia Domain Models">
      <file>[NEW] @[backend_v2/models/domain/wikipedia.py]</file>
      <action>Create WikipediaSearchResultItem and WikipediaPageSummaryResult using ConfigDict(strict=True, extra='forbid').</action>
      <constraint invariant="strict_pydantic_v2_rust">All models must enforce strict Pydantic V2 schemas.</constraint>
    </step>
  </phase>

  <phase id="2" name="WIKIPEDIA ASYNC CLIENT &amp; TOOLS">
    <step id="2.1" name="Implement WikipediaClient">
      <file>[NEW] @[backend_v2/services/mcp/wikipedia_client.py]</file>
      <action>Create async WikipediaClient using httpx.AsyncClient with custom User-Agent, language subdomain routing, and character truncation.</action>
      <constraint invariant="blocking_the_fastapi_thread">Must be 100% async non-blocking using httpx.</constraint>
      <constraint invariant="anti_god_file_dumping">Keep file under 150 lines.</constraint>
    </step>
    <step id="2.2" name="Implement WikipediaSearchTool and WikipediaReadTool">
      <file>[NEW] @[backend_v2/services/mcp/tools/wikipedia.py]</file>
      <action>Implement BaseTool subclasses for mcp_wikipedia_search and mcp_wikipedia_read.</action>
      <constraint invariant="single_responsibility_principle">Each tool encapsulates its declaration and execution.</constraint>
    </step>
  </phase>

  <phase id="3" name="DISPATCHER REGISTRATION">
    <step id="3.1" name="Register Wikipedia Tools in ToolDispatcher">
      <file>@[backend_v2/services/mcp/mcp_tool_loop.py]</file>
      <action>Instantiate DISPATCHER with TavilyTool, WikipediaSearchTool, and WikipediaReadTool.</action>
      <constraint invariant="strategy_pattern_mandate">Dispatcher provides O(1) tool lookup via tool_id registry.</constraint>
    </step>
  </phase>

  <phase id="4" name="SEED DATA MUTATION">
    <step id="4.1" name="Update mcp_gateways in seed_data.json">
      <file>@[backend_v2/seed/seed_data.json#L106-L132]</file>
      <action>Apply bounded mutation protocol: backup seed_data.json, add mcp_wikipedia_search and mcp_wikipedia_read to sys_8172bda70c8641c5 tools array, verify syntax, run backend audit loop, and re-seed.</action>
      <constraint invariant="03_seed_vault.md">Must execute timestamped backup and bounded edit.</constraint>
    </step>
  </phase>

  <phase id="5" name="AUTOMATED AUDIT &amp; QUALITY GATES">
    <step id="5.1" name="Create unit tests for Wikipedia Client and Tools">
      <file>[NEW] @[backend_v2/tests/unit/services/mcp/test_wikipedia_client.py]</file>
      <file>[NEW] @[backend_v2/tests/unit/services/mcp/tools/test_wikipedia_tools.py]</file>
      <action>Implement ISTQB tests covering positive paths, 404 handling, network errors, language routing, and character truncation.</action>
      <constraint invariant="anti_happy_path_mandate">At least 2 negative test cases per component.</constraint>
    </step>
    <step id="5.2" name="Run Backend Quality Gate">
      <action>Execute uv run python scripts/backend_audit_loop.py backend_v2/services/mcp --test</action>
      <constraint invariant="zero_tolerance_audit_loop">100% pass on Ruff, MyPy, and Pytest coverage.</constraint>
    </step>
  </phase>
</execution_protocol>
```

---

## Verification Plan

### Automated Tests
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/services/mcp/wikipedia_client.py --test
uv run python scripts/backend_audit_loop.py backend_v2/services/mcp/tools/wikipedia.py --test
uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/mcp/test_wikipedia_client.py --test
uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/mcp/tools/test_wikipedia_tools.py --test
```

### Manual Verification
1. Run `uv run python backend_v2/seed/run_seed.py local` and verify `mcp_gateways` contains 3 tools.
2. Launch Studio V2 Flutter App -> Navigate to `System Settings` -> `MCP-yhdyskäytävät` -> Verify Wikipedia Search and Article Reader appear with localized Finnish titles.
3. Open `StepBuilderView` for a specialist step -> Verify `FilterChip` allows selecting `Wikipedia-haku` alongside `Tavily AI -haku`.
