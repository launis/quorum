# Phase 7: AST Guardrail Hardening (Mathematical Drift Prevention)

**Phase Title:** Phase 7: AST Guardrail Hardening (Mathematical Drift Prevention)
**Objective:** Enforce `QGR001` (getattr/hasattr) and `QGR002` (.get(key, default)) at FATAL severity in `services/` and `hooks/`, introduce new rule `QGR012` (`isinstance(..., dict)` detection at FATAL severity in `services/` and `hooks/`), harden path normalization against relative path evasion, and add automated AST verification tests to make it mathematically impossible for new duck-typing or anti-patterns to enter the codebase.

**Source Reference:** @[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md#L319-L329] (Phase 7: AST Guardrail Hardening)

**Expected Target Files:**
- `[MODIFY]` @[scripts/_ast_guardrails.py]
- `[MODIFY]` @[scripts/backend_audit_loop.py]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_ast_guardrails.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 6. Verify workers and cache boundaries are strictly typed.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[scripts/_ast_guardrails.py] and @[scripts/backend_audit_loop.py].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] `QGR001`, `QGR002`, and new `QGR012` [NEW] locked at `FATAL` severity for `services/` and `hooks/` in @[scripts/_ast_guardrails.py].
    - [ ] Robust path normalization implemented to prevent relative path evasion.
    - [ ] `backend_audit_loop.py` in @[scripts/backend_audit_loop.py] unconditionally fails on FATAL violations.
    - [ ] Automated AST verification unit tests in @[backend_v2/tests/unit/scripts/test_ast_guardrails.py] verifying 0 unsuppressed violations across `backend_v2/services/` and `backend_v2/hooks/`.
    - [ ] Quality gate passes: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`.
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
    <backend>@[scripts/_ast_guardrails.py]</backend>
    <backend>@[scripts/backend_audit_loop.py]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT allow unsuppressed `FATAL` violations in `services/` or `hooks/`.
  </anti_targets>

  <step id="1" name="AST GUARDRAIL FATAL LOCKING & TEST VERIFICATION">
    <action>Update AST rules to enforce FATAL severity and add QGR012.</action>
    <action>Execute full AST test suite in `backend_v2/tests/unit/scripts/test_ast_guardrails.py`.</action>
  </step>

  <validation_gate>
    uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_ast_guardrails.py --test
    uv run python scripts/backend_audit_loop.py backend_v2/ --test
  </validation_gate>
</execution_protocol>
```
