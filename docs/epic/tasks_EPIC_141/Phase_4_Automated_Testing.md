# Phase 4: Automated Testing Strategy

**Overview:** Provide robust regression test coverage for the newly decomposed architecture, strictly adhering to the `ai_testing_standards` (ISTQB guidelines).
**Target Files:** @[backend_v2/tests/unit/test_synthesis_payload_compression.py], @[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py], @[backend_v2/tests/unit/test_dag_taskgroup.py], @[backend_v2/tests/unit/test_bug_synthesis_hook.py], @[backend_v2/tests/unit/test_epic93_contract_verification.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by the previous phase. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <dod_checklist>
    <!-- Planner MUST inject parsed Epic Definition of Done items here -->
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents\rules\00-antigravity-core.md]</rule>
    <rule>@[.agents\rules\01-python-backend.md]</rule>
  </required_context_rules>

  <anti_targets>
    <!-- Planner MUST list strictly forbidden files/methods here -->
  </anti_targets>

  <step id="1" name="Implementation">
    <action>[NEW] @[backend_v2/tests/unit/test_synthesis_payload_compression.py]: Test cases for `SynthesisPayloadCompressor`: Validating deep copy integrity, ensuring heavy metadata keys are stripped, validating application of `settings.max_synthesis_evaluations`.</action>
    <action>[NEW] @[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py]: Test cases for `MatrixSensorPromptBuilder`: Validating CDATA encapsulation around user-provided strings, verifying separation of static vs dynamic messages for caching.</action>
    <action>[MODIFY] @[backend_v2/tests/unit/test_dag_taskgroup.py]: Update references to remove `sp_7a8b9c0d1e2f3a4b` and validate dynamic `model_strategy == "synthesis"` routing.</action>
    <action>[MODIFY] @[backend_v2/tests/unit/test_bug_synthesis_hook.py]: Verify that `synthesis_distiller.py` functions correctly with the newly abstracted `SynthesisPayloadCompressor`.</action>
    <action>[MODIFY] @[backend_v2/tests/unit/test_epic93_contract_verification.py]: Add structural assertions to ensure the new `extractive_sensor_service.py` adheres to the architectural contract.</action>
  </step>

  <validation_gate>
    <!-- Planner MUST inject specific grep_search and pytest verification commands here -->
  </validation_gate>
</execution_protocol>
```
