# Unified Implementation Plan: Inter-Model Epistemic Parity, Provider-Agnostic Cognitive Tiers & E2E Pipeline Variance Optimizations

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

## Objective
Harden the cognitive evaluation architecture across the Single Source of Truth (SSOT) data vault `@[backend_v2/seed/seed_data.json]`, the Python backend (`backend_v2`), the Flutter client (`client_app_v2`), and the E2E variance test harness (`scripts/run_e2e_variance_test.py` and `scripts/diff_executions.py`). 

This unified plan eliminates inter-model epistemic divergence between Google Gemini 3.8 Flash and OpenAI GPT-5.1 on Sitra foresight strategy (`data/test_inputs_sitra`) and hybrid work dialogue (`docs/jwdatat`) corpuses by:
1. **Disambiguating Upper Bloom & Kahneman Matrices:** Ontologically hardening Level 5 Criteria Anchoring (`tda_5198e13cde3447fe9d0737a80abe458c`), Level 6 Creation (`tda_07ef835fd139e70fd9d9f2151dc9a5aa`), Scale 1 Qualitative Association (`tda_ab3ebf5a42f0d72eca9acceeb2e12ce1`), and Scale 2 Deliberative Pause (`tda_5fc55ef72665907c426e2598cddde565`) with strict anti-patterns and contrastive pairs.
2. **Eliminating Infrastructure Coupling via Provider-Agnostic Cognitive Tiers:** Replacing legacy freeform string strategies (`"fast"`, `"deep"`, `"reasoning"`, `"synthesis"`, `"openai_strict"`) with a typed `CognitiveTier` ontology (`FAST`, `BALANCED`, `DEEP`, `REASONING`) mapped across multiple model providers (`GOOGLE`, `OPENAI`, `ANTHROPIC`).
3. **Establishing Computational Reasoning Symmetry:** Symmetrizing thinking token budgets across providers (e.g. OpenAI `DEEP` tier allocated 4,096 thinking tokens mapping to `reasoning_effort: "medium"` to symmetrically match Gemini `DEEP`).
4. **Calibrating Execution Strictness & Eliminating Phantom Penalties:** Upgrading Workflow 3 to `default_strictness_level: 70` ($e = 1.5071$) and synchronously wiring `"enforce_passivity_penalty"` into Step 4 Coach `post_hooks` alongside `passivity_penalty: 0.05`.
5. **Modernizing Quorum Studio UI:** Refactoring `step_builder_view.dart` to present vendor-neutral Cognitive Tiers with dynamic resolution badges, isolating workflow authors from infrastructure churn and replacing hardcoded sizing doubles with design tokens.
6. **Enforcing Pure Telemetry & Report Transparency:** Upgrading `run_e2e_variance_test.py` and `diff_executions.py` to always report real provider names (`Google Vertex AI`, `OpenAI`), allowed token ceilings (`max_tokens`, `thinking_budget_tokens`, `reasoning_effort`), rate limits (`tpm_limit`, `rpm_limit`), and human-readable names, strictly banning raw database IDs (`wf_...`, `sp_...`, `sys_...`) and abstract top-level strategy aliases (`evaluation_strategy`, `test_strategy`) in report headlines.
7. **Enabling Scientific Cross-Provider E2E Variance Testing:** Upgrading `run_e2e_variance_test.py` with `--providers` support, allowing sequential multi-provider runs that preserve step-level cognitive tier differentiation without brutal environment variable flattening.

---

## User Review Required

> [!IMPORTANT]
> **Measure 1 Token & Latency Budget Decision:**
> Step 2 (Archivist) evaluates 30 atoms in Bloom's Taxonomy. Under Best-of-3 ensemble evaluation (3 parallel calls per atom = 90 total calls), assigning strategy `REASONING` (8,192 thinking tokens) would generate up to $90 \times 8,192 \approx 737,280$ thinking tokens in Step 2 alone. This would multiply total workflow thinking tokens by nearly $6\times$, triggering 60 RPM Gemini rate limits and causing Arq worker job timeouts ($>15$ minutes).
> **Approved Solution:** Step 2 is upgraded to `CognitiveTier.DEEP` (`thinking_budget_tokens: 4096`), which provides structured analytical reasoning depth within safe latency ($<180$ seconds) and token limits.

> [!CAUTION]
> **Measure 2 Empirical Falsification & Architecture Ban:**
> The proposal to disable Best-of-3 on baseline levels (Bloom 1–2, Kahneman 1) was empirically falsified by `diff_report_2026-09-16_1314.md`. Level 1 atoms (`tda_216cc3fd...` and `tda_ab3ebf5a...`) had **0.0% consistency and maximum entropy (1.000)**. Baseline levels test dogmatic statements and intuitive heuristics, not mechanical regex. Furthermore, `backend_v2/tests/unit/seed/test_matrix_anchoring_rules.py:230` enforces 100% `high_entropy: true` across all 305 matrix atoms. **Best-of-3 remains 100% active on all atoms.**

> [!WARNING]
> **Measure 4 Phantom Penalty Trap:**
> Setting `passivity_penalty = 0.05` on `wf_03a1d71000000003` without adding `"enforce_passivity_penalty"` to Step 4 (`sp_25664f44773a4354`) `post_hooks` is a silent NO-OP because no step in Workflow 3 emits the `passivity_detected` flag (Step 7 Judge is not present in Workflow 3). Both must be updated synchronously.

> [!NOTE]
> **Telemetry & Reporting Mandate:**
> All reporting and CLI outputs across `run_e2e_variance_test.py` and `diff_executions.py` MUST report concrete physical reality: actual provider, allowed token capacity ceilings (`max_tokens`, `thinking_budget_tokens`, `reasoning_effort`, `tpm_limit`, `rpm_limit`), and human-readable localized names. Printing raw opaque IDs (`wf_...`, `sp_...`, `sys_...`) or abstract strategy wrapper aliases (`evaluation_strategy`, `test_strategy`) in report headlines is strictly banned.

---

## Scope & Target Boundaries

- **Python Backend Domain & Schemas (`backend_v2/`):**
  - `[MODIFY]` `@[backend_v2/models/v2_core.py#L428-L468]` (Define `CognitiveTier(StrEnum)` and `LLMProvider(StrEnum)`; refactor `SystemConfigModelRegistry` to use `default_provider: LLMProvider` and `tier_definitions: dict[LLMProvider, dict[CognitiveTier, ModelProfile]]`)
  - `[MODIFY]` `@[backend_v2/models/v2_core.py#L520-L611]` (In `Step` class aliased as `V2Step`, replace `model_strategy` with `cognitive_tier: CognitiveTier = CognitiveTier.FAST`; update `@model_validator` `validate_step_consistency` at `#L583-L610`)
  - `[MODIFY]` `@[backend_v2/models/v2_core.py#L1541-L1578]` & `@[backend_v2/models/dtos/trace.py#L40-L58]` (Add optional `provider_override: LLMProvider | None = None` to `ExecutionCreateDTO` and `ExecutionCreate` domain ingress payload)
  - `[MODIFY]` `@[backend_v2/models/dtos/studio.py#L200-L230]` & `@[backend_v2/models/dtos/studio.py#L612-L632]` (1-Hop Studio Caller: update `StepCreateDTO` and `StepUpdateDTO` replacing `model_strategy` with `cognitive_tier: CognitiveTier`)
  - `[MODIFY]` `@[backend_v2/services/studio/workflow_service.py#L570-L590]` (1-Hop Service Caller: update `create_draft_step` to set `cognitive_tier=CognitiveTier.FAST`)
  - `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/base.py#L54-L66]` (1-Hop Strategy Caller: update `StrategyContext` replacing `model_strategy: str | None` with `cognitive_tier: CognitiveTier`)
  - `[MODIFY]` `@[backend_v2/services/orchestrator/dag_executor.py#L269-L281]` (1-Hop DAG Caller: pass `cognitive_tier=step_def.cognitive_tier` when instantiating `StrategyContext`)
  - `[MODIFY]` `@[backend_v2/llm/client.py#L85-L165]` (Implement `LLMClient.from_tier()`; eliminate `strategy_aliases` duct-tape and string alias resolution loop)
  - `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/llm.py#L569-L581]` (Resolve client via `step.cognitive_tier` and execution-level provider)
  - `[MODIFY]` `@[backend_v2/worker.py#L1008-L1058]`, `@[backend_v2/worker.py#L1252-L1255]`, `@[backend_v2/worker.py#L1434-L1437]` (Decouple hardcoded strings `"synthesis"`, `"strict"`, `"fast"` in distillation, row explanation, and variance tasks; migrate to `CognitiveTier.BALANCED`, `FAST`, `DEEP` subordinated to `execution.provider`)
  - `[MODIFY]` `@[backend_v2/services/chat_parser.py#L149-L163]` & `@[backend_v2/hooks/interaction_hook.py#L92-L96]` (Migrate internal utility calls to `CognitiveTier.FAST`)
- **Target Data Vault (`@[backend_v2/seed/seed_data.json]`):**
  - `[MODIFY]` `@[backend_v2/seed/seed_data.json#L7-L91]` (Restructure `system_config.models` into normalized `tier_definitions` for Google and OpenAI; calibrate reasoning temperatures to `1.0`; calibrate OpenAI `DEEP` thinking budget to 4096 tokens)
  - `[MODIFY]` `@[backend_v2/seed/seed_data.json#L2685-L2727]` (Bloom Level 5: `tda_5198e13cde3447fe9d0737a80abe458c` complete `tda_assertions` block)
  - `[MODIFY]` `@[backend_v2/seed/seed_data.json#L2998-L3038]` (Bloom Level 6: `tda_07ef835fd139e70fd9d9f2151dc9a5aa` complete `tda_assertions` block)
  - `[MODIFY]` `@[backend_v2/seed/seed_data.json#L3263-L3303]` (Kahneman Level 1: `tda_ab3ebf5a42f0d72eca9acceeb2e12ce1` complete `tda_assertions` block)
  - `[MODIFY]` `@[backend_v2/seed/seed_data.json#L3475-L3515]` (Kahneman Level 2: `tda_5fc55ef72665907c426e2598cddde565` complete `tda_assertions` block)
  - `[MODIFY]` `@[backend_v2/seed/seed_data.json#L18805-L19046]` (Calibrate `wf_03a1d71000000003.default_strictness_level = 70` and `passivity_penalty = 0.05`)
  - `[MODIFY]` `@[backend_v2/seed/seed_data.json#L19572-L19614]` (Step 2 `sp_f22db9f1dde048b7`: upgrade to `deep`)
  - `[MODIFY]` `@[backend_v2/seed/seed_data.json#L19660-L19708]` (Step 4 Coach `sp_25664f44773a4354`: add `"enforce_passivity_penalty"` to `post_hooks`)
  - `[MODIFY]` `@[backend_v2/seed/seed_data.json#L19500-L19890]` (Migrate all `model_strategy` fields to `cognitive_tier`)
- **Flutter Client Domain & Quorum Studio (`client_app_v2/`):**
  - `[MODIFY]` `@[client_app_v2/lib/core/models/enums.dart#L1-L40]` (Define `enum CognitiveTier { @JsonValue('fast') fast, @JsonValue('balanced') balanced, @JsonValue('deep') deep, @JsonValue('reasoning') reasoning }` and `enum LLMProvider`)
  - `[MODIFY]` `@[client_app_v2/lib/features/studio/models/model_config.dart#L10-L51]` (Update `ModelConfig` and `LlmModelConfig` to support `defaultProvider` and `tierDefinitions: Map<String, Map<String, LlmModelConfig>>`)
  - `[MODIFY]` `@[client_app_v2/lib/features/studio/models/workflow.dart#L78-L123]` (Update `NodeStrategyLlm` and `NodeStrategyLogic` Freezed models with `CognitiveTier cognitiveTier`)
  - `[MODIFY]` `@[client_app_v2/lib/features/execution/models/execution_step.dart#L1-L38]` (Update `ExecutionStep` Freezed model with `CognitiveTier? cognitiveTier`)
  - `[MODIFY]` `@[client_app_v2/lib/features/studio/views/step_builder_view.dart#L430-L480]` (Refactor dropdown to present vendor-neutral Cognitive Tiers with dynamic resolution chip; replace hardcoded `SizedBox(height: 24)` with `AppSpacing.p24`)
  - `[MODIFY]` `@[client_app_v2/lib/l10n/app_en.arb]` & `@[client_app_v2/lib/l10n/app_fi.arb]` (Add localized strings for Cognitive Tiers and resolution status chips)
- **E2E & Variance Runner Harness (`scripts/`):**
  - `[MODIFY]` `@[scripts/run_e2e_variance_test.py#L1250-L1305]` & `@[scripts/run_e2e_variance_test.py#L1307-L1410]` (Eliminate `STRATEGY_ALIASES` brute-force env injection; add `--providers` multi-provider runner; upgrade telemetry logging to always output real provider, token limits, and human-readable names without raw IDs)
  - `[MODIFY]` `@[scripts/diff_executions.py#L233-L244]`, `@[scripts/diff_executions.py#L1230-L1286]` & `@[scripts/diff_executions.py#L2170-L2240]` (Upgrade `PhysicalModelBindingDTO` with `provider`, `tpm_limit`, `rpm_limit`, `reasoning_effort`; eliminate legacy hardcoded fallback models; update Markdown report generator to format physical model bindings and workflow provenance with localized names and full token capacity limits, strictly banning raw database IDs and high-level wrapper names in report headlines)
- **Target Unit & Regression Tests:**
  - `[MODIFY]` `@[backend_v2/tests/unit/seed/test_matrix_anchoring_rules.py#L220-L260]` (Assert anti-patterns and contrastive pairs for all 4 hardened atoms; verify 100% `high_entropy: true`)
  - `[NEW]` `@[backend_v2/tests/unit/llm/test_llm_client_tiers.py]` (Verify `LLMClient.from_tier()` O(1) resolution across providers and fail-fast behavior)
  - `[MODIFY]` `@[backend_v2/tests/unit/test_model_registry.py#L80-L115]` (Update registry instantiation to use `tier_definitions` and verify validation)
  - `[MODIFY]` `@[backend_v2/tests/unit/test_seed_architectural_guardrails.py#L122-L165]` & `@[backend_v2/tests/unit/test_seed_architectural_guardrails.py#L390-L430]` (Assert `tier_definitions` and `cognitive_tier`)
  - `[MODIFY]` `@[backend_v2/tests/unit/test_v2_core_strictness.py#L60-L115]` (Update `Step` instantiation to use `cognitive_tier=CognitiveTier.FAST`)
  - `[MODIFY]` `@[backend_v2/tests/unit/test_run_e2e_variance_test.py#L445-L465]` (Update assertion from `model_strategy == "fast"` to `cognitive_tier == "deep"`)
  - `[MODIFY]` `@[client_app_v2/test/features/studio/models/workflow_test.dart]` & `@[client_app_v2/test/features/studio/views/step_builder_view_test.dart]` (Verify Freezed models and UI dropdown)
- **Target Database Sync:**
  - `[MODIFY]` `@[data/db_v2.json]` (Persisted exclusively via `run_seed.py local` after in-memory pre-flight verification)
- **Target Architecture Documentation & Knowledge Items:**
  - `[VERIFY]` `@[docs/architecture/08_matrix_explanations.md]` (BARS progression verified present)
  - `[MODIFY]` `@[docs/architecture/01_system_context_and_invariants.md]` (Synchronized via `/tier7-describe-architecture`)
  - `[MODIFY]` `@[docs/architecture/03_cognitive_orchestration_engine.md]` (Synchronized via `/tier7-describe-architecture`)
  - `[MODIFY]` `@[ki_prompt_orchestration_and_matrix_evaluation.md]`
  - `[MODIFY]` `@[ki_unified_matrix_scoring_strictness.md]`
  - `[MODIFY]` `@[ki_tda_best_of_three_flash.md]`
  - `[MODIFY]` `@[ki_provider_agnostic_caching.md]`

---

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Cognitive Tier Domain SSOT**<br>`v2_core.py#L428-L468`<br>`seed_data.json#L7-L91` | Freeform string `model_strategy` (`"fast"`, `"openai_strict"`). Flat `dict[str, ModelProfile]` mixing provider names with roles. | `CognitiveTier` and `LLMProvider` as strict `StrEnum`s. Registry structured as `dict[LLMProvider, dict[CognitiveTier, ModelProfile]]`. | Ban speculative dynamic tier creation. Lock strictly to 4 canonical tiers (`FAST`, `BALANCED`, `DEEP`, `REASONING`). | `audit_database_atoms.py` and `run_seed.py --dry-run` assert 100% tier completeness across all providers. |
| **Step Domain Model & 1-Hop Studio DTOs**<br>`v2_core.py#L520-L611`<br>`dtos/studio.py#L200-L632` | Class misnaming (`WorkflowStep` vs SSOT `Step`), string duck typing in `validate_step_consistency`, legacy string `model_strategy` in studio DTOs. | `Step.cognitive_tier: CognitiveTier = CognitiveTier.FAST`. Studio `StepCreateDTO` and `StepUpdateDTO` typed with `cognitive_tier: CognitiveTier`. | Pruned retaining dual fields (`model_strategy` alongside `cognitive_tier`). Single strict SSOT contract. | `backend_v2/tests/unit/test_v2_core_strictness.py` and `backend_audit_loop.py` pass 100%. |
| **Client Resolution Engine**<br>`client.py#L85-L165`<br>`strategies/llm.py#L569-L581` | Duck-typed `while isinstance(target_strategy, str)` string alias resolution chains and `get_settings().strategy_aliases`. | Direct O(1) resolution via `LLMClient.from_tier(tier, provider=active_provider)`. Raise typed `ConfigurationError` on unconfigured tiers. | Do not build a runtime model proxy or load balancer. Execution strictly binds to one deterministic provider per run. | Unit test `test_llm_client_from_tier_resolves_all_providers()` asserting correct profile instantiation. |
| **Execution Ingress Contract**<br>`dtos/trace.py#L40-L58`<br>`v2_core.py#L1541-L1578` | Hallucinated DTO path `models/dtos/execution.py`. Passing provider overrides via unstructured environment variables or ad-hoc kwargs. | Add typed `provider_override: LLMProvider | None = None` to `ExecutionCreateDTO` and `ExecutionCreate` domain model. | Pruned creating separate ingress endpoints per provider. Single unified execution pipeline. | MyPy strict validation passes; `run_e2e_variance_test.py` serializes valid Pydantic DTO. |
| **1-Hop Orchestrator & Studio Services**<br>`strategies/base.py#L54-L66`<br>`dag_executor.py#L269-L281`<br>`workflow_service.py#L570-L590` | String `model_strategy: str | None = None` in `StrategyContext` and `"fast"` string literal in `create_draft_step`. | `StrategyContext.cognitive_tier: CognitiveTier`. DAG executor passes `step_def.cognitive_tier`. Studio sets `CognitiveTier.FAST`. | Pruned optional strategy fallbacks. Every step context guarantees non-null `cognitive_tier`. | `uv run pytest backend_v2/tests/unit/services/orchestrator/` passes 100%. |
| **Flutter Studio & Model Registry SSOT**<br>`model_config.dart#L10-L51`<br>`enums.dart#L1-L40`<br>`step_builder_view.dart#L430-L480` | Flat `Map<String, LlmModelConfig> models` in Flutter desynchronized from backend `tier_definitions`. Hardcoded `SizedBox(height: 24)` spacing double. | `enums.dart` defines `CognitiveTier` and `LLMProvider`. `ModelConfig` defines `defaultProvider` and `tierDefinitions`. UI uses `AppSpacing.p24`. | Pruned creating complex Dart provider adapters. Models reflect backend Pydantic schema 1:1. | `flutter test test/features/studio/models/workflow_test.dart` passes. |
| **Telemetry & Reporting Transparency**<br>`run_e2e_variance_test.py#L1250-L1305`<br>`diff_executions.py#L233-L244`<br>`diff_executions.py#L1230-L1286`<br>`diff_executions.py#L2170-L2240` | Printing raw opaque IDs (`wf_...`, `sp_...`, `sys_...`) in report headers, generic strategy wrappers (`evaluation_strategy`), or legacy fallback models (`gemini-2.5-flash`). | Always report real provider (`Google Vertex AI`, `Google AI Studio`, `OpenAI`), allowed token ceilings (`max_tokens`, `thinking_budget_tokens`, `reasoning_effort`), rate limits (`tpm_limit`, `rpm_limit`), and human-readable localized names. In `diff_executions.py`, render `#L2170-L2240` section with localized workflow names, full token capacity limits, and physical model binding table, strictly banning raw database IDs and high-level wrapper names in report headlines. | Pruned displaying redundant internal database hash keys; present pure human/forensic telemetry. | Automated test asserting `PhysicalModelBindingDTO` and diff report Markdown contain real provider, token limits, and zero raw IDs in headlines. |
| **Reasoning Depth Symmetry**<br>`seed_data.json#L7-L91`<br>`openai_adapter.py` | Banned leaving `thinking_budget_tokens: 2048` on OpenAI profiles while Gemini runs `deep` (4096), forcing OpenAI into `reasoning_effort: "low"`. | Mandatory: Calibrate OpenAI `DEEP` tier `thinking_budget_tokens: 4096` (`reasoning_effort: "medium"`), establishing computational symmetry. | Pruned custom CLI flags or hardcoded overrides; managed sovereignly by `openai_adapter.py`. | Proof: `scripts/run_e2e_variance_test.py` telemetry displays `Reasoning Effort: medium` for OpenAI `DEEP`. |
| **Step 2 Blueprint Strategy**<br>`seed_data.json#L19572-L19614` | Banned running high-level Bloom taxonomy (30 atoms) on zero-thinking `"fast"` strategy. | Set `cognitive_tier = CognitiveTier.DEEP` (`thinking_budget_tokens: 4096`). Provides structured reasoning without 8k token explosion. | Pruned proposing unregistered ad-hoc strategies or jumping to 8,192 token `REASONING`. | Proof: Telemetry in `diff_report` confirms Step 2 executes with `deep` tier and 4,096 thinking tokens. |
| **Matrix Atom Entropy Invariant**<br>(100% matrix atoms in seed vault) | Banned turning off Best-of-3 on baseline levels (Measure 2). Baseline atoms had 0.0% consistency in empirical runs. | Preserve `high_entropy: true` across 100% of matrix atoms per `ki_tda_best_of_three_flash.md`. | Pruned bifurcated DAG batch partitioning and single-pass exceptions. | Proof: `test_matrix_anchoring_rules.py::test_all_matrix_atoms_have_high_entropy_activated` passes 100%. |
| **Workflow Strictness**<br>`seed_data.json#L18805-L19046` | Banned treating 70% as an anchor validation gate (it only impacts math scoring and prompt strictness). | Set `default_strictness_level = 70` (`StrictnessAnchor.BALANCED`, $e = 1.5071$). Dampens superficial scores cleanly. | Pruned hardcoding non-standard strictness steps outside the continuous slider range. | Proof: `audit_database_atoms.py --strict` returns 0 issues; workflow tests assert strictness 70. |
| **Penalty Hook Decoupling**<br>`seed_data.json#L19660-L19708` | Banned "Phantom Penalties" where `passivity_penalty: 0.05` is set on Workflow but no step emits `passivity_detected`. | 1) Add `"enforce_passivity_penalty"` to Step 4 `sp_25664f44773a4354.post_hooks`.<br>2) Set `passivity_penalty = 0.05` on `wf_03a1d71000000003`. | Pruned setting `post_hoc_penalty` until a Falsifier step is physically present in the workflow. | Proof: `backend_v2/tests/unit/hooks/test_scoring.py` verifies passivity penalty execution. |
| **Worker Decoupling**<br>`worker.py#L1008-L1437` | Hardcoded `"strict"`, `"synthesis"`, `"fast"` strategy strings in synthesis and row explanation loops. | Background tasks explicitly request `CognitiveTier.BALANCED`, `FAST`, or `DEEP` subordinated to `execution.provider`. | Do not create separate worker classes per provider. Worker remains 100% provider-agnostic. | Integration test `test_synthesis_worker_executes_with_openai_provider()` verifying zero hardcoded Google references. |
| **Quorum Studio UI**<br>`step_builder_view.dart#L430-L480`<br>`workflow.dart#L78-L123` | Dropdown displaying raw model names (`DEEP (gemini-3.8-flash)`). Saving provider-specific strings in step JSON. | Dropdown displays localized `CognitiveTier` labels. Step payload stores strictly `cognitive_tier`. Read-only resolution chip. | Do not add in-situ provider switching inside the step builder. Step builder governs only cognitive intent. | `flutter test test/features/studio/views/step_builder_view_test.dart` verifying dropdown contains only 4 tiers. |
| **E2E Variance Test Runner**<br>`run_e2e_variance_test.py#L1307-L1410` | `STRATEGY_ALIASES` environment variable flattening all workflow steps into a single model profile. | Multi-provider execution loop via `--providers google openai`. Each run executes full workflow step tier dynamics. | Do not rewrite `diff_executions.py`. Telemetry models already record `physical_model` and `model_strategy`. | Automated test run comparing Google vs. OpenAI runs with identical tier sequences producing zero missing step telemetry. |
| **Test Fixture Parity**<br>`test_seed_architectural_guardrails.py`<br>`test_model_registry.py`<br>`test_run_e2e_variance_test.py` | Legacy unit tests expecting flat `models` dictionary or asserting `archivist["model_strategy"] == "fast"`. | Synchronously update test assertions to validate `tier_definitions`, `cognitive_tier`, and Step 2 `deep` tier. | Pruned creating duplicate test files; update existing regression tests directly. | Pytest suite passes 100% with zero regression failures. |
| **Bloom Level 6 (Creation)**<br>`seed_data.json#L2998-L3038` | Banned allowing thematic clustering, renaming, or summarization of external source documents to satisfy original creation. | Pure Pydantic V2 `TDAAssertion`. Explicit anti-pattern banning thematic clustering without causal mechanics. Plasma-aerobraking tensor contrastive exemplar. | Pruned redundant sub-claims or weighting flags. Hardening resides 100% in declarative TDA parameters. | Proof: `audit_database_atoms.py --strict` returns 0 issues; `test_matrix_anchoring_rules.py` asserts exact anti-pattern. |
| **Bloom Level 5 (Evaluation)**<br>`seed_data.json#L2685-L2727` | Banned passive regulatory standard citations (CSRD, ISO 9001) passing as criteria anchoring without active performance auditing. | Pure Pydantic V2 `TDAAssertion`. Explicit anti-pattern banning citation of standards merely as compliance context. ASME Section VIII hydrostatic pressure contrastive exemplar. | Pruned separate prompt block splits. Preserves single sovereign BARS scale hierarchy. | Proof: `audit_database_atoms.py --strict` returns 0 issues; `test_matrix_anchoring_rules.py` asserts exact anti-pattern. |
| **Kahneman Level 2 (Pause)**<br>`seed_data.json#L3475-L3515` | Banned allowing retrospective post-hoc notes about file errors or procedural difficulties to count as active deliberative pauses. | Add anti-pattern banning post-hoc retrospective comments and logistical/file-handling notes. Require active deliberative pause questioning substantive domain assumptions. | Pruned adding new file-filtering flags in prompt compiler; harden atom criteria natively. | Proof: `test_matrix_anchoring_rules.py` asserts exact anti-pattern; both models evaluate `FAILED` on user's duplicate file comment. |
| **Kahneman Level 1 (Association)**<br>`seed_data.json#L3263-L3303` | Banned attributing metaphors or analogies contained in cited external sources or conversational partner prompts to the human user. | Add anti-pattern banning quoting, citing, transcribing, or prompting with external source metaphors. Electrical percolation contrastive exemplar. | Pruned creating complex speaker-attribution regex parsers; enforce via TDA anti-pattern. | Proof: `test_matrix_anchoring_rules.py` asserts exact anti-pattern; Gemini no longer passes user on Sitra's quoted phrase. |

---

```xml
<execution_protocol>
  <phase id="1" name="PRE-IMPLEMENTATION CLEANUPS &amp; TECHNICAL DEBT ERADICATION">
    <step id="1.1" name="SEED DATA BACKUP">
      <action>Create a timestamped backup copy of `backend_v2/seed/seed_data.json` in `backend_v2/seed/backups/seed_data_backup_[TIMESTAMP].json` before modifying JSON structures.</action>
      <constraint invariant="live_database_mutation">Never modify the active database directly; all changes must originate in seed_data.json.</constraint>
    </step>
    <step id="1.2" name="TECHNICAL DEBT ERADICATION ACROSS TOUCHED ENTITIES &amp; 1-HOP CALLERS">
      <action>Perform 7-item technical debt sweep and eradication across touched entities and 1-hop callers:
        1. Touched atoms: `tda_07ef835fd139e70fd9d9f2151dc9a5aa` (Bloom L6), `tda_5198e13cde3447fe9d0737a80abe458c` (Bloom L5), `tda_ab3ebf5a42f0d72eca9acceeb2e12ce1` (Kahneman L1), `tda_5fc55ef72665907c426e2598cddde565` (Kahneman L2). Eradicate open-ended ambiguity tokens (`e.g.`, `etc.`, `i.e.`), screaming imperatives, and enforce concept description length &lt;= 180 chars.
        2. Touched workflows and step blueprints: `wf_03a1d71000000003`, `sp_f22db9f1dde048b7` (Step 2), `sp_25664f44773a4354` (Step 4). Verified zero unmapped fallback keys, exact Opaque Stripe IDs, and zero legacy string slugs in foreign keys.
        3. 1-Hop DTOs and Services: In `@[backend_v2/models/dtos/studio.py#L200-L230]` and `@[backend_v2/models/dtos/studio.py#L612-L632]`, `@[backend_v2/services/studio/workflow_service.py#L570-L590]`, `@[backend_v2/services/orchestrator/strategies/base.py#L54-L66]`, and `@[backend_v2/services/orchestrator/dag_executor.py#L269-L281]`, eradicate legacy string `model_strategy` references in favor of strongly-typed `CognitiveTier`.
        4. Flutter Studio Models &amp; Design Tokens:
           - In `@[client_app_v2/lib/features/studio/models/model_config.dart#L10-L51]`, eliminate legacy flat `Map<String, LlmModelConfig> models` in favor of typed `tierDefinitions: Map<String, Map<String, LlmModelConfig>>`.
           - In `@[client_app_v2/lib/features/studio/views/step_builder_view.dart#L480]`, replace hardcoded magic double `const SizedBox(height: 24)` with design token `AppSpacing.p24` and update `labelText: l10n.studioModelStrategyLabel` to `l10n.studioCognitiveTierLabel`.
        5. Backend String Strategy Cleanups:
           - In `@[backend_v2/worker.py#L1009]`, `#L1253]`, and `#L1435]`, replace hardcoded string literals (`"synthesis"`, `"strict"`) with typed `CognitiveTier` references.
           - In `@[backend_v2/llm/client.py#L125-L128]` and `@[backend_v2/settings.py]`, eradicate `strategy_aliases` configuration and the `while isinstance(target_strategy, str):` loop in favor of direct O(1) tier lookup.
        6. Forensic Test Runner Fallback Purge:
           - In `@[scripts/diff_executions.py#L1261-L1285]`, delete legacy hardcoded fallback models (`gemini-2.5-flash`, `gemini-2.5-pro`, `claude-3-5-sonnet`).
        7. ISTQB Negative Partition Assurance:
           - In `@[backend_v2/tests/unit/seed/test_matrix_anchoring_rules.py]`, add negative test partitions asserting rejection of all 4 anti-patterns.
           - In `@[backend_v2/tests/unit/llm/test_llm_client_tiers.py]`, add negative test partitions asserting fail-fast `ConfigurationError` on unconfigured providers or tiers.
      </action>
    </step>
  </phase>

  <phase id="2" name="CORE DOMAIN SCHEMA &amp; MODEL REGISTRY EVOLUTION">
    <step id="2.1" name="DEFINE COGNITIVE TIER AND LLM PROVIDER ONTOLOGY">
      <action>In `@[backend_v2/models/v2_core.py#L30-L50]`:
        1. Define `CognitiveTier(StrEnum)`: `FAST = "fast"`, `BALANCED = "balanced"`, `DEEP = "deep"`, `REASONING = "reasoning"`.
        2. Define `LLMProvider(StrEnum)`: `GOOGLE = "google"`, `OPENAI = "openai"`, `ANTHROPIC = "anthropic"`, `AZURE_OPENAI = "azure_openai"`, `LOCAL = "local"`.
      </action>
    </step>
    <step id="2.2" name="EVOLVE SYSTEM CONFIG MODEL REGISTRY SCHEMA">
      <action>In `@[backend_v2/models/v2_core.py#L457-L468]`:
        Update `SystemConfigModelRegistry` schema:
        ```python
        class SystemConfigModelRegistry(V2CoreBase):
            model_config = ConfigDict(strict=True, extra="forbid", frozen=True, title="model_registry")
            id: str = Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="System config ID")
            type: Literal["model_registry"] = Field(default="model_registry")
            slug: str | None = Field(default=None)
            default_provider: LLMProvider = Field(default=LLMProvider.GOOGLE)
            tier_definitions: dict[LLMProvider, dict[CognitiveTier, ModelProfile]] = Field(
                description="Strongly typed matrix mapping providers and cognitive tiers to physical profiles"
            )
        ```
        Add `@model_validator(mode="after")` enforcing that every registered provider implements all four `CognitiveTier` values (`FAST`, `BALANCED`, `DEEP`, `REASONING`).
      </action>
    </step>
    <step id="2.3" name="UPDATE EXECUTION INGRESS DTOS">
      <action>In `@[backend_v2/models/dtos/trace.py#L40-L58]` and `@[backend_v2/models/v2_core.py#L1541-L1578]`:
        Add `provider_override: LLMProvider | None = None` to `ExecutionCreateDTO` and `ExecutionCreate` domain model.
      </action>
    </step>
    <step id="2.4" name="UPDATE STEP DOMAIN MODEL">
      <action>In `@[backend_v2/models/v2_core.py#L520-L611]`:
        In class `Step` (aliased as `V2Step`), replace `model_strategy: str | None = None` (#L566-L572) with `cognitive_tier: CognitiveTier = CognitiveTier.FAST`. Update `@model_validator` `validate_step_consistency` (#L583-L610) to assert `self.cognitive_tier in CognitiveTier`.
      </action>
    </step>
    <step id="2.5" name="UPDATE 1-HOP STUDIO DTOS &amp; ORCHESTRATOR SERVICES">
      <action>
        1. In `@[backend_v2/models/dtos/studio.py#L200-L230]` &amp; `@[backend_v2/models/dtos/studio.py#L612-L632]`: Replace `model_strategy` with `cognitive_tier: CognitiveTier` in `StepCreateDTO` and `StepUpdateDTO`.
        2. In `@[backend_v2/services/studio/workflow_service.py#L570-L590]`: Update `create_draft_step` to set `cognitive_tier=CognitiveTier.FAST`.
        3. In `@[backend_v2/services/orchestrator/strategies/base.py#L54-L66]`: Update `StrategyContext` replacing `model_strategy: str | None` with `cognitive_tier: CognitiveTier`.
        4. In `@[backend_v2/services/orchestrator/dag_executor.py#L269-L281]`: Pass `cognitive_tier=step_def.cognitive_tier` when constructing `StrategyContext`.
      </action>
    </step>
    <step id="2.6" name="UPDATE FLUTTER CORE ENUMS &amp; MODEL CONFIG">
      <action>
        1. In `@[client_app_v2/lib/core/models/enums.dart#L1-L40]`: Add `CognitiveTier` enum with `@JsonValue` mappings for `fast`, `balanced`, `deep`, `reasoning`.
        2. In `@[client_app_v2/lib/features/studio/models/model_config.dart#L10-L51]`: Update `ModelConfig` and `LlmModelConfig` to support `defaultProvider` and `tierDefinitions: Map<String, Map<String, LlmModelConfig>>`.
      </action>
    </step>
  </phase>

  <phase id="3" name="SEED VAULT MIGRATION &amp; TIER STRUCTURE DEFINITION">
    <step id="3.1" name="MIGRATE MODEL REGISTRY IN SEED DATA">
      <action>In `@[backend_v2/seed/seed_data.json#L7-L91]`, restructure `system_config.models` into normalized `tier_definitions` for Google and OpenAI:
        - `google`:
          - `fast`: `gemini/gemini-3.8-flash`, `thinking_budget_tokens: 0`, `temperature: 0.1`, `max_tokens: 32768`, `rpm_limit: 200`, `tpm_limit: 4000000`
          - `balanced`: `gemini/gemini-3.8-flash`, `thinking_budget_tokens: 2048`, `temperature: 1.0`, `max_tokens: 65536`, `rpm_limit: 60`, `tpm_limit: 4000000`
          - `deep`: `gemini/gemini-3.8-flash`, `thinking_budget_tokens: 4096`, `temperature: 1.0`, `max_tokens: 65536`, `rpm_limit: 60`, `tpm_limit: 4000000`
          - `reasoning`: `gemini/gemini-3.8-flash`, `thinking_budget_tokens: 8192`, `temperature: 1.0`, `max_tokens: 65536`, `rpm_limit: 60`, `tpm_limit: 4000000`
        - `openai`:
          - `fast`: `openai/gpt-5.1` (or `gpt-4o-mini`), `thinking_budget_tokens: 0`, `temperature: 1.0`, `max_tokens: 32768`, `rpm_limit: 500`, `tpm_limit: 1000000`
          - `balanced`: `openai/gpt-5.1`, `thinking_budget_tokens: 2048` (`reasoning_effort: "low"`), `temperature: 1.0`, `max_tokens: 32768`, `rpm_limit: 500`, `tpm_limit: 1000000`
          - `deep`: `openai/gpt-5.1`, `thinking_budget_tokens: 4096` (`reasoning_effort: "medium"`), `temperature: 1.0`, `max_tokens: 32768`, `rpm_limit: 500`, `tpm_limit: 1000000`
          - `reasoning`: `openai/gpt-5.1`, `thinking_budget_tokens: 8192` (`reasoning_effort: "high"`), `temperature: 1.0`, `max_tokens: 32768`, `rpm_limit: 500`, `tpm_limit: 1000000`
      </action>
    </step>
    <step id="3.2" name="MIGRATE WORKFLOW STEP BLUEPRINTS IN SEED DATA">
      <action>In `@[backend_v2/seed/seed_data.json#L19500-L19890]`, migrate all step blueprints:
        - Rename `"model_strategy"` to `"cognitive_tier"`.
        - Map `"fast"` -> `"fast"`, `"reasoning"` -> `"reasoning"`.
      </action>
    </step>
  </phase>

  <phase id="4" name="STEP BLUEPRINT COGNITIVE UPGRADE &amp; WORKFLOW CALIBRATION">
    <step id="4.1" name="UPGRADE STEP 2 ARCHIVIST TO COGNITIVE TIER DEEP">
      <action>In `@[backend_v2/seed/seed_data.json#L19572-L19614]`, locate Step 2 Archivist (`sp_f22db9f1dde048b7`) and set:
        - `"cognitive_tier": "deep"`.
      </action>
    </step>
    <step id="4.2" name="CALIBRATE WORKFLOW 3 STRICTNESS TO 70%">
      <action>In `@[backend_v2/seed/seed_data.json#L18805-L19046]`, locate `wf_03a1d71000000003` and update:
        - `"default_strictness_level": 70` (#L18825).
      </action>
    </step>
    <step id="4.3" name="WIRE PASSIVITY HOOK AND ACTIVATE WORKFLOW PENALTY">
      <action>Synchronously update Step 4 and Workflow 3:
        1. In `sp_25664f44773a4354.post_hooks` (#L19694-L19697), add `"enforce_passivity_penalty"`.
        2. In `wf_03a1d71000000003` (#L19045), set `"passivity_penalty": 0.05`.
      </action>
    </step>
  </phase>

  <phase id="5" name="ONTOLOGICAL HARDENING OF BLOOM'S TAXONOMY">
    <step id="5.1" name="HARDEN BLOOM LEVEL 6 CREATION ATOM (tda_07ef835fd139e70fd9d9f2151dc9a5aa)">
      <action>Update `tda_07ef835fd139e70fd9d9f2151dc9a5aa` in `@[backend_v2/seed/seed_data.json#L2998-L3038]`:
        1. Add explicit anti-pattern banning thematic clustering without causal mechanics.
        2. Expand acceptance criteria requiring explicit boundary constraints.
        3. Replace contrastive example with plasma-aerobraking tensor exemplar.
      </action>
    </step>
    <step id="5.2" name="HARDEN BLOOM LEVEL 5 CRITERIA ANCHORING ATOM (tda_5198e13cde3447fe9d0737a80abe458c)">
      <action>Update `tda_5198e13cde3447fe9d0737a80abe458c` in `@[backend_v2/seed/seed_data.json#L2685-L2727]`:
        1. Add anti-pattern banning passive regulatory citation without performance auditing.
        2. Update contrastive example with ASME Section VIII hydrostatic pressure exemplar.
      </action>
    </step>
  </phase>

  <phase id="6" name="ONTOLOGICAL HARDENING OF KAHNEMAN'S DUAL PROCESS THEORY">
    <step id="6.1" name="HARDEN KAHNEMAN LEVEL 2 DELIBERATIVE PAUSE (tda_5fc55ef72665907c426e2598cddde565)">
      <action>Update `tda_5fc55ef72665907c426e2598cddde565` in `@[backend_v2/seed/seed_data.json#L3475-L3515]`:
        1. Add anti-pattern banning retrospective post-hoc procedural/file reflections.
        2. Replace contrastive example with laminar flow vs. sensor logging exemplar.
      </action>
    </step>
    <step id="6.2" name="HARDEN KAHNEMAN LEVEL 1 QUALITATIVE ASSOCIATION (tda_ab3ebf5a42f0d72eca9acceeb2e12ce1)">
      <action>Update `tda_ab3ebf5a42f0d72eca9acceeb2e12ce1` in `@[backend_v2/seed/seed_data.json#L3263-L3303]`:
        1. Add anti-pattern banning quoting external source metaphors.
        2. Replace contrastive example with electrical percolation exemplar.
      </action>
    </step>
  </phase>

  <phase id="7" name="BACKEND RESOLUTION ENGINE &amp; WORKER DECOUPLING">
    <step id="7.1" name="REFACTOR LLMCLIENT.FROM_TIER">
      <action>In `@[backend_v2/llm/client.py#L85-L165]`:
        1. Implement `LLMClient.from_tier(cls, tier: CognitiveTier, repository: SystemRepository, provider: LLMProvider | None = None, pipeline_name: str | None = None)`.
        2. Eliminate legacy `while isinstance(target_strategy, str):` loop and `get_settings().strategy_aliases`.
      </action>
    </step>
    <step id="7.2" name="DECOUPLE STEP EXECUTOR LLM STRATEGY RESOLUTION">
      <action>In `@[backend_v2/services/orchestrator/strategies/llm.py#L569-L581]`:
        Resolve LLM client via `LLMClient.from_tier(step.cognitive_tier, self.system_repo, provider=execution_context.provider)`.
      </action>
    </step>
    <step id="7.3" name="DECOUPLE SYNTHESIS WORKER TASKS">
      <action>In `@[backend_v2/worker.py]`:
        1. Replace `synthesis_model_strategy = "synthesis"` with `CognitiveTier.BALANCED` at `#L1008-L1058`.
        2. Replace `LLMClient.from_strategy("strict")` at line 1253 with `CognitiveTier.FAST`.
        3. Replace `LLMClient.from_strategy("strict")` at line 1435 with `CognitiveTier.DEEP`.
        All calls pass `provider=execution.provider`.
      </action>
    </step>
    <step id="7.4" name="UPDATE INTERNAL BACKEND UTILITIES">
      <action>In `@[backend_v2/services/chat_parser.py#L149-L163]` and `@[backend_v2/hooks/interaction_hook.py#L92-L96]`:
        Call `LLMClient.from_tier(CognitiveTier.FAST, repository=system_repo)`.
      </action>
    </step>
  </phase>

  <phase id="8" name="FLUTTER QUORUM STUDIO &amp; TELEMETRY UI ALIGNMENT">
    <step id="8.1" name="UPDATE FREEZED DOMAIN MODELS">
      <action>In `@[client_app_v2/lib/features/studio/models/workflow.dart#L78-L123]` and `@[client_app_v2/lib/features/execution/models/execution_step.dart#L1-L38]`:
        1. Update `NodeStrategyLlm` and `WorkflowStep` with `@JsonKey(name: 'cognitive_tier') CognitiveTier cognitiveTier`.
        2. Update `ExecutionStep` with `@JsonKey(name: 'cognitive_tier') CognitiveTier? cognitiveTier`.
      </action>
    </step>
    <step id="8.2" name="ADD LOCALIZATION STRINGS">
      <action>In `app_en.arb` and `app_fi.arb`, add strings for `studioTierFast`, `studioTierBalanced`, `studioTierDeep`, `studioTierReasoning`, `studioCognitiveTierLabel`, and resolution chips. Run `flutter gen-l10n`.</action>
    </step>
    <step id="8.3" name="REFACTOR STEP BUILDER VIEW DROPDOWN">
      <action>In `@[client_app_v2/lib/features/studio/views/step_builder_view.dart#L430-L480]`:
        Replace raw model keys dropdown with `CognitiveTier` dropdown and read-only resolution chip. Replace `const SizedBox(height: 24)` with `AppSpacing.p24`.
      </action>
    </step>
    <step id="8.4" name="RUN BUILD RUNNER FOR FREEZED GENERATION">
      <action>Execute `dart run build_runner build --delete-conflicting-outputs` in `client_app_v2`.</action>
    </step>
  </phase>

  <phase id="9" name="MULTI-PROVIDER E2E VARIANCE TEST RUNNER &amp; FORENSIC DIFF TELEMETRY">
    <step id="9.1" name="UPGRADE RUN_E2E_VARIANCE_TEST.PY PROVIDER RUNNER">
      <action>In `@[scripts/run_e2e_variance_test.py#L1307-L1410]`:
        1. Remove `STRATEGY_ALIASES` environment variable injection.
        2. Add `--providers` CLI parameter supporting sequential multi-provider execution runs (e.g. `--providers google openai`).
        3. Pass `provider_override` in `ExecutionCreateDTO` payload per run.
      </action>
    </step>
    <step id="9.2" name="UPGRADE RUN_E2E_VARIANCE_TEST.PY TELEMETRY PRINTING">
      <action>In `@[scripts/run_e2e_variance_test.py#L1250-L1305]` &amp; `#L1373-L1387`:
        Update `resolve_model_telemetry()`, `print_model_telemetry()`, and per-run startup logging:
        1. Always print actual provider (`Google Vertex AI`, `Google AI Studio`, `OpenAI`).
        2. Always print exact token limits: `max_tokens` (output ceiling), `thinking_budget_tokens` / `reasoning_effort` (thinking token budget), `tpm_limit` (tokens/min), `rpm_limit` (requests/min), `effective_temperature`.
        3. Print human-readable localized workflow and step names (e.g. "Sitra Megatrendit 2026", "Archivist", "Analyst", "Coach").
        4. Strictly ban raw opaque database IDs (`wf_...`, `sp_...`, `sys_...`) and abstract top-level strategy wrapper aliases (`evaluation_strategy`, `test_strategy`) in user-facing logging.
      </action>
    </step>
    <step id="9.3" name="UPGRADE DIFF_EXECUTIONS.PY FORENSIC MODEL BINDINGS &amp; REPORT FORMATTING">
      <action>In `@[scripts/diff_executions.py]`:
        1. Update `PhysicalModelBindingDTO` (`#L233-L244`) to add fields: `provider: str`, `tpm_limit: int | None = None`, `rpm_limit: int | None = None`, `reasoning_effort: str | None = None`.
        2. Eliminate hardcoded legacy fallback models (`gemini-2.5-flash`, `gemini-2.5-pro`, `claude-3-5-sonnet`) in `resolve_physical_model_bindings()` (`#L1230-L1286`).
        3. In the Markdown report generator (`#L2170-L2240`), render physical model bindings table and workflow provenance using localized human names and exact token capacity limits, strictly banning raw database IDs and high-level wrapper names in report headlines.
      </action>
    </step>
  </phase>

  <phase id="10" name="REGRESSION UNIT TEST EXPANSION &amp; TIER VERIFICATION">
    <step id="10.1" name="EXPAND MATRIX ANCHORING UNIT TESTS">
      <action>Update `@[backend_v2/tests/unit/seed/test_matrix_anchoring_rules.py#L220-L260]` to assert anti-patterns and contrastive pairs for all 4 hardened atoms alongside the 7 existing stabilized atoms.</action>
    </step>
    <step id="10.2" name="VERIFY 100% BEST-OF-3 ENTROPY INVARIANT">
      <action>Verify `test_all_matrix_atoms_have_high_entropy_activated()` passes 100% (Measure 2 rejection enforcement).</action>
    </step>
    <step id="10.3" name="ADD LLMCLIENT TIER UNIT TESTS">
      <action>Create `@[backend_v2/tests/unit/llm/test_llm_client_tiers.py]` verifying `LLMClient.from_tier()` across providers and fail-fast behavior on unconfigured tiers.</action>
    </step>
    <step id="10.4" name="SYNCHRONIZE REGRESSION TEST SUITE FIXTURES">
      <action>Synchronize existing regression test fixtures to prevent broken test suites:
        1. In `@[backend_v2/tests/unit/test_model_registry.py#L80-L115]`: Update `SystemConfigModelRegistry` test instantiations to provide valid `tier_definitions`.
        2. In `@[backend_v2/tests/unit/test_seed_architectural_guardrails.py#L122-L165]` &amp; `@[backend_v2/tests/unit/test_seed_architectural_guardrails.py#L390-L430]`: Update `test_model_strategies_are_bound_to_registry` and `test_synthesis_strategy_isolation` to assert `tier_definitions` and `cognitive_tier`.
        3. In `@[backend_v2/tests/unit/test_v2_core_strictness.py#L60-L115]`: Update `Step` instantiations to use `cognitive_tier=CognitiveTier.FAST`.
        4. In `@[backend_v2/tests/unit/test_run_e2e_variance_test.py#L445-L465]`: Update assertion from `model_strategy == "fast"` to `cognitive_tier == "deep"`.
      </action>
    </step>
    <step id="10.5" name="RUN FLUTTER UNIT TESTS">
      <action>Execute `flutter test test/features/studio/models/workflow_test.dart` and `flutter test test/features/studio/views/step_builder_view_test.dart`.</action>
    </step>
  </phase>

  <phase id="11" name="PRE-FLIGHT VALIDATION, LINTER &amp; QUALITY GATES">
    <step id="11.1" name="TWO-PHASE PRE-FLIGHT IN-MEMORY VALIDATION">
      <action>Execute `uv run python backend_v2/seed/run_seed.py local --dry-run` and `uv run python scripts/audit_database_atoms.py --strict` to verify schema integrity, tier definitions, and atom contracts.</action>
    </step>
    <step id="11.2" name="LOCAL DATABASE SEED SYNC">
      <action>Execute `uv run python backend_v2/seed/run_seed.py local` to persist updated seed data to `@[data/db_v2.json]`.</action>
    </step>
    <step id="11.3" name="FULL BACKEND QUALITY GATE">
      <action>Execute `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/seed/test_matrix_anchoring_rules.py --test`.</action>
    </step>
    <step id="11.4" name="FULL FLUTTER QUALITY GATE">
      <action>Execute `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/step_builder_view_test.dart`.</action>
    </step>
  </phase>

  <phase id="12" name="KNOWLEDGE ITEM &amp; ARCHITECTURAL DOCUMENTATION SYNCHRONIZATION">
    <step id="12.1" name="UPDATE KNOWLEDGE ITEMS">
      <action>Update:
        - `ki_prompt_orchestration_and_matrix_evaluation.md` (Bloom L5-L6 and Kahneman L1-L2 anti-patterns and provenance boundaries)
        - `ki_unified_matrix_scoring_strictness.md` (Strictness 70% and passivity hook wiring)
        - `ki_tda_best_of_three_flash.md` (100% Best-of-3 entropy coverage invariant)
        - `ki_provider_agnostic_caching.md` (Provider-Agnostic Cognitive Tiers architecture)
      </action>
    </step>
    <step id="12.2" name="INVOKE /tier7-DESCRIBE-ARCHITECTURE">
      <action>Invoke `/tier7-describe-architecture` for `@[docs/architecture/01_system_context_and_invariants.md]` and `@[docs/architecture/03_cognitive_orchestration_engine.md]`.</action>
    </step>
  </phase>
</execution_protocol>
```

---

## Anti-Happy-Path Test Scenarios

1. **Negative Scenario 1 (Thematic Grouping Rejection):** A submission clusters diverse source items into umbrella pillars without an explicit operational or causal mechanism. The evaluator MUST evaluate `tda_07ef835fd139e70fd9d9f2151dc9a5aa` as `FAILED`.
2. **Negative Scenario 2 (Passive Mandate Citation Rejection):** A submission lists regulatory directives as compliance obligations without benchmarking observed telemetry against their explicit limits. The evaluator MUST evaluate `tda_5198e13cde3447fe9d0737a80abe458c` as `FAILED`.
3. **Negative Scenario 3 (The Lazy Observer Reflection Pass Rejection):** A user allows multi-persona dialogue to run unmonitored, then writes in reflection: *"Pysähdyin pohtimaan, että olisiko pitänyt rajata tarkemmin."* The evaluator MUST evaluate `tda_5fc55ef72665907c426e2598cddde565` as `FAILED`.
4. **Negative Scenario 4 (Quoted Metaphor Attribution Fallacy Rejection):** A user pastes an external report into the chat containing narrative metaphors (*"Sitran näkemyksen mukaan tulevaisuus ei vain vyöry päälle..."*). The evaluator MUST evaluate `tda_ab3ebf5a42f0d72eca9acceeb2e12ce1` as `FAILED`.
5. **Negative Scenario 5 (Provider Capability Asymmetry Guard):** An unconfigured provider or model without thinking capabilities is assigned to `CognitiveTier.DEEP`. Pre-flight validation fails fast with `ValidationError`, requiring explicit `thinking_budget_tokens > 0` for deep/reasoning tiers.
6. **Negative Scenario 6 (Partial Provider Registration Guard):** A provider is registered in `seed_data.json` with only `FAST` and `BALANCED` configured. Pre-flight dry-run fails fast with `ValidationError`, asserting that every provider must implement all four canonical `CognitiveTier`s.
7. **Negative Scenario 7 (Reasoning Latency & Token Explosion Guard):** Step 2 (Archivist) is assigned `CognitiveTier.DEEP` (4,096 tokens), rejecting `REASONING` (8,192 tokens), capping thinking tokens to $\approx 368,000$ and preventing Arq worker timeouts and 60 RPM Gemini rate limits.
8. **Negative Scenario 8 (Phantom Penalty Silent Bypass Guard):** Setting `passivity_penalty = 0.05` on `wf_03a1d71000000003` without adding `"enforce_passivity_penalty"` to Step 4 Coach `post_hooks` is prevented by synchronous verification.
9. **Negative Scenario 9 (Opaque ID & Top-Level Name Leaks in Telemetry Guard):** Automated assertion in test suite verifying that report headers in `diff_executions.py` and startup telemetry in `run_e2e_variance_test.py` strictly print human-readable localized names, real providers, and explicit token limits (`max_tokens`, `thinking_budget`, `tpm_limit`, `rpm_limit`), and contain zero raw database IDs or abstract strategy aliases in headlines.

---

## Verification Plan

### Automated Tests
1. **Matrix Anchoring & Entropy Verification:**
   ```powershell
   uv run pytest backend_v2/tests/unit/seed/test_matrix_anchoring_rules.py -vv
   ```
2. **Cognitive Tier Client Resolution Tests:**
   ```powershell
   uv run pytest backend_v2/tests/unit/llm/test_llm_client_tiers.py -vv
   ```
3. **Database Atom Linter:**
   ```powershell
   uv run python scripts/audit_database_atoms.py --strict
   ```
4. **Two-Phase Seeder Pre-Flight Dry Run:**
   ```powershell
   uv run python backend_v2/seed/run_seed.py local --dry-run
   ```
5. **Backend Quality Gate (Ruff, MyPy Strict, Pytest):**
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/seed/test_matrix_anchoring_rules.py --test
   ```
6. **Flutter Client Quality Gate:**
   ```powershell
   uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/step_builder_view_test.dart
   ```

### End-to-End Multi-Provider Benchmark Verification
Run the cross-model variance test across both providers on Sitra input data:
```powershell
uv run python scripts/run_e2e_variance_test.py data/test_inputs_sitra --workflow wf_03a1d71000000003 --providers google openai --cooldown-seconds 10 --no-noise --dev
```
Verify that:
1. Run 1 executes natively on Google using Google's tiered profiles (`FAST`, `DEEP`, `REASONING`, `BALANCED`).
2. Run 2 executes natively on OpenAI using OpenAI's tiered profiles (`FAST`, `DEEP` with medium effort, `REASONING` with high effort, `BALANCED` with low effort).
3. Both runs preserve step-level cognitive differentiation.
4. Telemetry logging and the differential Markdown report print:
   - Real provider: `Google (AI Studio / Vertex AI)` vs `OpenAI Platform`
   - Allowed token limits: `max_tokens` (32,768 / 65,536), thinking budget (4,096 tok / reasoning effort: "medium"), TPM limit (4,000,000 / 1,000,000), RPM limit (60 / 500), effective temperature (1.0)
   - Localized human-readable names (e.g. "Archivist", "Analyst", "Coach") without raw database IDs (`wf_...`, `sp_...`, `sys_...`) or abstract top-level strategy wrapper aliases.
5. Both models achieve 100% consensus on the 4 hardened atoms:
   - `tda_07ef835fd139e70fd9d9f2151dc9a5aa` (FAILED)
   - `tda_5198e13cde3447fe9d0737a80abe458c` (FAILED)
   - `tda_5fc55ef72665907c426e2598cddde565` (FAILED)
   - `tda_ab3ebf5a42f0d72eca9acceeb2e12ce1` (FAILED)
6. The Bloom score drift ($\Delta = +11.4$) is eliminated.
