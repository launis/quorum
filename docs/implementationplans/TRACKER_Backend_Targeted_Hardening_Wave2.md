# Tracker: Targeted Backend Hardening Wave 2 (Core, Hooks, LLM Adapters & Services)

@[docs/KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTO.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTO.md] (Askel 3.2: Vaihe 2c - Wave 2)

- [ ] **[NOK] Execution:** `uv run python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave2.md --gate backend --model gemini-4-argon-medium --continue-on-failure`

### Post-Implementation Gates

- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave2.md]" --gate backend --model gemini-4-argon-medium --continue-on-failure`
  - [x] @[backend_v2/context.py]
  - [x] @[backend_v2/core/rate_limit.py]
  - [x] @[backend_v2/core/template_processor.py]
  - [x] @[backend_v2/core/telemetry.py]
  - [x] @[backend_v2/utils/linguistics/stemmer.py]
  - [x] @[backend_v2/services/pii_analyzer.py]
  - [x] @[backend_v2/services/usage_service.py]
  - [x] @[backend_v2/services/progress.py]
  - [x] @[backend_v2/utils/scoring/base_engine.py]
  - [x] @[backend_v2/hooks/hydration.py]
  - [x] @[backend_v2/hooks/metadata.py]
  - [x] @[backend_v2/hooks/dlq_guard.py]
  - [x] @[backend_v2/hooks/context_mapper.py]
  - [x] @[backend_v2/hooks/references.py]
  - [x] @[backend_v2/hooks/interaction_hook.py]
  - [ ] @[backend_v2/hooks/archival.py]
  - [ ] @[backend_v2/hooks/metrics.py]
  - [ ] @[backend_v2/hooks/input_processing.py]
  - [ ] @[backend_v2/llm/directives.py]
  - [ ] @[backend_v2/llm/prompt_builder.py]
  - [ ] @[backend_v2/llm/adapters/deepseek_adapter.py]
  - [ ] @[backend_v2/llm/adapters/mock_adapter.py]
  - [ ] @[backend_v2/llm/adapters/adapter_factory.py]
  - [ ] @[backend_v2/llm/adapters/anthropic_adapter.py]
  - [ ] @[backend_v2/llm/adapters/openai_adapter.py]
  - [ ] @[backend_v2/llm/adapters/ai_studio_adapter.py]
  - [ ] @[backend_v2/services/web_fetcher.py]
  - [ ] @[backend_v2/services/ingress/multi_channel_ingress_service.py]
  - [ ] @[backend_v2/services/source_verification_service.py]
  - [ ] @[backend_v2/services/factories/output_profile_factory.py]
  - [ ] @[backend_v2/services/studio/auth_validator.py]
  - [ ] @[backend_v2/services/studio/prompt_block_service.py]
  - [ ] @[backend_v2/services/studio/output_profile_service.py]
  - [ ] @[backend_v2/services/execution/context_service.py]
  - [ ] @[backend_v2/services/execution/resumption_service.py]
  - [ ] @[backend_v2/services/execution/override_service.py]

- [ ] **[SKIPPED] Tier 2 Hardening (Frontend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave2.md]" --gate frontend --model gemini-4-argon-medium` (Zero frontend targets in backend targeted hardening).
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Final Verification Quality Gate
- [ ] **[NOK]** Universal Backend Quality Gate:
  ```powershell
  uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict
  ```

