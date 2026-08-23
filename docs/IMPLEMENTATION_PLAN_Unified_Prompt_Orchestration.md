# Architectural Implementation Plan: Zero-XML UI & Automated Prompt Assembly Pipeline

## 1. Executive Summary & First Principles

### 1.1 Context & Motivation
In Quorum, cognitive evaluation relies on foundational LLMs (Gemini, Claude) instructed via Server-Driven Prompts. Currently, the Studio UI exposes raw text fields (`ai_description`) across dozens of granular prompt blocks (`system_rule`, `matrix`, `role`, `protocol`, `execution_persona`), requiring humans to understand and manually construct XML tags (`<banned_concepts>`, `<role_enforcement>`, `<theory_context>`) and `ALL-CAPS` directive anchors.

Furthermore, Studio Steps currently associate up to 27 redundant, fine-grained `system_rule` blocks (e.g. `block_mandate1..6`, `block_oprule1..4`, `block_rule1..6`), creating UI clutter, cognitive overload, and fragile prompt configurations.

### 1.2 The Architectural Goal: Zero-XML UI & Automated Prompt Assembly
1. **Zero-XML UI**: The human user in Studio UI or Matrix Editor writes **pure, natural text and structured lists** (e.g. `objective`, list of `banned_concepts`, `evaluation_rules`, `theory_grounding` citations). The user NEVER writes raw XML tags.
2. **Deterministic Prompt Compilation (Clean Stack Model)**: The backend compiler (`PromptFactory`, `LocalizationCompiler`, `MatrixSensorPromptBuilder`) deterministically assembles these structured models into a 100% Context Caching-compliant, 4-tier XML hierarchy.
3. **Global Mandates SSOT**: Universal system rules (Null Hypothesis, Anti-Score, Hallucination Ban, Language Mandates) are injected automatically from `global_mandates.py` without requiring manual block selection in the Studio UI.
4. **Preserve Dynamic Matrix Creation**: Creating new matrices remains 100% dynamic, plug-and-play, and decoupled from underlying system rules.

---

## 2. The Unified 4-Layer Prompt Architecture (Clean Stack Model)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: GLOBAL SYSTEM INVARIANTS (Automated by Backend)                    │
│   Source: backend_v2/models/prompts/global_mandates.py                      │
│   Injected into: static prefix (100% Gemini Context Cacheable)              │
│   Tags: <language_mandate>, <null_hypothesis_mandate>, <anti_score_mandate>,│
│         <epistemic_glossary>, <verbatim_extraction_mandate>, etc.           │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 2: STEP GOVERNANCE & PROTOCOLS (Configured in Step Blueprint)         │
│   - <EXECUTION_PERSONA>: Miten LLM parseroi (Deterministic Parser / XAI)    │
│   - <ROLE_DIRECTIVE>: Toimintamoodi (Prosecutor / Analyst / Coach)          │
│   - <EXTRACTION_PROTOCOL>: Evidenssin leikkaussäännöt (Zero-Trust Quotes)   │
│   - <TASK_DIRECTIVES>: Step-specific heuristics (e.g. Passivity, PII)       │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 3: DOMAIN CRITERIA MATRIX (Configured in Matrix PromptBlock)          │
│   - OBJECTIVE: Pure rubric objective string                                 │
│   - <evaluation_rules>: Specific evaluation boundaries                      │
│   - <banned_concepts>: Explicit negative heuristics                         │
│   - <theory_context>: Verbatim academic citation (from TheoryGrounding DTO) │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 4: DYNAMIC CLAIMS & EVIDENCE PAYLOAD (Per-Execution Dynamic Tail)     │
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
1. **`backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L140-L176`**:
   - Eliminate anti-pattern `find_value_by_key` that uses `hasattr(obj, "__dict__")`, `hasattr(obj, key)`, and `getattr(obj, key)` recursive loops. Replace with strictly typed dictionary lookup or Pydantic DTO extraction (`ContextBuilder`).
   - Eliminate hardcoded `slug` checks (`if getattr(b, "slug", None) in ("matrix_causal_analyst", "block_taskperformativity"):`) in compliance with `slug_data_relation_ban` and `zero_db_hardcoding_mandate`.
2. **Cross-Domain DTO Parity (`client_app_v2/lib/features/studio/models/prompt_block.dart#L197-L230`)**:
   - Update Dart `PromptBlock` Freezed class to mirror backend fields synchronously, avoiding `disallowUnrecognizedKeys: true` client crashes when fetching blocks with new fields:
     - `String? objective`
     - `@JsonKey(name: 'evaluation_rules') @Default([]) List<String> evaluationRules`
     - `@JsonKey(name: 'banned_concepts') @Default([]) List<String> bannedConcepts`
     - `@JsonKey(name: 'role_enforcement') String? roleEnforcement`

**Target Files:**
- `@[backend_v2/models/v2_core.py#L405-L545]`
- `@[client_app_v2/lib/features/studio/models/prompt_block.dart#L197-L230]`
- `@[backend_v2/models/prompts/matrix_evaluation.py#L1-L20]`
- `@[backend_v2/models/prompts/global_mandates.py#L1-L161]`

**Tasks:**
1. Enhance `PromptBlock` in `v2_core.py`:
   - Keep `ai_description: str | None = Field(default=None)` as backward-compatible computed/raw property.
   - Add structured optional fields to `PromptBlock`:
     - `objective: str | None = Field(default=None, description="Pure rubric objective.")`
     - `evaluation_rules: list[str] = Field(default_factory=list, description="Specific evaluation boundaries.")`
     - `banned_concepts: list[str] = Field(default_factory=list, description="Explicit negative heuristics.")`
     - `role_enforcement: str | None = Field(default=None, description="Role directive enforcement.")`
   - Add `@model_validator(mode="after")` to compile structured fields into clean, XML-wrapped `ai_description` if structured fields are provided while `ai_description` is None.
2. Verify `ConfigDict(strict=True, extra="forbid")` compliance across all updated models.
3. Run `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/prompt_block.dart --build`.

---

### Phase 2: Compiler Layer Automated Assembly & Context Cache Optimization

**Target Files:**
- `@[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L170-L265]`
- `@[backend_v2/services/orchestrator/localization_compiler.py#L79-L160]`
- `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L37-L92]`
- `@[backend_v2/services/orchestrator/prompt_compiler_adapter.py#L1-L140]`

**Tasks:**
1. Update `PromptFactory.build`:
   - Move `GLOBAL_MANDATES_XML` into Layer 1 of `base_system_prompt` (static prefix), removing it from dynamic `user_payload` / `exec_params` to maximize Context Caching hit rate.
   - Format `execution_persona_block` cleanly into `<EXECUTION_PERSONA>...</EXECUTION_PERSONA>`.
   - Format `role_block` into `<ROLE_DIRECTIVE>...</ROLE_DIRECTIVE>`.
   - Format `protocol_block` into `<EXTRACTION_PROTOCOL>...</EXTRACTION_PROTOCOL>`.
   - Wrap task heuristics and rules into `<TASK_DIRECTIVES>...</TASK_DIRECTIVES>`.
2. Update `MatrixSensorPromptBuilder.build_caching_prefix`:
   - Include `GLOBAL_MANDATES_XML` in the static caching prefix for matrix sensor evaluation.
   - Compile matrix objective, evaluation rules, and banned concepts with strict XML wrappers (`<objective>`, `<evaluation_rules>`, `<banned_concepts>`).
   - Wrap `theory_grounding.citation_reference` into `<theory_context>`.
3. In `LocalizationCompiler.compile_static_instructions`:
   - Sanitize legacy HTML entities (`&lt;` -> `<` and `&gt;` -> `>`) so XML compiles cleanly.

---

### Phase 3: Seed Data & Step Simplification (Database Optimization)

**Target Files:**
- `@[backend_v2/seed/seed_data.json]`
- `@[data/db_v2.json]`

**Tasks:**
1. Execute Seed Vault Protocol (Step 2 Backup to `backend_v2/seed/backups/seed_data_<timestamp>.json`).
2. Fix corrupted HTML entities in `seed_data.json`:
   - Change `&lt;mechanical_anchors&gt;` to `<mechanical_anchors>` in `blk_b4912f9ff3a24b31` (`block_taskperformativity`).
3. Streamline `criteria_block_ids` across all LLM steps in `seed_data.json`:
   - Remove redundant global mandate blocks (`block_headermandates`, `block_mandate5`, `block_rule1..6`, `block_headerrules`, `block_instructionnohallucination`, `block_instructionlanguage_dynamic`, `block_headerinstructions`) from individual step `criteria_block_ids`, as they are now 100% handled automatically by Layer 1 `global_mandates.py`.
   - Keep only step-specific task directives (e.g. `block_heuristic1..3`, `block_protocol1`) and the primary matrix block (`matrix_...`).
4. Re-seed local database: `uv run python backend_v2/seed/run_seed.py local`.

---

### Phase 4: Flutter Studio UI Alignment (Zero-XML User Experience)

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
   - `promptBlockObjectiveLabel`, `promptBlockRulesLabel`, `promptBlockBannedConceptsLabel`, `promptBlockCompiledPreviewTitle`.
4. Run `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`.

---

### Phase 5: Automated Quality Gates & AST Verification (ISTQB Compliant)

**Target Files:**
- `@[backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py]` (NEW)
- `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_prompt_factory.py]`
- `@[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]`

**Tasks:**
1. Build AST Guardrail Tests in `test_ast_prompt_xml_sovereignty.py`:
   - Verify that all prompt compilation paths produce valid XML structure with proper Layer 1-4 ordering.
   - Negative Test 1: Feed unescaped raw user payloads to verify CDATA / XML escaping.
   - Negative Test 2: Feed malformed / missing structured fields to verify Fail-Fast Pydantic validation.
   - Negative Test 3: AST verification that `PromptBlock` rejects extra keys with `extra="forbid"`.
2. Expand unit tests in `test_prompt_factory.py` and `test_matrix_sensor_prompt_builder.py`:
   - Test structured prompt compilation from structured `PromptBlock` fields.
   - Test backward compatibility when legacy raw `ai_description` is provided.
   - Test that `GLOBAL_MANDATES_XML` is present in `base_system_prompt` and absent from `user_payload`.
3. Run backend audit: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/ --test`.

---

## 5. Verification & Acceptance Criteria

1. **Zero Manual XML**: Creating a new matrix in Studio UI or via API with plain text fields produces a fully compliant, XML-structured system prompt.
2. **Context Cache Integrity**: Prefix prompt hashes remain 100% static across identical matrix evaluations.
3. **Step Simplicity**: Step configuration in Studio UI has fewer clutter blocks while maintaining 100% of evaluation rigor.
4. **Full Test Suite Pass**: All Ruff formatting, MyPy strict typing, Pytest suites, and Flutter analyzer passes with zero errors.

---

## 6. Execution Command
To begin implementation of Phase 1 upon approval, the command is:
`/tier2-execute @[docs/IMPLEMENTATION_PLAN_Unified_Prompt_Orchestration.md]`
