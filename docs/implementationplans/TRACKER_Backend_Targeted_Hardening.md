# Tracker: Targeted Backend Hardening (Workers, SDUI Adapters & Utilities)

@[docs/KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTO.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTO.md] (Askel 3.2: Vaihe 2b-3)

- [ ] **[NOK] Execution:** `uv run python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_Backend_Targeted_Hardening.md --gate backend --model gemini-4-argon-medium --continue-on-failure`

### Post-Implementation Gates

- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening.md]" --gate backend --model gemini-4-argon-medium --continue-on-failure`
  - [x] @[backend_v2/workers/execution_worker.py]
  - [x] @[backend_v2/workers/report_worker.py]
  - [x] @[backend_v2/workers/synthesis_reducers.py]
  - [x] @[backend_v2/workers/synthesis_tasks.py]
  - [x] @[backend_v2/workers/synthesis_worker.py]
  - [x] @[backend_v2/workers/variance_synthesis.py]
  - [x] @[backend_v2/services/sdui/sdui_mapper_service.py]
  - [x] @[backend_v2/services/sdui/adapters/base_adapter.py]
  - [ ] @[backend_v2/services/sdui/adapters/causal_graph_adapter.py]
  - [ ] @[backend_v2/services/sdui/adapters/executive_summary_adapter.py]
  - [ ] @[backend_v2/services/sdui/adapters/global_score_adapter.py]
  - [ ] @[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py]
  - [ ] @[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]
  - [ ] @[backend_v2/services/sdui/adapters/mcp_audit_adapter.py]
  - [ ] @[backend_v2/services/sdui/adapters/metadata_adapter.py]
  - [ ] @[backend_v2/services/sdui/adapters/penalties_adapter.py]
  - [ ] @[backend_v2/services/sdui/adapters/printable_sources_adapter.py]
  - [ ] @[backend_v2/services/sdui/adapters/synthesis_text_adapter.py]
  - [ ] @[backend_v2/services/sdui/adapters/variance_adapter.py]
  - [ ] @[backend_v2/services/sdui/adapters/warning_card_adapter.py]
  - [ ] @[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]
  - [ ] @[backend_v2/utils/math_utils.py]
  - [ ] @[backend_v2/utils/alias_engine.py]
  - [ ] @[backend_v2/utils/normalization.py]
  - [ ] @[backend_v2/utils/paths.py]
  - [ ] @[backend_v2/utils/pydantic_utils.py]
  - [ ] @[backend_v2/utils/ranked_round_robin.py]
  - [ ] @[backend_v2/utils/redis_patcher.py]
  - [ ] @[backend_v2/utils/static_charts.py]
  - [ ] @[backend_v2/utils/finops_trace_analyzer.py]
  - [ ] @[backend_v2/services/translation_service.py]
  - [ ] @[backend_v2/llm/caching_service.py]
  - [ ] @[backend_v2/services/llm_task_executor.py]
  - [ ] @[backend_v2/services/chat_normalizer.py]
  - [ ] @[backend_v2/services/sdui/sanitizers/mcp_presentation_sanitizer.py]
  - [ ] @[backend_v2/services/orchestrator/localization_compiler.py]

- [ ] **[SKIPPED] Tier 2 Hardening (Frontend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening.md]" --gate frontend --model gemini-4-argon-medium` (Zero frontend targets in backend targeted hardening).
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Final Verification Quality Gate
- [ ] **[NOK]** Universal Backend Quality Gate:
  ```powershell
  uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict
  ```
