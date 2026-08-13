# EPIC 142: Phase 4 - Atomic Test Alignment (Test Expansion)

## Objective
Align test data fixtures and assertions across unit tests, E2E tests, and seed data to correctly use `ExecutionStatus` instead of raw booleans/strings, and to assert accurately calculated matrix scores instead of assuming 100% pass rates.

## Scope
**Target Files:**
- `@[backend_v2/tests/unit/services/test_matrix_domain_parser.py]`
- `@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py]`
- `@[backend_v2/tests/unit/test_epic93_contract_verification.py]`
- `@[backend_v2/tests/unit/hooks/test_scoring.py]`
- `@[backend_v2/tests/unit/services/orchestrator/test_context_router.py]`
- `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py]`
- `@[backend_v2/tests/unit/services/test_blueprint.py]`
- `@[backend_v2/seed/seed_data.json]`
- `@[client_app_v2/test/]`

### [MODIFY] backend_v2/tests/unit/test_epic93_contract_verification.py
Update `evaluated_atoms` boolean assertions to `ExecutionStatus`.

### [MODIFY] backend_v2/tests/unit/hooks/test_scoring.py
Update `evaluated_atoms` boolean assertions to `ExecutionStatus`.

### [MODIFY] backend_v2/tests/unit/services/orchestrator/test_context_router.py
Update `evaluated_atoms` boolean assertions to `ExecutionStatus`.

### [MODIFY] backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py
Update `evaluated_atoms` boolean assertions to `ExecutionStatus`.

### [MODIFY] backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py
Update `evaluated_atoms` boolean assertions to `ExecutionStatus`.

### [MODIFY] backend_v2/tests/unit/services/test_blueprint.py
Update `evaluated_atoms` boolean assertions to `ExecutionStatus`.

### [MODIFY] backend_v2/tests/unit/services/test_matrix_domain_parser.py
Assert matrix scores drop appropriately for failed atoms.

### [MODIFY] backend_v2/seed/seed_data.json
Update seed data matrix scores to align with backend changes.

### [MODIFY] client_app_v2/test/
Fix SDUI Parity Tests to match updated math logic.

```xml
<execution_protocol level="2_execute">
  <step id="1" name="Unit Test Assertion and Fixture Migration">
    <action>Modify the unit tests listed in scope to replace all boolean `True`/`False` and `"PASS"`/`"FAIL"` assignments in `evaluated_atoms` with `ExecutionStatus.PASSED` / `ExecutionStatus.FAILED`.</action>
    <action>Update mathematical assertions where tests previously assumed a 100% score (or raw_score of 1.0 / 5.0) for matrices that contain failed atoms, replacing them with the correct percentage based on `ExecutionStatus.PASSED` / `total_valid_atoms`.</action>
    <constraint invariant="zero_legacy_fallback_hacks">Models must remain mathematically pure. If legacy test data crashes validation, it must be fixed at the source.</constraint>
    <constraint invariant="anti_happy_path_compliance">Every implementation plan MUST include explicit test scenarios with concrete inputs and expected outputs for BOTH success AND failure paths.</constraint>
  </step>

  <step id="2" name="Seed Data and E2E Integration Alignment">
    <action>Use `grep_search` and `view_file` with precise `StartLine` and `EndLine` constraints on `seed_data.json` to identify and update statically defined mock `raw_score` and `evaluated_atoms` to align with the new scoring logic.</action>
    <constraint invariant="context_amnesia_prevention">You MUST use scoped line boundaries (`#Lnn-mm` syntax) when dealing with massive files, specifically: `seed_data.json`.</constraint>
  </step>

  <step id="3" name="Frontend SDUI Parity Test Alignment">
    <action>Search through `client_app_v2/test/` for JSON fixtures corresponding to backend updates. Ensure the expected `raw_score` in the mock objects matches the new values from backend test data.</action>
    <action>Run the flutter test suite and fix any failing parity assertions.</action>
    <constraint invariant="sdui_contract_fracture_prevention">The Backend and Frontend models are mathematically coupled via Server-Driven UI (SDUI).</constraint>
  </step>

  <step id="4" name="Global Audit and Verification">
    <action>Run `uv run python scripts/backend_audit_loop.py backend_v2 --test` to verify backend tests pass and formatting is correct.</action>
    <action>Run `uv run python scripts/flutter_audit_loop.py client_app_v2/test --build` to ensure frontend tests pass.</action>
    <action>Run the Final E2E REST API Verification Gate: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`.</action>
    <constraint invariant="quality_gate_execution">Enforce automated audit testing after completing a cohesive logical step.</constraint>
  </step>
</execution_protocol>
```
