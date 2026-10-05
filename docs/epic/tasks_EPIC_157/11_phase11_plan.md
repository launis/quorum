# Phase 11: Extended Dict Eradication (Tests, scripts/, Mapping)

**Overview:** Close the dict-audit blind spots: `_is_naked_dict_subscript` matches `dict`, `Dict`, `Mapping`, and `MutableMapping` with `Any` / `object` values; fix `_is_test_file` in `scripts/_ast_guardrails.py` and `is_test` in `scripts/audit_dict_eradication.py` to use path check `backend_v2/tests/` (so `test_settings.py` is scanned as production); annotation checks run in test files; Stage 10 runs `audit_dict_eradication.py backend_v2 scripts --strict`. Eradicate census P (390 lines: tests 304 in 80 files, `scripts/` 86 in 9 files) and census M (10 production sites in 6 files).

**Source:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md#L597-L616] Phase 11: Extended Dict Eradication (Tests, scripts/, Mapping)

**Target Files:**
- `[MODIFY]` @[scripts/audit_dict_eradication.py]
- `[MODIFY]` @[scripts/_ast_guardrails.py]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]
- `[MODIFY]` @[scripts/backend_audit_loop.py#L282-L477]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_backend_audit_loop.py]
- `[MODIFY]` @[backend_v2/core/test_settings.py]
- `[MODIFY]` @[backend_v2/hooks/input_processing.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py]
- `[MODIFY]` @[backend_v2/services/ingress/pdf_chat_extractor.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Phase 10 eradicated # type: ignore comments and enforced strict mypy ignore accounting.</action>
    <action>Look forward: Verify extended dict eradication across tests, scripts, and Mapping constructs prepares for client-side Dart permissive map eradication in Phase 12.</action>
    <constraint>If Census P or M returns non-zero violations under strict scanning, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]) and the Tracker document (@[docs/epic/EPIC_157_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_157/11_phase11_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`.</directive>
  </step>

  <dod_checklist>
    <item>Census commands P and M return 0 matches.</item>
    <item>_is_test_file uses backend_v2/tests/ path check ensuring core/test_settings.py is scanned as production.</item>
    <item>Stage 10 in backend_audit_loop.py#L282-L477 executes audit_dict_eradication.py over backend_v2 and scripts.</item>
    <item>uv run python scripts/audit_dict_eradication.py backend_v2 scripts --strict reports TOTAL VIOLATIONS: 0.</item>
    <item>uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict passes.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_opentelemetry_logfire_observability.md]</knowledge_item>
    <knowledge_item>@[ki_shared_storage_driver_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Do NOT modify Dart files during Phase 11 (quarantined strictly for Phase 12).</anti_target>
    <anti_target>Do NOT reintroduce legacy mock persistence fixtures in tests (banned by QGR014).</anti_target>
  </anti_targets>

  <validation_gate>
    <action>Execute Extended Dict Audit: `uv run python scripts/audit_dict_eradication.py backend_v2 scripts --strict` reports TOTAL VIOLATIONS: 0.</action>
    <action>Execute Global Backend Audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict` passes with all stages clean.</action>
  </validation_gate>
</execution_protocol>
```
