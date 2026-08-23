# Architectural Implementation Plan: Zero-XML UI & Automated Prompt Assembly Pipeline

## 1. Executive Summary & First Principles

### 1.1 Context & Motivation
In Quorum, cognitive evaluation relies on foundational LLMs (Gemini, Claude) instructed via Server-Driven Prompts. Currently, the Studio UI exposes raw text fields (`ai_description`) across dozens of granular prompt blocks (specifically: `system_rule`, `matrix`, `role`, `protocol`, `execution_persona`), requiring humans to understand and manually construct XML tags (`<banned_concepts>`, `<role_enforcement>`, `<theory_context>`) and `ALL-CAPS` directive anchors.

Furthermore, Studio Steps currently associate up to 27 redundant, fine-grained `system_rule` blocks (specifically: `block_headermandates`, `block_mandate2..5`, `block_headerrules`, `block_rule1..6`, `block_oprule1..3`, `block_headerinstructions`, `block_instructionlanguage_dynamic`), creating UI clutter, cognitive overload, and fragile prompt configurations.

### 1.2 The Architectural Goal: Zero-XML UI & Automated Prompt Assembly
1. **Zero-XML UI**: The human user in Studio UI or Matrix Editor writes **pure, natural text and structured lists** (specifically: `objective`, list of `banned_concepts`, `evaluation_rules`, `role_enforcement`, and `theory_grounding` citations). The user NEVER writes raw XML tags.
2. **Deterministic Prompt Compilation (Clean Stack Model)**: The backend compiler (`PromptFactory`, `LocalizationCompiler`, `MatrixSensorPromptBuilder`) deterministically assembles these structured models into a 100% Context Caching-compliant, 4-tier XML hierarchy.
3. **Global Mandates SSOT**: Universal system rules (Null Hypothesis, Anti-Score, Anti-ID, Epistemic Glossary, Semantic Bleed, Verbatim Extraction, Extension Anchoring, Tone, Schema Purity, Context Segregation, Language Mandates) are injected automatically from `global_mandates.py` without requiring manual block selection in the Studio UI.
4. **Preserve Dynamic Matrix Creation**: Creating new matrices remains 100% dynamic, plug-and-play, and decoupled from underlying system rules.

> **SESSION EXECUTION PLAN**: This plan MUST be executed across 3 separate `/tier2-execute` sessions:
> - **Session A**: Phase 1 + Phase 2 (Backend Models + Compiler Layer)
> - **Session B**: Phase 3 (Seed Data Simplification)
> - **Session C**: Phase 4 + Phase 5 (Flutter UI + Tests)

---

## 2. The Unified 4-Layer Prompt Architecture (Clean Stack Model)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: GLOBAL SYSTEM INVARIANTS (Automated by Backend)                    │
│   Source: backend_v2/models/prompts/global_mandates.py                      │
│   Injected into: static prefix (100% Gemini Context Cacheable)              │
│   Tags: <global_system_mandates> containing:                                │
│         <language_mandate>, <anti_score_mandate>, <anti_id_mandate>,        │
│         <epistemic_glossary>, <semantic_bleed_mandate>,                     │
│         <null_hypothesis_mandate>, <verbatim_extraction_mandate>,           │
│         <extension_anchoring_mandate>, <tone_mandate>,                      │
│         <schema_purity_mandate>, <context_segregation_mandate>              │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 2: STEP GOVERNANCE & PROTOCOLS (Configured in Step Blueprint)         │
│   - <EXECUTION_PERSONA>: How LLM parses (Deterministic Parser or XAI)      │
│   - <ROLE_DIRECTIVE>: Operational mode (Prosecutor, Analyst, or Coach)      │
│   - <EXTRACTION_PROTOCOL>: Evidence extraction rules (Zero-Trust Quotes)    │
│   - <TASK_DIRECTIVES>: Step-specific heuristics (Passivity, PII, Tone)      │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 3: DOMAIN CRITERIA MATRIX (Configured in Matrix PromptBlock)          │
│   - <CRITERIA_GUIDELINES> containing:                                       │
│     - <objective>: Pure rubric objective string                             │
│     - <evaluation_rules>: Specific evaluation boundaries                    │
│     - <banned_concepts>: Explicit negative heuristics                       │
│     - <role_enforcement>: Role enforcement directive                        │
│     - <theory_context>: Verbatim academic citation (from TheoryGrounding)   │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 4: DYNAMIC CLAIMS & EVIDENCE PAYLOAD (Per-Execution Dynamic Tail)     │
│   - <execution_context>: Target locale, document date, mechanical anchors   │
│   - <context>: User source document (HTML-escaped, cached)                  │
│   - <user_payload>: LinkedAtomGraph nodes with obfuscated aliases (a0..an)  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Required Context Rules & Knowledge Items

<required_context_rules>
- @[.agents/rules/00-antigravity-core.md] (Strict Windows 11, Zero-Fallback, Atomic Commits)
- @[.agents/rules/01-python-backend.md] (Pydantic V2 strictness, ConfigDict extra=forbid, no duct-tape)
- @[.agents/rules/02_flutter_desktop.md] (Flutter Riverpod, AppLocalizations, no hardcoded colors/strings)
- @[.agents/rules/03_seed_vault.md] (Database seed integrity, UUID preservation, prompt text preservation)
- @[.agents/rules/05_llm_architecture.md] (XML Structural Sovereignty, Context Caching, Alias Engine)
- @[ki_llm_extraction_architecture.md]
- @[ki_global_config_sovereignty.md]
- @[ki_ast_guardrail_testing.md]
</required_context_rules>

---

## 4. Phase-by-Phase Technical Implementation Plan

### Phase 1: Pre-Requisite Technical Debt Cleanups & Domain Models

#### Pre-Implementation Technical Debt Cleanups (Boy Scout Rule)
1. **`@[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L140-L176]`**:
   - Eliminate anti-pattern `find_value_by_key` that uses `hasattr(obj, "__dict__")`, `hasattr(obj, key)`, and `getattr(obj, key)` recursive reflection loops. Replace with a strictly typed `MechanicalAnchorsDTO` Pydantic model (`ConfigDict(strict=True, extra='ignore')`) hydrated from `llm_context_data` at the call boundary.
   - Eliminate hardcoded `slug` checks (`if getattr(b, "slug", None) in ("matrix_causal_analyst", "block_taskperformativity"):`) in compliance with `slug_data_relation_ban` and `zero_db_hardcoding_mandate`. Replace with structural checks: `b.category_id == PromptBlockCategory.MATRIX` combined with checking whether `MechanicalAnchorsDTO` contains active non-zero metrics.
2. **`@[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L88-L132]`**:
   - Eliminate 7 nested `.get(key, default)` chains for `execution_time` resolution. This violates `fail_fast_hydration_mandate` and `the_duct_tape_ban`. Replace with an `ExecutionTimeResolver` pure function that uses structured Pydantic DTOs or explicit key lookups with Fail-Fast handling on missing keys.
   - Remove `isinstance(llm_context_data, dict)` guard on L88 — the parameter is typed `dict[str, Any]`.
3. **`@[backend_v2/services/orchestrator/localization_compiler.py#L95]` & `@[backend_v2/services/orchestrator/localization_compiler.py#L171]`**:
   - Replace `LANGUAGE_NAMES.get(target_locale.split("-")[0].lower(), "English")` lazy fallback with Fail-Fast validation: if the locale is not in `LANGUAGE_NAMES`, raise `AppException(message=f"Unsupported target_locale '{target_locale}'", status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})`.
   - Update `LocalizationCompiler.compile_static_instructions` (L97-L115) to compile from structured fields (`objective`, `evaluation_rules`, `banned_concepts`, `role_enforcement`) when `ai_description` is `None`, instead of raising `ConfigurationError("PromptBlock is missing mandatory 'ai_description'")`.
4. **`@[backend_v2/models/v2_core.py#L505-L540]`**:
   - Translate all Finnish error messages in `PromptBlock.pre_validate_block_consistency` (`"Jos scales on valittu käyttöön..."`, `"Jokaisella scorella pitää olla vähintään yksi claim."`, `"Kun category_id on 'matrix'..."`) to English per `english_language_mandate`.
5. **Cross-Domain DTO Parity (`@[client_app_v2/lib/features/studio/models/prompt_block.dart#L197-L230]`)**:
   - Update Dart `PromptBlock` Freezed class to mirror backend fields synchronously, avoiding `disallowUnrecognizedKeys: true` client crashes when fetching blocks with new fields:
     - `String? objective`
     - `@JsonKey(name: 'evaluation_rules') @Default([]) List<String> evaluationRules`
     - `@JsonKey(name: 'banned_concepts') @Default([]) List<String> bannedConcepts`
     - `@JsonKey(name: 'role_enforcement') String? roleEnforcement`
   - **ATOMIC COMMIT MANDATE**: The Python `v2_core.py` and Dart `prompt_block.dart` changes MUST be committed in the same `git commit` to prevent White Screen of Death from `disallowUnrecognizedKeys: true`.

**Target Files:**
- `@[backend_v2/models/v2_core.py#L405-L545]`
- `@[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L88-L204]`
- `@[backend_v2/services/orchestrator/localization_compiler.py#L95-L175]`
- `@[client_app_v2/lib/features/studio/models/prompt_block.dart#L197-L230]`
- `@[backend_v2/models/prompts/matrix_evaluation.py#L1-L20]`
- `@[backend_v2/models/prompts/global_mandates.py#L1-L161]`

**Tasks:**
1. Enhance `PromptBlock` in `v2_core.py` using PEP 593 `Annotated` syntax:
   - Keep `ai_description: Annotated[str | None, Field(default=None, description="Legacy/fallback raw English cognitive instructions.")] = None`.
   - Add structured optional fields to `PromptBlock` as **pure data fields** (NO auto-compilation into `ai_description`):
     - `objective: Annotated[str | None, Field(default=None, description="Pure rubric objective.")] = None`
     - `evaluation_rules: Annotated[list[str], Field(default_factory=list, description="Specific evaluation boundaries.")] = []`
     - `banned_concepts: Annotated[list[str], Field(default_factory=list, description="Explicit negative heuristics.")] = []`
     - `role_enforcement: Annotated[str | None, Field(default=None, description="Role directive enforcement.")] = None`
   - **DO NOT** add a `@model_validator(mode="after")` for auto-compilation. XML wrapping is the Compiler Layer's responsibility (Phase 2). The Domain Model stores pure data only.
2. Verify `ConfigDict(strict=True, extra="forbid")` compliance across all updated models.
3. Synchronize `PromptBlock` in `client_app_v2/lib/features/studio/models/prompt_block.dart` with Freezed and JSON serialization.
4. Run `uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --test` and `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/prompt_block.dart --build`.

---

### Phase 2: Compiler Layer Automated Assembly & Context Cache Optimization

> **SESSION A continues here** — this phase is coupled with Phase 1.

**Target Files:**
- `@[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L170-L265]`
- `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L37-L92]`
- `@[backend_v2/services/orchestrator/prompt_compiler_adapter.py#L1-L140]`
- `@[backend_v2/services/orchestrator/localization_compiler.py#L79-L116]`

**Tasks:**
1. Update `PromptFactory.build`:
   - Move `GLOBAL_MANDATES_XML` into Layer 1 of `base_system_prompt` (static prefix), removing it from dynamic `exec_params` (currently at L242: `exec_params += f"{GLOBAL_MANDATES_XML}\n"`). This maximizes Context Caching hit rate since the system prompt prefix becomes a longer, stable cacheable block.
   - Add **structured field compilation**: When `PromptBlock.objective`, `evaluation_rules`, `banned_concepts`, or `role_enforcement` are populated, the compiler wraps them in XML tags (`<objective>`, `<evaluation_rules>`, `<banned_concepts>`, `<role_enforcement>`) inside `<CRITERIA_GUIDELINES>`.
   - Format `execution_persona_block` cleanly into `<EXECUTION_PERSONA>...</EXECUTION_PERSONA>`.
   - Format `role_block` into `<ROLE_DIRECTIVE>...</ROLE_DIRECTIVE>`.
   - Format `protocol_block` into `<EXTRACTION_PROTOCOL>...</EXTRACTION_PROTOCOL>`.
   - Wrap task heuristics and rules into `<TASK_DIRECTIVES>...</TASK_DIRECTIVES>`.
2. Update `MatrixSensorPromptBuilder.build_caching_prefix`:
   - **CRITICAL GAP FIX**: Prepend `GLOBAL_MANDATES_XML.strip()` into `system_content` at Layer 1 of the static caching prefix. Currently, matrix sensor evaluations run WITHOUT global mandates (language mandate, null hypothesis, verbatim extraction). This is a live quality gap.
   - Compile matrix objective, evaluation rules, and banned concepts with strict XML wrappers (`<objective>`, `<evaluation_rules>`, `<banned_concepts>`).
   - Wrap `theory_grounding.citation_reference` into `<theory_context>` and ensure `source_url` is strictly excluded from the LLM prompt.
3. **BLAST RADIUS NOTE — `worker.py`**: `@[backend_v2/worker.py#L900]`, `@[backend_v2/worker.py#L1064]`, and `@[backend_v2/worker.py#L1164]` also inject `GLOBAL_MANDATES_XML` into dynamic user context for synthesis operations. These usages are CORRECT for the synthesis pipeline (where the system prompt is the synthesis block's `ai_description`, and mandates belong in the dynamic user context). Do NOT modify these — they serve a different architectural pipeline.

---

### Phase 3: Seed Data & Step Simplification (Database Optimization)

> **SESSION B starts here** — Execute `/tier5-session-handover` after completing Phase 2, then `/tier2-execute` in a new session.

**Target Files:**
- `@[backend_v2/seed/seed_data.json]`
- `@[data/db_v2.json]`

**Tasks:**
1. Execute Seed Vault Protocol (Step 2 Backup to `backend_v2/seed/backups/seed_data_<timestamp>.json`).
2. Fix corrupted HTML entities in `seed_data.json`:
   - Change `&lt;mechanical_anchors&gt;` to `<mechanical_anchors>` in `blk_b4912f9ff3a24b31` (`block_taskperformativity`).
3. **PROGRAMMATIC REDUNDANCY VERIFICATION (MANDATORY PRE-REQUISITE)**: Before removing any block from `criteria_block_ids`, write and execute a Python audit script (in `scratch/`) that:
   - Loads `seed_data.json` and extracts the `ai_description` of each candidate block for removal.
   - Compares each block's content against `GLOBAL_MANDATES_XML` constant to mathematically prove the block's instructions are already covered.
   - Outputs a pass/fail report per block. Only blocks with 100% coverage may be removed.
4. Streamline `criteria_block_ids` across all LLM steps in `seed_data.json` (ONLY for blocks verified in Task 3):
   - Remove verified redundant global mandate blocks (specifically and exhaustively: `block_headermandates`, `block_mandate2`, `block_mandate3`, `block_mandate5`, `block_headerrules`, `block_rule1`, `block_rule2`, `block_rule3`, `block_rule4`, `block_rule5`, `block_rule6`, `block_oprule1`, `block_oprule2`, `block_oprule3`, `block_instructionnohallucination`, `block_instructionlanguage_dynamic`, `block_headerinstructions`) from individual step `criteria_block_ids`, as they are now 100% handled automatically by Layer 1 `global_mandates.py`.
   - Keep only step-specific task directives (specifically: `block_heuristic1`, `block_heuristic2`, `block_heuristic3`, `block_protocol1`) and the primary matrix block.
5. Re-seed local database: `uv run python backend_v2/seed/run_seed.py local`.

---

### Phase 4: Flutter Studio UI Alignment (Zero-XML User Experience)

> **SESSION C starts here** — Execute `/tier5-session-handover` after completing Phase 3, then `/tier2-execute` in a new session.

**Target Files:**
- `@[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart#L400-L550]`
- `@[client_app_v2/lib/features/studio/views/step_builder_view.dart#L700-L850]`
- `@[client_app_v2/lib/l10n/app_en.arb]` & `@[client_app_v2/lib/l10n/app_fi.arb]`

**Tasks:**
1. In `prompt_block_builder_view.dart`:
   - Replace raw `ai_description` textarea with structured form sections:
     - `Objective`: Single-line / multi-line text input for pure rubric goal.
     - `Evaluation Rules`: Reorderable dynamic list with Add / Remove rule buttons.
     - `Banned Concepts`: Dynamic list with Add / Remove negative heuristic items.
     - `Role Enforcement`: Optional role enforcement text input.
   - Add a read-only live "Compiled Prompt Preview" button/sheet that shows the generated XML without allowing manual XML entry.
2. In `step_builder_view.dart`:
   - Streamline Step criteria selection list now that global system rules are automatically applied by Layer 1.
3. Add corresponding localization keys in `app_en.arb` and `app_fi.arb`:
   - `promptBlockObjectiveLabel`, `promptBlockRulesLabel`, `promptBlockBannedConceptsLabel`, `promptBlockRoleEnforcementLabel`, `promptBlockCompiledPreviewTitle`, `promptBlockAddRuleButton`, `promptBlockAddBannedConceptButton`.
4. Run `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`.

---

### Phase 5: Automated Quality Gates, AST Verification & Knowledge Base Synchronization (ISTQB Compliant)

> **SESSION C continues here** — this phase is coupled with Phase 4.

**Target Files:**
- `@[backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py]` (NEW)
- `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_prompt_factory.py]`
- `@[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]`
- `@[backend_v2/tests/unit/models/prompts/test_matrix_evaluation.py]`
- `@[ki_llm_extraction_architecture.md]`
- `@[.agents/rules/05_llm_architecture.md]`

**Tasks:**
1. Build AST Guardrail Tests in `test_ast_prompt_xml_sovereignty.py` adhering strictly to `ki_ast_guardrail_testing.md`:
   - Use recursive Python `ast` module parsing (no `str.find` for AST checks).
   - Negative Test 1: Verify AST scanner flags missing `extra="forbid"` on `PromptBlock` model definitions.
   - Negative Test 2: Verify AST scanner flags any `hasattr` or `getattr` calls in `prompt_factory.py`.
   - Negative Test 3: Verify AST scanner flags hardcoded slug comparisons in `prompt_factory.py`.
   - Negative Test 4: Verify that prompt compilation produces valid XML structure with proper Layer 1-4 ordering (`<global_system_mandates>`, `<ROLE_DIRECTIVE>`, `<EXTRACTION_PROTOCOL>`, `<CRITERIA_GUIDELINES>`).
   - Negative Test 5: Feed unescaped raw user payloads with `<, >, &` characters to verify CDATA and XML escaping integrity without syntax breakage.
   - Negative Test 6: Verify that `MatrixSensorPromptBuilder.build_caching_prefix` contains `<global_system_mandates>` tag (regression gate).
   - Negative Test 7: Verify that `PromptBlock` with BOTH `ai_description` AND structured fields (`objective`) does NOT auto-compile or mutate `ai_description` — the two coexist independently.
2. Expand unit tests in `test_prompt_factory.py`, `test_matrix_sensor_prompt_builder.py`, and `test_matrix_evaluation.py`:
   - Test structured prompt compilation from structured `PromptBlock` fields (`objective`, `evaluation_rules`, `banned_concepts`, `role_enforcement`) — XML wrapping MUST happen in the Compiler, not in the Domain Model.
   - Test backward compatibility when legacy raw `ai_description` is provided without structured fields.
   - Test that `GLOBAL_MANDATES_XML` is present in `base_system_prompt` and absent from `user_payload`.
   - Test that `MatrixSensorPromptBuilder.build_caching_prefix` includes `GLOBAL_MANDATES_XML` in the system message.
   - Update existing test assertions in `test_prompt_factory.py` (L144: change `assert ... in payload.user_payload` to `assert ... in payload.base_system_prompt`) to match Layer 1 static prefix placement.
   - Negative Test: `PromptFactory.build` with `llm_context_data` missing expected keys Fail-Fast crashes (no silent `.get()` defaults).
   - Negative Test: `LocalizationCompiler.compile_static_instructions` with invalid `target_locale` raises `AppException` (no silent `"English"` fallback).
3. Run backend audit: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/ --test`.
4. Knowledge Base & Rule Synchronization (Dual-Axis Documentation Paradigm):
   - Update `@[ki_llm_extraction_architecture.md]` with the Zero-XML UI paradigm and the 4-Layer Clean Stack Model specification (`zero_xml_ui_mandate` and `four_layer_clean_stack_assembly`).
   - Synchronize `@[.agents/rules/05_llm_architecture.md]` to enforce that XML tags are generated exclusively by the compiler layer (`PromptFactory`, `MatrixSensorPromptBuilder`, `LocalizationCompiler`) and are strictly forbidden from being manually constructed in UI inputs or stored in raw text fields.

---

## 5. Verification & Acceptance Criteria

1. **Zero Manual XML**: Creating a new matrix in Studio UI or via API with plain text fields produces a fully compliant, XML-structured system prompt.
2. **Context Cache Integrity**: Prefix prompt hashes remain 100% static across identical matrix evaluations.
3. **Step Simplicity**: Step configuration in Studio UI has fewer clutter blocks while maintaining 100% of evaluation rigor.
4. **Full Test Suite Pass**: All Ruff formatting, MyPy strict typing, Pytest suites, and Flutter analyzer passes with zero errors.

---

## 6. Execution Command
To begin implementation of **Session A (Phase 1 + Phase 2)** upon approval, start a NEW chat session and execute:
`/tier2-execute @[docs/IMPLEMENTATION_PLAN_Unified_Prompt_Orchestration.md]`

> [!IMPORTANT]
> After completing Session A, execute `/tier5-session-handover` before proceeding to Session B (Phase 3) and Session C (Phase 4+5).
