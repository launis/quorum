<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
</required_context_rules>

# Phase 1: Pre-Implementation Technical Debt Cleanups, 100% `CognitiveTier` Enum Enforcement & `LLMClient.from_strategy` Eradication

**Overview:** Resolve Chapter 7 of `@[docs/arkkitehtuurin_parannuskohteet.md#L232-329]` (`@[docs/arkkitehtuurin_parannuskohteet.md#L261-283]`) and all 4 pre-existing technical debt warnings discovered in the touched scope (`@[scripts/ablation_live_executor.py#L153-L180]`, `@[scripts/ablation_live_executor.py#load_seed_data]`, `@[scripts/ablation_live_executor.py#L651-L691]`, `@[backend_v2/tests/fakes/in_memory_uow.py#L941-L996]`, and `@[backend_v2/tests/fakes/in_memory_uow.py#L1165-L1221]`). Enforce `CognitiveTier` Enum Single Source of Truth (SSOT) in `PipelineConfig.default_strategy` and `PIPELINE_REGISTRY` (`@[backend_v2/models/enums.py#L182-L188]` / `@[backend_v2/models/enums.py#L182-L188]`), migrate all 5 production and operational script call sites (`@[backend_v2/services/chat_parser.py#L72-L346]` / `@[backend_v2/services/chat_parser.py#L136-L346]`, `@[backend_v2/hooks/interaction_hook.py#L44-L185]` / `@[backend_v2/hooks/interaction_hook.py#L44-L185]`, `@[backend_v2/hooks/linguistics.py#L78-L231]` / `@[backend_v2/hooks/linguistics.py#L78-L231]`, `@[backend_v2/hooks/source_verification_hook.py#L155-L282]` / `@[backend_v2/hooks/source_verification_hook.py#L156-L282]`, and `@[scripts/ablation_live_executor.py#L651-L691]`) and 14 unit test suites from `LLMClient.from_strategy` to `LLMClient.from_tier` (`@[backend_v2/llm/client.py#L129-312]`, per `direct_sdk_calls` and `internal_utility_llm_execution` in `@[.agents/rules/05_llm_architecture.md#L18-20]`), delete the legacy `LLMClient.from_strategy` bridge (`@[backend_v2/llm/client.py#L44-L863]` inside `@[backend_v2/llm/client.py#L44-L863]`), and enforce static AST guardrail protection in `@[scripts/_ast_guardrails.py#L781-L3519]`.

**Source:** `@[docs/epic/EPIC_162_studio_target_sync_cognitive_tier_and_dag_occ_resilience.md]` Phase 1: Pre-Implementation Technical Debt Cleanups, 100% `CognitiveTier` Enum Enforcement & `LLMClient.from_strategy` Eradication

**Target Files:**
- `[MODIFY] @[scripts/ablation_live_executor.py#L153-L180]`
- `[MODIFY] @[scripts/ablation_live_executor.py#L651-L691]`
- `[MODIFY] @[scripts/run_ablation_benchmark.py#L490-L1148]`
- `[MODIFY] @[backend_v2/tests/fakes/in_memory_uow.py#L941-L996]`
- `[MODIFY] @[backend_v2/tests/fakes/in_memory_uow.py#L1165-L1221]`
- `[MODIFY] @[backend_v2/models/enums.py#L1051-L1065]`
- `[MODIFY] @[backend_v2/services/chat_parser.py#L72-L346]`
- `[MODIFY] @[backend_v2/hooks/interaction_hook.py#L44-L185]`
- `[MODIFY] @[backend_v2/hooks/linguistics.py#L78-L231]`
- `[MODIFY] @[backend_v2/hooks/source_verification_hook.py#L155-L282]`
- `[MODIFY] @[backend_v2/llm/client.py#L44-L863]`
- `[MODIFY] @[scripts/_ast_guardrails.py#L781-L3519]`
- `[MODIFY] @[backend_v2/tests/unit/models/test_enums.py#L240-L245]`
- `[MODIFY] @[backend_v2/tests/unit/llm/test_llm_client_tiers.py#L193-L208]`
- `[MODIFY] @[backend_v2/tests/unit/llm/test_provider_retry_after.py#L131-L133]`
- `[MODIFY] @[backend_v2/tests/unit/services/test_chat_parser.py#L37-L87]`
- `[MODIFY] @[backend_v2/tests/unit/hooks/test_interaction_hook.py#L120-L186]`
- `[MODIFY] @[backend_v2/tests/unit/hooks/test_linguistics.py#L487-L543]`
- `[MODIFY] @[backend_v2/tests/unit/hooks/test_source_verification_hook.py#L178-L250]`
- `[MODIFY] @[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py#L135-L184]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_ablation_live_executor.py#L519-L553]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_run_ablation_benchmark.py#L904-L918]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py#L154-L286]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py#L311-L420]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py#L477-L550]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_rag_preflight_chat_inflation.py#L42-L135]`
- `[MODIFY] @[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py#L139-L288]`
- `[MODIFY] @[backend_v2/tests/test_fastdev_frozen.py#L13-L48]`
- `[MODIFY] @[backend_v2/tests/unit/test_ast_domain_security_guardrails.py#L19-L31]`
- `[MODIFY] @[backend_v2/tests/unit/test_ast_domain_security_guardrails.py#L214-L232]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2935-L2987]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`@[scripts/ablation_live_executor.py#L153-L180]`**<br>**`@[scripts/ablation_live_executor.py#L153-L180]`**<br>**`@[backend_v2/tests/fakes/in_memory_uow.py#L217-L299]`**<br>**`@[backend_v2/tests/fakes/in_memory_uow.py#L217-L299]`** | Eradicate `TD_DICT_GET` warnings (`data.get("system_config", [])` in `load_seed_data` and `telemetry.get(strat)` at `#L649-L687`), untyped `tuple[str, str]` on `compare_strategies`, and `TD_MODEL_FACTORY` inline dict literal warnings in `in_memory_uow.py`. | Type `AblationLiveExecutionConfigDTO.compare_strategies` as `tuple[LaxCognitiveTier, LaxCognitiveTier] \| None = None`, replace `.get()` calls with explicit `"system_config" in data` and `strat in telemetry` membership checks, and extract module-level `_hydrate_in_memory_execution_record` and `_hydrate_in_memory_proposition_node` helpers in `in_memory_uow.py`. | Do NOT introduce new storage abstractions or external fixture frameworks; keep `in_memory_uow.py` and `ablation_live_executor.py` self-contained. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --targets scripts/ablation_live_executor.py backend_v2/tests/fakes/in_memory_uow.py` |
| **`@[backend_v2/models/enums.py#L1051-L1065]`**<br>**`@[backend_v2/services/chat_parser.py#L72-L346]`**<br>**`@[backend_v2/hooks/interaction_hook.py#L44-L185]`**<br>**`@[backend_v2/hooks/linguistics.py#L78-L231]`**<br>**`@[backend_v2/hooks/source_verification_hook.py#L155-L282]`** | Eradicate typing `PipelineConfig.default_strategy` as `str \| None = None`, passing raw `"fast"` string literals in `PIPELINE_REGISTRY`, and calling `LLMClient.from_strategy("fast", ...)` in backend services and hooks. | Type `PipelineConfig.default_strategy` as `CognitiveTier \| None = None`, use `CognitiveTier.FAST` in `PIPELINE_REGISTRY`, and call `await LLMClient.from_tier(CognitiveTier.FAST, ...)` across all 5 production and script call sites. | Do NOT create intermediate strategy-resolver wrapper functions; pass `CognitiveTier.FAST` directly to `LLMClient.from_tier`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/enums.py backend_v2/services/chat_parser.py backend_v2/hooks/interaction_hook.py backend_v2/hooks/linguistics.py backend_v2/hooks/source_verification_hook.py --test --ast-strict` |
| **`@[backend_v2/llm/client.py#L44-L863]`**<br>**`@[scripts/_ast_guardrails.py#L781-L3519]`** | Eradicate the legacy `LLMClient.from_strategy` string-coercion shim (`@[backend_v2/llm/client.py#L44-L863]`) and legacy unit tests mocking or invoking `from_strategy`. | Delete `LLMClient.from_strategy` from `LLMClient`, enforce static AST guardrail checks in `QuorumGuardrailVisitor.visit_Call` banning `.from_strategy(...)` and string-literal `LLMClient.from_tier("...")` calls, and migrate all 16 unit test files to `LLMClient.from_tier(CognitiveTier.<TIER>, ...)`. | Zero deprecated transition aliases or `@deprecated` shims on `LLMClient`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/llm/client.py scripts/_ast_guardrails.py --test --ast-strict` |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read `@[docs/epic/EPIC_162_studio_target_sync_cognitive_tier_and_dag_occ_resilience.md]`, `@[docs/epic/EPIC_162_audit_report.md]`, `@[backend_v2/models/enums.py#L1051-L1065]`, `@[backend_v2/llm/client.py#L129-312]`, `@[backend_v2/llm/client.py#L314-L681]`, `@[scripts/ablation_live_executor.py#L153-L180]`, `@[scripts/ablation_live_executor.py#L651-L691]`, `@[backend_v2/tests/fakes/in_memory_uow.py#L941-L996]`, and `@[backend_v2/tests/fakes/in_memory_uow.py#L1165-L1221]`.</action>
    <action>Look forward: Verify Step 1.1 resolves all 4 touched-scope technical debt items in `scripts/ablation_live_executor.py` and `backend_v2/tests/fakes/in_memory_uow.py`, Step 1.2 enforces `CognitiveTier` Enum typing on `PipelineConfig.default_strategy` and migrates all 5 production/script callers to `LLMClient.from_tier`, and Step 1.3 deletes `LLMClient.from_strategy`, adds static AST guardrail enforcement in `scripts/_ast_guardrails.py`, and migrates all 16 unit test suites.</action>
    <constraint invariant="direct_sdk_calls">All `LLMClient` initializations MUST route exclusively through `LLMClient.from_tier(CognitiveTier.&lt;TIER&gt;, repository=repo)` with zero string-based strategy bridges.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, synchronize architectural corrections back into @[docs/epic/EPIC_162_studio_target_sync_cognitive_tier_and_dag_occ_resilience.md] and @[docs/epic/EPIC_162_tracker.md]. Update # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_162/01_phase1_plan.md] @[docs/epic/EPIC_162_tracker.md].</directive>
  </step>

  <touched_artifacts>
    <backend>@[scripts/ablation_live_executor.py]</backend>
    <backend>@[scripts/run_ablation_benchmark.py]</backend>
    <backend>@[backend_v2/tests/fakes/in_memory_uow.py]</backend>
    <backend>@[backend_v2/models/enums.py]</backend>
    <backend>@[backend_v2/services/chat_parser.py]</backend>
    <backend>@[backend_v2/hooks/interaction_hook.py]</backend>
    <backend>@[backend_v2/hooks/linguistics.py]</backend>
    <backend>@[backend_v2/hooks/source_verification_hook.py]</backend>
    <backend>@[backend_v2/llm/client.py]</backend>
    <backend>@[scripts/_ast_guardrails.py]</backend>
    <backend>@[backend_v2/tests/unit/models/test_enums.py]</backend>
    <backend>@[backend_v2/tests/unit/llm/test_llm_client_tiers.py]</backend>
    <backend>@[backend_v2/tests/unit/llm/test_provider_retry_after.py]</backend>
    <backend>@[backend_v2/tests/unit/services/test_chat_parser.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_interaction_hook.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_linguistics.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_source_verification_hook.py]</backend>
    <backend>@[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_ablation_live_executor.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_run_ablation_benchmark.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_rag_preflight_chat_inflation.py]</backend>
    <backend>@[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py]</backend>
    <backend>@[backend_v2/tests/test_fastdev_frozen.py]</backend>
    <backend>@[backend_v2/tests/unit/test_ast_domain_security_guardrails.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]</backend>
  </touched_artifacts>

  <dod_checklist>
    <item>All 4 touched-scope technical debt items in @[scripts/ablation_live_executor.py#L153-L180], @[scripts/ablation_live_executor.py#L651-L691], @[backend_v2/tests/fakes/in_memory_uow.py#L941-L996], and @[backend_v2/tests/fakes/in_memory_uow.py#L1165-L1221] resolved (`0` findings in `scripts/audit_technical_debt.py`).</item>
    <item>`PipelineConfig.default_strategy` in @[backend_v2/models/enums.py#L1051-L1065] typed as `CognitiveTier | None = None` and `PIPELINE_REGISTRY` entries `"chat_parser"`, `"studio_generation"`, and `"interaction_hook"` updated to `default_strategy=CognitiveTier.FAST`.</item>
    <item>All 5 production and script call sites (@[backend_v2/services/chat_parser.py#L72-L346], @[backend_v2/hooks/interaction_hook.py#L44-L185], @[backend_v2/hooks/linguistics.py#L78-L231], @[backend_v2/hooks/source_verification_hook.py#L155-L282], and @[scripts/ablation_live_executor.py#L651-L691]) migrated to `LLMClient.from_tier`.</item>
    <item>`LLMClient.from_strategy` (@[backend_v2/llm/client.py#L44-L863]) completely deleted from `@[backend_v2/llm/client.py#L44-L863]`.</item>
    <item>`QuorumGuardrailVisitor.visit_Call` in @[scripts/_ast_guardrails.py#L781-L3519] statically bans `.from_strategy(...)` calls and string-literal `LLMClient.from_tier("...")` calls.</item>
    <item>All 16 unit test suites migrated to `LLMClient.from_tier(CognitiveTier.&lt;TIER&gt;, ...)` and passing `backend_audit_loop.py --test --ast-strict`.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
    <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Do NOT retain `LLMClient.from_strategy` as a deprecated alias or backward-compatibility wrapper (`zero_backward_compatibility_planning_ban`).</anti_target>
    <anti_target>Do NOT pass raw string literals (`"fast"`, `"balanced"`, `"deep_thinking"`) into `LLMClient.from_tier`.</anti_target>
    <anti_target>Do NOT modify Flutter `.dart` files or database DDL in Phase 1.</anti_target>
  </anti_targets>

  <step id="1.1" name="Pre-Implementation Technical Debt Cleanups in ablation_live_executor.py and in_memory_uow.py">
    <action>In @[scripts/ablation_live_executor.py#L153-L180], update `AblationLiveExecutionConfigDTO.compare_strategies` to `tuple[LaxCognitiveTier, LaxCognitiveTier] | None = None` (importing `CognitiveTier` and `LaxCognitiveTier` from `backend_v2.models.enums`). In `load_seed_data` (`@[scripts/ablation_live_executor.py#load_seed_data]`), replace `data.get("system_config", [])` with `"system_config" in data` membership resolution. In `@[scripts/ablation_live_executor.py#L153-L180]`, replace `telemetry.get(strat)` with `telemetry[strat] if strat in telemetry else None` and replace `LLMClient.from_strategy(strat_1, repository=repo)` / `LLMClient.from_strategy(strat_2, repository=repo)` with `LLMClient.from_tier(CognitiveTier(strat_1), repository=repo)` / `LLMClient.from_tier(CognitiveTier(strat_2), repository=repo)`.</action>
    <action>In @[backend_v2/tests/fakes/in_memory_uow.py#L217-L299] and @[backend_v2/tests/fakes/in_memory_uow.py#L217-L299], extract module-level typed hydration helpers `_hydrate_in_memory_execution_record` and `_hydrate_in_memory_proposition_node` so inline dict literal `model_validate({...})` calls at lines 1040 and 1154 are eliminated cleanly with zero `TD_MODEL_FACTORY` warnings.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_ablation_live_executor.py#L519-L553] and @[backend_v2/tests/unit/scripts/test_run_ablation_benchmark.py#L904-L918], update mocks and assertions from `LLMClient.from_strategy` to `LLMClient.from_tier` with `CognitiveTier` enum arguments and verify `AblationBenchmarkRunner` coerces `compare_strategies` in live mode.</action>
    <constraint invariant="the_zero_compromise_pledge">Zero `.get()` dictionary fallbacks in operational script or fake state hydration paths.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --targets scripts/ablation_live_executor.py backend_v2/tests/fakes/in_memory_uow.py</audit_command>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/ablation_live_executor.py backend_v2/tests/fakes/in_memory_uow.py backend_v2/tests/unit/scripts/test_ablation_live_executor.py --test --ast-strict</audit_command>
  </step>

  <step id="1.2" name="PipelineConfig.default_strategy CognitiveTier Enum Enforcement &amp; Production Call-Site Migration">
    <action>In @[backend_v2/models/enums.py#L1051-L1065] (`@[backend_v2/models/enums.py#L1051-L1065]`), change `PipelineConfig.default_strategy` from `Annotated[str | None, Field(default=None, description="Default cognitive tier if not overridden")] = None` to `Annotated[CognitiveTier | None, Field(default=None, description="Default cognitive tier if not overridden")] = None`, and update `PIPELINE_REGISTRY` entries `"chat_parser"`, `"studio_generation"`, and `"interaction_hook"` to `default_strategy=CognitiveTier.FAST`.</action>
    <action>In @[backend_v2/services/chat_parser.py#L72-L346] (`@[backend_v2/services/chat_parser.py#L136-L346]`), import `CognitiveTier` from `backend_v2.models.enums` and replace `await LLMClient.from_strategy("fast", repository=system_repo, pipeline_name="chat_parser", registry_id=registry_id, provider=provider_override)` with `await LLMClient.from_tier(CognitiveTier.FAST, repository=system_repo, pipeline_name="chat_parser", registry_id=registry_id, provider=provider_override)`.</action>
    <action>In @[backend_v2/hooks/interaction_hook.py#L44-L185] (`@[backend_v2/hooks/interaction_hook.py#L44-L185]`), import `CognitiveTier` from `backend_v2.models.enums` and replace `await LLMClient.from_strategy("fast", repository=system_repo, pipeline_name="interaction_hook", registry_id=registry_id, provider=provider_override)` with `await LLMClient.from_tier(CognitiveTier.FAST, repository=system_repo, pipeline_name="interaction_hook", registry_id=registry_id, provider=provider_override)`.</action>
    <action>In @[backend_v2/hooks/linguistics.py#L78-L231] (`@[backend_v2/hooks/linguistics.py#L78-L231]`), import `CognitiveTier` from `backend_v2.models.enums` and replace `await LLMClient.from_strategy("fast", repository=deps.system_repo, pipeline_name="linguistics_hook", registry_id=registry_id, provider=provider_override)` with `await LLMClient.from_tier(CognitiveTier.FAST, repository=deps.system_repo, pipeline_name="linguistics_hook", registry_id=registry_id, provider=provider_override)`.</action>
    <action>In @[backend_v2/hooks/source_verification_hook.py#L155-L282] (`@[backend_v2/hooks/source_verification_hook.py#L156-L282]`), import `CognitiveTier` from `backend_v2.models.enums` and replace `await LLMClient.from_strategy("fast", repository=deps.system_repo, pipeline_name="source_verification", registry_id=registry_id, provider=provider_override)` with `await LLMClient.from_tier(CognitiveTier.FAST, repository=deps.system_repo, pipeline_name="source_verification", registry_id=registry_id, provider=provider_override)`.</action>
    <action>In @[backend_v2/tests/unit/models/test_enums.py#L240-L245], @[backend_v2/tests/unit/services/test_chat_parser.py#L37-L87], @[backend_v2/tests/unit/hooks/test_interaction_hook.py#L120-L186], @[backend_v2/tests/unit/hooks/test_linguistics.py#L487-L543], and @[backend_v2/tests/unit/hooks/test_source_verification_hook.py#L178-L250], update all test assertions and `monkeypatch`/`patch.object` targets from `from_strategy` and `"fast"` to `from_tier` and `CognitiveTier.FAST`, and add negative validation tests verifying `PipelineConfig(default_strategy="fast")` fails under `strict=True`.</action>
    <constraint invariant="internal_utility_llm_execution">Internal LLM utilities and hooks MUST initialize clients via `await LLMClient.from_tier(CognitiveTier.FAST, repository=repo)`.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/enums.py backend_v2/services/chat_parser.py backend_v2/hooks/interaction_hook.py backend_v2/hooks/linguistics.py backend_v2/hooks/source_verification_hook.py backend_v2/tests/unit/models/test_enums.py backend_v2/tests/unit/services/test_chat_parser.py backend_v2/tests/unit/hooks/test_interaction_hook.py backend_v2/tests/unit/hooks/test_linguistics.py backend_v2/tests/unit/hooks/test_source_verification_hook.py --test --ast-strict</audit_command>
  </step>

  <step id="1.3" name="Eradication of LLMClient.from_strategy, Static AST Guardrail Enforcement &amp; Unit Test Suite Migration">
    <action>In @[backend_v2/llm/client.py#L44-L863], delete the `LLMClient.from_strategy` classmethod (`@[backend_v2/llm/client.py#L44-L863]`) completely while retaining `LLMClient.from_tier` (`@[backend_v2/llm/client.py#L129-312]`) as the sole factory entrypoint.</action>
    <action>In @[scripts/_ast_guardrails.py#L781-L3519], update `QuorumGuardrailVisitor.visit_Call` so that any call to `.from_strategy(...)` or any call to `LLMClient.from_tier(...)` passing a string literal (`ast.Constant` with `isinstance(val, str)`) as the first positional argument or `tier=` keyword argument triggers a `GuardrailSeverity.FATAL` violation.</action>
    <action>In @[backend_v2/tests/unit/llm/test_llm_client_tiers.py#L193-L208], @[backend_v2/tests/unit/llm/test_provider_retry_after.py#L131-L133], @[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py#L135-L184], @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py#L154-L286], @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py#L311-L420], @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py#L477-L550], @[backend_v2/tests/unit/services/orchestrator/test_rag_preflight_chat_inflation.py#L42-L135], @[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py#L139-L288], @[backend_v2/tests/test_fastdev_frozen.py#L13-L48], @[backend_v2/tests/unit/test_ast_domain_security_guardrails.py#L19-L31], @[backend_v2/tests/unit/test_ast_domain_security_guardrails.py#L214-L232], and @[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2935-L2987], migrate all `from_strategy` usages to `LLMClient.from_tier(CognitiveTier.&lt;TIER&gt;, ...)` and add positive and negative AST guardrail unit tests verifying `.from_strategy(...)` and string-literal `LLMClient.from_tier("fast")` are rejected.</action>
    <constraint invariant="ast_guardrail_mandate">Static AST guardrails MUST block any reintroduction of `.from_strategy(...)` or string-literal tier arguments to `LLMClient.from_tier`.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/llm/client.py scripts/_ast_guardrails.py backend_v2/tests/unit/llm/test_llm_client_tiers.py backend_v2/tests/unit/llm/test_provider_retry_after.py backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py backend_v2/tests/unit/services/orchestrator/test_rag_preflight_chat_inflation.py backend_v2/tests/unit/test_dag_executor_prompt_blocks.py backend_v2/tests/test_fastdev_frozen.py backend_v2/tests/unit/test_ast_domain_security_guardrails.py backend_v2/tests/unit/scripts/test_ast_guardrails.py --test --ast-strict</audit_command>
  </step>

  <test_contracts>
    <test name="test_pipeline_config_default_strategy_enforces_cognitive_tier_enum" category="positive">
      <input>PIPELINE_REGISTRY["chat_parser"], PIPELINE_REGISTRY["studio_generation"], and PIPELINE_REGISTRY["interaction_hook"] inspected</input>
      <expected>All three PipelineConfig entries have default_strategy === CognitiveTier.FAST (isinstance of CognitiveTier)</expected>
    </test>
    <test name="test_pipeline_config_rejects_raw_string_default_strategy_under_strict_mode" category="negative">
      <input>PipelineConfig(description="Test", default_strategy="fast") under ConfigDict(strict=True)</input>
      <expected>Raises pydantic.ValidationError</expected>
    </test>
    <test name="test_llm_client_has_no_from_strategy_attribute" category="negative">
      <input>Inspect LLMClient.__dict__ for "from_strategy" attribute</input>
      <expected>"from_strategy" is absent from LLMClient</expected>
    </test>
    <test name="test_ast_guardrail_flags_from_strategy_call_as_fatal" category="negative">
      <input>Python source snippet calling `await LLMClient.from_strategy("fast", repository=repo)` scanned by scan_source_code_for_guardrails</input>
      <expected>Emits GuardrailSeverity.FATAL violation banning from_strategy</expected>
    </test>
    <test name="test_ast_guardrail_flags_string_literal_in_from_tier_as_fatal" category="boundary">
      <input>Python source snippet calling `await LLMClient.from_tier("fast", repository=repo)` scanned by scan_source_code_for_guardrails</input>
      <expected>Emits GuardrailSeverity.FATAL violation requiring CognitiveTier Enum member</expected>
    </test>
    <test name="test_ablation_live_executor_config_coerces_lax_cognitive_tier_pair" category="positive">
      <input>AblationLiveExecutionConfigDTO.model_validate with compare_strategies=("fast", "deep_thinking")</input>
      <expected>Validates to (CognitiveTier.FAST, CognitiveTier.DEEP_THINKING) and initializes clients via LLMClient.from_tier</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run touched-scope technical debt check: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --targets scripts/ablation_live_executor.py backend_v2/tests/fakes/in_memory_uow.py backend_v2/models/enums.py backend_v2/llm/client.py backend_v2/services/chat_parser.py backend_v2/hooks/interaction_hook.py backend_v2/hooks/linguistics.py backend_v2/hooks/source_verification_hook.py`.</action>
    <action>Run Phase 1 backend quality gate: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/enums.py backend_v2/llm/client.py backend_v2/services/chat_parser.py backend_v2/hooks/interaction_hook.py backend_v2/hooks/linguistics.py backend_v2/hooks/source_verification_hook.py scripts/ablation_live_executor.py scripts/_ast_guardrails.py backend_v2/tests/fakes/in_memory_uow.py --test --ast-strict`.</action>
  </validation_gate>
</execution_protocol>
