# EPIC 134: v2_core.py God Code Decomposition

## 1. Goal Description & Background (Objective & Problem Statement)
This Epic focuses on decomposing the massive "God Code" file `@[backend_v2/models/v2_core.py]` (1702 lines, 107+ import consumers) as mandated by the parent EPIC 133. Currently, this file violates the Quorum architectural rules by acting as a monolithic dumping ground for 50+ distinct Pydantic model classes spanning at least 8 unrelated business domains (I18N, Prompt Ontology, LLM Configuration, MCP Infrastructure, Lexicons, Workflow DAG Definitions, Execution Lifecycle, Report/Scorecard Presentation). This directly violates `anti_god_file_dumping` (400-line hard limit), `strict_model_location` (which explicitly bans "dumping new models into the monolithic v2_core.py"), and `domain_model_purity_mandate`.

Additionally, the file contains:
1. **Finnish string literals** in error messages and field descriptions (specifically L258 `"Vain tiivis kuvaus itse konseptista, ei ajo-ohjeita"`, L259 `"Mitä ankkuria etsitään"`, L262 `"Varsinainen sääntö, joka datan on täytettävä"`, L296 `"Käänteinen sääntö (myrkyn etsintä) vaatii EHDOTTOMASTI 'EXISTS' -aggregaation..."`, L303, L307, L494, L500-501, L511, L525-526) violating `english_language_mandate`.
2. **Hardcoded `Literal` strings** that MUST be centralized Enums per `domain_model_purity_mandate` (specifically `Literal["EXISTS", "ALL_MUST_COMPLY"]`, `Literal["EXTRACTIVE_SENSOR", "COGNITIVE_JUDGEMENT"]`, `Literal["sentence", "paragraph", "document", "adjacent_paragraphs"]`, `Literal["llm", "logic"]`, `Literal["safe", "unsafe"]`, `Literal["markdown", "hero_insight", "grid"]`, `Literal["1d_metrics", "2d_compare", "3d_matrix", "default", "text_only", "matrix_summary"]`, `Literal["full", "titles_only", "none"]`, `Literal["original", "custom", "normalized_100"]`, `Literal["pdf", "docx", "raw_json", "xlsx"]`).
3. **`hasattr()` duck-typing** (L471 `hasattr(s, "score")`) and **`getattr()` fallbacks** (L506, L508) inside `PromptBlock.pre_validate_block_consistency`.
4. **Bottom-of-file circular dependency resolution** via deferred imports and `model_rebuild()` calls (L1683-1702) that MUST be carefully managed during extraction.

The objective is to implement the Strangler Fig pattern to split the 50+ classes into cohesive domain-specific files under `@[backend_v2/models/domain/]` and `@[backend_v2/models/dtos/]`, achieving a target state where v2_core.py contains fewer than 300 lines (Hollow Shell proxy during transition, then residual cross-domain models after sunset). All Finnish strings will be translated to English, all hardcoded Literals will be converted to centralized Enums, and all duck-typing will be eradicated.

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (What We Will REMOVE)
- **INTENTIONALLY DROPPED**: All 50+ class definitions currently in `@[backend_v2/models/v2_core.py]` will be physically relocated to dedicated domain files. The original file will be reduced to a Hollow Shell proxy (Strangler Fig pattern) during transition, then to a minimal residual file containing only cross-domain models that cannot be cleanly separated.
- **INTENTIONALLY DROPPED**: All Finnish string literals in error messages and field descriptions (12+ instances across TDAAssertion and PromptBlock validators).
- **INTENTIONALLY DROPPED**: All raw `Literal[...]` type annotations that have a closed set of values. These will be replaced with centralized Enum classes in `@[backend_v2/models/enums.py]`.
- **INTENTIONALLY DROPPED**: `hasattr(s, "score")` at L471 inside `PromptBlock.pre_validate_block_consistency` — replaced by `isinstance(s, dict)` guard with direct `.score` attribute access on the else branch.
- **INTENTIONALLY DROPPED**: `getattr(scale, "claims", None)` at L506 and `getattr(scale, "score", None)` at L508 — replaced by direct typed attribute access.

### Retained SSOT Invariants (What We Will RETAIN)
- All class names, field names, field types, and JSON serialization shapes will remain **100% identical**. Zero behavioral change for API consumers.
- The `__all__` export list in v2_core.py will be maintained via Strangler Fig re-exports during transition.
- The `model_rebuild()` calls for circular dependency resolution will be preserved and relocated to the appropriate target files.
- The `TYPE_CHECKING` guard for `ExecutionRecord` forward references to `state.py` will be preserved.

### Compliance & Modernity Gates
- **Test Contract Specification**: The generated extraction plans MUST include `<test_contracts>` XML blocks for extracted components, defining exact regression tests to lock in current behavior (Golden Master) before extraction.
- **Pydantic Strictness**: All extracted models MUST retain their existing `ConfigDict` settings. Models inheriting from `V2CoreBase` get `ConfigDict(strict=True, extra="forbid", frozen=True)` automatically. Models using `BaseModel` directly (specifically `ErrorDetailsDTO`, `HydratedAtomDTO`, `ExtractedValueDTO`, `AtomResultDTO`, `BaseMatrixXAI`, `BaseTDAExtraction`) MUST preserve their explicit `ConfigDict`.
- **English Language Mandate**: All Finnish error messages and field descriptions MUST be translated to English during extraction.
- **Enum Centralization**: All closed-set `Literal[...]` types MUST be converted to Enum classes (with corresponding `Lax` aliases) in `@[backend_v2/models/enums.py]`.
- **Zero Duck-Typing**: All `hasattr()`, `getattr()` with defaults inside validators MUST be replaced with typed access patterns.
- **Strangler Fig Proxy**: The original `v2_core.py` MUST remain as a Hollow Shell proxy during transition, re-exporting all moved classes, to ensure zero import breakage across 107+ consumers.

### Producer-Consumer Integration Check
- **Producer**: Database seeder (`@[backend_v2/seed/seed_registry.py]`), REST API routers (`@[backend_v2/api/routers/]`).
- **Consumer**: 107+ files across the entire backend (services, hooks, routers, tests, LLM handlers, database repositories). The structural changes MUST NOT alter any serialized JSON shape.

> [!WARNING]
> **Circular Dependency Resolution**: `v2_core.py` currently uses bottom-of-file deferred imports (L1683-1689) and `model_rebuild()` calls (L1691-1701) to resolve circular dependencies with `state.py` and `view/sdui.py`. When extracting `ExecutionRecord` and report DTOs, these resolution mechanisms MUST be carefully relocated. The executor MUST verify that `model_rebuild()` is called AFTER all participating modules are imported.

> [!WARNING]
> **Existing `domain/mcp.py` Collision**: `@[backend_v2/models/domain/mcp.py]` already exists (218 lines) and currently imports `MCPAuditTrace` from `v2_core.py` (line 13). When extracting `AllowedMCPTool`, `MCPAuditTrace`, and `SystemConfigMCPGateways` from v2_core.py, they MUST be merged INTO the existing `domain/mcp.py` file (not a new file). The executor MUST update the import at `domain/mcp.py` L13 to become a local class definition.

### Complete Class Routing Map (Post-Decomposition)

| Class | Current Location (v2_core.py lines) | Target Location |
|-------|-------------------------------------|-----------------|
| `I18nText` | L96-184 | [NEW] `@[backend_v2/models/domain/i18n.py]` |
| `TheoryGrounding` | L187-196 | [NEW] `@[backend_v2/models/domain/prompt_blocks.py]` |
| `AcceptanceCriterion` | L199-203 | [NEW] `@[backend_v2/models/domain/prompt_blocks.py]` |
| `AntiPattern` | L206-210 | [NEW] `@[backend_v2/models/domain/prompt_blocks.py]` |
| `TDAAssertion` | L213-310 | [NEW] `@[backend_v2/models/domain/prompt_blocks.py]` |
| `MatrixClaim` | L313-328 | [NEW] `@[backend_v2/models/domain/prompt_blocks.py]` |
| `MatrixRow` | L331-340 | [NEW] `@[backend_v2/models/domain/prompt_blocks.py]` |
| `MatrixScale` | L343-360 | [NEW] `@[backend_v2/models/domain/prompt_blocks.py]` |
| `PromptBlock` | L363-531 | [NEW] `@[backend_v2/models/domain/prompt_blocks.py]` |
| `ChatMessageDTO` | L534-543 | [NEW] `@[backend_v2/models/domain/chat.py]` |
| `ChatHistoryDTO` | L546-553 | [NEW] `@[backend_v2/models/domain/chat.py]` |
| `DataDictionaryField` | L556-562 | [NEW] `@[backend_v2/models/domain/execution_lifecycle.py]` |
| `ModelProfile` | L565-589 | [NEW] `@[backend_v2/models/domain/llm_config.py]` |
| `SystemConfigModelRegistry` | L592-600 | [NEW] `@[backend_v2/models/domain/llm_config.py]` |
| `AllowedMCPTool` | L603-611 | [MODIFY] `@[backend_v2/models/domain/mcp.py]` (MERGE) |
| `MCPAuditTrace` | L614-633 | [MODIFY] `@[backend_v2/models/domain/mcp.py]` (MERGE) |
| `SystemConfigMCPGateways` | L636-644 | [MODIFY] `@[backend_v2/models/domain/mcp.py]` (MERGE) |
| `LexiconConfigPayload` | L647-653 | [NEW] `@[backend_v2/models/domain/lexicons.py]` |
| `SystemConfigPerformativeLexicons` | L656-668 | [NEW] `@[backend_v2/models/domain/lexicons.py]` |
| `LexiconSuggestionListDTO` | L671-676 | [NEW] `@[backend_v2/models/domain/lexicons.py]` |
| `Step` | L679-766 | [NEW] `@[backend_v2/models/domain/workflow_steps.py]` |
| `StepRule` | L769-801 | [NEW] `@[backend_v2/models/domain/workflow_steps.py]` |
| `Role` | L804-811 | [NEW] `@[backend_v2/models/domain/workflow_steps.py]` |
| `QuestionnaireItem` | L814-819 | [NEW] `@[backend_v2/models/domain/workflow.py]` |
| `ExpectedInput` | L822-881 | [NEW] `@[backend_v2/models/domain/workflow.py]` |
| `HumanOverrideRequest` | L884-891 | STAYS in `@[backend_v2/models/v2_core.py]` |
| `HumanOverrideDTO` | L894-901 | STAYS in `@[backend_v2/models/v2_core.py]` |
| `ScorecardAtomDTO` | L904-922 | [NEW] `@[backend_v2/models/dtos/report_data.py]` |
| `TDAPending` | L925-926 | [NEW] `@[backend_v2/models/dtos/report_data.py]` |
| `TDAEvaluated` | L929-933 | [NEW] `@[backend_v2/models/dtos/report_data.py]` |
| `TDADlq` | L936-939 | [NEW] `@[backend_v2/models/dtos/report_data.py]` |
| `TDAStateUnion` | L942 | [NEW] `@[backend_v2/models/dtos/report_data.py]` |
| `MatrixScorecardRowDTO` | L945-1011 | [NEW] `@[backend_v2/models/dtos/report_data.py]` |
| `SynthesisConfigDTO` | L1014-1050 | STAYS in `@[backend_v2/models/v2_core.py]` |
| `ErrorDetailsDTO` | L1053-1056 | [NEW] `@[backend_v2/models/dtos/report_data.py]` |
| `HydratedAtomDTO` | L1059-1067 | [NEW] `@[backend_v2/models/dtos/report_data.py]` |
| `ExtractedValueDTO` | L1070-1073 | [NEW] `@[backend_v2/models/dtos/report_data.py]` |
| `AtomResultDTO` | L1076-1117 | [NEW] `@[backend_v2/models/dtos/report_data.py]` |
| `ExecutionMetricsDTO` | L1120-1125 | [NEW] `@[backend_v2/models/dtos/report_data.py]` |
| `ReportDataDTO` | L1128-1202 | [NEW] `@[backend_v2/models/dtos/report_data.py]` |
| `OutputLayoutBlock` | L1205-1241 | STAYS in `@[backend_v2/models/v2_core.py]` |
| `OutputProfile` | L1244-1328 | STAYS in `@[backend_v2/models/v2_core.py]` |
| `Workflow` | L1331-1457 | [NEW] `@[backend_v2/models/domain/workflow.py]` |
| `FrozenContext` | L1460-1471 | [NEW] `@[backend_v2/models/domain/execution_lifecycle.py]` |
| `ExecutionCreate` | L1474-1495 | [NEW] `@[backend_v2/models/domain/execution_lifecycle.py]` |
| `ExecutionStepState` | L1498-1510 | [NEW] `@[backend_v2/models/domain/execution_lifecycle.py]` |
| `ExtensionMetricsDTO` | L1513-1519 | [NEW] `@[backend_v2/models/dtos/report_data.py]` |
| `RenderedSynthesisCache` | L1522-1539 | [NEW] `@[backend_v2/models/domain/execution_lifecycle.py]` |
| `ExecutionRecord` | L1542-1596 | [NEW] `@[backend_v2/models/domain/execution_lifecycle.py]` |
| `JobAcceptedDTO` | L1598-1603 | STAYS in `@[backend_v2/models/v2_core.py]` |
| `EvidenceRejectionRequest` | L1606-1609 | STAYS in `@[backend_v2/models/v2_core.py]` |
| WorkflowSchemaResponse (type alias) | L1612 | STAYS in `@[backend_v2/models/v2_core.py]` |
| `BaseMatrixXAI` | L1615-1623 | [NEW] `@[backend_v2/models/domain/llm_extraction.py]` |
| `BaseTDAExtraction` | L1626-1680 | [NEW] `@[backend_v2/models/domain/llm_extraction.py]` |

**Post-decomposition v2_core.py residual** (~250 lines):
`HumanOverrideRequest`, `HumanOverrideDTO`, `SynthesisConfigDTO`, `OutputLayoutBlock`, `OutputProfile`, `JobAcceptedDTO`, `EvidenceRejectionRequest`, WorkflowSchemaResponse, Strangler Fig re-exports (during transition), `model_rebuild()` section.

### New Enum Classes Required in `@[backend_v2/models/enums.py]`

| Enum Name | Values | Replaces Literal in |
|-----------|--------|---------------------|
| `AggregationMode` | `EXISTS`, `ALL_MUST_COMPLY` | `TDAAssertion.aggregation_mode` |
| `EvaluationTrack` | `EXTRACTIVE_SENSOR`, `COGNITIVE_JUDGEMENT` | `TDAAssertion.evaluation_track` |
| `BoundingBoxScope` | `sentence`, `paragraph`, `document`, `adjacent_paragraphs` | `TDAAssertion.bounding_box_scope` |
| `StepExecutionType` | `llm`, `logic` | `Step.type` |
| `StepSafety` | `safe`, `unsafe` | `Step.safety` |
| `ExpectedSduiType` | `markdown`, `hero_insight`, `grid` | `StepRule.expected_sdui_type` |
| `PresetView` | `1d_metrics`, `2d_compare`, `3d_matrix`, `default`, `text_only`, `matrix_summary` | `OutputLayoutBlock.preset_view` |
| `TextDeliveryMode` | `full`, `titles_only`, `none` | `OutputLayoutBlock.text_delivery_mode` |
| `DisplayScale` | `original`, `custom`, `normalized_100` | `OutputProfile.display_scale` |
| `ExportFormat` | `pdf`, `docx`, `raw_json`, `xlsx` | `SynthesisConfigDTO.allowed_exports`, `Workflow.allowed_exports` |

Each Enum MUST also have a corresponding `Lax` type alias (using `Union[EnumType, str]` pattern) for database ingestion tolerance, following the existing pattern in `@[backend_v2/models/enums.py]`.

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Golden Master & Coverage Verification (MANDATORY PREREQUISITE)
- **Step 1.1**: Run `uv run pytest --cov=backend_v2.models.v2_core backend_v2/tests/ --cov-report=term-missing` to verify current test coverage. Coverage MUST be above 80% before any decomposition begins. If below 80%, write Golden Master tests capturing the exact current output BEFORE proceeding.
- **Step 1.2**: Catalog all import consumers via `grep_search` for `from backend_v2.models.v2_core import`. The preliminary count is 107+ files. The executor MUST produce the exhaustive consumer-to-class mapping before Phase 2 begins.

### Phase 2: Enum Centralization (PREREQUISITE for Domain Extraction)
- **Step 2.1**: Create the 10 new Enum classes listed in Section 2 inside `@[backend_v2/models/enums.py]`, following the existing `StrEnum` + `Lax` alias pattern.
- **Step 2.2**: Update the `Literal[...]` type annotations inside v2_core.py to reference the new Enums (with `Lax` variants for database-facing fields). This step modifies v2_core.py in-place WITHOUT moving classes.
- **Step 2.3**: Run `uv run python scripts/backend_audit_loop.py backend_v2 --test` to verify zero behavioral change. Perform atomic `git commit`.

### Phase 3: Finnish String Eradication & Duck-Typing Cleanup
- **Step 3.1**: Translate ALL Finnish error messages and field descriptions in v2_core.py to English. The complete list of Finnish strings to translate is:
  - L258: Replace literal string `"Vain tiivis kuvaus itse konseptista, ei ajo-ohjeita"` with `"Concise description of the concept itself, no execution instructions"`
  - L259: Replace literal string `"Mitä ankkuria etsitään (ent. STEP 1)"` with `"The anchor target to search for"`
  - L262: Replace literal string `"Varsinainen sääntö, joka datan on täytettävä (ent. EXTRACTION CONDITION)"` with `"The actual rule that the data must satisfy"`
  - L296: Replace literal string `"Käänteinen sääntö (myrkyn etsintä) vaatii EHDOTTOMASTI 'EXISTS' -aggregaation..."` with `"Inverse evidence (poison detection) REQUIRES 'EXISTS' aggregation mode..."`
  - L303: Replace literal string `"EXTRACTIVE_SENSOR -rata vaatii vähintään yhden haettavan faktan (facts_to_find)."` with `"EXTRACTIVE_SENSOR track requires at least one fact to find (facts_to_find)."`
  - L307: Replace literal string `"EXTRACTIVE_SENSOR -rata vaatii määrittämään loogisen lausekkeen (logical_expression)."` with `"EXTRACTIVE_SENSOR track requires a logical expression (logical_expression)."`
  - L494: Replace literal string `"on oltava suurempi kuin scale_min"` with `"must be greater than scale_min"`
  - L500-501: Replace literal string `"Jos scales on valittu käyttöön, siellä on pakko olla vähintään yksi MatrixScale (len > 0)."` with `"If scales are enabled, at least one MatrixScale must be present (len > 0)."`
  - L511: Replace literal string `"Jokaisella scorella pitää olla vähintään yksi claim."` with `"Each scale score must have at least one claim."`
  - L525-526: Replace literal string `"Kun category_id on 'matrix', computed_min ja computed_max on pakko pystyä laskemaan (scales-taulukosta)."` with `"When category_id is 'matrix', computed_min and computed_max must be computable from the scales array."`
- **Step 3.2**: Replace `hasattr(s, "score")` at L471 with a proper `isinstance(s, dict)` / typed attribute guard. Replace `getattr(scale, "claims", None)` at L506 and `getattr(scale, "score", None)` at L508 with equivalent typed access patterns. **EXCEPTION**: `isinstance(data, dict)` guards inside `@model_validator(mode="before")` methods are valid Pydantic V2 patterns and MUST be preserved.
- **Step 3.3**: Run `uv run python scripts/backend_audit_loop.py backend_v2 --test`. Perform atomic `git commit`.

### Phase 4: Domain Extraction & Strangler Fig Proxy (Batched Sub-Phases)

Each sub-phase creates one new target file, moves the corresponding classes, and adds Strangler Fig re-exports to v2_core.py. The extraction order is determined by the dependency graph (foundational types first).

- **Step 4.1** [NEW] `@[backend_v2/models/domain/i18n.py]`: Extract `I18nText` (L96-184). This class is the most foundational — used by nearly all other models. It MUST be extracted first. Strangler Fig re-export added to v2_core.py.
- **Step 4.2** [NEW] `@[backend_v2/models/domain/prompt_blocks.py]`: Extract `TheoryGrounding`, `AcceptanceCriterion`, `AntiPattern`, `TDAAssertion`, `MatrixClaim`, `MatrixRow`, `MatrixScale`, `PromptBlock` (L187-531). Depends on `I18nText` from Step 4.1. Strangler Fig re-exports added.
- **Step 4.3** [NEW] `@[backend_v2/models/domain/llm_config.py]`: Extract `ModelProfile`, `SystemConfigModelRegistry` (L565-600). Depends on `I18nText`. Strangler Fig re-exports added.
- **Step 4.4** [MODIFY] `@[backend_v2/models/domain/mcp.py]`: MERGE `AllowedMCPTool`, `MCPAuditTrace`, `SystemConfigMCPGateways` (L603-644) INTO the existing `domain/mcp.py` file. Update the existing import at `domain/mcp.py` L13 (`from backend_v2.models.v2_core import MCPAuditTrace`) to become a local class definition. Strangler Fig re-exports added to v2_core.py.
- **Step 4.5** [NEW] `@[backend_v2/models/domain/lexicons.py]`: Extract `LexiconConfigPayload`, `SystemConfigPerformativeLexicons`, `LexiconSuggestionListDTO` (L647-676). Strangler Fig re-exports added.
- **Step 4.6** [NEW] `@[backend_v2/models/domain/chat.py]`: Extract `ChatMessageDTO`, `ChatHistoryDTO` (L534-553). Strangler Fig re-exports added.
- **Step 4.7** [NEW] `@[backend_v2/models/domain/workflow_steps.py]`: Extract `Step`, `StepRule`, `Role` (L679-811). Depends on `I18nText`. Strangler Fig re-exports added.
- **Step 4.8** [NEW] `@[backend_v2/models/domain/workflow.py]`: Extract `Workflow`, `QuestionnaireItem`, `ExpectedInput` (L814-881, L1331-1457). Depends on `I18nText`, `Step`, `StepRule`. The `Workflow.get_allowed_layout_targets()` method references `TargetBlockType` from enums — this import MUST follow. Strangler Fig re-exports added.
- **Step 4.9** [NEW] `@[backend_v2/models/domain/llm_extraction.py]`: Extract `BaseMatrixXAI`, `BaseTDAExtraction` (L1615-1680). Depends on `LLMExtractedQuote` from `dtos/quote_evidence.py`. Strangler Fig re-exports added.
- **Step 4.10** [NEW] `@[backend_v2/models/dtos/report_data.py]`: Extract `ScorecardAtomDTO`, `TDAPending`, `TDAEvaluated`, `TDADlq`, `TDAStateUnion`, `MatrixScorecardRowDTO`, `ErrorDetailsDTO`, `HydratedAtomDTO`, `ExtractedValueDTO`, `AtomResultDTO`, `ExecutionMetricsDTO`, `ReportDataDTO`, `ExtensionMetricsDTO` (L904-1202, L1513-1519). This is the largest extraction group. Depends on `I18nText`, `MCPAuditTrace`, `HumanOverrideDTO`, `QuoteEvidenceDTO`, `ReasoningStepDTO`, `AnySduiBlock`. Strangler Fig re-exports added.
- **Step 4.11** [NEW] `@[backend_v2/models/domain/execution_lifecycle.py]`: Extract `DataDictionaryField`, `FrozenContext`, `ExecutionCreate`, `ExecutionStepState`, `RenderedSynthesisCache`, `ExecutionRecord` (L556-562, L1460-1596). Depends on `MCPAuditTrace`, `ScorecardAtomDTO`, `ExtensionMetricsDTO`, `AnySduiBlock`, `WorkflowInputs`, `ExecutionCoreFields`. **CRITICAL**: `ExecutionRecord` uses `TYPE_CHECKING` for forward references to `state.py`. The deferred import and `model_rebuild()` call (currently at L1683-1691) MUST be relocated to this new file.
- **Step 4.12**: After ALL 11 extraction sub-steps complete, run `uv run python scripts/backend_audit_loop.py backend_v2 --test` to verify all Strangler Fig re-exports work correctly. Perform atomic `git commit`.

> [!IMPORTANT]
> **model_rebuild() Relocation Strategy**: The bottom-of-file section (L1683-1702) contains critical circular dependency resolution. After extraction:
> 1. `ExecutionRecord.model_rebuild()` MUST move to `backend_v2/models/domain/execution_lifecycle.py` (bottom of file, after deferred imports of `state.py` types).
> 2. The SDUI `model_rebuild()` calls (`SduiRadarChartBlock`, `SduiScatterPlotBlock`, `SduiMatrixTableBlock`, `SduiMetrics1DBlock`) currently depend on `I18nText`, `MatrixScorecardRowDTO`, and `LaxXaiExtensionType`. After extraction, these will be importable from `domain/i18n.py` and `dtos/report_data.py` respectively. The `model_rebuild()` calls MUST move to `@[backend_v2/models/view/sdui.py]` (bottom of file) or remain in v2_core.py if circular dependencies prevent it.

### Phase 5: Import Migration (Batched Strangler Fig Sunset)
- **Step 5.1**: Update import paths in batches of maximum 5 files per batch. For each batch:
  1. Update `from backend_v2.models.v2_core import X` to the canonical new location (specifically `from backend_v2.models.domain.i18n import I18nText`, `from backend_v2.models.domain.prompt_blocks import PromptBlock`, and similar).
  2. Run `uv run python scripts/backend_audit_loop.py backend_v2 --test` after each batch.
  3. Perform atomic `git commit` after each passing batch.
  4. If the session exceeds 10 file modifications, schedule `/tier5-session-handover`.
- **Step 5.2**: After ALL 107+ consumers are migrated, remove the Strangler Fig re-exports from `@[backend_v2/models/v2_core.py]`.
- **Step 5.3**: Run the global audit loop one final time to confirm zero import errors.

> [!WARNING]
> **Session Management**: With 107+ consumers to migrate in batches of 5, Phase 5 requires at least 22 batches. The executor MUST use `/tier5-session-handover` between batches to prevent Context Amnesia. Each handover MUST update the tracker with the exact list of completed batches.

### Phase 6: Frontend Flutter UI Enum Synchronization
- **Step 6.1**: Run `uv run python scripts/flutter_audit_loop.py client_app_v2 --build` to ensure Enum parity. If new Enum values (specifically `AggregationMode`, `EvaluationTrack`, `BoundingBoxScope`, `StepExecutionType`, `StepSafety`, `ExpectedSduiType`, `PresetView`, `TextDeliveryMode`, `DisplayScale`, `ExportFormat`) cross the SDUI boundary, update the corresponding Dart enums in `@[client_app_v2/lib/core/models/enums.dart]`. Internal domain models that do NOT cross the SDUI boundary do NOT require Freezed model syncing.

### Phase 7: Verification & E2E Integration Gate
- **Step 7.1**: Execute the Python backend audit loop globally: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.
- **Step 7.2**: Execute the Flutter audit loop: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`.
- **Step 7.3**: Run database re-seed to verify model parsing: `uv run python backend_v2/seed/run_seed.py local`.

## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)
- `v2_core.py` contains fewer than 300 lines and ONLY the following residual classes: `HumanOverrideRequest`, `HumanOverrideDTO`, `SynthesisConfigDTO`, `OutputLayoutBlock`, `OutputProfile`, `JobAcceptedDTO`, `EvidenceRejectionRequest`, WorkflowSchemaResponse.
- ALL 10 new target files are created and contain their respective classes with correct `ConfigDict` settings and no service logic.
- ALL Finnish string literals are translated to English.
- ALL hardcoded `Literal[...]` annotations are replaced with centralized Enum classes.
- No `hasattr()` or `getattr()` duck-typing fallbacks exist inside model validators (exception: valid Pydantic V2 `isinstance(data, dict)` guards in `@model_validator(mode="before")`).
- ALL 107+ import consumers point directly to the canonical new file locations (no Strangler Fig re-exports remain).
- ALL `model_rebuild()` calls are relocated to their correct modules and execute successfully.
- **Orphaned Fixture Cleanup & DI Re-wiring**: ALL unused legacy test fixtures MUST be deleted, and if any dependency injection graphs were affected, they MUST be correctly re-wired to point to the new domain `__init__.py` export boundaries.
- **Security Parity Verification**: ALL internal Pydantic validators (`@model_validator`, `@field_validator`) have been mechanically verified to function exactly as they did in the original file, with zero lost business logic or security/tenant isolation rules.
- ALL existing unit tests pass without modification (except test imports).
- Coverage remains above 80% for the affected domain.

### Automated Unit Tests
- `uv run python scripts/backend_audit_loop.py backend_v2 --test`
- `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`

### Manual Verification Steps
- Verify that database re-seed succeeds: `uv run python backend_v2/seed/run_seed.py local`.
- Verify that v2_core.py has fewer than 300 lines via `Get-Content backend_v2/models/v2_core.py | Measure-Object -Line`.

### MANDATORY Final E2E REST API Verification Gate
- Set environment variable `RUN_LIVE_E2E=true` and run `uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`.

## 5. Execution Command
Open a new chat window and execute the following command:

`/tier1-planner @[c:\src\quorum\docs\epic\EPIC_134_v2_core_god_code_decomposition.md]`
