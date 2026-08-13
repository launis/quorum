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
    <action>[NEW] @[backend_v2/tests/unit/test_synthesis_payload_compression.py]: Test cases for `SynthesisPayloadCompressor`. MUST include positive tests for deep copy integrity and metadata stripping, AND at least two negative tests (e.g. handling missing keys, malformed dictionaries) to satisfy `anti_happy_path_mandate`. MUST use `polyfactory` for mock data.</action>
    <action>[NEW] @[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py]: Test cases for `MatrixSensorPromptBuilder`. MUST include positive tests for CDATA encapsulation and message segregation, AND at least two negative tests (e.g. empty strings, null inputs) to satisfy `anti_happy_path_mandate`. MUST use `polyfactory` for mock data.</action>
    <action>[MODIFY] @[backend_v2/tests/unit/test_dag_taskgroup.py]: Add a specific new test case to validate the dynamic `model_strategy == "synthesis"` routing logic injected into `dag_executor.py` during Phase 1. Do NOT attempt to remove non-existent `sp_7a8b9c0d1e2f3a4b` references.</action>
    <action>[NEW] @[backend_v2/tests/unit/test_synthesis_distiller_hook.py]: Create a dedicated unit test file to verify that the core logic of `synthesis_distiller.py` functions correctly with the newly abstracted `SynthesisPayloadCompressor`. (Do NOT overload `test_bug_synthesis_hook.py` as it strictly tests startup hook registration).</action>
    <action>[MODIFY] @[backend_v2/tests/unit/test_epic93_contract_verification.py]: Add structural assertions (e.g. using `ast` or reflection) to ensure both the new `extractive_sensor_service.py` and `MatrixExplanationService` strictly adhere to their architectural contracts and don't violate single responsibility.</action>
  </step>

  <validation_gate>
    <!-- Planner MUST inject specific grep_search and pytest verification commands here -->
  </validation_gate>
</execution_protocol>
```
