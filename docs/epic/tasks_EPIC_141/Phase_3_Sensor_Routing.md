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
    <action>[MODIFY] @[backend_v2/services/orchestrator/synthesis_distiller.py]: Ruthlessly delete the legacy fallback extraction logic for `MatrixScorecardRowDTO` arrays (`isinstance(atoms, list)` logic) in `_assemble_matrices_to_explain`. Enforce `the_no_legacy_mandate` by strictly requiring the lightweight dictionary model for matrix evaluations.</action>
    <action>[NEW] @[backend_v2/services/orchestrator/matrix_explanation_service.py]: Abstract the remaining `_assemble_matrices_to_explain` logic out of `synthesis_distiller.py` into a dedicated service (`MatrixExplanationService`) to ensure the hook remains lightweight and prevents God Code.</action>
  </step>

  <validation_gate>
    <!-- Planner MUST inject specific grep_search and pytest verification commands here -->
  </validation_gate>
</execution_protocol>
```
