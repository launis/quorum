# Phase 2: Distiller Extraction & Payload Compression Isolation

**Overview:** Resolve the "God File" bottleneck in `synthesis_distiller.py` by abstracting payload compression, and implement global DB-driven constraints for synthesis evaluations to restore narrative depth.
**Target Files:** @[backend_v2/services/orchestrator/synthesis_payload_compressor.py], @[backend_v2/services/orchestrator/synthesis_distiller.py#L30-L113], @[backend_v2/settings.py#L42-L598], @[backend_v2/models/domain/synthesis.py], @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L20-L161], @[client_app_v2/lib/features/execution/models/distilled_evaluation.dart], @[backend_v2/tests/unit/test_bug_synthesis_hook.py#L9-L21], @[backend_v2/tests/unit/test_epic93_contract_verification.py#L205-L230]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by the previous phase. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <dod_checklist>
    - [ ] `SynthesisPayloadCompressor` extracted successfully.
    - [ ] `settings.max_synthesis_evaluations` governs the evaluation count constraint.
    - [ ] `DistilledEvaluation` Pydantic model enforces Fail-Fast validation.
    - [x] `synthesis_engine.py` successfully updated to consume `DistilledEvaluation` object references. (N/A: Engine already decoupled and strictly typed via GlobalAtomBlackboard in Epic 101).
    - [x] Dart `distilled_evaluation.dart` model updated to enforce strict schema parity.
    - [x] Unit tests pass successfully without fixture-related crashes.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents\rules\00-antigravity-core.md]</rule>
    <rule>@[.agents\rules\01-python-backend.md]</rule>
  </required_context_rules>

  <anti_targets>
    - Do not modify `synthesis.py` (legacy god file).
    - Do not allow fuzzy/fallback parsing in the new Dart `distilled_evaluation` model.
    - Do not append compression logic directly to the distillation hook.
  </anti_targets>

  <step id="1" name="Implementation">
    <action>[NEW] @[backend_v2/services/orchestrator/synthesis_payload_compressor.py]: Extract `_compress_synthesis_payload` from `synthesis_distiller.py`. Encapsulate the deep-copy and metadata-stripping logic within a `SynthesisPayloadCompressor` class/function. Implement strict Pydantic V2 typing to manage heterogeneous payloads safely. Enforce dictionary access (`tda_id_to_atom_context[atom_id]`) to trigger Fail-Fast KeyError crashes.</action>
    <action>[MODIFY] @[backend_v2/services/orchestrator/synthesis_distiller.py#L30-L113]: Delete `_compress_synthesis_payload`. Import and utilize `SynthesisPayloadCompressor`. Refactor the hardcoded `[:20]` cutoff for evaluations, replacing it with `settings.max_synthesis_evaluations`.</action>
    <action>[MODIFY] @[backend_v2/settings.py#L42-L598]: Inject a new application setting: `max_synthesis_evaluations` (default: 40) under the appropriate system concurrency or configuration section.</action>
    <action>[MODIFY] @[backend_v2/models/domain/synthesis.py]: Refactor the loose `lite_ev` dictionary structure generated during distillation into a strictly typed `DistilledEvaluation` Pydantic V2 model to enforce Fail-Fast validation.</action>
    <action>[MODIFY] @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L20-L161]: Consumer Crash Prevention. Update the engine to consume the strict `DistilledEvaluation` model using object references instead of dictionary access. [RESOLVED: N/A - synthesis_engine.py was already fully decoupled from dictionary access during Epic 101 via GlobalAtomBlackboard. False requirement hallucinated during Epic planning.]</action>
    <action>[NEW] @[client_app_v2/lib/features/execution/models/distilled_evaluation.dart]: Frontend Parsing Crash Prevention. Create the Dart Freezed model for `DistilledEvaluation` to maintain strict schema parity and set `disallowUnrecognizedKeys: true` on the `@Freezed` annotation.</action>
    <action>[MODIFY] @[backend_v2/tests/unit/test_bug_synthesis_hook.py#L9-L21]: Fixture Migration: Update mocked test fixtures.</action>
    <action>[MODIFY] @[backend_v2/tests/unit/test_epic93_contract_verification.py#L205-L230]: Fixture Migration: Update mocked test fixtures to prevent crash loops.</action>
  </step>

  <validation_gate>
    <action>Run backend audit: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test`</action>
    <action>Run frontend audit to generate Freezed models: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models/distilled_evaluation.dart --build`</action>
    <action>Grep check that `_compress_synthesis_payload` is no longer in `synthesis_distiller.py`</action>
  </validation_gate>
</execution_protocol>
```
