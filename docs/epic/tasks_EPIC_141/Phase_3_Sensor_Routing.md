# Phase 3: Sensor Routing & Matrix Explanation Architecture

## Objective
Restore Context Alignment and Zero-Trust integrity in the Tripartite Pipeline by segregating matrix assertion mapping and fixing prompt CDATA encapsulation.

## Scope
### [NEW] `backend_v2/services/orchestrator/extractive_sensor_service.py`
- Abstract the complex Matrix assertion mapping and evaluation parsing logic out of `dag_executor.py` and `synthesis_distiller.py`.
- Introduce a dedicated service pattern (`ExtractiveSensorService`) for routing boolean matrix extractions.

### [MODIFY] `backend_v2/models/dtos/dag_models.py`
- Update `AtomExecutionState` to store causal justifications (`causal_reasoning`) correctly without introducing bloat to the DAG execution envelope.

### [MODIFY] `backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py`
- Fix CDATA encapsulation bugs (XML Structural Sovereignty). Ensure that dynamic payload fields like `<question>` and `<extraction_rule>` are perfectly sanitized via `TemplateProcessor.encapsulate_payload()` to prevent XML injection breaks.
