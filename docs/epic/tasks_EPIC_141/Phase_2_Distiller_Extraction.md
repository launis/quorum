# Phase 2: Distiller Extraction & Payload Compression Isolation

## Objective
Resolve the "God File" bottleneck in `synthesis_distiller.py` by abstracting payload compression, and implement global DB-driven constraints for synthesis evaluations to restore narrative depth.

## Scope
### [NEW] `backend_v2/services/orchestrator/synthesis_payload_compressor.py`
- Extract `_compress_synthesis_payload` from `synthesis_distiller.py`.
- Encapsulate the deep-copy and metadata-stripping logic within a `SynthesisPayloadCompressor` class/function.
- Implement strict Pydantic V2 typing to manage heterogeneous payloads safely.

### [MODIFY] `backend_v2/services/orchestrator/synthesis_distiller.py`
- Delete `_compress_synthesis_payload`.
- Import and utilize `SynthesisPayloadCompressor`.
- Refactor the hardcoded `[:20]` cutoff for evaluations, replacing it with `settings.max_synthesis_evaluations`.

### [MODIFY] `backend_v2/settings.py`
- Inject a new application setting: `max_synthesis_evaluations` (default: 40) under the appropriate system concurrency or configuration section.

### [MODIFY] `backend_v2/models/domain/synthesis.py`
- Refactor the loose `lite_ev` dictionary structure generated during distillation into a strictly typed `DistilledEvaluation` Pydantic V2 model to enforce Fail-Fast validation.
