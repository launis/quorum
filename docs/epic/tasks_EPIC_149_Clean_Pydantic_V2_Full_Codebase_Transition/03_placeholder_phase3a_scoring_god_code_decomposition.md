# Phase 3A: scoring.py God Code Decomposition (Strangler Fig Proxy Pattern)

**Phase Title:** Phase 3A: scoring.py God Code Decomposition (Strangler Fig Proxy Pattern)
**Objective:** Decompose the monolithic 1,347 LOC (64.3 KB) `scoring.py` file into a modular `backend_v2/hooks/scoring/` package with 4 isolated modules (<400 LOC each: `falsifier_hook.py`, `passivity_hook.py`, `matrix_hook.py`, `normalization_hook.py`), a temporary models module `models.py`, and a Strangler Fig facade in `__init__.py` re-exporting all legacy symbols per PEP 484 and `ki_god_code_prevention.md` to preserve 100% of existing behavior and test pass rates.

**Source Reference:** @[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md#L215-L233] (Phase 3: Sub-Phase 3A: scoring.py God Code Decomposition)

**Expected Target Files:**
- `[MODIFY]` @[backend_v2/hooks/scoring.py]
- `[NEW]` @[backend_v2/hooks/scoring/__init__.py]
- `[NEW]` @[backend_v2/hooks/scoring/falsifier_hook.py]
- `[NEW]` @[backend_v2/hooks/scoring/passivity_hook.py]
- `[NEW]` @[backend_v2/hooks/scoring/matrix_hook.py]
- `[NEW]` @[backend_v2/hooks/scoring/normalization_hook.py]
- `[NEW]` @[backend_v2/hooks/scoring/models.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_scoring.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 2. Verify all repositories return typed Pydantic models.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/hooks/scoring.py] and @[backend_v2/tests/unit/hooks/test_scoring.py].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] `scoring.py` decomposed into `backend_v2/hooks/scoring/` package with all modules <400 LOC:
      - `falsifier_hook.py` (<200 LOC): `apply_scoring_logic` hook.
      - `passivity_hook.py` (<200 LOC): `enforce_passivity_penalty` hook.
      - `matrix_hook.py` (<450 LOC): `matrix_scoring_hook` + quote evidence validation.
      - `normalization_hook.py` (<350 LOC): `normalize_matrix_scores` + `recalculate`.
      - `__init__.py`: Strangler Fig facade re-exporting `apply_scoring_logic`, `enforce_passivity_penalty`, `matrix_scoring_hook`, `normalize_matrix_scores`, and `recalculate` with explicit `__all__` and redundant import aliases per PEP 484.
    - [ ] `scoring/models.py` created with Strangler Fig temporary DTOs for structural decomposition.
    - [ ] Unit tests pass: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/hooks/test_scoring.py --test` with zero behavioral regressions.
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
    <backend>@[backend_v2/hooks/scoring.py]</backend>
    <backend>@[backend_v2/hooks/scoring/__init__.py]</backend>
    <backend>@[backend_v2/hooks/scoring/falsifier_hook.py]</backend>
    <backend>@[backend_v2/hooks/scoring/passivity_hook.py]</backend>
    <backend>@[backend_v2/hooks/scoring/matrix_hook.py]</backend>
    <backend>@[backend_v2/hooks/scoring/normalization_hook.py]</backend>
    <backend>@[backend_v2/hooks/scoring/models.py]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT migrate HookState to Pydantic V2 in Sub-Phase 3A (strictly reserved for Sub-Phase 3B).
    - Do NOT modify `backend_v2/services/orchestrator/` in Sub-Phase 3A (reserved for Phase 4).
  </anti_targets>

  <step id="1" name="GOD CODE DECOMPOSITION OF SCORING.PY">
    <action>Decompose @[backend_v2/hooks/scoring.py] into `backend_v2/hooks/scoring/` package modules per `ki_god_code_prevention.md`.</action>
    <action>Create @[backend_v2/hooks/scoring/__init__.py] re-exporting all symbols with `__all__` and redundant aliases.</action>
    <action>Verify zero regression in @[backend_v2/tests/unit/hooks/test_scoring.py].</action>
  </step>

  <validation_gate>
    uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/hooks/test_scoring.py --test
  </validation_gate>
</execution_protocol>
```
