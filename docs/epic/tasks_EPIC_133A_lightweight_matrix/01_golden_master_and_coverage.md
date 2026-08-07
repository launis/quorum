<system_prompt>
  <objective>Generate Implementation Plan for Phase 1: Golden Master & Coverage Verification</objective>
  <context>
    Epic: @[c:\src\quorum\docs\epic\EPIC_133A_lightweight_matrix.md]
  </context>
  
  <execution_protocol level="1_planner">
    <step id="1.0" name="STRATEGIC ALIGNMENT CHECK">
      <action>Verify that `lightweight_matrix.py` has not already been modified. Check current test coverage.</action>
    </step>
    <step id="1.1" name="UN-SKIP LEGACY TESTS">
      <action>Open `@[c:\src\quorum\backend_v2\tests\unit\models\dtos\test_lightweight_matrix.py]`. Find all 10 tests marked with `@pytest.mark.skip("Legacy architecture obsolete")` at lines 13, 32, 81, 187, 232, 243, 262, 328, 395, 500.</action>
      <action>Remove the `@pytest.mark.skip` decorators.</action>
      <action>Refactor these 10 tests to pass with the current architecture BEFORE any domain logic is extracted. Do NOT write new tests from scratch yet; fix the legacy ones first to lock down the current behavior.</action>
      <demolish>REMOVE: @pytest.mark.skip("Legacy architecture obsolete") from all 10 legacy tests.</demolish>
    </step>
    <step id="1.2" name="VERIFY COVERAGE">
      <action>Run `uv run pytest --cov=backend_v2.models.dtos.lightweight_matrix backend_v2/tests/ --cov-report=term-missing`.</action>
      <action>Verify line coverage is mathematically >80%. If below 80%, write additional Golden Master Characterization Tests for `lightweight_matrix.py` to freeze current behavior.</action>
    </step>
    <validation_gate>
      Run: `uv run python scripts/backend_audit_loop.py backend_v2 --test`
      Assert: All tests in `test_lightweight_matrix.py` pass and none are skipped.
    </validation_gate>
    <anti_targets>
      DO NOT modify `backend_v2/models/dtos/lightweight_matrix.py` in this phase. Strictly tests only.
    </anti_targets>
  </execution_protocol>
</system_prompt>
