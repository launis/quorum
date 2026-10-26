# Implementation Plan: Dynamic MCP Gateway Presentation, Synthesis Directives SSOT & Dumb Painter SDUI Parity

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
  <knowledge_item>@[ki_mcp_tool_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_hybrid_ui_sanitization.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
</required_context_rules>

## Architectural Summary

### User Mandates & Problem Statement
1. **Clean Executive Presentation (Zero Technical Fluff)**:
   - In execution `exe_2dff974f323146e3`, external tool findings in the report under *"Ulkoinen faktantarkistus ja tietolähteet"* displayed raw CDATA tags and unparsed JSON dictionaries:
     `Ulkoinen havainto / MCP-haun tulos: <![CDATA[{"query":"Työterveyslaitos Stanford etätyö","results":[{"url":...`
   - User directive: *"ei tarvitse näkyä teknistä, pelkästään siisti raportti, tee raportin siisteysohjeistus täysin sen mukaan, miten kaikki synteesiohjaus tapahtuu, käytä samaa periaatetta"*.
2. **Dynamic MCP Gateways & Zero Hardcoded Wrappers (EPIC 159 Parity)**:
   - In accordance with Quorum's Dynamic MCP Architecture ([`ki_mcp_tool_protocol.md`](file:///c:/src/quorum/knowledge/mcp_tool_protocol/artifacts/ki_mcp_tool_protocol.md) and [`EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md`](file:///c:/src/quorum/docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md)), all static wrappers (`tavily.py`, `wikipedia.py`, `wikipedia_client.py`) were permanently eradicated.
   - Quorum operates strictly as an **MCP Client** via [`GenericMCPClient`](file:///c:/src/quorum/backend_v2/services/mcp/generic_mcp_client.py) and [`ToolDispatcher`](file:///c:/src/quorum/backend_v2/services/mcp/dispatcher.py).
   - Dedicated backend routes (specifically `/api/v2/system/mcp/wikipedia`) and loopback endpoints (`http://127.0.0.1:8000/...`) are **strictly prohibited** as architectural antipatterns violating `localhost_endpoint_hardcoding_ban` and tripping `MCPUrlValidator` SSRF defenses.
   - Any external research gateway (Wikipedia, Tavily, PubMed, ArXiv) is integrated **100% dynamically** through Studio V2 Gateway Management (`POST /api/studio/mcp-gateways` and `POST /api/studio/mcp-gateways/{id}/discover`) with zero backend router additions.
3. **Synthesis Prompt Directives SSOT & Dumb Painter Parity**:
   - Establish `SYNTHESIS_EXTERNAL_EVIDENCE_MANDATE` directly in `backend_v2/models/prompts/synthesis/style_directives.py` as an immutable prompt constant.
   - Enforce 100% Dumb Painter semantic parity: Flutter UI and WeasyPrint PDF receive pre-sanitized, pre-budgeted structures without client-side text mutation.

### Synthesis Steering Architectural Principles
Quorum's synthesis directives (`synthesis_directives.py`, `style_directives.py`, `sdui_directives.py`, and `ki_hybrid_ui_sanitization.md`) establish the following strict presentation invariants:
1. **Anti-Technical & Anti-Jargon Purity**: Never leak system identifiers, DAG step keys, CDATA fences, raw JSON syntax, or protocol acronyms ("MCP") into executive presentation tiers.
2. **Substantive Finding Extraction**: Presentation adapters must extract verified substantive claims and evidence content (specifically the top result finding, snippet, or text) rather than dumping raw JSON payloads.
3. **Two-Tier Sentence-Boundary Character Budgeting**: Enforce length budgeting strictly using `enforce_sentence_boundary_budget` (scanning within $[0.60, 1.0]$ budget window) so findings conclude gracefully on natural punctuation (`.`, `!`, `?`) without mid-word or mid-thought truncation.
4. **Dumb Painter Semantic Parity**: Maintain 100% presentation parity between the Flutter Desktop client (SDUI `MarkdownBlock`) and WeasyPrint PDF (`report_template.jinja2`) by sanitizing text deterministically in the Python service tier before serialization into `ReportDataDTO` and SDUI blocks.
5. **Dynamic Tool Dispatching & Zero-Code Gateway Scaling**: All MCP tools declared on workflows flow through `ToolDispatcher.resolve_primary_search_tool()`. New MCP servers are discovered at runtime; the presentation tier handles arbitrary tool findings dynamically based on standard content fields (`content`, `snippet`, `text`, `summary`, `finding`).

---

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline Test Assertion** (`@[backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py#L120-L240]`) | Stale assertion expecting legacy prefixed tool id `"mcp_tavily_search"`. | Assert SSOT canonical tool ID `"tavily_search"` matching `seed_data.json`. | Zero secondary fallback assertions or `or` matching. | `uv run pytest backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py` passes 100%. |
| **Settings SSOT** (`@[backend_v2/settings.py#L54-L1043]`) | Hardcoded 8000-char budget or arbitrary presentation truncation in downstream adapters; hardcoding loopback ports or provider URLs. | Central `mcp_presentation_max_chars: Annotated[int, Field(default=300, ge=100, le=2000)] = 300` in Settings SSOT. | Pruned all provider-specific URL settings (`wikipedia_api_url`, loopback flags); zero localhost hardcodes. | `uv run pytest backend_v2/tests/unit/test_settings.py`. |
| **MCP Wire DTOs** (`@[backend_v2/models/dtos/mcp.py#L631-L657]`, `@[backend_v2/models/dtos/mcp.py#L660-L711]`) | Defining ad-hoc Pydantic models inside service/router files or parsing JSON with `json.loads()` and `isinstance(data, dict)`. | Extend `MCPSearchResultItemDTO` and `MCPStructuredContentDTO` with optional standard fields (`snippet`, `text`, `summary`, `description`, `finding`) with `ConfigDict(strict=True, extra="forbid", frozen=True)`. | Zero provider-specific DTO models; 100% generic MCP JSON-RPC 2.0 schema support via Rust `.model_validate_json()`. | `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/mcp.py --test --ast-strict`. |
| **Synthesis Prompt Directives SSOT** (`@[backend_v2/models/prompts/synthesis/style_directives.py]`, `@[backend_v2/models/prompts/synthesis/__init__.py]`, `@[backend_v2/models/prompts/__init__.py]`) | Ad-hoc prompt strings scattered in worker methods or soft instructions in UI. | Static `SYNTHESIS_EXTERNAL_EVIDENCE_MANDATE` XML block constant strictly exported in `__all__` per Prompt Asset SSOT. | Zero dynamic f-string formatting inside mandate; 100% static prefix for prompt caching. | `uv run pytest backend_v2/tests/unit/models/prompts/test_synthesis_directives.py`. |
| **Synthesis Worker Assembly** (`@[backend_v2/workers/synthesis_worker.py#L91-L639]`) | Assembling `sys_prompt` without external evidence guardrails, allowing raw CDATA/JSON in Phase 2 narrative. | Static concatenation of `SYNTHESIS_EXTERNAL_EVIDENCE_MANDATE` into `sys_prompt` in `generate_profile_synthesis_and_pdf_task`. | Zero conditional branching on gateway presence; universal synthesis prompt invariant. | `uv run pytest backend_v2/tests/unit/models/prompts/test_synthesis_directives.py`. |
| **Zero Hardcoded Routers Ban** (`@[backend_v2/api/routers/system/__init__.py]`) | Creating pseudo-MCP FastAPI loopback routers (/api/v2/system/mcp/wikipedia) to simulate external MCP tools. | Absolute zero internal tool routers. Rely 100% on external MCP servers connected via GenericMCPClient and discovered via Studio API. | Complete elimination of wikipedia_mcp_server.py, mcp_wikipedia.py, and loopback configs. | Static AST audit passes; zero localhost endpoints in routes or seed data. |
| **Sanitization Service** (`[NEW] @[backend_v2/services/sdui/sanitizers/__init__.py]`, `[NEW] @[backend_v2/services/sdui/sanitizers/mcp_presentation_sanitizer.py]`) | Leaking raw CDATA fences, raw JSON syntax, `json.loads()` with `isinstance(root, dict)`, or negative key filtering sets. | Deterministic static `McpPresentationSanitizer.sanitize_finding(...)`: CDATA stripping, Rust `MCPStructuredContentDTO.model_validate_json` extraction, HTML stripping, whitespace normalization, sentence budgeting, and terminal punctuation. | Zero complex NLP/LLM summarization passes; pure deterministic Python service under 150 lines. | `uv run python scripts/backend_audit_loop.py backend_v2/services/sdui/sanitizers/mcp_presentation_sanitizer.py --test --ast-strict`. |
| **Sources Adapter** (`@[backend_v2/services/sdui/adapters/printable_sources_adapter.py#L64-L324]`) | Raw `trace.response_summary.strip()` string concatenation dumping raw CDATA/JSON into `MarkdownBlock`. | Route `trace.response_summary` through `McpPresentationSanitizer.sanitize_finding` before appending to markdown lines, omitting empty/invalid lines. | Zero client-side Flutter regexes or Dart markdown parsers; pure Dumb Painter SDUI contract. | `uv run pytest backend_v2/tests/unit/services/sdui/adapters/test_printable_sources_mcp_sanitization.py`. |
| **Report Data DTO Hydration** (`@[backend_v2/services/blueprint.py#L126-L686]`) | Hydrating un-sanitized `MCPAuditTrace` instances into `ReportDataDTO.mcp_tool_audit`, leaking CDATA/JSON to PDF Jinja templates. | Universal pre-serialization sanitization: sanitize `audit.response_summary` via `McpPresentationSanitizer.sanitize_finding` for all items in `mcp_audit_data`. | Zero dual-pipeline branching; single in-place model copy path for all audit traces. | `uv run pytest backend_v2/tests/unit/services/test_blueprint_combined_costs.py`. |
| **Report Template Presentation** (`@[backend_v2/templates/report_template.jinja2#L256-L289]`) | Blind rendering of `audit.response_summary | md | safe` without empty/whitespace guard. | Wrap in `{% if audit.response_summary %}` block, guaranteeing clean PDF rendering without empty boxes. | Zero complex template logic or Jinja macros; clean Dumb Painter static rendering. | `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`. |
| **Localization SSOT** (`@[backend_v2/l10n/fi.json#L110-L125]`, `@[backend_v2/l10n/en.json#L110-L125]`) | Technical protocol jargon `"MCP-haun tulos"` / `"MCP retrieval result"` in executive presentation. | Clean executive labels `"Ulkoinen havainto:"` / `"External finding:"`. | Zero dynamic string concatenation or fallback strings in adapters. | Automated JSON localization key parity check. |
| **Sanitizer Unit Test Suite** (`[NEW] @[backend_v2/tests/unit/services/sdui/sanitizers/__init__.py]`, `[NEW] @[backend_v2/tests/unit/services/sdui/sanitizers/test_mcp_presentation_sanitizer.py]`) | Missing test package marker `__init__.py`; testing only happy paths without boundary conditions. | Package marker `__init__.py` plus ISTQB 7-scenario matrix covering real Tavily CDATA JSON, generic plain text, sentence budgeting, empty/whitespace, and malformed inputs. | Pure unit tests without database or network dependencies. | `uv run pytest backend_v2/tests/unit/services/sdui/sanitizers/test_mcp_presentation_sanitizer.py`. |
| **SDUI Adapter Test Suite** (`[NEW] @[backend_v2/tests/unit/services/sdui/adapters/test_printable_sources_mcp_sanitization.py]`) | Verifying SDUI output without asserting absence of raw CDATA or technical keys. | Explicit assertions proving `MarkdownBlock` text contains zero `<![CDATA[`, zero `{"query":`, and clean substantive findings. | Zero full-stack server spin-up; in-memory `AdapterContext` tests. | `uv run pytest backend_v2/tests/unit/services/sdui/adapters/test_printable_sources_mcp_sanitization.py`. |

---

## Target Boundaries

### TARGET FILES (Scoped for Modification & Creation)
- `[MODIFY] @[backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py#L120-L240]`
- `[MODIFY] @[backend_v2/settings.py#L54-L1043]`
- `[MODIFY] @[backend_v2/models/dtos/mcp.py#L631-L657]`
- `[MODIFY] @[backend_v2/models/dtos/mcp.py#L660-L711]`
- `[MODIFY] @[backend_v2/models/prompts/synthesis/style_directives.py]`
- `[MODIFY] @[backend_v2/models/prompts/synthesis/__init__.py]`
- `[MODIFY] @[backend_v2/models/prompts/__init__.py]`
- `[MODIFY] @[backend_v2/workers/synthesis_worker.py#L91-L639]`
- `[NEW] @[backend_v2/services/sdui/sanitizers/__init__.py]`
- `[NEW] @[backend_v2/services/sdui/sanitizers/mcp_presentation_sanitizer.py]`
- `[MODIFY] @[backend_v2/services/sdui/adapters/printable_sources_adapter.py#L64-L324]`
- `[MODIFY] @[backend_v2/services/blueprint.py#L126-L686]`
- `[MODIFY] @[backend_v2/templates/report_template.jinja2#L256-L289]`
- `[MODIFY] @[backend_v2/l10n/fi.json#L110-L125]`
- `[MODIFY] @[backend_v2/l10n/en.json#L110-L125]`
- `[NEW] @[backend_v2/tests/unit/services/sdui/sanitizers/__init__.py]`
- `[NEW] @[backend_v2/tests/unit/services/sdui/sanitizers/test_mcp_presentation_sanitizer.py]`
- `[NEW] @[backend_v2/tests/unit/services/sdui/adapters/test_printable_sources_mcp_sanitization.py]`

### CONTEXT FILES (Strictly Read-Only)
- `@[backend_v2/services/length_budget_enforcer.py#L19-109]`
- `@[backend_v2/models/prompts/synthesis/synthesis_directives.py]`
- `@[backend_v2/models/domain/system_config.py#L297-369]`
- `@[backend_v2/services/mcp/generic_mcp_client.py#L760-775]`
- `@[backend_v2/services/mcp/dispatcher.py#L233-395]`
- `@[backend_v2/services/mcp/url_validator.py]`
- `@[backend_v2/api/routers/system/__init__.py]`

---

## Pre-Implementation Technical Debt Cleanups (Phase 1)
In accordance with the Scoped Boy Scout Rule and `touched_scope_tech_debt_mandate`:
1. `@[backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py#L120-L240]`: The test function asserts `typed_trace.tool_id == "mcp_tavily_search"`. The active tool definition in `seed_data.json` is `tavily_search`. Update assertion to `typed_trace.tool_id == "tavily_search"` to ensure baseline integration suite passes 100%.

---

```xml
<execution_protocol>
  <step id="1" name="TECHNICAL DEBT RESOLUTION &amp; BASELINE INTEGRATION GATE">
    <target_files>
      <file>[MODIFY] @[backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py#L120-L240]</file>
    </target_files>
    <action>In `backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py`, update the legacy assertion in `test_full_e2e_tavily_extraction_to_sdui_bibliography_live` from `assert typed_trace.tool_id == "mcp_tavily_search"` to `assert typed_trace.tool_id == "tavily_search"` to match the SSOT tool identifier.</action>
    <constraint invariant="scoped_boy_scout">Repair the failing baseline assertion in the touched integration test before introducing presentation layer changes.</constraint>
    <verification>Run `uv run pytest backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py` and verify all tests pass.</verification>
  </step>

  <step id="2" name="CENTRAL CONFIGURATION SSOT EXTENSION">
    <target_files>
      <file>[MODIFY] @[backend_v2/settings.py#L54-L1043]</file>
    </target_files>
    <action>In `backend_v2/settings.py`, add `mcp_presentation_max_chars` to the `Settings` class:
```python
mcp_presentation_max_chars: Annotated[
    int,
    Field(
        default=300,
        ge=100,
        le=2000,
        description="Maximum character budget for external findings rendered in SDUI and executive report presentation before sentence-boundary truncation",
    ),
] = 300
```
    </action>
    <constraint invariant="central_config_sovereignty">Ensure character limit is governed centrally in Settings without magic numbers or hardcoded limits. Zero localhost or pseudo-MCP server settings.</constraint>
    <verification>Run `uv run pytest backend_v2/tests/unit/test_settings.py` to confirm settings validation passes.</verification>
  </step>

  <step id="3" name="GENERIC MCP WIRE DTO EXTENSION">
    <target_files>
      <file>[MODIFY] @[backend_v2/models/dtos/mcp.py#L631-L657]</file>
      <file>[MODIFY] @[backend_v2/models/dtos/mcp.py#L660-L711]</file>
    </target_files>
    <action>
In `backend_v2/models/dtos/mcp.py`:
- Extend `MCPSearchResultItemDTO` (`#L631-L657`) with optional `snippet`, `text`, and `summary` fields:
  ```python
  snippet: Annotated[str | None, Field(default=None, description="Search hit snippet or abstract extract")] = None
  text: Annotated[str | None, Field(default=None, description="Plain text content extract")] = None
  summary: Annotated[str | None, Field(default=None, description="Encyclopedic or article summary")] = None
  ```
- Extend `MCPStructuredContentDTO` (`#L660-L711`) with optional `summary`, `description`, `text`, `message`, and `finding` fields:
  ```python
  summary: Annotated[str | None, Field(default=None, description="Executive summary of structured tool output")] = None
  description: Annotated[str | None, Field(default=None, description="Descriptive narrative of tool output")] = None
  text: Annotated[str | None, Field(default=None, description="Direct text response body")] = None
  message: Annotated[str | None, Field(default=None, description="Status or informational message")] = None
  finding: Annotated[str | None, Field(default=None, description="Key factual or analytical finding")] = None
  ```
Enforce `ConfigDict(strict=True, extra="forbid", frozen=True)` across both DTOs to enable Rust `.model_validate_json()` hydration without untyped dictionary duck-typing.
    </action>
    <constraint invariant="the_zero_compromise_pledge">All wire payloads MUST validate through typed Pydantic V2 DTOs with extra="forbid". Zero naked dictionaries.</constraint>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/mcp.py --test --ast-strict`.</verification>
  </step>

  <step id="4" name="SYNTHESIS PROMPT DIRECTIVES SSOT EXTENSION">
    <target_files>
      <file>[MODIFY] @[backend_v2/models/prompts/synthesis/style_directives.py]</file>
      <file>[MODIFY] @[backend_v2/models/prompts/synthesis/__init__.py]</file>
      <file>[MODIFY] @[backend_v2/models/prompts/__init__.py]</file>
      <file>[MODIFY] @[backend_v2/workers/synthesis_worker.py#L91-L639]</file>
    </target_files>
    <action>
1. In `backend_v2/models/prompts/synthesis/style_directives.py`:
   - Add constant `SYNTHESIS_EXTERNAL_EVIDENCE_MANDATE`:
```python
SYNTHESIS_EXTERNAL_EVIDENCE_MANDATE: str = (
    "<external_evidence_mandate>\n"
    "- EXTERNAL EVIDENCE PRESENTATION MANDATE: When citing or incorporating external verification findings "
    "(specifically web searches or encyclopedic references), present ONLY clean, substantive empirical statements.\n"
    "- ZERO TECHNICAL NOISE: You MUST NOT output raw JSON keys, tool protocol tokens, CDATA tags, query strings, "
    "or search engine scoring metrics into narrative text or citations.\n"
    "- EXECUTIVE RELEVANCE: Synthesize external evidence directly into fluent, evidence-grounded prose concluding on complete sentences.\n"
    "</external_evidence_mandate>"
)
```
   - Add `SYNTHESIS_EXTERNAL_EVIDENCE_MANDATE` to `__all__` in `style_directives.py`.
2. In `backend_v2/models/prompts/synthesis/__init__.py` and `backend_v2/models/prompts/__init__.py`:
   - Re-export `SYNTHESIS_EXTERNAL_EVIDENCE_MANDATE`.
3. In `backend_v2/workers/synthesis_worker.py` (lines 91–639):
   - Import `SYNTHESIS_EXTERNAL_EVIDENCE_MANDATE` and inject into `sys_prompt` in `generate_profile_synthesis_and_pdf_task`:
```python
sys_prompt = (
    f"{SYNTHESIS_SYSTEM_PROMPT}\n\n"
    f"{SYNTHESIS_SDUI_MANDATES}\n\n"
    f"{ANTI_JARGON_MANDATE_BLOCK}\n\n"
    f"{SYNTHESIS_EXTERNAL_EVIDENCE_MANDATE}\n\n"
    f"{STATIC_LINGUISTIC_PROTOCOL}"
)
```
    </action>
    <constraint invariant="prompt_asset_ssot_mandate">All static prompt directives MUST reside in `backend_v2/models/prompts`. Static prefix must be 100% cacheable without dynamic f-strings.</constraint>
    <verification>Run `uv run pytest backend_v2/tests/unit/models/prompts/test_synthesis_directives.py`.</verification>
  </step>

  <step id="5" name="MCP PRESENTATION SANITIZER IMPLEMENTATION &amp; UNIT TESTING">
    <target_files>
      <file>[NEW] @[backend_v2/services/sdui/sanitizers/__init__.py]</file>
      <file>[NEW] @[backend_v2/services/sdui/sanitizers/mcp_presentation_sanitizer.py]</file>
      <file>[NEW] @[backend_v2/tests/unit/services/sdui/sanitizers/__init__.py]</file>
      <file>[NEW] @[backend_v2/tests/unit/services/sdui/sanitizers/test_mcp_presentation_sanitizer.py]</file>
    </target_files>
    <action>
1. Create package markers `backend_v2/services/sdui/sanitizers/__init__.py` and `backend_v2/tests/unit/services/sdui/sanitizers/__init__.py`.
2. Create `McpPresentationSanitizer` in `backend_v2/services/sdui/sanitizers/mcp_presentation_sanitizer.py` implementing the deterministic enforcement of `SYNTHESIS_EXTERNAL_EVIDENCE_MANDATE` without `json.loads()` or untyped dictionary duck-typing:
   - `sanitize_finding(raw_summary: str | None, max_chars: int | None = None) -> str | None`:
   - If `raw_summary` is None, empty, or whitespace-only, return `None`.
   - Strip `<![CDATA[` prefix and `]]>` suffix.
   - Strip markdown code fences (` ```json ` or ` ``` `).
   - If candidate starts with `{` and ends with `}`, validate via `MCPStructuredContentDTO.model_validate_json(candidate, strict=False)`:
     * Inspect `parsed.results`: for each `MCPSearchResultItemDTO` item, check static attributes `item.content`, `item.snippet`, `item.text`, and `item.summary` for the first non-empty string.
     * If `parsed.results` yields no text, check top-level static attributes on `MCPStructuredContentDTO`: `parsed.answer`, `parsed.summary`, `parsed.description`, `parsed.text`, `parsed.message`, and `parsed.finding`.
   - If candidate is plain text (or fallback when `ValidationError` occurs on malformed pseudo-JSON):
     * Strip structural JSON/XML noise tokens and remove HTML tags via `re.sub(r"<[^>]+>", " ", text)`.
     * Normalize multiple whitespace/newlines to single spaces.
     * Strip leading/trailing quotation marks and non-text delimiters.
   - Apply sentence-boundary character budgeting:
     * Determine `budget = max_chars if max_chars is not None else get_settings().mcp_presentation_max_chars`.
     * If `len(clean_text) > budget`, invoke `enforce_sentence_boundary_budget(clean_text, budget)`.
     * If result does not terminate with sentence punctuation (`.`, `!`, `?`), append `.`.
   - Return clean sanitized string, or `None` if resulting text is empty.
3. Create comprehensive unit tests in `backend_v2/tests/unit/services/sdui/sanitizers/test_mcp_presentation_sanitizer.py` covering:
   - Full Tavily CDATA JSON payload from real execution `exe_2dff974f323146e3`.
   - Generic search plain text extract wrapped in CDATA.
   - Structured JSON without `results` (sample payload: `{"summary": "Tutkimus osoittaa..."}`).
   - Markdown code-fenced JSON.
   - Empty/whitespace CDATA payloads (returning None).
   - Sentence-boundary budgeting enforcement on 500-char text exceeding 300 budget.
   - Malformed pseudo-JSON handling (treating gracefully as string without crashing).
    </action>
    <constraint invariant="strict_pydantic_v2_rust">Use `MCPStructuredContentDTO.model_validate_json()` and static dot-notation; zero `json.loads()`, zero `isinstance(..., dict)`, and zero `.get()` calls.</constraint>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/sdui/sanitizers/mcp_presentation_sanitizer.py --test --ast-strict`.</verification>
  </step>

  <step id="6" name="SOURCES ADAPTER &amp; BLUEPRINT TRANSFORMER INTEGRATION">
    <target_files>
      <file>[MODIFY] @[backend_v2/services/sdui/adapters/printable_sources_adapter.py#L64-L324]</file>
      <file>[MODIFY] @[backend_v2/services/blueprint.py#L126-L686]</file>
      <file>[MODIFY] @[backend_v2/templates/report_template.jinja2#L256-L289]</file>
      <file>[NEW] @[backend_v2/tests/unit/services/sdui/adapters/test_printable_sources_mcp_sanitization.py]</file>
    </target_files>
    <action>
1. In `backend_v2/services/sdui/adapters/printable_sources_adapter.py` (`PrintableSourcesAdapter.build` lines 64–324):
   - Import `McpPresentationSanitizer`.
   - Sanitize `trace.response_summary` before appending to `mcp_lines`:
     ```python
     if trace.response_summary and trace.response_summary.strip():
         clean_finding = McpPresentationSanitizer.sanitize_finding(trace.response_summary)
         if clean_finding:
             mcp_lines.append(f"  - **{mcp_result_label}** {clean_finding}")
     ```
2. In `backend_v2/services/blueprint.py` (`BlueprintTransformer.build_report_dto` lines 126–686):
   - When assembling `mcp_audit_data`, sanitize `response_summary` on all `MCPAuditTrace` instances before storing in `ReportDataDTO`, preserving strict `str` typing on `MCPAuditTrace.response_summary`:
     ```python
     for idx, audit in enumerate(mcp_audit_data):
         sanitized = McpPresentationSanitizer.sanitize_finding(audit.response_summary)
         clean_summary = ""
         if sanitized is not None:
             clean_summary = sanitized
         if audit.id in evidence_to_axes:
             axis_names = {
                 block_to_axis[block_id]
                 for block_id in evidence_to_axes[audit.id]
                 if block_id in block_to_axis
             }
             mcp_audit_data[idx] = audit.model_copy(update={
                 "response_summary": clean_summary,
                 "impacted_axis_names": sorted(list(axis_names)),
             })
         elif clean_summary != audit.response_summary:
             mcp_audit_data[idx] = audit.model_copy(update={"response_summary": clean_summary})
     ```
3. In @[backend_v2/templates/report_template.jinja2#L256-L289]:
   - Verify that `audit.response_summary` renders cleanly inside an `{% if audit.response_summary %}` block:
     ```jinja2
     {% if audit.response_summary %}
     <div style="font-size: 12px; color: #555; margin-bottom: 10px; line-height: 1.5; clear: both;">
         {{ audit.response_summary | md | safe }}
     </div>
     {% endif %}
     ```
4. Create `backend_v2/tests/unit/services/sdui/adapters/test_printable_sources_mcp_sanitization.py` verifying that:
   - When `mcp_traces` with CDATA JSON (Tavily) or CDATA plain text are passed to `PrintableSourcesAdapter`, the resulting `MarkdownBlock` text contains neither `<![CDATA[` nor `{"query":` nor raw curly braces.
   - The substantive finding is present in the markdown text and formatted under `- **Ulkoinen havainto:**`.
    </action>
    <constraint invariant="dumb_painter_ui">Ensure PDF and SDUI output structures receive 100% pre-sanitized text.</constraint>
    <verification>Run `uv run pytest backend_v2/tests/unit/services/sdui/adapters/test_printable_sources_adapter.py backend_v2/tests/unit/services/sdui/adapters/test_printable_sources_mcp_sanitization.py`.</verification>
  </step>

  <step id="7" name="LOCALIZATION CLEANUP (ANTI-JARGON REFINEMENT)">
    <target_files>
      <file>[MODIFY] @[backend_v2/l10n/fi.json#L110-L125]</file>
      <file>[MODIFY] @[backend_v2/l10n/en.json#L110-L125]</file>
    </target_files>
    <action>
In `backend_v2/l10n/fi.json`:
- Change `"sources_mcp_result": "Ulkoinen havainto / MCP-haun tulos:"` to `"sources_mcp_result": "Ulkoinen havainto:"`.
In `backend_v2/l10n/en.json`:
- Change `"sources_mcp_result": "External finding / MCP retrieval result:"` to `"sources_mcp_result": "External finding:"`.
    </action>
    <constraint invariant="anti_jargon_mandate">Remove internal protocol acronyms ('MCP') from user-facing report presentation.</constraint>
    <verification>Run `uv run python -c "import json; fi=json.load(open('backend_v2/l10n/fi.json', encoding='utf-8')); en=json.load(open('backend_v2/l10n/en.json', encoding='utf-8')); assert fi['sources_mcp_result'] == 'Ulkoinen havainto:'; assert en['sources_mcp_result'] == 'External finding:'"`.</verification>
  </step>

  <step id="8" name="FULL-DUPLEX SDUI SEMANTIC PARITY &amp; GLOBAL QUALITY GATES">
    <target_files>
      <file>[MODIFY] @[backend_v2/services/sdui/adapters/printable_sources_adapter.py#L64-324]</file>
      <file>[NEW] @[backend_v2/services/sdui/sanitizers/mcp_presentation_sanitizer.py]</file>
      <file>[VERIFY] @[backend_v2/api/routers/system/__init__.py]</file>
    </target_files>
    <action>
Execute the global backend quality audit and semantic parity verification gates.
Verify that @[backend_v2/api/routers/system/__init__.py] defines zero pseudo-MCP routers or loopback endpoints, strictly upholding the Zero Hardcoded Routers Ban.
    </action>
    <constraint invariant="zero_tolerance_audit_loop">All Ruff linting, MyPy strict typing, and Pytest suites must pass without errors or suppressions.</constraint>
    <verification>
Execute the following verification commands:
1. `uv run python scripts/backend_audit_loop.py backend_v2/services/sdui/sanitizers/mcp_presentation_sanitizer.py --test --ast-strict`
2. `uv run python scripts/backend_audit_loop.py backend_v2/services/sdui/adapters/printable_sources_adapter.py --test --ast-strict`
3. `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`
4. `uv run pytest backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py`
    </verification>
  </step>
</execution_protocol>
```

---

## ISTQB Test Scenarios & Coverage Matrix

### Positive & Negative Partition Scenarios

| Scenario ID | Test Name | Partition Type | Input Condition | Expected Result |
| :--- | :--- | :--- | :--- | :--- |
| **TC-SAN-01** | `test_tavily_real_cdata_json_sanitized` | Positive Valid | CDATA wrapped JSON with `query` and `results[0].content` | Strips CDATA, extracts substantive sentence from `content`, formats with terminal period, zero JSON artifacts |
| **TC-SAN-02** | `test_plain_text_cdata_sanitized` | Positive Valid | `<![CDATA[Faktalähde: Työterveyslaitos on suomalainen tutkimuslaitos.]]>` | Strips CDATA, preserves clean plain text, resolves badge to `Ulkoinen havainto:` |
| **TC-SAN-03** | `test_sentence_boundary_budgeting_long_content` | Boundary Condition | 600-character single finding string, max_chars=300 | Cuts cleanly at sentence terminal punctuation within $[180, 300]$ character window |
| **TC-SAN-04** | `test_empty_or_whitespace_cdata_returns_none` | Negative Equivalence | `<![CDATA[   ]]>` or `None` or `""` | Returns `None`, adapter omits empty line |
| **TC-SAN-05** | `test_malformed_pseudo_json_recovery` | Negative Resilient | `<![CDATA[{"corrupted: json string without closing]]>` | Recovers as plain text, strips XML tags and dangling braces, returns clean sentence |
| **TC-SAN-06** | `test_sdui_printable_sources_zero_technical_leakage` | Parity Integration | `AdapterContext` containing real Tavily and generic search traces | `MarkdownBlock` text contains `Ulkoinen havainto:` with clean finding; zero occurrence of `<![CDATA[`, `{"query":`, or raw technical keys |

---

## Verification Plan & Commands

### Localized Unit Tests
```powershell
uv run pytest backend_v2/tests/unit/services/sdui/sanitizers/test_mcp_presentation_sanitizer.py
uv run pytest backend_v2/tests/unit/services/sdui/adapters/test_printable_sources_mcp_sanitization.py
uv run pytest backend_v2/tests/unit/services/sdui/adapters/test_printable_sources_adapter.py
uv run pytest backend_v2/tests/unit/models/prompts/test_synthesis_directives.py
```

### Two-Stage Backend Audit Gates
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/services/sdui/sanitizers/mcp_presentation_sanitizer.py --test --ast-strict
uv run python scripts/backend_audit_loop.py backend_v2/services/sdui/adapters/printable_sources_adapter.py --test --ast-strict
uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py --test
```

### Full-Pipeline Integration & Parity Verification
```powershell
uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py
uv run pytest backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py
```
