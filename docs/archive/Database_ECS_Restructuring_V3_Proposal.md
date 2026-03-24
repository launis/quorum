# Architectural Proposal: Database Restructuring (ECS Pattern)

**Status:** Proposed (Phase 3 / V3 Candidate)
**Context:** Quorum V2 Backend
**Author:** AI Orchestrator
**Date:** March 14, 2026

## 1. Problem Statement
Currently, the Quorum V2 architecture suffers from a structural coupling between the Pydantic backend models (`dag_executor.py`, evaluation hooks, agent inputs) and the hardcoded `component_id`s in the database (`seed_data.json`).
- Data is passed as a flat, dynamically permitted dictionary (`**kwargs` / `extra="allow"`).
- To evaluate a score, backend functions explicitly look for hardcoded prefixes like `matrix_judge` or `block_rule1`.
- **The Issue:** True "Zero-Deploy Administration" requires the backend to be completely ignorant of specific database keys. If a user creates a completely new widget type in the UI, the Python backend should process it generically without requiring a code update to recognize the new key.

## 2. Proposed Solution: Entity-Component-System (ECS) Meta-Classification
We propose moving from a flat Key-Value structure to a Meta-Classified List structure (Entity Component System). 

Instead of treating the data as an arbitrary dictionary, all inputs, outputs, and UI hints are normalized into a list of generic `EvaluationItem` (or `CognitiveComponent`) objects. The backend logic operates purely on the `type` meta-tag, never on the specific `id`.

### 2.1 Current State (Flat Key-Value)
```json
// Database / Workflow Input
{
  "matrix_judge": 5.0,
  "block_rule1": "Do not hallucinate.",
  "is_priority": true
}
```
*Python must explicitly know what `matrix_judge` means to scale it.*

### 2.2 Proposed State (Meta-Classified ECS)
```json
// Database / Workflow Input
"evaluation_items": [
  { 
    "id": "matrix_judge", 
    "type": "numeric_scale", 
    "value": 5.0, 
    "metadata": { "max_val": 10.0 } 
  },
  { 
    "id": "block_rule1", 
    "type": "text_instruction", 
    "value": "Do not hallucinate.",
    "metadata": { "strictness": 100 }
  },
  { 
    "id": "is_priority", 
    "type": "boolean_flag", 
    "value": true,
    "metadata": {}
  }
]
```

## 3. Implementation Blueprint

### Phase A: Backend Model Evolution
1. Define a rigorous Union of Pydantic models for the components: `NumericComponent`, `TextComponent`, `BooleanComponent`.
2. Refactor `WorkflowInputs` and Agent Input models to accept `List[CognitiveComponent]` instead of `extra="allow"`.
3. Update `dag_executor.py` and hook pipelines:
   ```python
   # FUTURE STATE DAG EXECUTOR LOGIC
   for item in inputs.evaluation_items:
       if item.type == "numeric_scale":
           # Generic scoring logic, absolutely no knowledge of "judge" or "falsifier"
           process_score(item.id, item.value, item.metadata.get("max_val"))
       elif item.type == "text_instruction":
           # Generic prompt compilation
           append_to_system_prompt(item.value, strictness=item.metadata.get("strictness"))
   ```

### Phase B: Database & Seeding Restructuring
1. The `backend_v2/seed/seed_data.json` matrices and blocks arrays must be restructured. Instead of `{"matrix_name": {"value": 5}}`, the database schema must strictly enforce the `type` tag.
2. The `Polymorphic Seeder` must explicitly map legacy data into these ECS containers during migration.

### Phase C: Client (Flutter) Adaptation
1. The Flutter UI (`SDUIWidgetFactory`) must unpack the `evaluation_items` array.
2. Widget mapping changes from switching on `hint['component_type']` to switching directly on the standardized `item.type`.

## 4. Architectural Benefits
* **Complete Decoupling:** The Python codebase becomes mathematically isolated from the business logic or database content.
* **True Zero-Deploy:** Administrators can spawn completely new types of evaluations or rules in the UI, and as long as they map to an existing `type` (e.g., `numeric_scale`), the backend will automatically process, log, and score them without a single line of Python being changed. 
* **Type Safety:** We regain the strict Pydantic typing that was lost when we had to rely on `extra="allow"` to support dynamic keys.

## 5. Risks & Considerations
* **Migration Cost:** This is a breaking change across the entire stack (Database -> Backend -> API -> Frontend). It requires a complete teardown of the current Y-Funnel data structure logic.
* **Payload Size:** Wrapping every single primitive value in an object dictionary increases the JSON payload size, though this is negligible in modern networking unless handling millions of rows.
