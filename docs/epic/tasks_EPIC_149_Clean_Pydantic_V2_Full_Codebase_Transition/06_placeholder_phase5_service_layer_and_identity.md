# Phase 5: Service Layer, Utility Services & Service Tests

**Phase Title:** Phase 5: Service Layer, Utility Services & Service Tests
**Objective:** Eliminate ALL `getattr(initiator, "organization_id", None)` chains (replace with direct attribute access on `ExecutionMetadata.organization_id`), `isinstance(x, dict)` branches, and `hasattr()` interface discovery from `backend_v2/services/execution.py` and all utility services, modernizing service unit tests atomically.

**Source Reference:** @[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md#L287-L306] (Phase 5: Service Layer, Utility Services & Service Tests)

**Expected Target Files:**
- `[MODIFY]` @[backend_v2/services/execution.py]
- `[MODIFY]` @[backend_v2/services/usage_service.py]
- `[MODIFY]` @[backend_v2/services/llm_task_executor.py]
- `[MODIFY]` @[backend_v2/services/translation_service.py]
- `[MODIFY]` @[backend_v2/services/source_verification_service.py]
- `[MODIFY]` @[backend_v2/services/blueprint.py]
- `[MODIFY]` @[backend_v2/services/studio/output_profile_service.py]
- `[MODIFY]` @[backend_v2/services/studio/prompt_block_service.py]
- `[MODIFY]` @[backend_v2/services/studio/workflow_service.py]
- `[MODIFY]` @[backend_v2/services/studio/system_config_service.py]
- `[MODIFY]` @[backend_v2/services/mcp/mcp_tool_loop.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_execution_service.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 4. Verify orchestrator strategies use strict DTOs.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/services/execution.py] and @[backend_v2/services/usage_service.py].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] `getattr(initiator, "organization_id", None)` replaced with direct `ExecutionMetadata.organization_id` access across all 15 instances in @[backend_v2/services/execution.py].
    - [ ] `hasattr()` interface discovery removed in @[backend_v2/services/usage_service.py] and @[backend_v2/services/llm_task_executor.py].
    - [ ] All `isinstance(..., dict)` checks eliminated from studio services.
    - [ ] Service unit tests in @[backend_v2/tests/unit/services/] modernized atomically.
    - [ ] Quality gate passes: `uv run python scripts/backend_audit_loop.py backend_v2/services/ --test`.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
    <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
    <knowledge_item>@[ki_domain_model_prompt_separation.md]</knowledge_item>
    <knowledge_item>@[ki_neuro_symbolic_agentic_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
    <knowledge_item>@[ki_app_error_boundary.md]</knowledge_item>
  </required_context_rules>

  <touched_artifacts>
    <backend>@[backend_v2/services/execution.py]</backend>
    <backend>@[backend_v2/services/usage_service.py]</backend>
    <backend>@[backend_v2/services/llm_task_executor.py]</backend>
    <backend>@[backend_v2/services/translation_service.py]</backend>
    <backend>@[backend_v2/services/source_verification_service.py]</backend>
    <backend>@[backend_v2/services/blueprint.py]</backend>
    <backend>@[backend_v2/services/studio/output_profile_service.py]</backend>
    <backend>@[backend_v2/services/studio/prompt_block_service.py]</backend>
    <backend>@[backend_v2/services/studio/workflow_service.py]</backend>
    <backend>@[backend_v2/services/studio/system_config_service.py]</backend>
    <backend>@[backend_v2/services/mcp/mcp_tool_loop.py]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT modify `backend_v2/worker.py` in Phase 5 (reserved for Phase 6).
    - Do NOT re-introduce `getattr`/`hasattr` fallback reflection.
  </anti_targets>

  <step id="1" name="SERVICE LAYER DUCK-TYPING ELIMINATION">
    <action>Refactor all service classes to eliminate getattr/hasattr and use direct typed attributes.</action>
    <action>Modernize service unit tests in `backend_v2/tests/unit/services/`.</action>
  </step>

  <validation_gate>
    uv run python scripts/backend_audit_loop.py backend_v2/services/ --test
  </validation_gate>
</execution_protocol>
```
