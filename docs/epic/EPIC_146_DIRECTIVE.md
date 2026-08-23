# DIRECTIVE: EPIC 146 SPECIFICATION & CANONICAL DIRECTIVE
# Title: EPIC 146 — Unified Prompt Orchestration and Cognitive Instruction Harmonization

This document serves as the exhaustive, deterministic Single Source of Truth directive for executing `/tier0-create-epic` to generate `docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md`.

---

## 1. Goal Description & Background (Objective & Strategic Scope)

### 1.1 Business Objective & Context
Quorum's cognitive evaluation and prompt orchestration architecture undergoes a generational paradigm shift (Clean Stack 2026 Model). This transformation consolidates two tightly coupled architectural improvements defined in @[docs/arkkitehtuurin_parannuskohteet.md#L244-L417]:
1. **Improvement Target 7 (Wave 1)**: Single Source of Truth for TDA Assertions — eliminating historical migration debt between `MatrixClaim.ai_description` and `TDAAssertion.concept_description`, establishing strict AST guardrails, and enforcing global configuration sovereignty.
2. **Improvement Target 8 (Wave 2)**: Zero-XML UI & Automated Prompt Assembly Pipeline — transitioning Studio UI to a pure natural-language and structured list model, introducing Layer 1 automated global mandates injection (@[backend_v2/models/prompts/global_mandates.py]), establishing 4-layer Clean Stack compilation, and purging 27 redundant prompt blocks.

### 1.2 Unified Paradigm Shift
- **Zero-XML UI**: Humans in Studio UI and Matrix Editor write pure text and structured lists (specifically: `objective`, `evaluation_rules`, `banned_concepts`, `role_enforcement`, `theory_grounding`). Humans NEVER construct XML tags (`<banned_concepts>`, `<role_enforcement>`) or ALL-CAPS directive anchors manually.
- **Compiler Layer Sovereignty**: The backend compiler (@[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L39-L290], @[backend_v2/services/orchestrator/localization_compiler.py#L22-L195], @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L18-L207]) is the sole authority responsible for assembling deterministic, 100% Context Caching-compliant XML hierarchies.
- **Layer 1 Global Mandates SSOT**: Universal system rules are centralized in @[backend_v2/models/prompts/global_mandates.py] and automatically injected into the static caching prefix.
- **TDA Assertion SSOT**: `TDAAssertion.concept_description` is the sole persistence container for claim-level evaluation rules. `MatrixClaim.ai_description` is permanently eradicated.

---

## 2. Mandatory Architectural Invariants & SSOT Matrix

### 2.1 Strict God Code Prevention Mandate (@[ki_god_code_prevention.md])
The Epic and its downstream implementation plans MUST adhere strictly to all directives in `ki_god_code_prevention.md` from day one:
- **Anti-God File Dumping (`anti_god_file_dumping`)**: Every discrete domain concept (specifically: `global_mandates.py`, `matrix_sensor_prompt_builder.py`, `prompt_compiler_adapter.py`) MUST have its own dedicated module. Files approaching 200 lines MUST be treated as an architectural smell and decomposed outwards. Generic dumping grounds (`core.py`, `utils.py`, `helpers.py`) are strictly forbidden.
- **Private Helper Bloat Ban (`private_helper_bloat_ban`)**: Logic extraction MUST default to creating new dedicated files rather than dumping private helper functions at the bottom of existing classes.
- **DRY Composition Mandate (`dry_composition_mandate`)**: Shared logic MUST be extracted into composable injected services, base classes, or mixins without copy-pasting.
- **Strategy & Registry Pattern (`strategy_pattern_mandate`)**: Branching logic based on types or enums MUST use static registries with Eager Loading instead of `if/elif/else` chains.
- **Protocol & Context Worker Architecture (`protocol_driven_worker_architecture`)**: Workers and services MUST use immutable `JobContext` models, strict Protocol interfaces, and RFC 7807 structured dual-logging.
- **Domain Model Purity (`domain_model_purity_mandate`)**: All models in `models/` and `dtos/` MUST be pure, stateless Data Transfer Objects (`ConfigDict(frozen=True, strict=True, extra="forbid")`). No database queries or service logic inside models.
- **Validation Context Injection (`validation_context_injection`)**: Dynamic validation configuration MUST be injected via `ValidationInfo.context` during instantiation, never hardcoded in model validators.
- **AST Boundary Verification (`ast_boundary_verification_mandate`)**: Method and class boundaries in files exceeding 300 lines MUST be verified using `ast.parse` scripts before defining line bounds.
- **Remedial Strangler Fig Proxy (`remedial_strangler_fig_proxy`)**: When decomposing central models (@[backend_v2/models/v2_core.py#L101-L191]), avoid circular imports, migrate downstream consumers in batches (maximum 5 files), run quality gates between batches, and delete temporary proxy facades after migration.

### 2.2 Complete SSOT Architecture Matrix
1. **Claim Instruction SSOT**: `TDAAssertion.concept_description` is the sole container. `MatrixClaim.ai_description` is permanently deleted across backend, database seed, and Flutter Freezed models.
2. **Global Configuration SSOT**: Minimum concept length (`tda_concept_min_length: 10`) is centrally defined in @[backend_v2/settings.py#L51-L716] and mirrored in @[client_app_v2/lib/core/models/enums.dart] (`SystemUiConstraints.tdaConceptMinLength`), eliminating magic numbers.
3. **Layer 1 Global Mandates SSOT**: 11 universal system mandates (Null Hypothesis, Anti-Score, Anti-ID, Epistemic Glossary, Semantic Bleed, Verbatim Extraction, Extension Anchoring, Tone, Schema Purity, Context Segregation, Language Mandates) are centralized in @[backend_v2/models/prompts/global_mandates.py] and injected into the static 100% Context Caching prefix.
4. **PromptBlock Domain SSOT**: `PromptBlock` stores structured pure data fields (specifically: `objective`, `evaluation_rules`, `banned_concepts`, `role_enforcement`, `theory_grounding`). The compiler layer deterministically wraps XML.
5. **Cross-Domain DTO Parity SSOT**: Python Pydantic models in `models/` and Flutter Freezed models in `client_app_v2/` maintain 1:1 serialisation parity. `tdaId` format is 32 hex chars (`tda_$uuidHex`), matching backend regex `^tda_[a-f0-9]{32}$`.
6. **Seed Vault SSOT (`seed_data.json`)**: 70 claims migrated verbatim (`prompt_preservation_mandate`), 152 `ai_description` keys on `MatrixClaim` purged, 27 redundant `system_rule` prompt blocks purged.

---

## 3. Deprecations & Sunset List (What We Will REMOVE)

| Item to Remove / Deprecate | Current Location | Destination / Replacement |
| :--- | :--- | :--- |
| `MatrixClaim.ai_description` | @[backend_v2/models/v2_core.py#L324-L341] | **INTENTIONALLY DROPPED** / Migrated to `TDAAssertion.concept_description` |
| `MatrixClaim.aiDescription` | @[client_app_v2/lib/features/studio/models/prompt_block.dart] | **INTENTIONALLY DROPPED** / Bound to `TDAAssertion.conceptDescription` |
| 152 `ai_description` keys | @[backend_v2/seed/seed_data.json] (claims) | **PURGED** / 70 empty assertions populated verbatim |
| 27 redundant `system_rule` blocks | @[backend_v2/seed/seed_data.json] | **PURGED** / Replaced by Layer 1 @[backend_v2/models/prompts/global_mandates.py] |
| Duck typing `getattr(claim, 'ai_description', None)` | @[backend_v2/services/studio/simulation_service.py#L140-L195] | **INTENTIONALLY DROPPED** / Direct iteration over `claim.tda_assertions` |
| Lazy fallback `rendered = data.ai_description or ""` | @[backend_v2/services/studio/simulation_service.py#L140-L195] | **INTENTIONALLY DROPPED** / Explicit `None` check |
| Reflection loop `find_value_by_key` (`hasattr`/`getattr`) | @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L140-L169] | **INTENTIONALLY DROPPED** / Replaced by typed anchors model |
| Hardcoded slug checks (`matrix_causal_analyst`) | @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L45-L290] | **INTENTIONALLY DROPPED** / Replaced by `b.category_id == MATRIX` check |
| 7 `.get()` fallback chains for `execution_time` | @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L45-L290] | **INTENTIONALLY DROPPED** / Replaced by `ExecutionTimeResolver` pure function |
| Lazy fallback `LANGUAGE_NAMES.get(..., "English")` | @[backend_v2/services/orchestrator/localization_compiler.py#L79-L115] | **INTENTIONALLY DROPPED** / Replaced by Fail-Fast `AppException` |
| Finnish error messages in `v2_core.py` | @[backend_v2/models/v2_core.py#L296-L321] | **INTENTIONALLY DROPPED** / Translated to English |
| Historical comments violating present tense | @[backend_v2/models/v2_core.py#L226-L321] | **INTENTIONALLY DROPPED** / Present tense description |
| Manual string clipping `uuidHex.substring(0, 16)` | @[client_app_v2/lib/features/studio/models/prompt_block.dart] | **INTENTIONALLY DROPPED** / Full 32 hex chars `tda_$uuidHex` |
| Duplicate UI widget `const SizedBox(height: 16)` | @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart] | **PURGED** (UI hygiene) |

---

## 4. Retained SSOT Invariants (What We Will RETAIN)

1. **`TDAAssertion` Core Fields**: `tda_id`, `concept_description`, `inverse_evidence`, `aggregation_mode`, `anchor_target`, `extraction_rule`.
2. **`MatrixClaim` Structure**: `label: I18nText` and `tda_assertions: list[TDAAssertion]`.
3. **`PromptBlock.ai_description`**: Retained as optional legacy fallback field (`str | None = None`) during transition.
4. **Prompt Preservation Mandate**: 100% mathematical fidelity of qualitative coaching text in 70 migrated claims.
5. **Step-Specific Task Directives**: `block_heuristic1`, `block_heuristic2`, `block_heuristic3`, `block_protocol1`, and primary matrix blocks retained in `criteria_block_ids`.
6. **Synthesis Pipeline Global Mandates**: Injections in @[backend_v2/worker.py] retained as correct for synthesis dynamic user context.

---

## 5. Two-Wave Phased Execution Roadmap (11 Phased Slices)

### 🌊 WAVE 1: TDA ASSERTION SSOT & PERSISTENCE HARMONIZATION (Improvement Target 7)
- **Phase 1: Pre-Requisite Technical Debt Cleanups & AST Guardrails**
  - [NEW] Create @[backend_v2/tests/unit/test_ast_matrix_claim_guardrails.py] with 8 AST/seed guardrail tests.
  - Scoped Boy Scout: Eliminate duck typing in @[backend_v2/services/studio/simulation_service.py#L140-L195] (`getattr`) and lazy fallback (`or ""`).
  - Pre-flight: Un-skip and fix @[backend_v2/tests/unit/test_tier4_schema_bug.py#L9-L75] to enforce modern V2 architecture.
- **Phase 2: Seed Data Migration & Vault Mutation**
  - Create timestamped backup in `backend_v2/seed/backups/`.
  - Migrate 70 claim instructions verbatim into `TDAAssertion.concept_description`.
  - Purge 152 `ai_description` keys on `MatrixClaim` in @[backend_v2/seed/seed_data.json].
  - Reseed local database: `uv run python backend_v2/seed/run_seed.py local`.
- **Phase 3: Backend Domain & Service Harmonization**
  - Update @[backend_v2/settings.py#L51-L716]: define `tda_concept_min_length: Annotated[int, Field(...)] = 10`.
  - Update @[backend_v2/models/v2_core.py#L226-L321] and @[backend_v2/models/v2_core.py#L324-L341]: `TDAAssertion.concept_description` with `min_length=10`, English field descriptions and error messages, delete `MatrixClaim.ai_description`, update historical comments.
  - Update @[backend_v2/hooks/atom_flattening.py#L34-L187]: direct access to `tda.concept_description` without manual strip calls.
  - Update @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L93-L207]: Fail-Fast exception with RFC 7807 `logger.error` if `assertion.question` is empty.
- **Phase 4: Flutter Studio Client Harmonization**
  - Update @[client_app_v2/lib/core/models/enums.dart]: add `tdaConceptMinLength(10)` to `SystemUiConstraints`.
  - Update @[client_app_v2/lib/features/studio/models/prompt_block.dart]: 32-hex `tdaId: 'tda_$uuidHex'`, delete `aiDescription` from `MatrixClaim`, run build runner.
  - Update @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]: bind to `tdaAssertions.first.conceptDescription` with validation against `SystemUiConstraints.tdaConceptMinLength`, remove duplicate spacing.
  - Update @[client_app_v2/lib/features/studio/views/components/bars_matrix_builder.dart] and @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart].
- **Phase 5: Test Suite Harmonization & Quality Gates**
  - Update 23 backend test files across Batch 1 (11 files), Batch 2a (6 files), Batch 2b (6 files), updating 39 short concept strings across 12 files to 10 or more characters.
  - Update Flutter test @[client_app_v2/test/features/studio/views/components/bars_matrix_builder_test.dart].
  - Run global audit loops: `backend_audit_loop.py` and `flutter_audit_loop.py --build`.

---

### 🌊 WAVE 2: ZERO-XML UI & CLEAN STACK PROMPT ENGINE (Improvement Target 8)
- **Phase 6: Layer 1 Global Mandates Injection & Compiler Foundation**
  - Centralize 11 system mandates in @[backend_v2/models/prompts/global_mandates.py].
  - Inject `GLOBAL_MANDATES_XML` into Layer 1 static prefix in @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L45-L290] and @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L36-L91].
  - Scoped Boy Scout in `prompt_factory.py`: eliminate `find_value_by_key` reflection loop, eliminate slug checks, eliminate 7 `.get()` fallback chains for `execution_time` (replace with `ExecutionTimeResolver` pure function).
  - Scoped Boy Scout in `localization_compiler.py`: Fail-Fast on unsupported `target_locale`.
- **Phase 7: Structured PromptBlock Domain Models & AST Guardrails**
  - Enhance `PromptBlock` in @[backend_v2/models/v2_core.py#L380-L544] with structured pure data fields: `objective`, `evaluation_rules`, `banned_concepts`, `role_enforcement`, `theory_grounding`. Translate Finnish validation errors to English in @[backend_v2/models/v2_core.py#L461-L544].
  - Update Dart `PromptBlock` Freezed class in @[client_app_v2/lib/features/studio/models/prompt_block.dart].
  - [NEW] Create AST guardrail suite @[backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py] (7 static tests).
- **Phase 8: Clean Stack Compiler Layer Assembly**
  - Update @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L45-L290] and @[backend_v2/services/orchestrator/localization_compiler.py#L79-L115] to assemble 4-layer XML hierarchy deterministically from structured fields.
  - Update @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L36-L91] to compile matrix objective, evaluation rules, and banned concepts into XML wrappers.
- **Phase 9: Flutter Studio Zero-XML UI Modernization**
  - Update @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]: structured inputs for Objective, Evaluation Rules list, Banned Concepts list, Role Enforcement, live read-only compiled preview.
  - Update @[client_app_v2/lib/features/studio/views/step_builder_view.dart]: streamlined criteria block selection.
  - Add ARB localization strings in `app_en.arb` and `app_fi.arb`.
- **Phase 10: Seed Vault Pruning & Database Reseeding**
  - Execute programmatic redundancy verification script proving candidate blocks are 100% covered by Layer 1.
  - Purge verified redundant global mandate blocks (specifically and exhaustively: `block_headermandates`, `block_mandate2`, `block_mandate3`, `block_mandate5`, `block_headerrules`, `block_rule1`, `block_rule2`, `block_rule3`, `block_rule4`, `block_rule5`, `block_rule6`, `block_oprule1`, `block_oprule2`, `block_oprule3`, `block_instructionnohallucination`, `block_instructionlanguage_dynamic`, `block_headerinstructions`).
  - Fix HTML entity in @[backend_v2/seed/seed_data.json].
  - Reseed local database: `uv run python backend_v2/seed/run_seed.py local`.
- **Phase 11: End-to-End Live Integration Verification Gate**
  - Execute live E2E integration test: `RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_epic_chain_e2e.py`.
  - Synchronize Knowledge Items (@[ki_llm_extraction_architecture.md]) and rules (@[.agents/rules/05_llm_architecture.md]).

---

## 6. Anti-Happy-Path Negative Verification Scenarios (ISTQB Compliant)

1. **NEG-01 (TDA Concept Too Short)**: `TDAAssertion(concept_description="Short")` -> raises Pydantic `ValidationError` (`min_length=10`).
2. **NEG-02 (MatrixClaim with ai_description)**: Deserializing dict containing `ai_description` -> raises Pydantic `ValidationError` (`extra_forbidden`).
3. **NEG-03 (MatrixSensor Empty Question)**: Trigger prompt builder with `assertion.question=""` -> raises `AppException(ErrorCodes.VALIDATION_FAILED)` with structured `logger.error`.
4. **NEG-04 (AST Scanner MatrixClaim Negative)**: Mock AST snippet of `MatrixClaim` with `ai_description` -> detected and flagged by AST scanner.
5. **NEG-05 (PromptFactory Missing Context Data)**: Missing expected keys in `llm_context_data` -> raises Fail-Fast `AppException` without silent fallback.
6. **NEG-06 (LocalizationCompiler Invalid Locale)**: Unsupported `target_locale` -> raises `AppException(ErrorCodes.VALIDATION_FAILED)` without fallback to `"English"`.
7. **NEG-07 (Raw User Payload with XML Characters)**: Unescaped `<, >, &` in payload -> CDATA and XML escaping preserved without broken XML syntax.
8. **NEG-08 (AST Scanner Reflection Ban)**: AST verification of `prompt_factory.py` -> flags any presence of `hasattr` or `getattr`.

---

## 7. Required Context Rules & Knowledge Items Registry

```xml
<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_testing.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_matrix_boolean_evaluation_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
</required_context_rules>
```
