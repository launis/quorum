# EPIC 146: Unified Prompt Orchestration and Cognitive Instruction Harmonization

> [!NOTE]
> **Scientific & Industrial Validation (2025-2026)**
> Modern foundational model architectures (Google DeepMind Gemini 1.5/2.0 context caching, Anthropic Claude prompt prefix caching) achieve up to 90% latency reduction and 75% FinOps cost efficiency when system instructions are structured with deterministic, 100% static prefixes followed by dynamic payloads at the tail. Separating structured schema composition from dynamic natural-language domain logic eliminates "Attention Dilution" and prevents prompt injection vulnerabilities in server-driven AI systems.

---

## 1. Goal Description & Background (Objective & Problem Statement)

### 1.1 Business Objective & Context
Quorum's cognitive evaluation and prompt orchestration architecture undergoes a generational paradigm shift (Clean Stack 2026 Model). This transformation consolidates two tightly coupled architectural improvements defined in @[docs/arkkitehtuurin_parannuskohteet.md#L244-L417]:
1. **Improvement Target 7 (Wave 1)**: Single Source of Truth for TDA Assertions — eliminating historical migration debt between `MatrixClaim.ai_description` and `TDAAssertion.concept_description`, establishing strict AST guardrails, and enforcing global configuration sovereignty.
2. **Improvement Target 8 (Wave 2)**: Zero-XML UI & Automated Prompt Assembly Pipeline — transitioning Studio UI to a pure natural-language and structured list model, introducing Layer 1 automated global mandates injection (@[backend_v2/models/prompts/global_mandates.py]), establishing 4-layer Clean Stack compilation, and purging 27 redundant prompt blocks.

### 1.2 Unified Paradigm Shift
- **Zero-XML UI**: Humans in Studio UI and Matrix Editor write pure text and structured lists (specifically and exhaustively: `objective`, `evaluation_rules`, `banned_concepts`, `role_enforcement`, `theory_grounding`). Humans NEVER construct XML tags (`<banned_concepts>`, `<role_enforcement>`) or ALL-CAPS directive anchors manually.
- **Compiler Layer Sovereignty**: The backend compiler (@[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L39-L290], @[backend_v2/services/orchestrator/localization_compiler.py#L22-L195], @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L18-L207]) is the sole authority responsible for assembling deterministic, 100% Context Caching-compliant XML hierarchies.
- **Layer 1 Global Mandates SSOT**: Universal system rules are centralized in @[backend_v2/models/prompts/global_mandates.py] and automatically injected into the static caching prefix.
- **TDA Assertion SSOT**: `TDAAssertion.concept_description` is the sole persistence container for claim-level evaluation rules. `MatrixClaim.ai_description` is permanently eradicated.

---

## 2. Architectural Impact & Compliance Matrix

### 2.1 Deprecations & Sunset List (What We Will REMOVE)

| Item to Remove / Deprecate | Current Location | Destination / Replacement |
| :--- | :--- | :--- |
| `MatrixClaim.ai_description` | @[backend_v2/models/v2_core.py#L324-L341] | **INTENTIONALLY DROPPED** / Migrated to `TDAAssertion.concept_description` |
| `MatrixClaim.aiDescription` | @[client_app_v2/lib/features/studio/models/prompt_block.dart] | **INTENTIONALLY DROPPED** / Bound to `TDAAssertion.conceptDescription` |
| 152 `ai_description` keys | @[backend_v2/seed/seed_data.json] (claims) | ✅ **ALREADY DONE** — 0 instances remain in seed_data.json |
| 27 redundant `system_rule` blocks | @[backend_v2/seed/seed_data.json] | ✅ **ALREADY DONE** — 0 matching block IDs remain in seed_data.json |
| Duck typing `getattr(claim, 'ai_description', None)` | @[backend_v2/services/studio/simulation_service.py#L181] | **INTENTIONALLY DROPPED** / Direct iteration over `claim.tda_assertions` |
| Lazy fallback `rendered = data.ai_description or ""` | @[backend_v2/services/studio/simulation_service.py#L159] | **INTENTIONALLY DROPPED** / Explicit `None` check |
| Reflection loop `find_value_by_key` (`hasattr`/`getattr`) | @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L140-L169] | **INTENTIONALLY DROPPED** / Replaced by typed `MechanicalAnchorsPayload` model |
| Hardcoded slug checks (`matrix_causal_analyst`) | @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L173] | **INTENTIONALLY DROPPED** / Replaced by `b.category_id == PromptBlockCategory.MATRIX` check |
| 7 `.get()` fallback chains for `execution_time` | @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L45-L290] | **INTENTIONALLY DROPPED** / Replaced by `ExecutionTimeResolver` pure function |
| Lazy fallback `LANGUAGE_NAMES.get(..., "English")` | @[backend_v2/services/orchestrator/localization_compiler.py#L95] | **INTENTIONALLY DROPPED** / Replaced by Fail-Fast `AppException` |
| Finnish error messages in `v2_core.py` | @[backend_v2/models/v2_core.py#L296-L321] and @[backend_v2/models/v2_core.py#L461-L544] | **INTENTIONALLY DROPPED** / Translated to English |
| Historical comments violating present tense | @[backend_v2/models/v2_core.py#L268] | **INTENTIONALLY DROPPED** / Present tense description |
| Manual string clipping `uuidHex.substring(0, 16)` | @[client_app_v2/lib/features/studio/models/prompt_block.dart] | ✅ **ALREADY DONE** — no `substring` calls found in prompt_block.dart |
| Duplicate UI widget `const SizedBox(height: 16)` | @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart] | **PURGED** (UI hygiene) |

### 2.2 Retained SSOT Invariants (What We Will RETAIN)

1. **`TDAAssertion` Core Fields**: `tda_id`, `concept_description`, `inverse_evidence`, `aggregation_mode`, `anchor_target`, `extraction_rule`.
2. **`MatrixClaim` Structure**: `label: I18nText` and `tda_assertions: list[TDAAssertion]`.
3. **`PromptBlock.ai_description`**: Retained for non-matrix blocks (specifically: system rules, scientific theories, extraction protocols) as the Single Source of Truth for instruction text.
4. **Prompt Preservation Mandate**: 100% mathematical fidelity of qualitative coaching text in 70 migrated claims.
5. **Step-Specific Task Directives**: `block_heuristic1`, `block_heuristic2`, `block_heuristic3`, `block_protocol1`, and primary matrix blocks retained in `criteria_block_ids`.
6. **Synthesis Pipeline Global Mandates**: Injections in @[backend_v2/worker.py] retained as correct for synthesis dynamic user context.

### 2.3 Quorum 2026 Invariants & Compliance Matrix

1. **Zero Legacy State Support & Zero Fallbacks**: Complete eradication of `MatrixClaim.ai_description` and redundant V1 blocks. No backward-compatibility shims, no fallback chains, and no dual-mode parsing. Clean slate DB re-seeding via `uv run python backend_v2/seed/run_seed.py local`.
2. **Central Config Sovereignty**: Minimum concept length (`tda_concept_min_length: 10`) centrally defined in @[backend_v2/settings.py#L51-L716] and mirrored in `SystemUiConstraints.tdaConceptMinLength` in @[client_app_v2/lib/core/models/enums.dart].
3. **Pydantic Strictness**: `ConfigDict(strict=True, extra='forbid')` enforced on all domain models and DTOs.
4. **Cross-Domain DTO Parity**: Backend Python Pydantic models and Flutter Dart Freezed models maintain 1:1 serialization parity. `tdaId` format is 32 hex chars (`tda_$uuidHex`), matching backend regex `^tda_[a-f0-9]{32}$`.
5. **Static-First Caching Topology**: 4-Layer Clean Stack compilation ensures Layer 1 global mandates and Layer 2-3 directives form a 100% cacheable static prefix. Dynamic user context is isolated at Layer 4.
6. **God Code Prevention & Clean Decomposition (@[ki_god_code_prevention.md])**:
   - **Anti-God File Dumping (`anti_god_file_dumping`)**: Every discrete domain concept (specifically: `global_mandates.py`, `matrix_sensor_prompt_builder.py`, `prompt_compiler_adapter.py`) MUST have its own dedicated module. Files approaching 200 lines MUST be treated as an architectural smell and decomposed outwards. Generic dumping grounds (`core.py`, `utils.py`, `helpers.py`) are strictly forbidden.
   - **Private Helper Bloat Ban (`private_helper_bloat_ban`)**: Logic extraction MUST default to creating new dedicated files rather than dumping private helper functions at the bottom of existing classes.
   - **DRY Composition Mandate (`dry_composition_mandate`)**: Shared logic MUST be extracted into composable injected services, base classes, or mixins without copy-pasting.
   - **Strategy & Registry Pattern (`strategy_pattern_mandate`)**: Branching logic based on types or enums MUST use static registries with Eager Loading instead of `if/elif/else` chains.
   - **Domain Model Purity (`domain_model_purity_mandate`)**: All models in `models/` and `dtos/` MUST be pure, stateless Data Transfer Objects (`ConfigDict(frozen=True, strict=True, extra="forbid")`). No database queries or service logic inside models.
   - **Validation Context Injection (`validation_context_injection`)**: Dynamic validation configuration MUST be injected via `ValidationInfo.context` during instantiation, never hardcoded in model validators.
   - **AST Boundary Verification (`ast_boundary_verification_mandate`)**: Method and class boundaries in files exceeding 300 lines (specifically `v2_core.py`) MUST be verified using `ast.parse` scripts before defining line bounds or editing.
   - **Clean-Cut Atomic Decomposition**: In active development mode, decomposing monolithic modules is executed cleanly and atomically across call-sites without temporary deprecated facades or dual-path fallback bridges.

### 2.4 Producer-Consumer Integration Check

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ DATA PRODUCERS                                                              │
│ - Seed Vault (@[backend_v2/seed/seed_data.json]): 152 TDA assertions        │
│ - Flutter Studio UI (Zero-XML forms): pure structured strings & lists       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ DOMAIN & VALIDATION BOUNDARY                                                │
│ - Pydantic V2 Models (@[backend_v2/models/v2_core.py])            │
│ - Freezed DTOs (@[client_app_v2/lib/features/studio/models/prompt_block.dart])│
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ COMPILER LAYER SOVEREIGNTY                                                  │
│ - Layer 1: @[backend_v2/models/prompts/global_mandates.py]                  │
│ - Layer 2-3: PromptFactory & MatrixSensorPromptBuilder                      │
│ - Layer 4: AliasEngine & LinkedAtomGraph payload compilation                │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ DATA CONSUMERS                                                              │
│ - LLM Execution Engine (Gemini / Anthropic Context Caching)                 │
│ - Atom Flattening Hook (@[backend_v2/hooks/atom_flattening.py#L34-L187])    │
│ - Simulation Service (@[backend_v2/services/studio/simulation_service.py])  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Phased Execution Plan (Implementation Strategy)

### 🌊 WAVE 1: TDA ASSERTION SSOT & PERSISTENCE HARMONIZATION (Improvement Target 7)

#### Phase 1: Pre-Requisite Technical Debt Cleanups & AST Guardrails
- **Pre-Implementation Technical Debt Cleanup**:
  - Eliminate duck typing in @[backend_v2/services/studio/simulation_service.py#L140-L195] by replacing `getattr(claim, 'ai_description', None)` with direct iteration over `claim.tda_assertions` reading `tda.concept_description`.
  - Clean up lazy fallback in @[backend_v2/services/studio/simulation_service.py#L140-L195] (`rendered = data.ai_description or ""` ) by replacing with explicit `None` check.
  - Un-skip and fix pre-existing broken test in @[backend_v2/tests/unit/test_tier4_schema_bug.py#L9-L75]: remove `@pytest.mark.skip`, fix `concept_description` from `I18nText` dictionary to plain string with 10 or more characters, and remove `ai_description` from claim fixture.
  - Verify @[backend_v2/tests/unit/test_schema_builder.py] to confirm `ai_description` refers to `PromptBlock` (retained) rather than `MatrixClaim`.
- **AST Guardrail Implementation**:
  - Create [NEW] @[backend_v2/tests/unit/test_ast_matrix_claim_guardrails.py] with 9 AST and seed guardrail tests:
    1. `test_seed_claims_have_no_ai_description`: Asserts 0 matrix claims in `seed_data.json` contain `ai_description`.
    2. `test_seed_claims_all_tda_assertions_have_valid_concept_description`: Asserts all 152 `tda_assertions` have `concept_description` with length >= 10.
    3. `test_settings_tda_concept_min_length_defined`: Asserts `backend_v2/settings.py` defines `tda_concept_min_length == 10`.
    4. `test_ast_matrix_claim_has_no_ai_description_field`: Verifies via `ast.parse` that `MatrixClaim` class in @[backend_v2/models/v2_core.py#L324-L341] does not define `ai_description`.
    5. `test_ast_tda_assertion_has_string_constraints_min_length_10`: Verifies via AST that `TDAAssertion.concept_description` in @[backend_v2/models/v2_core.py#L226-L321] enforces `min_length=10`.
    6. `test_simulation_service_ast_no_claim_ai_description_access`: Asserts @[backend_v2/services/studio/simulation_service.py] contains no `getattr(claim, 'ai_description', ...)` or `claim.ai_description` accesses.
    7. `test_simulation_service_ast_no_hasattr_getattr`: Verifies via `ast.parse` that @[backend_v2/services/studio/simulation_service.py] contains 0 `getattr` and 0 `hasattr` calls.
    8. `test_ast_guardrail_catches_invalid_matrix_claim_negative`: Proves AST scanner detects violations by passing a mock AST node of `MatrixClaim` containing `ai_description: str`.
    9. `test_ast_guardrail_catches_missing_string_constraints_negative`: Proves AST scanner detects violations by passing a mock AST node of `TDAAssertion` without `StringConstraints(min_length=10)`.

#### Phase 2: Seed Data Migration & Vault Mutation
> [!NOTE]
> **Neuro-Symbolic Verification (Tier 0 Audit Result):** Codebase grep confirms `seed_data.json` already has 0 `ai_description` keys on claims and 0 redundant global mandate block IDs. Phase 2 scope is reduced to VERIFICATION-ONLY.

- **Seed Verification Script**: Execute a read-only validation script from scratch/ to confirm:
  - 0 `ai_description` keys remain on any `MatrixClaim` in `prompt_blocks`.
  - All 152 `TDAAssertion` objects have non-empty `concept_description` (pre-min_length enforcement).
- **Seed Integrity & Reseed**: Validate JSON parsing of @[backend_v2/seed/seed_data.json] and execute database re-seeding via `uv run python backend_v2/seed/run_seed.py local`.
- **Checkpoint**: Atomic commit and session handover.

#### Phase 3: Backend Domain & Service Harmonization
- **Settings & Domain Models**:
  - Modify @[backend_v2/settings.py#L51-L716]: Define `tda_concept_min_length: Annotated[int, Field(description="Minimum character length for TDA assertion concept descriptions.")] = 10`.
  - Modify @[backend_v2/models/v2_core.py#L226-L321]: In `TDAAssertion`, update `concept_description` to `Annotated[str, StringConstraints(strip_whitespace=True, min_length=10)] = Field(description="Concise concept definition for this assertion, not runtime instructions")`.
  - Update adjacent Finnish descriptions on `TDAAssertion` to English: `anchor_target` (`description="Target anchor to search for during extraction"`) and `extraction_rule` (`description="The extraction rule that data must satisfy"`).
  - Modify @[backend_v2/models/v2_core.py#L324-L341]: In `MatrixClaim`, delete the `ai_description: str` field entirely, leaving only `label: I18nText` and `tda_assertions: list[TDAAssertion]`.
  - Boy Scout: Replace historical comment in `v2_core.py` with present-tense description: `# Monolingual concept description consumed by the LLM extraction pipeline`.
  - Boy Scout: Translate 3 Finnish error messages in `validate_math_logic` validator in @[backend_v2/models/v2_core.py#L226-L321] to English:
    - `"Inverse evidence (poison detection) strictly requires 'EXISTS' aggregation mode."`
    - `"EXTRACTIVE_SENSOR track requires at least one fact in facts_to_find."`
    - `"EXTRACTIVE_SENSOR track requires a defined logical_expression."`
- **Hooks & Prompt Builders**:
  - **VERIFICATION-ONLY** for @[backend_v2/hooks/atom_flattening.py#L133]: Confirm `tda.concept_description.strip()` is already used (verified by Tier 0 audit — no migration needed, `.strip()` is standard whitespace normalization).
  - Update @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L93-L207]: Enforce Fail-Fast exception with RFC 7807 structured `logger.error` if `assertion.question` is empty string before generating XML question block.
- **ATOMIC Test Fixture Harmonization (Merged from Phase 5)**:
  - Update mock claims across 23 backend test files in 2 batches, updating 39 short concept strings across 12 files to 10 or more characters:
  - Batch 1 (Core Services & Hooks):
    1. @[backend_v2/tests/unit/services/test_blueprint.py]
    2. @[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py]
    3. @[backend_v2/tests/unit/test_epic93_contract_verification.py]
    4. @[backend_v2/tests/unit/test_worker.py]
    5. @[backend_v2/tests/unit/hooks/test_atom_flattening.py]
    6. @[backend_v2/tests/unit/hooks/test_scoring.py]
    7. @[backend_v2/tests/unit/services/test_matrix_domain_parser.py]
    8. @[backend_v2/tests/unit/services/orchestrator/test_atomizer.py]
    9. @[backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py]
    10. @[backend_v2/tests/unit/services/orchestrator/test_schema_matrix_bug.py]
    11. @[backend_v2/tests/unit/services/orchestrator/test_schema_matrix_omission.py]
  - Batch 2a (Orchestration & Strategies — 6 files):
    12. @[backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py]
    13. @[backend_v2/tests/unit/services/orchestrator/test_causal_analyst_schema.py]
    14. @[backend_v2/tests/unit/services/studio/test_workflow_service.py]
    15. @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]
    16. @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_prompt_factory.py]
    17. @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_epic_60_decoupling.py]
  - Batch 2b (Integration, Bugs & Verification — 6 files):
    18. @[backend_v2/tests/integration/test_lazy_llm_simulation.py]
    19. @[backend_v2/tests/integration/test_epic_chain_e2e.py]
    20. @[backend_v2/tests/unit/models/domain/test_prompt_block_computed_bug.py]
    21. @[backend_v2/tests/unit/services/orchestrator/test_atom_id_order_bug.py]
    22. @[backend_v2/tests/unit/test_tier4_schema_bug.py]
    23. @[backend_v2/tests/unit/test_schema_builder.py]
  - **Frontend Test Fixtures Update**:
    - Update @[client_app_v2/test/features/studio/views/components/bars_matrix_builder_test.dart] removing `aiDescription` parameter from `MatrixClaim` test fixtures.
  - **Quality Gates (MANDATORY BEFORE CHECKPOINT)**:
    - Run `uv run python scripts/backend_audit_loop.py backend_v2 --test`
    - Run `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`
- **Checkpoint**: Atomic commit and session handover.

#### Phase 4: Flutter Studio Client Harmonization
- **Centralized Enums & Freezed Models**:
  - Modify @[client_app_v2/lib/core/models/enums.dart]: Add `tdaConceptMinLength(10)` to `SystemUiConstraints` enum.
  - Modify @[client_app_v2/lib/features/studio/models/prompt_block.dart]:
    - In `TDAAssertion.create` factory, replace `tdaId: 'tda_${uuidHex.substring(0, 16)}'` with `tdaId: 'tda_$uuidHex'` to produce 32 hex chars, ensuring 1:1 regex parity with backend `^tda_[a-f0-9]{32}$`.
    - Remove `required String aiDescription` from `MatrixClaim` Freezed model definition.
  - Run build runner: `dart run build_runner build --delete-conflicting-outputs`.
- **Studio Views Alignment**:
  - Modify @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]: Instantiate `MatrixClaim` with `label` and `tdaAssertions` containing default `TDAAssertion.create(conceptDescription: 'CRITICAL MANDATE: ', inverseEvidence: false, aggregationMode: AggregationMode.exists)`. Remove `claim.aiDescription` TextFormField. Route rule editing directly to `claim.tdaAssertions.first.conceptDescription` with form validator checking `value.trim().length >= SystemUiConstraints.tdaConceptMinLength.value`. Clean up redundant duplicate `const SizedBox(height: 16)`.
  - Modify @[client_app_v2/lib/features/studio/views/components/bars_matrix_builder.dart]: Replace display of `claim.aiDescription` with `claim.tdaAssertions.isNotEmpty ? claim.tdaAssertions.first.conceptDescription : ''`.
  - Modify @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]: Update default `MatrixClaim` instantiation in dialog to omit `aiDescription` and supply valid `tdaAssertions` via `TDAAssertion.create`.
- **Checkpoint**: Atomic commit and session handover.

#### Phase 5: MERGED INTO PHASE 3
> [!IMPORTANT]
> **Tier 0 Atomicity Mandate:** Phase 5 test fixture updates have been merged into Phase 3 to prevent the catastrophic failure scenario where `StringConstraints(min_length=10)` enforcement on `TDAAssertion.concept_description` causes 39+ test fixtures to crash before they are updated. This enforces the "Atomic Data & Test Migration" invariant.

---

### 🌊 WAVE 2: ZERO-XML UI & CLEAN STACK PROMPT ENGINE (Improvement Target 8)

#### Phase 6: Layer 1 Global Mandates Injection & Compiler Foundation
- **Global Mandates SSOT**:
  - ✅ **ALREADY DONE**: 11 system mandates already centralized in @[backend_v2/models/prompts/global_mandates.py] (`GLOBAL_MANDATES_XML` constant with 11 named XML blocks).
- **Static Prefix Injection (Context Cache Migration)**:
  - In @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L242]: **REMOVE** `GLOBAL_MANDATES_XML` from `exec_params` (user payload). **INJECT** into Layer 1 of `base_system_prompt` (static prefix) with exact insertion order: `GLOBAL_MANDATES_XML` → `execution_persona_block.ai_description` → `ROLE_DIRECTIVE` → `EXTRACTION_PROTOCOL` → `CRITERIA_GUIDELINES`.
  - In @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L36-L91]: Prepend `GLOBAL_MANDATES_XML.strip()` into Layer 1 of the static caching prefix.
- **Scoped Boy Scout Refactoring in Compiler**:
  - In `prompt_factory.py#L140-L169`: completely eliminate `find_value_by_key` reflection loop. Eradicate all `hasattr()` and `getattr()` calls across the entire module. Replace with typed `MechanicalAnchorsPayload` Pydantic model defined in @[backend_v2/models/domain/] with exactly these fields:
    ```python
    class MechanicalAnchorsPayload(V2CoreBase):
        model_config = ConfigDict(strict=True, extra="forbid")
        word_count: int = Field(description="Word count of the source document.")
        say_do_gap: float = Field(description="Say-Do gap ratio metric.")
        automation_bias: float = Field(description="Automation bias detection score.")
        performative_patterns: list[PerformativePattern] = Field(
            default_factory=list,
            description="Detected performative phrase patterns.",
        )
    ```
  - In `prompt_factory.py#L173`: eliminate hardcoded slug checks (replace with `b.category_id == PromptBlockCategory.MATRIX`).
  - In `prompt_factory.py#L86-L132`: eliminate all 7 `.get()` fallback chains and naked dict probing for `execution_time` (replace with `ExecutionTimeResolver` pure function in @[backend_v2/services/orchestrator/strategies/llm_execution/]). Enforce `no_naked_dicts_in_state`: all context data consumed by the compiler must use strictly typed Pydantic models.
  - In @[backend_v2/services/orchestrator/localization_compiler.py#L95]: Replace `LANGUAGE_NAMES.get(..., "English")` lazy fallback with Fail-Fast validation raising `AppException(VALIDATION_FAILED)`.

#### Phase 7: Structured PromptBlock Domain Models & AST Guardrails
- **Pydantic Domain Models**:
  - Enhance `PromptBlock` in @[backend_v2/models/v2_core.py#L380-L544] with structured pure data fields:
    - `objective: Annotated[str | None, Field(default=None, description="Pure rubric objective.")] = None`
    - `evaluation_rules: Annotated[list[str], Field(default_factory=list, description="Specific evaluation boundaries.")] = []`
    - `banned_concepts: Annotated[list[str], Field(default_factory=list, description="Explicit negative heuristics.")] = []`
    - `role_enforcement: Annotated[str | None, Field(default=None, description="Role directive enforcement.")] = None`
  - Translate all Finnish error messages in `PromptBlock.pre_validate_block_consistency` in @[backend_v2/models/v2_core.py#L380-L544] to English.
- **Flutter Freezed Synchronization**:
  - Update Dart `PromptBlock` Freezed class in @[client_app_v2/lib/features/studio/models/prompt_block.dart] with `objective`, `evaluationRules`, `bannedConcepts`, `roleEnforcement`.
  - Run build runner: `dart run build_runner build --delete-conflicting-outputs`.
- **AST Guardrail Implementation**:
  - Create [NEW] @[backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py] with 8 static AST tests verifying:
    1. `ConfigDict(strict=True, extra="forbid")` on all new domain models.
    2. Zero `hasattr()` or `getattr()` calls in @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L45-L290].
    3. Zero `find_value_by_key` function definitions in @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L45-L290].
    4. Zero `.slug` checks in @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L45-L290].
    5. Zero naked dictionary traversals (`isinstance(x, dict)`) in mechanical anchors extraction.
    6. Strict XML layer ordering compliance (Layer 1 global mandates → Layer 2 persona/role → Layer 3 protocol/guidelines → Layer 4 runtime awareness).
    7. Negative test detecting and failing on any newly introduced `hasattr`/`getattr` calls.
    8. Negative test detecting and failing on any newly introduced `.get()` fallback chains.

#### Phase 8: Clean Stack Compiler Layer Assembly
- **Deterministic XML Assembly**:
  - Update @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L45-L290] and @[backend_v2/services/orchestrator/localization_compiler.py#L79-L115] to assemble the 4-layer XML hierarchy deterministically from structured fields when `ai_description` is `None`.
  - Update @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L36-L91] to compile matrix objective, evaluation rules, and banned concepts with strict XML wrappers (`<objective>`, `<evaluation_rules>`, `<banned_concepts>`), and wrap `theory_grounding.citation_reference` into `<theory_context>` while strictly excluding `source_url` from the prompt.

#### Phase 9: Flutter Studio Zero-XML UI Modernization
- **UI Views Modernization**:
  - In @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]: Replace raw `ai_description` textarea with structured form sections (Objective input, Evaluation Rules dynamic list, Banned Concepts dynamic list, Role Enforcement input, and read-only live "Compiled Prompt Preview" modal/sheet).
  - In @[client_app_v2/lib/features/studio/views/step_builder_view.dart]: Streamline step criteria block selection list now that global system rules are automatically applied by Layer 1.
  - Add corresponding localization keys in `client_app_v2/lib/l10n/app_en.arb` and `client_app_v2/lib/l10n/app_fi.arb`.
  - Run `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`.

#### Phase 10: Seed Vault Pruning & Database Reseeding
- **Programmatic Redundancy Verification**: Execute Python audit script in `scratch/` proving candidate blocks are 100% covered by `GLOBAL_MANDATES_XML`.
- **Vault Pruning**:
  - Remove verified redundant global mandate blocks (specifically and exhaustively: `block_headermandates`, `block_mandate2`, `block_mandate3`, `block_mandate5`, `block_headerrules`, `block_rule1`, `block_rule2`, `block_rule3`, `block_rule4`, `block_rule5`, `block_rule6`, `block_oprule1`, `block_oprule2`, `block_oprule3`, `block_instructionnohallucination`, `block_instructionlanguage_dynamic`, `block_headerinstructions`) from individual step `criteria_block_ids` in @[backend_v2/seed/seed_data.json].
  - Fix corrupted HTML entity in `seed_data.json` (`&lt;mechanical_anchors&gt;` -> `<mechanical_anchors>`).
  - Reseed local database: `uv run python backend_v2/seed/run_seed.py local`.

#### Phase 11: End-to-End Live Integration Verification Gate
- **Live LLM Verification**: Execute live E2E integration test via PowerShell:
  - `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_epic_chain_e2e.py`
- **Knowledge Base & Rule Synchronization**:
  - Update `@[ki_llm_extraction_architecture.md]` with Zero-XML UI paradigm and 4-Layer Clean Stack Model specification.
  - Synchronize `@[.agents/rules/05_llm_architecture.md]` enforcing that XML tags are generated exclusively by the compiler layer.

---

## 4. Definition of Done (DoD) & Verification Plan

### 4.1 Definition of Done (DoD)
1. **Zero MatrixClaim `ai_description`**: 0 instances of `ai_description` remain on `MatrixClaim` in backend, frontend, or database seed.
2. **Zero Empty TDA Concept Descriptions**: All 152 TDA assertions in `seed_data.json` have `concept_description` with length >= 10 characters.
3. **Global Config SSOT**: `tda_concept_min_length: 10` is defined in `backend_v2/settings.py` and `SystemUiConstraints.tdaConceptMinLength` in `client_app_v2/lib/core/models/enums.dart`.
4. **Zero-XML UI**: Studio UI users input pure natural text and structured lists; XML compilation is handled exclusively by the compiler layer.
5. **Context Cache Prefix Stability**: Layer 1-3 form a 100% static, cacheable system prompt prefix with dynamic data isolated at Layer 4.
6. **Audit Gates Passed**: 100% pass on `backend_audit_loop.py` and `flutter_audit_loop.py --build` with zero warnings or errors.

### 4.2 Automated Unit & AST Tests
```powershell
# AST Guardrails Suite
uv run pytest backend_v2/tests/unit/test_ast_matrix_claim_guardrails.py
uv run pytest backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py

# Global Backend Audit Loop
uv run python scripts/backend_audit_loop.py backend_v2 --test

# Global Flutter Audit Loop
uv run python scripts/flutter_audit_loop.py client_app_v2 --build
```

### 4.3 Anti-Happy-Path Negative Verification Scenarios (ISTQB Compliant)

1. **NEG-01 (TDA Concept Too Short)**: `TDAAssertion(concept_description="Short")` -> raises Pydantic `ValidationError` (`min_length=10`).
2. **NEG-02 (MatrixClaim with ai_description)**: Deserializing dict containing `ai_description` -> raises Pydantic `ValidationError` (`extra_forbidden`).
3. **NEG-03 (MatrixSensor Empty Question)**: Trigger prompt builder with `assertion.question=""` -> raises `AppException(ErrorCodes.VALIDATION_FAILED)` with structured `logger.error`.
4. **NEG-04 (AST Scanner MatrixClaim Negative)**: Mock AST snippet of `MatrixClaim` with `ai_description` -> detected and flagged by AST scanner.
5. **NEG-05 (PromptFactory Missing Context Data)**: Missing expected keys in `llm_context_data` -> raises Fail-Fast `AppException` without silent fallback.
6. **NEG-06 (LocalizationCompiler Invalid Locale)**: Unsupported `target_locale` -> raises `AppException(ErrorCodes.VALIDATION_FAILED)` without fallback to `"English"`.
7. **NEG-07 (Raw User Payload with XML Characters)**: Unescaped `<, >, &` in payload -> CDATA and XML escaping preserved without broken XML syntax.
8. **NEG-08 (AST Scanner Reflection Ban)**: AST verification of `prompt_factory.py` -> flags any presence of `hasattr` or `getattr`.

### 4.4 Mandatory Final E2E REST API Verification Gate
```powershell
$env:RUN_LIVE_E2E="true"
uv run pytest backend_v2/tests/integration/test_epic_chain_e2e.py
```

---

## 5. Required Context & Governance (Rules & KI Registry)

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
  <knowledge_item>@[ki_synthesis_payload_compression.md]</knowledge_item>
  <knowledge_item>@[ki_context_enriched_pipeline.md]</knowledge_item>
</required_context_rules>
```
