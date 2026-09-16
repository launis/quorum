# Task Checklist: Unified Cognitive Parity, Provider-Agnostic Tiers & E2E Pipeline Variance Optimizations

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
  <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
  <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
  <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
  <knowledge_item>@[ki_tda_best_of_three_flash.md]</knowledge_item>
  <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

- [x] **Phase 1: Pre-Implementation Cleanups & Technical Debt Eradication**
  - [x] 1.1 Create timestamped backup of `backend_v2/seed/seed_data.json` in `backend_v2/seed/backups/seed_data_backup_[TIMESTAMP].json`
  - [x] 1.2 Perform technical debt audit on touched atoms in `blk_f921c7c0989b47e8` (`tda_07ef835fd139e70fd9d9f2151dc9a5aa`, `tda_5198e13cde3447fe9d0737a80abe458c`) and `blk_109dab5b6b3f403a` (`tda_ab3ebf5a42f0d72eca9acceeb2e12ce1`, `tda_5fc55ef72665907c426e2598cddde565`), verifying zero ambiguity tokens (`e.g.`, `etc.`), zero screaming imperatives, description <= 180 chars, strict Pydantic V2 schemas, and zero legacy string slugs in foreign keys
  - [x] 1.3 Eliminate 1-hop caller debt: replace legacy string `model_strategy` references across `StepCreateDTO` and `StepUpdateDTO` (`@[backend_v2/models/dtos/studio.py#L200-L632]`), `create_draft_step` (`@[backend_v2/services/studio/workflow_service.py#L570-L590]`), `StrategyContext` (`@[backend_v2/services/orchestrator/strategies/base.py#L54-L66]`), and DAG construction (`@[backend_v2/services/orchestrator/dag_executor.py#L269-L281]`) with strongly-typed `CognitiveTier`
  - [x] 1.4 Flutter Studio model and design token cleanups: replace flat `Map<String, LlmModelConfig> models` in `@[client_app_v2/lib/features/studio/models/model_config.dart#L10-L51]` with typed `tierDefinitions: Map<String, Map<String, LlmModelConfig>>`; replace magic spacing double `const SizedBox(height: 24)` in `@[client_app_v2/lib/features/studio/views/step_builder_view.dart#L480]` with design token `AppSpacing.p24`, and update `labelText: l10n.studioModelStrategyLabel` to `l10n.studioCognitiveTierLabel`
  - [x] 1.5 Backend worker and client strategy cleanups: replace raw strategy strings (`"synthesis"`, `"strict"`) in `@[backend_v2/worker.py#L1009]`, `#L1253`, `#L1435` with typed `CognitiveTier` references; eliminate ad-hoc `strategy_aliases` dictionary in `@[backend_v2/settings.py]` and the `while isinstance(target_strategy, str):` loop in `@[backend_v2/llm/client.py#L125-L160]` in favor of direct O(1) tier lookup
  - [x] 1.6 Purge deprecated fallback models: delete legacy hardcoded fallback models (`gemini-2.5-flash`, `gemini-2.5-pro`, `claude-3-5-sonnet`) in `@[scripts/diff_executions.py#L1261-L1285]`
  - [x] 1.7 ISTQB negative partition assurance: add test partitions in `@[backend_v2/tests/unit/seed/test_matrix_anchoring_rules.py]` asserting rejection of all 4 anti-patterns, and in `@[backend_v2/tests/unit/llm/test_llm_client_tiers.py]` asserting fail-fast `ConfigurationError` on unconfigured providers or tiers

- [x] **Phase 2: Core Domain Schema & Model Registry Evolution (Cognitive Tiers & Provider Ontology)**
  - [x] 2.1 Define canonical `CognitiveTier(StrEnum)` (`FAST`, `BALANCED`, `DEEP`, `REASONING`) and `LLMProvider(StrEnum)` (`GOOGLE`, `OPENAI`, `ANTHROPIC`, `AZURE_OPENAI`, `LOCAL`) in `@[backend_v2/models/v2_core.py#L30-L50]`
  - [x] 2.2 Evolve `SystemConfigModelRegistry` in `@[backend_v2/models/v2_core.py#L428-L468]` to support `default_provider: LLMProvider` and `tier_definitions: dict[LLMProvider, dict[CognitiveTier, ModelProfile]]` with strict Pydantic V2 `@model_validator(mode="after")` enforcing full tier completeness across every registered provider
  - [x] 2.3 Update `ExecutionCreateDTO` in `@[backend_v2/models/dtos/trace.py#L40-L58]` and `ExecutionCreate` in `@[backend_v2/models/v2_core.py#L1541-L1578]` with optional `provider_override: LLMProvider | None = None`
  - [x] 2.4 Update `Step` (aliased as `V2Step`) in `@[backend_v2/models/v2_core.py#L520-L611]` to replace `model_strategy` with `cognitive_tier: CognitiveTier = CognitiveTier.FAST` and update `validate_step_consistency` (#L583-L610)
  - [x] 2.5 Update 1-Hop Studio DTOs and Orchestrator Services: `StepCreateDTO` and `StepUpdateDTO` in `@[backend_v2/models/dtos/studio.py#L200-L632]`, `create_draft_step` in `@[backend_v2/services/studio/workflow_service.py#L570-L590]`, `StrategyContext` in `@[backend_v2/services/orchestrator/strategies/base.py#L54-L66]`, and `@[backend_v2/services/orchestrator/dag_executor.py#L269-L281]`
  - [x] 2.6 Update Flutter Core Enums (`@[client_app_v2/lib/core/models/enums.dart#L1-L40]`) and `ModelConfig` (`@[client_app_v2/lib/features/studio/models/model_config.dart#L10-L51]`) with `CognitiveTier` and `tierDefinitions`

- [x] **Phase 3: Seed Vault Migration & Tier Structure Definition**
  - [x] 3.1 Restructure `system_config.models` in `@[backend_v2/seed/seed_data.json#L7-L91]` into normalized `tier_definitions` for Google and OpenAI providers (`FAST`, `BALANCED`, `DEEP`, `REASONING`)
  - [x] 3.2 Align all reasoning model temperatures to `1.0` and set OpenAI `DEEP` thinking budget to `4096` tokens (`reasoning_effort: "medium"`), establishing computational symmetry with Gemini `DEEP`
  - [x] 3.3 Migrate all `model_strategy` fields to `cognitive_tier` across all step blueprints in `@[backend_v2/seed/seed_data.json#L19500-L19890]`

- [x] **Phase 4: Step Blueprint Cognitive Upgrade & Workflow Calibration**
  - [x] 4.1 Upgrade Step 2 Archivist `sp_f22db9f1dde048b7` in `@[backend_v2/seed/seed_data.json#L19572-L19614]`: set `cognitive_tier = CognitiveTier.DEEP` (4,096 thinking tokens; reject `REASONING` 8k to prevent 737k token explosion and Arq worker timeouts)
  - [x] 4.2 Calibrate Workflow 3 `wf_03a1d71000000003` in `@[backend_v2/seed/seed_data.json#L18805-L19046]`: set `default_strictness_level = 70` (`StrictnessAnchor.BALANCED`, $e = 1.5071$)
  - [x] 4.3 Eliminate Phantom Penalty: add `"enforce_passivity_penalty"` to Step 4 Coach `sp_25664f44773a4354.post_hooks` (#L19694-L19697) AND set `wf_03a1d71000000003.passivity_penalty = 0.05` (#L19045)

- [x] **Phase 5: Ontological Hardening of Bloom's Taxonomy**
  - [x] 5.1 Update Bloom Level 6 `tda_07ef835fd139e70fd9d9f2151dc9a5aa` in `@[backend_v2/seed/seed_data.json#L2998-L3038]` with thematic clustering anti-pattern, explicit criteria, and plasma-aerobraking tensor contrastive example
  - [x] 5.2 Update Bloom Level 5 `tda_5198e13cde3447fe9d0737a80abe458c` in `@[backend_v2/seed/seed_data.json#L2685-L2727]` with regulatory standard citation anti-pattern and ASME Section VIII hydrostatic pressure contrastive example

- [x] **Phase 6: Ontological Hardening of Kahneman's Dual Process Theory**
  - [x] 6.1 Update Kahneman Level 2 `tda_5fc55ef72665907c426e2598cddde565` in `@[backend_v2/seed/seed_data.json#L3475-L3515]` with post-hoc file reflection anti-pattern and laminar flow / sensor logging contrastive example
  - [x] 6.2 Update Kahneman Level 1 `tda_ab3ebf5a42f0d72eca9acceeb2e12ce1` in `@[backend_v2/seed/seed_data.json#L3263-L3303]` with external source quote anti-pattern and electrical percolation contrastive example

- [x] **Phase 7: Backend Resolution Engine & Worker Decoupling**
  - [x] 7.1 Implement `LLMClient.from_tier(cls, tier, repository, provider)` in `@[backend_v2/llm/client.py#L85-L165]` and eradicate legacy string alias resolution loops and `strategy_aliases` duct-tape
  - [x] 7.2 Update `@[backend_v2/services/orchestrator/strategies/llm.py#L569-L581]` to resolve client via `step.cognitive_tier` and execution-level provider
  - [x] 7.3 Decouple `@[backend_v2/worker.py]` distillation, row explanation, and variance tasks from hardcoded `"strict"` and `"synthesis"` strings, migrating to `CognitiveTier.BALANCED`, `CognitiveTier.FAST`, and `CognitiveTier.DEEP` subordinated to `execution.provider` (#L1008-L1058, #L1252-L1255, #L1434-L1437)
  - [x] 7.4 Update internal backend utilities (`@[backend_v2/services/chat_parser.py#L149-L163]`, `@[backend_v2/hooks/interaction_hook.py#L92-L96]`) to request `CognitiveTier.FAST`

- [x] **Phase 8: Flutter Quorum Studio & Telemetry UI Alignment**
  - [x] 8.1 Update Freezed domain models in `client_app_v2`: update `NodeStrategyLlm`, `WorkflowStep` (`@[client_app_v2/lib/features/studio/models/workflow.dart#L78-L123]`), and `ExecutionStep` (`@[client_app_v2/lib/features/execution/models/execution_step.dart#L1-L38]`) with `@JsonKey(name: 'cognitive_tier') CognitiveTier cognitiveTier`
  - [x] 8.2 Add localized labels in `client_app_v2/lib/l10n/app_en.arb` and `app_fi.arb` for Cognitive Tiers (`studioTierFast`, `studioTierBalanced`, `studioTierDeep`, `studioTierReasoning`, `studioCognitiveTierLabel`) and dynamic resolution chips
  - [x] 8.3 Refactor `@[client_app_v2/lib/features/studio/views/step_builder_view.dart#L430-L480]` dropdown to present vendor-neutral Cognitive Tiers with read-only resolution chip showing active provider's underlying physical model; replace magic double `const SizedBox(height: 24)` with `AppSpacing.p24`
  - [x] 8.4 Run `build_runner` for Freezed generation in `client_app_v2`: `dart run build_runner build --delete-conflicting-outputs`

- [x] **Phase 9: Multi-Provider E2E Variance Test Runner & Forensic Diff Telemetry**
  - [x] 9.1 Refactor `@[scripts/run_e2e_variance_test.py#L1307-L1410]` to eliminate `STRATEGY_ALIASES` brute-force environment variable injection and add `--providers` CLI parameter supporting multi-provider sequential runs (e.g. `--providers google openai`)
  - [x] 9.2 Upgrade `@[scripts/run_e2e_variance_test.py#L1250-L1305]` startup and per-run telemetry printouts: always print actual provider (`Google Vertex AI`, `Google AI Studio`, `OpenAI`), allowed token ceilings (`max_tokens`, `thinking_budget_tokens`, `reasoning_effort`), rate limits (`tpm_limit`, `rpm_limit`), and human-readable workflow/step names, strictly eliminating raw opaque IDs (`wf_...`, `sp_...`, `sys_...`) and abstract top-level strategy aliases (`evaluation_strategy`, `test_strategy`) in user-facing logging
  - [x] 9.3 Upgrade `@[scripts/diff_executions.py]` `PhysicalModelBindingDTO` (#L233-L244) and Markdown report generator (#L2170-L2240): add `provider`, `tpm_limit`, `rpm_limit`, and `reasoning_effort` fields; eliminate hardcoded legacy fallback models (`gemini-2.5-flash`); render physical model binding table and workflow provenance using localized human-readable names and full token capacity limits, strictly banning raw database IDs and high-level wrapper names in report headlines
  - [x] 9.4 Verify that in `diff_executions.py` reporting, section headers and provenance blocks strictly display localized human names for all workflows and matrices, while preserving exact Stripe IDs in sub-bullets and detail views for auditability

- [x] **Phase 10: Regression Unit Test Expansion & Tier Verification**
  - [x] 10.1 Expand `@[backend_v2/tests/unit/seed/test_matrix_anchoring_rules.py#L220-L260]` to assert anti-patterns and contrastive pairs for all 4 hardened atoms alongside the 7 existing stabilized atoms
  - [x] 10.2 Verify 100% Best-of-3 entropy invariant passes via `test_all_matrix_atoms_have_high_entropy_activated()` (Measure 2 rejection enforcement)
  - [x] 10.3 Add unit tests in `@[backend_v2/tests/unit/llm/test_llm_client_tiers.py]` verifying `LLMClient.from_tier()` O(1) resolution across all providers and fail-fast behavior on unconfigured tiers
  - [x] 10.4 Synchronize regression test fixtures: `@[backend_v2/tests/unit/test_model_registry.py#L80-L115]`, `@[backend_v2/tests/unit/test_seed_architectural_guardrails.py#L122-L165]` & `#L390-L430`, `@[backend_v2/tests/unit/test_v2_core_strictness.py#L60-L115]`, and `@[backend_v2/tests/unit/test_run_e2e_variance_test.py#L445-L465]`
  - [x] 10.5 Run and verify Flutter unit tests (`workflow_test.dart`, `step_builder_view_test.dart`)

- [x] **Phase 11: Pre-Flight Validation, Linter & Quality Gates**
  - [x] 11.1 Run in-memory pre-flight validation (`uv run python backend_v2/seed/run_seed.py local --dry-run` and `uv run python scripts/audit_database_atoms.py --strict`)
  - [x] 11.2 Re-seed local development database (`uv run python backend_v2/seed/run_seed.py local`)
  - [x] 11.3 Run full backend quality gate (`uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --test`)
  - [x] 11.4 Run full flutter quality gate (`uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_test.dart`)

- [x] **Phase 12: Knowledge Item (KI) & Architectural Documentation Synchronization**
  - [x] 12.1 Update `ki_prompt_orchestration_and_matrix_evaluation.md` with Bloom Levels 5-6 and Kahneman Levels 1-2 anti-patterns and provenance boundaries
  - [x] 12.2 Update `ki_unified_matrix_scoring_strictness.md` with default strictness 70% and synchronous passivity penalty post-hook wiring
  - [x] 12.3 Update `ki_tda_best_of_three_flash.md` with 100% Best-of-3 entropy coverage confirmation and empirical rejection of selective single-pass entropy
  - [x] 12.4 Update `ki_provider_agnostic_caching.md` with the Provider-Agnostic Cognitive Tiers architecture and multi-provider prefix caching topologies
  - [x] 12.5 Update `docs/architecture/08_matrix_explanations.md` with exact BARS progression definitions, anti-patterns, and context targets for Bloom and Kahneman (Verified Complete)
  - [x] 12.6 Route `/tier7-describe-architecture` for `docs/architecture/01_system_context_and_invariants.md` (Document Cognitive Tiers, strictness 70%, and passivity penalty 0.05)
  - [x] 12.7 Route `/tier7-describe-architecture` for `docs/architecture/03_cognitive_orchestration_engine.md` (Document `LLMClient.from_tier()`, Step 2 `DEEP`, and multi-provider pipeline execution)

---

# Session Handover Context
## Achieved
- 100% completion of Phases 1–12 across Backend Python (`backend_v2`), Flutter Client (`client_app_v2`), Seed Vault (`seed_data.json`), Knowledge Items (`knowledge/`), and Test Suites (`scripts/`, `tests/`).
- Established Provider-Agnostic Cognitive Tiers (`FAST`, `BALANCED`, `DEEP`, `REASONING`) across domain schemas, Pydantic DTOs, Freezed models, and UI selectors with O(1) resolution via `LLMClient.from_tier()`.
- Symmetrized reasoning computational budgets between OpenAI and Google (OpenAI `DEEP` allocated 4,096 thinking tokens mapping to `reasoning_effort: "medium"`).
- Step 2 Archivist (`sp_f22db9f1dde048b7`) set to `CognitiveTier.DEEP` (4k tokens; reject `REASONING` 8k to prevent 737k token explosion and worker timeouts).
- Calibrated Workflow 3 (`wf_03a1d71000000003`) to default strictness 70% ($e = 1.5071$) with synchronous passivity penalty 0.05 wired to Step 4 Coach post-hook `"enforce_passivity_penalty"`.
- Ontologically hardened Bloom Levels 5–6 and Kahneman Levels 1–2 with explicit anti-patterns and contrastive pairs.
- Upgraded telemetry reporting in `run_e2e_variance_test.py` and `diff_executions.py` to display real providers, token limits, and localized human names, strictly banning raw IDs and wrapper aliases in report headlines.
- Re-seeded database into `data/db_v2.json` with 0 atom audit errors.
- Verified 100% pass across all 143 unit tests and 21 Flutter tests.
- Synchronized all 4 Knowledge Items (`ki_prompt_orchestration_and_matrix_evaluation.md`, `ki_unified_matrix_scoring_strictness.md`, `ki_tda_best_of_three_flash.md`, `ki_provider_agnostic_caching.md`) and their `metadata.json` files.

## Learned
- In `Step`, field validation on `cognitive_tier` runs before model validation; passing `cognitive_tier=None` raises field `ValidationError` rather than model validator `ValueError`.
- `backend_audit_loop.py` infers the target module under test from the target file path. For testing seed/json rules, running pytest directly against the target test suite verifies coverage correctly.
- Updating Knowledge Items first allows architectural pillar documents (`docs/architecture/01_` through `06_`) to be synchronized cleanly in a fresh session via `/tier7-describe-architecture`, complying with the Dual-Axis Documentation Paradigm.

## Remaining
- Perform atomic `git commit` to save the full implementation state.
- Route post-implementation verification through `/tier8-audit-plan` or run `/tier7-describe-architecture` for pillars 01 and 03.

## Resume Command
```bash
/tier8-audit-plan @[docs\implementationplans\IMPLEMENTATION_PLAN_Unified_Cognitive_Parity_Variance_Optimizations.md]
```
