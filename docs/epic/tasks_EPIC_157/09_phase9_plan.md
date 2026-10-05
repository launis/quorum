# Phase 9: Suppression & Cast Eradication (# noqa, cast(Any, ...))

**Overview:** Delete the `[REASON: ...]` authorization so that every `# noqa` comment token is a FATAL violation; delete the AST inline suppressor (`CommentSuppressor`) from `scripts/_ast_guardrails.py`, `scripts/backend_audit_loop.py#L282-L477`, and `scripts/audit_warning_baseline.py`; add `cast(Any, ...)` detection to the call audit; and eradicate census N (76 comment tokens in 30 files) and the residual census X (11 calls in 5 files). Third-party attribute reads in `backend_v2/llm/provider.py` and `backend_v2/llm/adapters/base_adapter.py` move to Pydantic V2 adapter DTOs validated with `model_validate(obj, from_attributes=True)`.

**Source:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md#L557-L582] Phase 9: Suppression & Cast Eradication (# noqa, cast(Any, ...))

**Target Files:**
- `[MODIFY]` @[scripts/audit_dict_eradication.py]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]
- `[MODIFY]` @[scripts/_ast_guardrails.py#L205-L322]
- `[MODIFY]` @[scripts/backend_audit_loop.py#L282-L477]
- `[MODIFY]` @[scripts/audit_warning_baseline.py]
- `[MODIFY]` @[backend_v2/llm/provider.py]
- `[MODIFY]` @[backend_v2/llm/adapters/base_adapter.py]
- `[MODIFY]` @[backend_v2/database/firestore_driver.py]
- `[MODIFY]` @[backend_v2/database/tinydb_driver.py]
- `[MODIFY]` @[backend_v2/logging_config.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py]
- `[MODIFY]` @[backend_v2/tests/fakes/in_memory_repositories.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm.py]
- `[MODIFY]` @[backend_v2/tests/integration/test_caching_integration.py]
- `[MODIFY]` @[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py]
- `[MODIFY]` @[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_context_mapper.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Phase 8 successfully integrated Stage 10 dict eradication in backend_audit_loop.py and synchronized Flutter Studio models.</action>
    <action>Look forward: Verify eradicating CommentSuppressor and # noqa tokens sets up clean # type: ignore eradication in Phase 10.</action>
    <constraint>If Census N or X shows unresolved suppressions or casts, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]) and the Tracker document (@[docs/epic/EPIC_157_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_157/09_phase9_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`.</directive>
  </step>

  <demolish>
    `CommentSuppressor`
  </demolish>

  <dod_checklist>
    <item>Census commands N and X return 0 matches.</item>
    <item>CommentSuppressor and inline # noqa: QGRxxx [REASON: ...] parser removed from scripts/_ast_guardrails.py#L205-L322.</item>
    <item>audit_dict_eradication.py detects every # noqa token and cast(Any, ...) call at FATAL severity.</item>
    <item>uv run python scripts/audit_dict_eradication.py backend_v2 --strict reports TOTAL VIOLATIONS: 0.</item>
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
    <anti_target>Do NOT eradicate # type: ignore comments during Phase 9 (quarantined strictly for Phase 10).</anti_target>
    <anti_target>Do NOT expand dict eradication to test files during Phase 9 (quarantined strictly for Phase 11).</anti_target>
  </anti_targets>

  <validation_gate>
    <action>Execute Census N and X: `uv run python scripts/audit_dict_eradication.py backend_v2 --strict` reports TOTAL VIOLATIONS: 0.</action>
    <action>Execute Global Backend Audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict` passes with all stages clean.</action>
  </validation_gate>
</execution_protocol>
```
