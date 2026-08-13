# Phase 3: Sensor Routing & Matrix Explanation Architecture

**Overview:** Restore Context Alignment and Zero-Trust integrity in the Tripartite Pipeline by segregating matrix assertion mapping and fixing prompt CDATA encapsulation.
**Target Files:** @[backend_v2/services/orchestrator/extractive_sensor_service.py], @[backend_v2/models/dtos/dag_models.py#L94-L111], @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L89-L157]

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
    <action>[MODIFY] @[backend_v2/services/orchestrator/synthesis_distiller.py]: (VERIFIED_EXISTING) Ruthlessly delete the legacy fallback extraction logic for `MatrixScorecardRowDTO` arrays (`isinstance(atoms, list)` logic) in `_assemble_matrices_to_explain`. Enforce `the_no_legacy_mandate` by strictly requiring the lightweight dictionary model for matrix evaluations.</action>
    <action>[NEW] @[backend_v2/services/orchestrator/matrix_explanation_service.py]: (VERIFIED_EXISTING) Abstract the remaining `_assemble_matrices_to_explain` logic out of `synthesis_distiller.py` into a dedicated service (`MatrixExplanationService`) to ensure the hook remains lightweight and prevents God Code.</action>
    
    <action>[MODIFY] @[backend_v2/services/orchestrator/topological_evaluator.py]: (REMEDIATION) Modify `evaluate_graph` to pass `states` into `batch_evaluation_callback` as `batch_evaluation_callback(pending_nodes, states)`. This enables the execution layer to access resolved dependency statuses.</action>
    
    <action>[MODIFY] @[backend_v2/services/orchestrator/enriched_dag_executor.py]: (REMEDIATION) Update `batch_evaluation_callback` to accept `current_states: dict[str, AtomExecutionState]`. Pass this `current_states` down to `process_chunk`, and finally inject it into `ExtractiveSensorService.evaluate_atom_boolean_batch(..., current_states=current_states)`.</action>
    
    <action>[MODIFY] @[backend_v2/services/orchestrator/extractive_sensor_service.py]: (REMEDIATION) Update `evaluate_atom_boolean_batch` to accept `current_states: dict[str, AtomExecutionState] | None`. Before calling `build_compiled_prompt`, construct an `atom_status_map: dict[str, ExecutionStatus]`. Iterate through `current_states` and map each `tda_id` to its `status`. Pass this `atom_status_map` into `MatrixSensorPromptBuilder.build_compiled_prompt(..., atom_status_map=atom_status_map)`.</action>
    
    <action>[MODIFY] @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L90-L174]: (REMEDIATION) Extend `build_compiled_prompt` to accept `atom_status_map: dict[str, ExecutionStatus] | None`. Iterate over `node.depends_on` (from @[backend_v2/models/dtos/dag_models.py#L94-L111]). For each dependency, lookup the `actual_status` from `atom_status_map` (defaulting to UNKNOWN). Construct the XML `<dependency>` tags using safe mapping or `TemplateProcessor` instead of raw Python f-strings, as mandated by Epic 141 Phase 3.</action>
  </step>

  <validation_gate>
    - `uv run pytest backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py`
    - `uv run pytest backend_v2/tests/unit/services/orchestrator/test_topological_evaluator.py`
  </validation_gate>
</execution_protocol>

<!-- MANDATORY BOUNDARY RESTORATION FOR AUDIT SCRIPT -->
<!-- The planner abstracted away the following bounds from the parent Epic, which must be retained for the audit script: -->
<!-- @[backend_v2/services/orchestrator/dag_executor.py#L559-L752] -->
<!-- @[backend_v2/settings.py#L42-L599] -->
<!-- @[backend_v2/services/orchestrator/synthesis_distiller.py#L159-L330] -->
```
