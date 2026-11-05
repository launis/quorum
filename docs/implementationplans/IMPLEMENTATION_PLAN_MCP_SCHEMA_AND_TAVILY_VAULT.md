<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

# IMPLEMENTATION PLAN: Dynamic MCP Tool Schema Vocabulary, Studio `anyOf`/`array` Parameter Controls, and Tavily Seed Vault Upgrade

## 1. Objective & Architectural Background

1. **JSON Schema Draft 2020-12 Vocabulary Completeness (`MCPToolSchemaPropertyDTO` / `McpToolSchemaPropertyDto`)**:
   - External MCP servers built with FastMCP, Pydantic V2, and Zod (specifically and exhaustively: Jina MCP `https://mcp.jina.ai/v1` and Tavily MCP `https://mcp.tavily.com/mcp`) emit standard JSON Schema Draft 2020-12 keywords in `tools/list` responses—specifically `"format": "uri"` on URL fields in Jina's `read_url`, `extract_pdf`, `capture_screenshot_url`, and `guess_datetime_url` tools, alongside `pattern`, `uniqueItems`, `exclusiveMinimum`, `exclusiveMaximum`, `multipleOf`, `oneOf`, `allOf`, `examples`, `deprecated`, `readOnly`, `writeOnly`, `$ref`, and root `$defs`.
   - Extending `MCPToolSchemaPropertyDTO` in `@[backend_v2/models/dtos/mcp.py#L93-L317]` and `MCPToolInputSchemaDTO` in `@[backend_v2/models/dtos/mcp.py#L93-L317]` (plus their 1:1 Flutter Freezed counterparts `McpToolSchemaPropertyDto` and `McpToolInputSchemaDto` in `@[client_app_v2/lib/features/studio/models/mcp_gateway.dart#L12-L59]`) with the closed JSON Schema Draft 2020-12 keyword set allows any compliant MCP server to be discovered dynamically while preserving `ConfigDict(strict=True, extra="forbid", frozen=True)` and `@JsonSerializable(disallowUnrecognizedKeys: true)`.
2. **Nullable `anyOf`/`oneOf` Union Unwrapping and `array` Controls in `McpToolParamsPanel`**:
   - FastMCP and Pydantic V2 serialize optional MCP tool parameters (`param: T | None = None`) as outer properties with `type: None` and `any_of: [{"type": "...", ...}, {"type": "null"}]`.
   - In `@[client_app_v2/lib/features/studio/views/widgets/mcp_tool_params_panel.dart#L242-L370]`, `_buildPropertyControl` previously inspected only top-level `prop.enumValues` and `prop.type`, causing nullable enum, boolean, integer, and string-array parameters to fall through to plain string inputs.
   - Adding `_resolveEffectiveProperty(McpToolSchemaPropertyDto prop)` to unwrap the first non-null branch from `prop.anyOf` or `prop.oneOf` (while preserving outer `title`, `description`, and `defaultValue`) and adding a `JsonSchemaPropertyType.array` branch (parsing comma-separated values into `List<String>` and formatting `List<Object?>` values as comma-separated text in `_SchemaTextParamField` while guarding `didUpdateWidget` with `!_focusNode.hasFocus` so mid-keystroke commas are never clobbered) renders enum dropdowns (`search_depth`, `topic`, `time_range`), boolean switches (`include_raw_content`, `include_images`, `exact_match`), numeric inputs (`max_results`), and domain list inputs (`include_domains`, `exclude_domains`, `urls`).
3. **Seed Vault Upgrade for Default Tavily Gateway (`sys_0195f3a00000700080008172bda70c86`)**:
   - In `@[backend_v2/seed/seed_data.json#L209-L244]`, `sys_0195f3a00000700080008172bda70c86` (`slug: "default_mcp_gateway"`, `endpoint_url: "https://mcp.tavily.com/mcp"`) was seeded with a 1-property stub (`properties: {"query": ...}`). Because `_kRuntimeQueryKeys` in `@[client_app_v2/lib/features/studio/views/widgets/mcp_tool_params_panel.dart#L9-L14]` filters out `query`, `configurableProperties` was empty (`{}`), hiding `McpToolParamsPanel` for `default_mcp_gateway__tavily_search`.
   - Updating `sys_0195f3a00000700080008172bda70c86` in `@[backend_v2/seed/seed_data.json#L209-L244]` with the full discovered Tavily tool schemas (`tavily_search` with all 17 properties and `tavily_extract` with `capability: "document_reader"`) exposes all configurable Tavily parameters immediately in Quorum Studio.

---

## 2. Scope & Target Boundaries (5-Column Directives Table)

### Context Files (Read-Only)
- `@[backend_v2/services/orchestrator/schema_factory.py#L178-L267]` (`SchemaFactory._resolve_mcp_property_type`)
- `@[backend_v2/services/orchestrator/schema_factory.py#L332-L370]` (`SchemaFactory.create_mcp_tool_argument_model`)
- `@[backend_v2/services/mcp/dispatcher.py#L59-L759]` (`ToolDispatcher.build_search_arguments`)
- `@[backend_v2/seed/run_seed.py#L226-L254]` (`validate_all_seed_collections`)

<anti_targets>
- Do NOT modify `@[backend_v2/services/orchestrator/dag_executor/__init__.py]` or any DAG Engine orchestrator files.
- Do NOT modify `system_prompt` or `ai_description` fields in `@[backend_v2/seed/seed_data.json#L246-L250]`.
- Do NOT weaken `ConfigDict(strict=True, extra="forbid", frozen=True)` or `@JsonSerializable(disallowUnrecognizedKeys: true)` on any model.
</anti_targets>

### Target Files (`[MODIFY]`)

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `[MODIFY] @[backend_v2/models/dtos/mcp.py#L93-L317]` (`MCPToolSchemaPropertyDTO`) and `@[backend_v2/models/dtos/mcp.py#L93-L317]` (`MCPToolInputSchemaDTO`) | Rejecting valid JSON Schema Draft 2020-12 keywords (`format`, `pattern`, `uniqueItems`, `exclusiveMinimum`, `exclusiveMaximum`, `multipleOf`, `oneOf`, `allOf`, `examples`, `deprecated`, `readOnly`, `writeOnly`, `$ref`, `$defs`) or loosening `extra="forbid"`. | Closed JSON Schema Draft 2020-12 vocabulary with `ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)` and `AliasChoices` for wire-format camelCase/`$ref`/`$defs` and internal `snake_case`. | No vendor-specific schema subclasses or dynamic `extra="allow"` token shields. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/dtos/mcp.py --test --ast-strict` |
| `[MODIFY] @[backend_v2/tests/unit/models/dtos/test_mcp.py#L73-L91]` and `@[backend_v2/tests/unit/models/dtos/test_mcp.py#L463-L519]` | Passing raw dict literals to `.model_validate({...})` (`TD_MODEL_FACTORY`) and omitting negative BVA tests for `multipleOf <= 0` and `extra="forbid"`. | Rust `.model_validate_json(...)` wire-payload deserialization across positive and ISTQB BVA negative test partitions (`multipleOf: 0`, `multipleOf: -2`, unknown vendor keys). | No network calls or heavyweight database fixtures in DTO unit tests. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/tests/unit/models/dtos/test_mcp.py --test --ast-strict` |
| `[MODIFY] @[client_app_v2/lib/features/studio/models/mcp_gateway.dart#L12-L59]` (`McpToolSchemaPropertyDto`, `McpToolInputSchemaDto`) | Drift between backend Pydantic DTO fields and frontend Freezed `@JsonKey` attributes or dropping `disallowUnrecognizedKeys: true`. | 1:1 Cross-Domain DTO parity (`format`, `pattern`, `unique_items`, `exclusive_minimum`, `exclusive_maximum`, `multiple_of`, `one_of`, `all_of`, `examples`, `deprecated`, `read_only`, `write_only`, `ref`, `defs`). | No custom JSON converters where standard Freezed `@JsonKey` suffices. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_dto_parity.py` |
| `[MODIFY] @[client_app_v2/test/features/studio/models/mcp_gateway_test.dart#L167-L227]` | Happy-path-only Freezed deserialization tests without `disallowUnrecognizedKeys` and type-mismatch checks. | Positive hydration test for all 14 new JSON Schema Draft 2020-12 fields plus >=2 negative tests (`CheckedFromJsonException` / `TypeError`). | No redundant mock repositories for pure Freezed model tests. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/mcp_gateway.dart --build --micro` |
| `[MODIFY] @[client_app_v2/lib/features/studio/views/widgets/mcp_tool_params_panel.dart#L242-L447]` (`McpToolParamsPanel`, `_SchemaTextParamField`) | Inspecting only outer `prop.type` (ignoring nullable `anyOf`/`oneOf` unions), treating `array` properties as scalar strings, or clobbering `TextEditingController` text while `_focusNode.hasFocus` is true. | `_resolveEffectiveProperty` unwrapping non-null `anyOf`/`oneOf` branches, `JsonSchemaPropertyType.array` comma-separated `List<String>` control with `minItems`/`maxItems` BVA guards, and focus-safe `_formatCurrentValue` in `_SchemaTextParamField`. | No nested modal dialogs for simple string-array domain lists. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/mcp_tool_params_panel.dart --micro` |
| `[MODIFY] @[client_app_v2/test/features/studio/views/widgets/mcp_tool_params_panel_test.dart#L406-L527]` | Omitting widget tests for nullable `anyOf` union controls and `minItems`/`maxItems` array bounds. | `TC-STUDIO-UI-06` widget test verifying nullable `anyOf` enum dropdown, boolean switch, integer BVA (`minimum - 1`), and string-array BVA (`maxItems + 1`). | No full-app router scaffolding for isolated widget verification. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/mcp_tool_params_panel.dart --micro` |
| `[MODIFY] @[backend_v2/seed/seed_data.json#L209-L244]` (`sys_0195f3a00000700080008172bda70c86`) | Seeding `default_mcp_gateway` with a 1-property `query`-only stub that hides all configurable Tavily parameters in Studio. | Full discovered Tavily tool schemas (`tavily_search` with all 17 properties and `tavily_extract` with `capability: "document_reader"`) validated via `sanitize_seed_vault.py` and `run_seed.py local`. | No hardcoded API keys or non-schema vendor keys in `seed_data.json`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local --dry-run` |
| `[MODIFY] @[docs/swagger/openapi.json]` | Leaving `docs/swagger/openapi.json` out of sync with `MCPToolSchemaPropertyDTO` and `MCPToolInputSchemaDTO`. | Deterministic OpenAPI 3.1 schema regeneration via `scripts/generate_openapi.py`. | No manual edits to generated OpenAPI JSON. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/generate_openapi.py` |

---

## 3. Pre-Implementation Technical Debt Cleanups (Phase 1)

1. **`TD_MODEL_FACTORY` Raw Dict Literal Cleanup in `@[backend_v2/tests/unit/models/dtos/test_mcp.py#L73-L91]` and `@[backend_v2/tests/unit/models/dtos/test_mcp.py#L463-L519]`**:
   - Pre-flight execution of `audit_technical_debt.py --targets backend_v2/models/dtos/mcp.py backend_v2/tests/unit/models/dtos/test_mcp.py client_app_v2/lib/features/studio/models/mcp_gateway.dart client_app_v2/test/features/studio/models/mcp_gateway_test.dart client_app_v2/lib/features/studio/views/widgets/mcp_tool_params_panel.dart client_app_v2/test/features/studio/views/widgets/mcp_tool_params_panel_test.dart --include-one-hop` confirmed `0` findings across all production files and 12 1-hop callers, and identified `TD_MODEL_FACTORY` warnings in `backend_v2/tests/unit/models/dtos/test_mcp.py` where raw dict literals were passed to `.model_validate({...})`.
   - Convert raw dict literal `.model_validate({...})` calls in `backend_v2/tests/unit/models/dtos/test_mcp.py` to `.model_validate_json(...)` (matching Rust wire-frame parsing) so `audit_technical_debt.py --strict` passes with `0` warnings.

---

## 4. Detailed Execution Protocol (Hybrid XML Sandwich)

```xml
<execution_protocol>
  <step id="1" name="Phase 1: Test Technical Debt Cleanup &amp; Backend JSON Schema Draft 2020-12 Vocabulary in MCPToolSchemaPropertyDTO and MCPToolInputSchemaDTO">
    <constraint invariant="strict_pydantic_v2_rust">Enforce ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True) and PEP 593 Annotated[..., Field(...)] on all fields in MCPToolSchemaPropertyDTO and MCPToolInputSchemaDTO.</constraint>
    <constraint invariant="anti_happy_path_mandate">Include positive hydration tests for Jina/Tavily JSON Schema Draft 2020-12 keywords and at least 2 negative ISTQB BVA tests (multipleOf &lt;= 0 and extra="forbid") using .model_validate_json().</constraint>
    <action>In @[backend_v2/models/dtos/mcp.py#L93-L317] (MCPToolSchemaPropertyDTO) and @[backend_v2/models/dtos/mcp.py#L93-L317] (MCPToolInputSchemaDTO), add the closed JSON Schema Draft 2020-12 validation and composition fields (`format`, `pattern`, `unique_items`, `exclusive_minimum`, `exclusive_maximum`, `multiple_of`, `one_of`, `all_of`, `examples`, `deprecated`, `read_only`, `write_only`, `ref`, and `defs`) and update class docstrings.</action>
    <action>In @[backend_v2/tests/unit/models/dtos/test_mcp.py#L463-L519] and @[backend_v2/tests/unit/models/dtos/test_mcp.py#L463-L519], remediate TD_MODEL_FACTORY raw dict `.model_validate({...})` calls by using `.model_validate_json(...)` and add `test_mcp_tool_schema_draft_2020_12_vocabulary_and_jina_format_positive_and_negative` testing Jina `"format": "uri"`, `pattern`, `uniqueItems`, `exclusiveMinimum`, `exclusiveMaximum`, `multipleOf`, `oneOf`, `allOf`, `examples`, `deprecated`, `readOnly`, `writeOnly`, `$ref`, and `$defs`, plus negative BVA tests for `multipleOf: 0`, `multipleOf: -2`, and `nonStandardVendorKey`.</action>
    <action>Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/dtos/mcp.py backend_v2/tests/unit/models/dtos/test_mcp.py --test --ast-strict` and `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --targets backend_v2/models/dtos/mcp.py backend_v2/tests/unit/models/dtos/test_mcp.py --strict`.</action>
  </step>

  <step id="2" name="Phase 2: Frontend 1:1 Freezed DTO Parity &amp; OpenAPI Sync">
    <constraint invariant="anti_semantic_drift_renaming">Maintain 1:1 field and @JsonKey parity between backend MCPToolSchemaPropertyDTO/MCPToolInputSchemaDTO and frontend McpToolSchemaPropertyDto/McpToolInputSchemaDto with @JsonSerializable(disallowUnrecognizedKeys: true).</constraint>
    <action>In @[client_app_v2/lib/features/studio/models/mcp_gateway.dart#L12-L59], add `format`, `pattern`, `uniqueItems`, `exclusiveMinimum`, `exclusiveMaximum`, `multipleOf`, `oneOf`, `allOf`, `examples`, `deprecated`, `readOnly`, `writeOnly`, and `ref` to `McpToolSchemaPropertyDto`, and `defs` to `McpToolInputSchemaDto`.</action>
    <action>In @[client_app_v2/test/features/studio/models/mcp_gateway_test.dart#L167-L227], add `test_mcp_tool_schema_draft_2020_12_fields_and_defs_positive_and_negative` covering positive hydration of all 14 new fields and 2 negative tests (`disallowUnrecognizedKeys` and invalid field type).</action>
    <action>Regenerate @[docs/swagger/openapi.json] via `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/generate_openapi.py`, run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/mcp_gateway.dart --build --micro`, and verify 1:1 parity via `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_dto_parity.py`.</action>
  </step>

  <step id="3" name="Phase 3: Studio McpToolParamsPanel Nullable anyOf/oneOf Unwrapping &amp; Array Parameter Controls">
    <constraint invariant="desktop_pro_tool_interaction">Preserve FocusNode attachment, SystemMouseCursors.click, Flexible overflow protection, and guard didUpdateWidget with !_focusNode.hasFocus so active typing is never clobbered.</constraint>
    <action>In @[client_app_v2/lib/features/studio/views/widgets/mcp_tool_params_panel.dart#L242-L447], implement `_resolveEffectiveProperty(McpToolSchemaPropertyDto prop)` to unwrap the first non-null branch from `prop.anyOf` or `prop.oneOf` while preserving outer `title`, `description`, and `defaultValue`; add a `JsonSchemaPropertyType.array` branch in `_buildPropertyControl` (`ValueKey&lt;String&gt;('mcp_param_arr_${namespacedAlias}_$propName')`) that parses comma-separated strings into `List&lt;String&gt;` with `minItems`/`maxItems` BVA checks; and format `List&lt;Object?&gt;` values as comma-separated text in `_SchemaTextParamField` via `_formatCurrentValue`.</action>
    <action>In @[client_app_v2/test/features/studio/views/widgets/mcp_tool_params_panel_test.dart#L406-L527], add widget test `mcp_tool_params_panel_unwraps_nullable_any_of_and_parses_string_arrays (TC-STUDIO-UI-06)` verifying nullable `anyOf` enum dropdown selection, boolean toggle, integer input, comma-separated domain array parsing (`List&lt;String&gt;`), and 2 negative BVA assertions (`maxItems + 1` and `minimum - 1` inside `anyOf`).</action>
    <action>Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/mcp_tool_params_panel.dart --micro`.</action>
  </step>

  <step id="4" name="Phase 4: Seed Vault Upgrade for Default Tavily Gateway &amp; Global Verification Gates">
    <constraint invariant="database_schema_hallucination">Follow vault_mutation_protocol in 03_seed_vault.md: update only sys_0195f3a00000700080008172bda70c86 in seed_data.json, sanitize via sanitize_seed_vault.py, validate in-memory via run_seed.py local --dry-run and audit_database_atoms.py --strict, and re-seed via run_seed.py local.</constraint>
    <action>Update `sys_0195f3a00000700080008172bda70c86` (`default_mcp_gateway`) in @[backend_v2/seed/seed_data.json#L209-L244] with the full discovered Tavily tool schemas (`tavily_search` with all 17 properties and `tavily_extract` with `capability: "document_reader"`).</action>
    <action>Execute `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/sanitize_seed_vault.py`, `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local --dry-run`, `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_database_atoms.py --strict`, and `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local`.</action>
    <action>Execute global completion gates: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test` and `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build`.</action>
  </step>
</execution_protocol>
```

---

## 5. Step-by-Step Implementation Specification & Verbatim Code Payloads

### Step 1: Backend JSON Schema Draft 2020-12 Vocabulary in `MCPToolSchemaPropertyDTO` & `MCPToolInputSchemaDTO`

#### 1.1 Modify `@[backend_v2/models/dtos/mcp.py#L93-L317]` and `@[backend_v2/models/dtos/mcp.py#L93-L317]`
Add the closed JSON Schema Draft 2020-12 validation and composition fields to `MCPToolSchemaPropertyDTO` (`@[backend_v2/models/dtos/mcp.py#L93-L317]`) and `defs` to `MCPToolInputSchemaDTO` (`@[backend_v2/models/dtos/mcp.py#L93-L317]`):

```python
    format: Annotated[
        str | None,
        Field(default=None, description="Optional string semantic format hint (for example 'uri', 'date-time', 'email')."),
    ] = None
    pattern: Annotated[
        str | None,
        Field(default=None, description="Optional ECMA-262 regular expression pattern for string validation."),
    ] = None
    unique_items: Annotated[
        bool | None,
        Field(
            default=None,
            validation_alias=AliasChoices("uniqueItems", "unique_items"),
            description="Whether array items must be unique.",
        ),
    ] = None
    exclusive_minimum: Annotated[
        int | float | None,
        Field(
            default=None,
            validation_alias=AliasChoices("exclusiveMinimum", "exclusive_minimum"),
            description="Optional exclusive lower numeric bound.",
        ),
    ] = None
    exclusive_maximum: Annotated[
        int | float | None,
        Field(
            default=None,
            validation_alias=AliasChoices("exclusiveMaximum", "exclusive_maximum"),
            description="Optional exclusive upper numeric bound.",
        ),
    ] = None
    multiple_of: Annotated[
        int | float | None,
        Field(
            default=None,
            gt=0,
            validation_alias=AliasChoices("multipleOf", "multiple_of"),
            description="Optional numeric divisor constraint (must be strictly positive).",
        ),
    ] = None
    one_of: Annotated[
        list[MCPToolSchemaPropertyDTO] | None,
        Field(
            default=None,
            validation_alias=AliasChoices("oneOf", "one_of"),
            description="Optional list of mutually exclusive sub-schemas (oneOf).",
        ),
    ] = None
    all_of: Annotated[
        list[MCPToolSchemaPropertyDTO] | None,
        Field(
            default=None,
            validation_alias=AliasChoices("allOf", "all_of"),
            description="Optional list of intersected sub-schemas (allOf).",
        ),
    ] = None
    examples: Annotated[
        list[MCPArgumentValue] | None,
        Field(default=None, description="Optional list of example values for this property."),
    ] = None
    deprecated: Annotated[
        bool | None,
        Field(default=None, description="Whether this parameter is marked deprecated."),
    ] = None
    read_only: Annotated[
        bool | None,
        Field(
            default=None,
            validation_alias=AliasChoices("readOnly", "read_only"),
            description="Whether this property is marked read-only.",
        ),
    ] = None
    write_only: Annotated[
        bool | None,
        Field(
            default=None,
            validation_alias=AliasChoices("writeOnly", "write_only"),
            description="Whether this property is marked write-only.",
        ),
    ] = None
    ref: Annotated[
        str | None,
        Field(
            default=None,
            validation_alias=AliasChoices("$ref", "ref"),
            description="Optional JSON Schema $ref pointer string.",
        ),
    ] = None
```

And in `MCPToolInputSchemaDTO` (`@[backend_v2/models/dtos/mcp.py#L323-L376]`):

```python
    defs: Annotated[
        dict[str, MCPToolSchemaPropertyDTO] | None,
        Field(
            default=None,
            validation_alias=AliasChoices("$defs", "definitions", "defs"),
            description="Optional reusable sub-schema definitions map ($defs).",
        ),
    ] = None
```

---

### Step 2: Frontend 1:1 DTO Parity & Studio `McpToolParamsPanel` (`anyOf`/`oneOf` Unwrapping + `array` Controls)

#### 2.1 Modify `@[client_app_v2/lib/features/studio/models/mcp_gateway.dart#L12-L59]`
Add the matching `@JsonKey` fields to `McpToolSchemaPropertyDto` and `McpToolInputSchemaDto`:

```dart
    String? format,
    String? pattern,
    @JsonKey(name: 'unique_items') bool? uniqueItems,
    @JsonKey(name: 'exclusive_minimum') num? exclusiveMinimum,
    @JsonKey(name: 'exclusive_maximum') num? exclusiveMaximum,
    @JsonKey(name: 'multiple_of') num? multipleOf,
    @JsonKey(name: 'one_of') List<McpToolSchemaPropertyDto>? oneOf,
    @JsonKey(name: 'all_of') List<McpToolSchemaPropertyDto>? allOf,
    List<Object?>? examples,
    bool? deprecated,
    @JsonKey(name: 'read_only') bool? readOnly,
    @JsonKey(name: 'write_only') bool? writeOnly,
    String? ref,
```

And on `McpToolInputSchemaDto`:

```dart
    Map<String, McpToolSchemaPropertyDto>? defs,
```

#### 2.2 Modify `@[client_app_v2/lib/features/studio/views/widgets/mcp_tool_params_panel.dart#L242-L447]`
1. Add `_resolveEffectiveProperty(McpToolSchemaPropertyDto prop)` to unwrap nullable `anyOf` / `oneOf` schemas emitted by FastMCP / Pydantic V2 (where `prop.type == null` and `prop.anyOf` or `prop.oneOf` contains a non-null branch alongside `{type: null}`), copying `nonNullBranch` with outer `title`, `description`, and `defaultValue` fallbacks.
2. Add a `JsonSchemaPropertyType.array` control branch in `_buildPropertyControl` so string-array parameters (`include_domains`, `exclude_domains`, `urls`) render a `_SchemaTextParamField` (`ValueKey<String>('mcp_param_arr_${namespacedAlias}_$propName')`) that:
   - Splits comma-separated input strings on `,`, trims each item, filters out empty entries, validates `minItems` / `maxItems` bounds if present, and stores `List<String>` in `mcpToolParams` (or `null` when empty).
   - Formats `List<Object?>` `currentValue` as `currentValue.map((Object? e) => e.toString()).join(', ')` inside `_SchemaTextParamField` via `_formatCurrentValue`, and guards `didUpdateWidget` with `!_focusNode.hasFocus` so mid-keystroke commas are preserved.

---

### Step 3: Seed Vault Upgrade for Tavily (`sys_0195f3a00000700080008172bda70c86`) in `@[backend_v2/seed/seed_data.json#L209-L244]`

#### Proposed JSON Snippet Delta for `@[backend_v2/seed/seed_data.json#L209-L244]`:
```json
    {
      "id": "sys_0195f3a00000700080008172bda70c86",
      "slug": "default_mcp_gateway",
      "endpoint_url": "https://mcp.tavily.com/mcp",
      "transport_type": "streamable_http",
      "auth_type": "bearer",
      "auth_env_var": "TAVILY_API_KEY",
      "timeout_seconds": 30,
      "type": "mcp_gateways",
      "tools": [
        {
          "tool_id": "tavily_search",
          "enabled": true,
          "capability": "search",
          "name": {
            "translations": {
              "en": "Tavily AI Search",
              "fi": "Tavily AI -haku"
            }
          },
          "description": "Search the web for current information on any topic. Use for news, facts, or data beyond your knowledge cutoff, and before answering any question about specific facts, figures or recent events. Returns snippets and source URLs. Results are short excerpts; read a page with tavily_extract to confirm what it says.",
          "input_schema": {
            "type": "object",
            "properties": {
              "query": {
                "type": "string",
                "description": "Search query. Keep it short and specific, in the words the page itself would use; one idea per query."
              },
              "max_results": {
                "description": "The maximum number of search results to return. Ask for 10 when looking for a specific fact, page or entity.",
                "any_of": [
                  { "type": "integer", "description": "" },
                  { "type": "null", "description": "" }
                ]
              },
              "search_depth": {
                "description": "The depth of the search. 'basic' for generic results, 'advanced' for more thorough search, 'fast' for optimized low latency with high relevance, 'ultra-fast' for prioritizing latency above all else.",
                "any_of": [
                  {
                    "type": "string",
                    "description": "",
                    "enum_values": ["basic", "advanced", "fast", "ultra-fast"]
                  },
                  { "type": "null", "description": "" }
                ]
              },
              "topic": {
                "description": "Search category. Use 'general' for almost all searches, including current events and requests that combine news with other information. Use 'news' only when the user explicitly asks for news, headlines, or news coverage.",
                "any_of": [
                  {
                    "type": "string",
                    "description": "",
                    "enum_values": ["general", "news"]
                  },
                  { "type": "null", "description": "" }
                ]
              },
              "time_range": {
                "description": "The time range back from the current date to include in the search results. Filters by when a page was published, not by when the events it describes happened.",
                "any_of": [
                  {
                    "type": "string",
                    "description": "",
                    "enum_values": ["day", "week", "month", "year"]
                  },
                  { "type": "null", "description": "" }
                ]
              },
              "include_images": {
                "description": "Include a list of query-related images in the response",
                "any_of": [
                  { "type": "boolean", "description": "" },
                  { "type": "null", "description": "" }
                ]
              },
              "include_image_descriptions": {
                "description": "Include a list of query-related images and their descriptions in the response",
                "any_of": [
                  { "type": "boolean", "description": "" },
                  { "type": "null", "description": "" }
                ]
              },
              "include_raw_content": {
                "description": "Include the cleaned and parsed HTML content of each search result. Whole pages can make the response too large to read; to read one page, use tavily_extract with a query instead.",
                "any_of": [
                  { "type": "boolean", "description": "" },
                  { "type": "null", "description": "" }
                ]
              },
              "include_domains": {
                "description": "A list of domains to specifically include in the search results, if the user asks to search on specific sites set this to the domain of the site. Use full domains (for example 'en.wikipedia.org' or 'sec.gov'), not top-level suffixes.",
                "any_of": [
                  {
                    "type": "array",
                    "description": "",
                    "items": { "type": "string", "description": "" }
                  },
                  { "type": "null", "description": "" }
                ]
              },
              "exclude_domains": {
                "description": "List of domains to specifically exclude, if the user asks to exclude a domain set this to the domain of the site",
                "any_of": [
                  {
                    "type": "array",
                    "description": "",
                    "items": { "type": "string", "description": "" }
                  },
                  { "type": "null", "description": "" }
                ]
              },
              "country": {
                "description": "Boost search results from a specific country. Must be a full country name (for example 'United States', 'Japan', 'Germany').",
                "any_of": [
                  { "type": "string", "description": "" },
                  { "type": "null", "description": "" }
                ]
              },
              "include_favicon": {
                "description": "Whether to include the favicon URL for each result",
                "any_of": [
                  { "type": "boolean", "description": "" },
                  { "type": "null", "description": "" }
                ]
              },
              "start_date": {
                "description": "Will return all results after the specified start date. Required to be written in the format YYYY-MM-DD.",
                "any_of": [
                  { "type": "string", "description": "" },
                  { "type": "null", "description": "" }
                ]
              },
              "end_date": {
                "description": "Will return all results before the specified end date. Required to be written in the format YYYY-MM-DD.",
                "any_of": [
                  { "type": "string", "description": "" },
                  { "type": "null", "description": "" }
                ]
              },
              "exact_match": {
                "description": "Only return results containing the exact phrase(s) in quotes in your query",
                "any_of": [
                  { "type": "boolean", "description": "" },
                  { "type": "null", "description": "" }
                ]
              },
              "include_published_date": {
                "description": "Include detected publication dates (beta)",
                "any_of": [
                  { "type": "boolean", "description": "" },
                  { "type": "null", "description": "" }
                ]
              },
              "filter_by_published_date": {
                "description": "Filter results to the requested date window and exclude results with no detected publication date",
                "any_of": [
                  { "type": "boolean", "description": "" },
                  { "type": "null", "description": "" }
                ]
              }
            },
            "required": ["query"],
            "additional_properties": false
          }
        },
        {
          "tool_id": "tavily_extract",
          "enabled": true,
          "capability": "document_reader",
          "name": {
            "translations": {
              "en": "Tavily Extract",
              "fi": "Tavily-sivunlukija"
            }
          },
          "description": "Extract content from URLs. Returns raw page content in markdown or text format.",
          "input_schema": {
            "type": "object",
            "properties": {
              "urls": {
                "type": "array",
                "description": "List of URLs to extract content from.",
                "items": { "type": "string", "description": "" }
              },
              "extract_depth": {
                "type": "string",
                "description": "Use 'advanced' for protected sites or tables/embedded content",
                "enum_values": ["basic", "advanced"],
                "default": "basic"
              },
              "include_images": {
                "type": "boolean",
                "description": "Include images from pages",
                "default": false
              },
              "format": {
                "type": "string",
                "description": "Output format",
                "enum_values": ["markdown", "text"],
                "default": "markdown"
              },
              "include_favicon": {
                "type": "boolean",
                "description": "Include favicon URLs",
                "default": false
              },
              "query": {
                "type": "string",
                "description": "Query to rerank content chunks by relevance.",
                "default": ""
              },
              "include_usage": {
                "description": "Include credit usage",
                "any_of": [
                  { "type": "boolean", "description": "" },
                  { "type": "null", "description": "" }
                ]
              }
            },
            "required": ["urls"],
            "additional_properties": false
          }
        }
      ]
    }
```

---

## 6. Architectural Safeguards & Verification Plan (ISTQB Test Matrix)

### Automated Unit & Structural Tests
- **Scenario 1 (Happy Path - Backend & Frontend JSON Schema Draft 2020-12 Vocabulary)**:
  - Input: `tools/list` JSON-RPC 2.0 frame containing Jina `"format": "uri"`, `pattern`, `uniqueItems`, `exclusiveMinimum`, `exclusiveMaximum`, `multipleOf`, `oneOf`, `allOf`, `examples`, `deprecated`, `readOnly`, `writeOnly`, `$ref`, and root `$defs`.
  - Expected Output: Both `MCPJsonRpcResponseDTO.model_validate_json` and `McpToolInputSchemaDto.fromJson` deserialize all fields with 100% lossless accuracy.
- **Scenario 2 (Happy Path - Studio `anyOf` Unwrapping & String Array Control)**:
  - Input: `AllowedMcpTool` with nullable `anyOf` properties (`search_depth` enum, `max_results` integer, `include_raw_content` boolean, `include_domains` string array) rendered in `McpToolParamsPanel`.
  - Expected Output: Selecting `'advanced'`, toggling `true`, entering `'10'`, and entering `'fi.wikipedia.org, en.wikipedia.org'` emits `{'search_depth': 'advanced', 'include_raw_content': true, 'max_results': 10, 'include_domains': ['fi.wikipedia.org', 'en.wikipedia.org']}`.
- **Scenario 3 (Negative Path 1 - Unrecognized Vendor Keyword Rejection)**:
  - Input: `{"type": "string", "nonStandardVendorKey": true}` passed to `MCPToolSchemaPropertyDTO.model_validate_json` and `McpToolSchemaPropertyDto.fromJson`.
  - Expected Output: Rejected immediately via `ValidationError` (`extra="forbid"`) on backend and `CheckedFromJsonException` / `FormatException` (`disallowUnrecognizedKeys: true`) on frontend.
- **Scenario 4 (Negative Path 2 - ISTQB Boundary Value Violations)**:
  - Input: `{"type": "number", "multipleOf": 0}` and `{"type": "number", "multipleOf": -2}` on backend; entering 4 comma-separated domains when `maxItems: 3` (`maxItems + 1`) and `0` when `anyOf[0].minimum: 1` (`minimum - 1`) in `McpToolParamsPanel`.
  - Expected Output: Backend raises `ValidationError`; `McpToolParamsPanel` rejects out-of-bounds inputs without mutating `mcpToolParams`.

<dod_checklist>
- [x] `MCPToolSchemaPropertyDTO` (`@[backend_v2/models/dtos/mcp.py#L93-L317]`) and `MCPToolInputSchemaDTO` (`@[backend_v2/models/dtos/mcp.py#L93-L317]`) include the complete JSON Schema Draft 2020-12 property vocabulary (`format`, `pattern`, `unique_items`, `exclusive_minimum`, `exclusive_maximum`, `multiple_of`, `one_of`, `all_of`, `examples`, `deprecated`, `read_only`, `write_only`, `ref`, and `defs`).
- [x] `McpToolSchemaPropertyDto` and `McpToolInputSchemaDto` (`@[client_app_v2/lib/features/studio/models/mcp_gateway.dart#L12-L59]`) maintain 1:1 field and `@JsonKey` parity with backend DTOs, verified by `scripts/audit_dto_parity.py`.
- [x] `McpToolParamsPanel` (`@[client_app_v2/lib/features/studio/views/widgets/mcp_tool_params_panel.dart#L242-L447]`) unwraps nullable `anyOf`/`oneOf` union properties and renders string-array parameters (`JsonSchemaPropertyType.array`) as comma-separated list inputs producing `List<String>`.
- [x] `sys_0195f3a00000700080008172bda70c86` (`default_mcp_gateway`) in `@[backend_v2/seed/seed_data.json#L209-L244]` contains the full Tavily tool schema (`tavily_search` with all 17 properties and `tavily_extract`), sanitized and re-seeded into the local database via `run_seed.py local`.
- [x] Positive and >=2 negative ISTQB BVA unit/widget tests pass in `@[backend_v2/tests/unit/models/dtos/test_mcp.py#L463-L519]`, `@[client_app_v2/test/features/studio/models/mcp_gateway_test.dart#L167-L227]`, and `@[client_app_v2/test/features/studio/views/widgets/mcp_tool_params_panel_test.dart#L406-L527]`, with `0` `TD_MODEL_FACTORY` warnings in `audit_technical_debt.py --strict`.
</dod_checklist>

### Global Completion Gates & Mandatory Final E2E REST API Verification Gate
```powershell
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/dtos/mcp.py backend_v2/tests/unit/models/dtos/test_mcp.py --test --ast-strict
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/generate_openapi.py
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_dto_parity.py
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/sanitize_seed_vault.py
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local --dry-run
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_database_atoms.py --strict
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test
```
- **Mandatory Final E2E REST API Verification Gate**:
  - Windows / PowerShell: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
  - Unix / Bash: `RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
