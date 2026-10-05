# Phase 12: Client Permissive Map Eradication (Dart)

**Overview:** Retype census R (193 non-codec `Map<String, dynamic>` occurrences in 48 hand-written files) to Freezed DTOs mirroring backend CLOSED models, or to `Map<String, Object?>` for backend OPEN-JSON fields. Implement `DGR005` in `scripts/_dart_guardrails.py` banning non-codec `Map<String, dynamic>`; promote `DGR001`, `DGR004` (Dart lint suppressions), and `DGR005` to unconditional FATAL severity in `scripts/_dart_guardrails.py` and `scripts/flutter_audit_loop.py`; and eradicate the 25 `// ignore:` suppressions across 23 files. `ExecutionRecord.contextVariables` and `ExecutionRecord.executionTrace` mirror the already typed backend fields `context_variables: ContextVariablesDTO` and `execution_trace: list[ErrorTraceEvent | TombstoneEvent | TraceEvent]`.

**Source:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md#L617-L631] Phase 12: Client Permissive Map Eradication (Dart)

**Target Files:**
- `[MODIFY]` @[scripts/_dart_guardrails.py]
- `[MODIFY]` @[scripts/flutter_audit_loop.py]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_dart_guardrails.py]
- `[MODIFY]` @[client_app_v2/lib/features/execution/models/execution_record.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/models/execution_metadata.dart]
- `[MODIFY]` @[scripts/audit_dto_parity.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Phase 11 eradicated all loose dicts across tests, scripts, and Mapping constructs in backend_v2.</action>
    <action>Look forward: Verify Dart permissive map eradication locks client-side strictness before the final zero-bypass gate in Phase 13.</action>
    <constraint>If Census R shows remaining loose Map&lt;String, dynamic&gt; occurrences or DGR005 fails, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]) and the Tracker document (@[docs/epic/EPIC_157_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_157/12_phase12_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`.</directive>
  </step>

  <dod_checklist>
    <item>Census command R returns 0 matches across client_app_v2/lib/.</item>
    <item>DGR005 implemented in scripts/_dart_guardrails.py banning loose Map&lt;String, dynamic&gt;.</item>
    <item>DGR001, DGR004, DGR005 enforced as unconditional FATAL severity in scripts/flutter_audit_loop.py.</item>
    <item>ExecutionRecord and ExecutionMetadata models retyped with full backend parity.</item>
    <item>uv run python scripts/flutter_audit_loop.py client_app_v2/ --build passes.</item>
    <item>uv run python scripts/audit_dto_parity.py passes.</item>
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
    <anti_target>Do NOT retype codec signatures (fromJson/toJson) to Object? (retained strictly per contract).</anti_target>
    <anti_target>Do NOT introduce ad-hoc dynamic types in Flutter presentation widgets.</anti_target>
  </anti_targets>

  <validation_gate>
    <action>Execute Census R: `Get-ChildItem client_app_v2/lib -Recurse -Filter "*.dart" | Select-String -Pattern "Map<String,\s*dynamic>"` returns 0 non-codec matches.</action>
    <action>Execute Flutter Audit: `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build` passes.</action>
    <action>Execute DTO Parity: `uv run python scripts/audit_dto_parity.py` passes.</action>
  </validation_gate>
</execution_protocol>
```
