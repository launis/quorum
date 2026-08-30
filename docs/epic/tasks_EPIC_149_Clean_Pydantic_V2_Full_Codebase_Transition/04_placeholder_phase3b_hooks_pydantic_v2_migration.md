# Phase 3B: Full Hooks Pydantic V2 Migration & Hook Tests (PRODUCERS FIRST)

**Phase Title:** Phase 3B: Full Hooks Pydantic V2 Migration & Hook Tests (PRODUCERS FIRST)
**Objective:** Eliminate ALL `isinstance(..., dict)`, `.get()`, and `getattr()` from all 11 hook files and the 4 decomposed scoring modules, transitioning `HookState` to typed `ExecutionInputsDTO` and `GlobalContextVarsDTO`, returning typed `HookDeltaDTO | None` from `HookResult.state_delta`, and modernizing hook tests across all 4 ISTQB partitions.

**Source Reference:** @[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md#L234-L258] (Phase 3: Sub-Phase 3B: Full Hooks Pydantic V2 Migration & Hook Tests)

**Expected Target Files:**
- `[MODIFY]` @[backend_v2/hooks/scoring/falsifier_hook.py]
- `[MODIFY]` @[backend_v2/hooks/scoring/passivity_hook.py]
- `[MODIFY]` @[backend_v2/hooks/scoring/matrix_hook.py]
- `[MODIFY]` @[backend_v2/hooks/scoring/normalization_hook.py]
- `[MODIFY]` @[backend_v2/hooks/validation.py]
- `[MODIFY]` @[backend_v2/hooks/source_verification_hook.py]
- `[MODIFY]` @[backend_v2/hooks/atom_flattening.py]
- `[MODIFY]` @[backend_v2/hooks/input_processing.py]
- `[MODIFY]` @[backend_v2/hooks/integrity.py]
- `[MODIFY]` @[backend_v2/hooks/linguistics.py]
- `[MODIFY]` @[backend_v2/hooks/llm.py]
- `[MODIFY]` @[backend_v2/hooks/context_mapper.py]
- `[MODIFY]` @[backend_v2/hooks/archival.py]
- `[MODIFY]` @[backend_v2/hooks/security.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_scoring.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_validation.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Sub-Phase 3A. Verify scoring package is cleanly decomposed.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/hooks/validation.py], @[backend_v2/hooks/source_verification_hook.py], and all hook modules.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] `HookState.inputs: dict[str, Any]` replaced with typed `ExecutionInputsDTO`.
    - [ ] `HookState.global_context_vars: dict[str, Any]` replaced with typed `GlobalContextVarsDTO`.
    - [ ] `HookResult.state_delta: dict[str, Any] | None` replaced with typed `HookDeltaDTO | None`.
    - [ ] All `isinstance(..., dict)`, `.get()`, and `getattr()` removed from all 11 hook files and 4 scoring modules.
    - [ ] All hook unit tests in @[backend_v2/tests/unit/hooks/] modernized atomically to cover 4 ISTQB partitions.
    - [ ] Quality gate passes: `uv run python scripts/backend_audit_loop.py backend_v2/hooks/ --test`.
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
    <backend>@[backend_v2/hooks/scoring/falsifier_hook.py]</backend>
    <backend>@[backend_v2/hooks/scoring/passivity_hook.py]</backend>
    <backend>@[backend_v2/hooks/scoring/matrix_hook.py]</backend>
    <backend>@[backend_v2/hooks/scoring/normalization_hook.py]</backend>
    <backend>@[backend_v2/hooks/validation.py]</backend>
    <backend>@[backend_v2/hooks/source_verification_hook.py]</backend>
    <backend>@[backend_v2/hooks/atom_flattening.py]</backend>
    <backend>@[backend_v2/hooks/input_processing.py]</backend>
    <backend>@[backend_v2/hooks/integrity.py]</backend>
    <backend>@[backend_v2/hooks/linguistics.py]</backend>
    <backend>@[backend_v2/hooks/llm.py]</backend>
    <backend>@[backend_v2/hooks/context_mapper.py]</backend>
    <backend>@[backend_v2/hooks/archival.py]</backend>
    <backend>@[backend_v2/hooks/security.py]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT modify `backend_v2/services/orchestrator/` in Phase 3B (strictly reserved for Phase 4).
    - Do NOT re-introduce raw dict returns in `HookResult.state_delta`.
  </anti_targets>

  <step id="1" name="FULL HOOKS PYDANTIC V2 MIGRATION">
    <action>Refactor all hooks to accept typed HookState and return HookDeltaDTO.</action>
    <action>Modernize hook unit tests in `backend_v2/tests/unit/hooks/`.</action>
  </step>

  <validation_gate>
    uv run python scripts/backend_audit_loop.py backend_v2/hooks/ --test
  </validation_gate>
</execution_protocol>
```
