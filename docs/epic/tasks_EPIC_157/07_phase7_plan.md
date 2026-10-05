# Phase 7: Mock-Emulation Sunset & QGR014 FATAL Hardening

**Overview:** Delete `DynamicRepoMethod` and `InMemoryBlueprintTransformerRepository`, replace `inject_fault` reflection with a positive registry, and land the hardened `QGR014` detections (a)-(g) at FATAL severity.

**Source:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md#L524-L542] Phase 7: Mock-Emulation Sunset & QGR014 FATAL Hardening

**Target Files:**
- `[MODIFY]` @[backend_v2/tests/fakes/in_memory_repositories.py#L128-L133]
- `[MODIFY]` @[backend_v2/tests/fakes/in_memory_repositories.py#L1747-L1835]
- `[MODIFY]` @[backend_v2/tests/fakes/in_memory_repositories.py#L1838-L1889]
- `[MODIFY]` @[backend_v2/tests/fakes/__init__.py]
- `[MODIFY]` @[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]
- `[MODIFY]` @[scripts/_ast_guardrails.py#L417-L831]
- `[MODIFY]` @[scripts/_ast_guardrails.py#L1133-L1137]
- `[MODIFY]` @[scripts/_ast_guardrails.py#L1319-L1360]
- `[MODIFY]` @[scripts/_ast_guardrails.py]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_ast_guardrails.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Phase 6 achieved Census A = 0, Census I = 0, Census D = 0, Census F = 0 across the entire codebase.</action>
    <action>Look forward: Verify that deleting DynamicRepoMethod and InMemoryBlueprintTransformerRepository and hardening QGR014 at FATAL severity permanently locks the test suite against persistence mocks.</action>
    <constraint>If any remaining import of InMemoryBlueprintTransformerRepository exists, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]) and the Tracker document (@[docs/epic/EPIC_157_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_157/07_phase7_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`.</directive>
  </step>

  <dod_checklist>
    <item>Select-String for DynamicRepoMethod, InMemoryBlueprintTransformerRepository, dict_to_obj returns 0 matches across backend_v2.</item>
    <item>Hardened QGR014 with detections (a)-(g) enforced at FATAL severity.</item>
    <item>uv run python scripts/_ast_guardrails.py backend_v2/tests/ --strict reports 0 violations.</item>
    <item>uv run python scripts/audit_dict_eradication.py backend_v2 --strict reports TOTAL VIOLATIONS: 0.</item>
    <item>Universal audit loop uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict passes.</item>
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
    <anti_target>Do NOT delete non-persistence service mocks governed by partial_mocking_srp_ban during Phase 7.</anti_target>
  </anti_targets>

  <validation_gate>
    <action>Execute Symbol Scan: `Select-String -Path backend_v2 -Pattern "DynamicRepoMethod|InMemoryBlueprintTransformerRepository|dict_to_obj" -Recurse` returns 0 matches.</action>
    <action>Execute AST Guardrails on tests: `uv run python scripts/_ast_guardrails.py backend_v2/tests/ --strict`.</action>
    <action>Execute Dict Audit: `uv run python scripts/audit_dict_eradication.py backend_v2 --strict` reports TOTAL VIOLATIONS: 0.</action>
    <action>Execute Backend Audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`.</action>
  </validation_gate>
</execution_protocol>
```
