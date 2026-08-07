# EPIC 133A: Lightweight Matrix God Code Decomposition

## 1. Goal Description & Background (Objective & Problem Statement)
This Epic focuses on decomposing the massive "God Code" file `@[backend_v2/models/dtos/lightweight_matrix.py]` (728 lines) as mandated by the parent EPIC 133. Currently, this file violates the Quorum architectural rules by acting as a God Object that embeds heavy business logic (`AnchorValidationService`, fuzzy matching, and database-driven alias hydration) directly inside Pydantic DTO validators. It also uses hardcoded Finnish string literals (specifically `"ei löydy"`, `"ei mainittu"`, `"ei sovelleta"`, `"ei lainausta"`, `"ei ole"`), `hasattr()` duck-typing, and `.get()` default-value fallbacks inside DTO properties.

The objective is to implement the Strangler Fig pattern to decouple pure Data Transfer Objects from business logic. The DTOs will be split into logical domains (specifically `backend_v2/models/dtos/atom_evaluation.py`), and all heavy validation/hydration logic (including BOTH `_enforce_null_hypothesis_before` and `_enforce_zero_variance_protocols`) will be moved to the Service layer (specifically into `@[backend_v2/services/orchestrator/anchor_validation_service.py]` and the calling orchestrator). The Orchestrator MUST expand aliases on the raw dictionary, instantly hydrate it via `.model_validate()`, and ONLY THEN execute heavy validation (exact forensic matching and spatial anchoring) on the strict DTO to prevent naked dictionary duck-typing. Hardcoded blacklist arrays will be converted to a centralized Lexicon constant (specifically in `backend_v2/models/constants.py`) and injected via `ValidationInfo.context` (stored in a `PrivateAttr` to allow `@property` access without altering the schema). This ensures strict adherence to the Zero-Compromise Pydantic V2, DDD, and Context Injection mandates.

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (What We Will REMOVE)
- **INTENTIONALLY DROPPED**: The usage of `AnchorValidationService` and `AliasEngine` directly within the `@model_validator` `_enforce_null_hypothesis_before` (lines 545-645) AND `_enforce_zero_variance_protocols` (lines 647-708) inside `AtomEvaluationItemDTO`. This logic moves entirely to the Service layer.
- **INTENTIONALLY DROPPED**: Hardcoded Finnish blacklist sets inside `evidence_found` properties on both `LightweightExtractionAtom` (line 232) and `AtomEvaluationItemDTO` (lines 484-501). These will be replaced by a dynamic Lexicon injected via `ValidationInfo.context` at the Service layer call site.
- **INTENTIONALLY DROPPED**: Inline usage of database MCP mapping within the DTO model initialization (lines 578-639).
- **INTENTIONALLY DROPPED**: All `hasattr(quote, "text")` duck-typing patterns (lines 238, 507, 687) — replaced by direct typed attribute access on `LLMExtractedQuote.text`.
- **INTENTIONALLY DROPPED**: All `isinstance(quote, dict)` and `.get()` fallback patterns inside `evidence_found` properties (lines 239, 508, 614, 620-624, 689) — replaced by strict Pydantic V2 typed access.
- **INTENTIONALLY DROPPED**: Inline `import re` statements inside `@field_validator` methods on `MatrixEvaluationItemDTO` (line 310) and `AtomEvaluationItemDTO` (line 451) — moved to top-level global import.

### Retained SSOT Invariants (What We Will RETAIN)
- The core schemas (`LightweightMatrixOutput`, `AtomEvaluationItemDTO`, `LightweightExtractionAtom`, `ReducedAtomDTO`, `ReasoningStepDTO`, `LevelStatsDTO`, `XAILogDto`, `OutputProfileConfig`, `MergedFactsDTO`, `MatrixEvaluationItemDTO`, `LightweightMatrixDTO`) will remain intact to ensure zero-behavioral change for JSON serialization boundaries. No field names, types, or serialization shapes will change.

### Compliance & Modernity Gates
- **Pydantic Strictness**: All DTOs must retain `ConfigDict(strict=True, extra='forbid')` (exceptions: `MergedFactsDTO` retains `ConfigDict(extra="allow", frozen=True)` per `duck_typing_token_shield_exception`, and `LightweightMatrixOutput.extensions` retains `dict[LaxXaiExtensionType, Any]`).
- **Service Layer Hydration Firewall**: Pydantic DTOs must be pure. Database and external data dependencies must be hydrated by the Service layer (specifically `RAGPreflightService` or `ContextRouter`) and injected into the DTO via `ValidationInfo.context`.
- **Context Injection Pattern**: Hardcoded blacklists MUST NOT pollute environment-dependent settings. The Orchestrator/Service layer MUST fetch the null-hypothesis blacklist set from a centralized static constant (specifically [NEW] `backend_v2/models/constants.py`) and inject it via `Model.model_validate(data, context={"null_hypothesis_blacklist": blacklist_set})`. To allow the `evidence_found` `@property` to access this without changing the public serialization schema, the DTO MUST store it internally using a Pydantic `PrivateAttr` (specifically `_null_hypothesis_blacklist: set[str] = PrivateAttr(default_factory=set)`) populated during an `@model_validator(mode="after")`.
- **English Language Mandate**: All hardcoded Finnish strings (`"ei löydy"`, `"ei mainittu"`, `"ei sovelleta"`, `"ei lainausta"`, `"ei ole"`) will be removed from inline code and placed into the injected blacklist configuration.
- **Zero Duck-Typing**: All `hasattr()` and `.get()` fallback patterns inside DTO `@property` methods and `@model_validator(mode="after")` methods will be replaced by direct typed attribute access with Fail-Fast crash. **EXCEPTION**: `isinstance(data, dict)` guards inside `@model_validator(mode="before")` are a valid Pydantic V2 structural pattern (data can arrive as dict or pre-validated model) and MUST NOT be flagged as duck-typing violations. Similarly, `isinstance(v, list)` guards inside `@field_validator(mode="before")` are valid Pydantic V2 type guards.

### Producer-Consumer Integration Check
- **Producer**: FastAPI execution routers (`@[backend_v2/api/routers/]`) and `@[backend_v2/services/orchestrator/dag_executor.py]`.
- **Consumer**: `@[backend_v2/services/orchestrator/matrix_reducer.py]` and downstream synthesis engines. The structural changes MUST NOT alter the serialized shape of `LightweightMatrixOutput`.

### Complete Class Routing Map (Post-Decomposition)
| Class | Current Location (lines) | Target Location |
|-------|-------------------------|----------------|
| `OutputProfileConfig` | L18-28 | `@[backend_v2/models/dtos/lightweight_matrix.py]` (STAYS) |
| `XAILogDto` | L30-40 | `@[backend_v2/models/dtos/lightweight_matrix.py]` (STAYS) |
| `LightweightMatrixOutput` | L42-133 | `@[backend_v2/models/dtos/lightweight_matrix.py]` (STAYS) |
| `LevelStatsDTO` | L136-148 | `@[backend_v2/models/dtos/lightweight_matrix.py]` (STAYS) |
| `MergedFactsDTO` | L150-158 | `@[backend_v2/models/dtos/lightweight_matrix.py]` (STAYS) |
| `LightweightExtractionAtom` | L160-285 | [NEW] `@[backend_v2/models/dtos/atom_evaluation.py]` (MOVES) |
| `ReasoningStepDTO` | L287-298 | [NEW] `@[backend_v2/models/dtos/atom_evaluation.py]` (MOVES) |
| `MatrixEvaluationItemDTO` | L300-314 | [NEW] `@[backend_v2/models/dtos/atom_evaluation.py]` (MOVES) |
| `AtomEvaluationItemDTO` | L316-708 | [NEW] `@[backend_v2/models/dtos/atom_evaluation.py]` (MOVES) |
| `ReducedAtomDTO` | L711-718 | [NEW] `@[backend_v2/models/dtos/atom_evaluation.py]` (MOVES) |
| `LightweightMatrixDTO` | L721-728 | [NEW] `@[backend_v2/models/dtos/atom_evaluation.py]` (MOVES) |

> [!WARNING]
> **Duplicate Validator Bug**: `AtomEvaluationItemDTO` contains TWO `@field_validator("chart_display_label", mode="before")` methods: `truncate_chart_label` (L426-432) and `_truncate_chart_label` (L456-475). Pydantic V2 will only execute one. This must be investigated and resolved during Phase 3 (Step 3.3b).

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Golden Master & Coverage Verification (MANDATORY PREREQUISITE)
- **Step 1.1**: Run `uv run pytest --cov=backend_v2.models.dtos.lightweight_matrix backend_v2/tests/ --cov-report=term-missing` to verify current test coverage of the target file. Coverage MUST be above 80% before any decomposition begins. If below 80%, write Golden Master tests capturing the exact current output BEFORE proceeding.
- **Step 1.2**: Catalog all 23+ import consumers discovered via workspace grep. The complete import consumer list is:
  - `@[backend_v2/worker.py]` → imports `LevelStatsDTO`, `LightweightMatrixOutput`
  - `@[backend_v2/utils/scoring/waterfall_engine.py]` → imports `LevelStatsDTO`, `XAILogDto`
  - `@[backend_v2/utils/scoring/pure_math_engine.py]` → imports `LevelStatsDTO`, `XAILogDto`
  - `@[backend_v2/utils/scoring/base_engine.py]` → imports `LevelStatsDTO`, `XAILogDto`
  - `@[backend_v2/utils/scoring/average_engine.py]` → imports `LevelStatsDTO`, `XAILogDto`
  - `@[backend_v2/utils/math_utils.py]` → imports `LevelStatsDTO`
  - `@[backend_v2/services/orchestrator/context_router.py]` → imports `LightweightMatrixOutput`, `OutputProfileConfig`
  - `@[backend_v2/services/orchestrator/matrix_reducer.py]` → imports `LightweightMatrixDTO`, `ReducedAtomDTO`
  - `@[backend_v2/services/matrix_domain_parser.py]` → imports multiple classes
  - `@[backend_v2/models/v2_core.py]` → imports `ReasoningStepDTO`
  - `@[backend_v2/models/dtos/trace.py]` → imports `LevelStatsDTO`
  - `@[backend_v2/hooks/scoring.py]` → imports multiple classes
  - `@[backend_v2/tests/unit/utils/test_math_utils.py]` → imports `LevelStatsDTO`
  - `@[backend_v2/tests/unit/utils/scoring/test_waterfall_engine.py]` → imports `LevelStatsDTO`
  - `@[backend_v2/tests/unit/utils/scoring/test_average_engine.py]` → imports `LevelStatsDTO`
  - `@[backend_v2/tests/unit/test_bug_lightweight_atom_truncation.py]` → imports `LightweightExtractionAtom`
  - `@[backend_v2/tests/unit/services/orchestrator/test_context_router.py]` → imports `OutputProfileConfig`
  - `@[backend_v2/tests/unit/services/test_execution.py]` → imports `ReasoningStepDTO` (3 inline imports)
  - `@[backend_v2/tests/unit/models/dtos/test_lightweight_matrix_schema.py]` → imports `AtomEvaluationItemDTO`
  - `@[backend_v2/tests/unit/models/dtos/test_lightweight_matrix.py]` → imports multiple classes
  - `@[backend_v2/tests/integration/test_lazy_llm_simulation.py]` → imports `AtomEvaluationItemDTO`, `ReasoningStepDTO`

### Phase 2: DTO Extraction & Strangler Fig Proxy
- **Step 2.1**: [NEW] Create new file `@[backend_v2/models/dtos/atom_evaluation.py]` and migrate the following classes into it (in dependency order): `ReasoningStepDTO`, `LightweightExtractionAtom`, `MatrixEvaluationItemDTO`, `AtomEvaluationItemDTO`, `ReducedAtomDTO`, `LightweightMatrixDTO`.
- **Step 2.2**: **Strangler Fig Re-Export Mandate**: In the original `@[backend_v2/models/dtos/lightweight_matrix.py]`, add re-export imports for ALL migrated classes from `atom_evaluation.py`. This ensures zero import breakage across all 23+ consumer files. The re-exports will be removed in Phase 4 after all consumers are migrated.
- **Step 2.3**: Run `uv run python scripts/backend_audit_loop.py backend_v2 --test` to verify zero-behavioral change. ALL existing tests MUST pass without modification at this point.

### Phase 3: Service Logic Extraction & Duck-Typing Eradication
- **Step 3.1**: Strip `AnchorValidationService` and `AliasEngine` imports and usage from BOTH `AtomEvaluationItemDTO._enforce_null_hypothesis_before` and `_enforce_zero_variance_protocols` validators. ALL heavy logic (exact forensic matching, fuzzy fallbacks, alias hydration, spatial anchoring validation) MUST be moved to the Service layer (specifically `AnchorValidationService` and the calling orchestrator). The orchestrator MUST use `AliasEngine` on the raw dictionary, instantly hydrate it via `model_validate()`, and THEN pass the typed DTO to `AnchorValidationService` for spatial anchoring validation. The complete list of `ValidationInfo.context` keys currently consumed inside `_enforce_null_hypothesis_before` and `_enforce_zero_variance_protocols` that MUST be migrated to the Service layer is:
  - `alias_map`: `dict[str, str]` — AliasEngine mapping for reasoning text hydration
  - `source_documents`: `list` — Static source documents for quote matching
  - `mcp_source_texts`: `dict[str, str]` — Dynamic MCP source texts for quote matching
  - `locale`: `str | None` — Locale for fuzz threshold calculation
  - `strictness_level`: `int` — Tier-based strictness modifier (default 50)
  - `source_text`: `str | None` — Full source text for quote integrity validation (used in `_enforce_zero_variance_protocols`)
  - `has_mcp_tools`: `bool` — Flag to skip source text matching when MCP tools are active (used in `_enforce_zero_variance_protocols`)
  - `system_locale`: `str | None` — System locale for fuzz threshold in zero-variance validation
- **Step 3.1b**: After service logic extraction, the DTO's `ValidationInfo.context` contract MUST be reduced to the following minimalist contract:
  ```python
  # Context keys injected by Service layer at model_validate() call site:
  # "null_hypothesis_blacklist": set[str]  — Dynamic blacklist injected from constants
  ```
  All 8 context keys listed in Step 3.1 MUST be completely removed from the DTO validators. The orchestrator/service layer takes full ownership of spatial anchoring validation, alias hydration, and quote verification.
- **Step 3.2**: Replace ALL `hasattr(quote, "text")` duck-typing with direct typed `quote.text` attribute access (since `exact_quotes` is already typed as `list[LLMExtractedQuote]`). Affected locations: `LightweightExtractionAtom.evidence_found` (line 238), `AtomEvaluationItemDTO.evidence_found` (line 507), and `AtomEvaluationItemDTO._enforce_zero_variance_protocols` (line 688).
- **Step 3.3**: Remove ALL `isinstance(quote, dict)` and `.get()` fallback patterns from `evidence_found` properties on both `LightweightExtractionAtom` (line 239) and `AtomEvaluationItemDTO` (line 508). Also remove `.get()` fallbacks inside `_enforce_zero_variance_protocols` (line 689) and `.get()` patterns inside `_enforce_null_hypothesis_before` (lines 550, 568, 573, 576-580, 614, 620-624). **EXCEPTION**: `isinstance(data, dict)` at line 548 inside `@model_validator(mode="before")` is a valid Pydantic V2 structural guard and MUST be preserved until the entire validator is extracted to the service layer.
- **Step 3.3b** (**BUG FIX**): Investigate and resolve the duplicate `@field_validator("chart_display_label", mode="before")` validators on `AtomEvaluationItemDTO`: `truncate_chart_label` (lines 426-432) and `_truncate_chart_label` (lines 456-475). Pydantic V2 will only execute one of these. Determine which one contains the correct logic and delete the other.
- **Step 3.4**: Move the `import re` statements from inline `@field_validator` methods (in `MatrixEvaluationItemDTO._clean_validation_decision` at line 310 and `AtomEvaluationItemDTO._clean_validation_decision` at line 451) to the top-level global import section of `atom_evaluation.py`.
- **Step 3.5**: Replace hardcoded Finnish blacklist sets in `evidence_found` properties with the injected `null_hypothesis_blacklist` from `ValidationInfo.context`. The two affected locations are: `LightweightExtractionAtom.evidence_found` (line 232) and `AtomEvaluationItemDTO.evidence_found` (lines 484-501). To allow the `@property` to access this runtime context, populate a `PrivateAttr` named `_null_hypothesis_blacklist` during an `@model_validator(mode="after")`. The default blacklist will be defined in a centralized constants file (specifically [NEW] `backend_v2/models/constants.py`) to keep environment settings pure.
- **Step 3.6**: Clean up module-level imports in `atom_evaluation.py`: after service logic extraction, remove the imports of `AnchorValidationService` (line 8), `AliasEngine` (line 10), `get_lexical_fuzz_threshold` (line 9), and the module-level `get_settings()` call (lines 12-15) if no remaining code in the file uses them. The `get_settings` import and module-level variables (`_schema_max_quotes_target`, `_schema_max_quotes`, `_schema_max_quote_length`) must be retained if the `@field_validator` truncation logic still references them.
- **Step 3.7**: **ATOMIC TEST FIXTURE MIGRATION**: Run `uv run python scripts/backend_audit_loop.py backend_v2 --test` to verify all changes. You MUST atomically update test fixtures in the exact same phase to prevent strictness crashes:
  1. Update fixtures that previously relied on the old hardcoded blacklists to inject the blacklist via the `context=` parameter.
  2. Because duck-typing (`isinstance(quote, dict)`) was eradicated in Steps 3.2 and 3.3, you MUST update all mock data in tests that previously passed raw dictionaries for `exact_quotes` to explicitly use instantiated `LLMExtractedQuote` objects (or strictly matching dictionary shapes if using `model_validate`).
  Specifically affected test files: `@[backend_v2/tests/unit/models/dtos/test_lightweight_matrix.py]`, `@[backend_v2/tests/unit/models/dtos/test_lightweight_matrix_schema.py]`, and `@[backend_v2/tests/integration/test_lazy_llm_simulation.py]`.

### Phase 4: Import Migration (Batched Strangler Fig Sunset)
- **Step 4.1**: Update import paths in batches of maximum 5 files per batch. For each batch:
  1. Update the `from backend_v2.models.dtos.lightweight_matrix import X` to `from backend_v2.models.dtos.atom_evaluation import X` for the migrated classes.
  2. Run `uv run python scripts/backend_audit_loop.py backend_v2 --test` after each batch.
  3. Perform an atomic `git commit` after each passing batch.
  4. If the session exceeds 10 file modifications, schedule a `/tier5-session-handover` before proceeding.
- **Step 4.2**: After ALL consumers are migrated, remove the Strangler Fig re-exports from `@[backend_v2/models/dtos/lightweight_matrix.py]`.
- **Step 4.3**: Run the global audit loop one final time to confirm zero import errors.

### Phase 5: Frontend Flutter UI Enum Synchronization
- **Step 5.1**: Run `uv run python scripts/flutter_audit_loop.py client_app_v2 --build` to ensure Enum parity. Update Dart enums in `@[client_app_v2/lib/core/models/enums.dart]` if new enum states (specifically status flags or visual intents) are introduced in the backend. Internal DTOs (`AtomEvaluationItemDTO`, `LightweightExtractionAtom`, `ReducedAtomDTO`, `MatrixEvaluationItemDTO`, `ReasoningStepDTO`, `LightweightMatrixDTO`) do not cross the SDUI boundary, so Freezed model syncing is not required for them.

### Phase 6: Verification & E2E Integration Gate
- **Step 6.1**: Execute the Python backend audit loop globally: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.
- **Step 6.2**: Execute the Flutter audit loop: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`.

## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)
- `lightweight_matrix.py` contains only `OutputProfileConfig`, `XAILogDto`, `LightweightMatrixOutput`, `LevelStatsDTO`, and `MergedFactsDTO` (approximately 160 lines) and contains no `@model_validator`s executing complex service or database lookups.
- `atom_evaluation.py` successfully encapsulates `ReasoningStepDTO`, `LightweightExtractionAtom`, `MatrixEvaluationItemDTO`, `AtomEvaluationItemDTO`, `ReducedAtomDTO`, and `LightweightMatrixDTO` without importing `AnchorValidationService` or `AliasEngine` at the top level.
- No hardcoded Finnish string arrays exist inside backend DTOs.
- No `hasattr()`, `isinstance(x, dict)`, or `.get()` duck-typing fallbacks exist inside DTO properties or validators.
- All Strangler Fig re-exports have been removed from `lightweight_matrix.py`.
- All unit tests pass, and coverage remains above 90%.

### Automated Unit Tests
- `uv run python scripts/backend_audit_loop.py backend_v2 --test`
- `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`

### Manual Verification Steps
- Verify that `LightweightMatrixOutput` still correctly parses execution data by running the local DB re-seed (`uv run python backend_v2/seed/run_seed.py local`).

### MANDATORY Final E2E REST API Verification Gate
- Set environment variable `RUN_LIVE_E2E=true` and run `uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`.

## 5. Execution Command
Avaa uusi keskusteluikkuna ja suorita seuraava komento (joka pakottaa uuden agentin lukemaan säännöt ja KI-dokumentin ensin):

`/tier1-planner @[c:\src\quorum\docs\epic\EPIC_133A_lightweight_matrix.md] Lue ehdottomasti ensin arkkitehtuurisäännöt @[c:\src\quorum\.agents\rules\00-antigravity-core.md] ja @[c:\src\quorum\.agents\rules\01-python-backend.md] sekä KI-dokumentti @[C:\Users\risto\.gemini\antigravity-ide\knowledge\god_code_prevention\artifacts\ki_god_code_prevention.md] ennen suunnittelun aloittamista.`
