# Phase 10: # type: ignore Eradication & Strict mypy Ignore Accounting

**Overview:** Eradicate census T (409 `# type: ignore` comments in 155 files); delete `[[tool.mypy.overrides]]` for `firestore_driver` and `factory` in `pyproject.toml#L131-L136` so `warn_unused_ignores = true` applies globally; remove the 5 dead entries in `per-file-ignores` in `pyproject.toml#L98-L101`; replace the 20 `[prop-decorator]` suppressions with ONE `disable_error_code = ["prop-decorator"]` entry; extend the comment audit of `scripts/audit_dict_eradication.py` to reject `# type: ignore` at FATAL severity; and add the Config Suppression Ratchet in `scripts/audit_dict_eradication.py` to verify frozen approved sets in `pyproject.toml` and `analysis_options.yaml` via `tomllib`. Batch 10.1 covers 25 production files and 3 `scripts/` files (71 comments); Batch 10.2 covers 127 test files (338 comments).

**Source:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md#L583-L596] Phase 10: # type: ignore Eradication & Strict mypy Ignore Accounting

**Target Files:**
- `[MODIFY]` @[pyproject.toml#L98-L101]
- `[MODIFY]` @[pyproject.toml#L131-L136]
- `[MODIFY]` @[scripts/audit_dict_eradication.py]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]
- `[MODIFY]` @[backend_v2/settings.py]
- `[MODIFY]` @[backend_v2/models/domain/overseer.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Phase 9 eradicated CommentSuppressor, # noqa tokens, and cast(Any, ...) calls.</action>
    <action>Look forward: Verify eradicating # type: ignore comments and locking mypy globally prepares for Phase 11 extended dict eradication across test files.</action>
    <constraint>If Census T returns non-zero unapproved comments or mypy fails under warn_unused_ignores = true, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]) and the Tracker document (@[docs/epic/EPIC_157_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_157/10_phase10_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`.</directive>
  </step>

  <dod_checklist>
    <item>Census command T returns 0 matches over backend_v2 and scripts.</item>
    <item>[[tool.mypy.overrides]] deleted from pyproject.toml#L131-L136 with warn_unused_ignores = true global.</item>
    <item>Dead entries in per-file-ignores removed from pyproject.toml#L98-L101.</item>
    <item>disable_error_code = ["prop-decorator"] configured for backend_v2/settings.py and overseer.py.</item>
    <item>Config Suppression Ratchet in audit_dict_eradication.py verifies frozen approved sets.</item>
    <item>uv run mypy backend_v2 reports 0 errors.</item>
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
    <anti_target>Do NOT retype test files or scripts for dict eradication in Phase 10 (quarantined strictly for Phase 11).</anti_target>
    <anti_target>Do NOT modify Dart files during Phase 10 (quarantined strictly for Phase 12).</anti_target>
  </anti_targets>

  <validation_gate>
    <action>Execute Census T: `uv run python scripts/audit_dict_eradication.py backend_v2 --strict` reports TOTAL VIOLATIONS: 0.</action>
    <action>Execute Strict Mypy: `uv run mypy backend_v2` reports 0 errors.</action>
    <action>Execute Global Backend Audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict` passes with all stages clean.</action>
  </validation_gate>
</execution_protocol>
```
