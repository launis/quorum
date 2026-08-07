# Phase 1: Golden Master & Coverage Verification

**Overview:** Verify test coverage is above 80% and catalog import consumers before beginning God Code decomposition.
**Target Files:** 
- `@[c:\src\quorum\backend_v2\models\dtos\lightweight_matrix.py]`
- `@[c:\src\quorum\backend_v2\tests\]`

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by the previous phase. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <dod_checklist>
    - All unit tests pass, and coverage remains above 90%.
  </dod_checklist>

  <required_context_rules>
    - @[c:\src\quorum\.agents\rules\00-antigravity-core.md]
    - @[c:\src\quorum\.agents\rules\01-python-backend.md]
    - @[c:\src\quorum\.agents\rules\04_directory_reference.md]
    - @[c:\Users\risto\.gemini\antigravity-ide\knowledge\god_code_prevention\artifacts\ki_god_code_prevention.md]
  </required_context_rules>

  <anti_targets>
    - Do NOT extract or move any DTOs in this phase.
    - Do NOT modify any business logic.
  </anti_targets>

  <step id="1" name="VERIFY COVERAGE">
    <action>Run `uv run pytest --cov=backend_v2.models.dtos.lightweight_matrix backend_v2/tests/ --cov-report=term-missing` to verify current test coverage of the target file.</action>
    <action>If coverage is below 80%, you MUST write Golden Master tests capturing the exact current output BEFORE proceeding.</action>
  </step>

  <step id="2" name="CATALOG IMPORT CONSUMERS">
    <action>Catalog all 23+ import consumers discovered via workspace grep. The complete import consumer list is defined in Epic Phase 1, Step 1.2.</action>
  </step>

  <validation_gate>
    - Run: `uv run pytest --cov=backend_v2.models.dtos.lightweight_matrix backend_v2/tests/ --cov-report=term-missing`
    - Assert that coverage is above 80% before declaring this phase complete.
  </validation_gate>
</execution_protocol>
```
