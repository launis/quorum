# Implementation Plan - Matrix Causal DAG Integration

Integrates Quorum's evaluation matrices (`tda_assertions` / `request.shuffled_atoms`) directly into the system's topological causal engine (`TopologicalEvaluator`). This allows matrix criteria to form logical dependency hierarchies (`depends_on: list[CausalEdge]`), enabling failed root preconditions to deterministically short-circuit child assertions (`ExecutionStatus.N_A`) without redundant LLM evaluation calls.

---

## User Review Required

> [!IMPORTANT]
> **Database & Schema Extension (`seed_data.json` & `TDAAssertion`):**
> Adds an optional `depends_on: list[CausalEdge] = Field(default_factory=list)` to the matrix rule schema. Existing matrices without explicit dependencies default to `depends_on=[]` and operate with 100% backward compatibility.

---

## Proposed Changes

### Layer 1: Domain Models & DTOs
#### `[MODIFY]` `backend_v2/models/v2_core.py`
- Import `CausalEdge` from `backend_v2.models.dtos.dag_models`.
- Add field `depends_on: list[CausalEdge] = Field(default_factory=list, description="Causal preconditions required for this assertion.")` to `TDAAssertion`.

#### `[MODIFY]` `backend_v2/models/dtos/engine.py`
- Import `CausalEdge` from `backend_v2.models.dtos.dag_models`.
- Add field `depends_on: list[CausalEdge] = Field(default_factory=list, description="Causal dependencies attached to this atom.")` to `FlattenedAtom`.

---

### Layer 2: Pipeline Hooks & Strategy
#### `[MODIFY]` `backend_v2/hooks/atom_flattening.py`
- Extract `TDAAssertion.depends_on` and pass it to the instantiated `FlattenedAtom(..., depends_on=assertion.depends_on)`.

#### `[MODIFY]` `backend_v2/services/orchestrator/engines/tda_engine.py`
- In `if request.shuffled_atoms:` (`L154–166`), construct `LinkedAtomGraph` nodes using each atom's own dependencies:
  ```python
  nodes = []
  for i, atom in enumerate(request.shuffled_atoms):
      extracted = ExtractedAtom(
          reasoning="Matrix assertion provided by orchestrator.",
          resolved_claim=atom.question,
          is_logical_deduction=True,
          source_quote=None,
          tda_id=atom.atom_id,
          source_id=_MATRIX_SOURCE_SENTINEL,
          source_sequence_index=i,
      )
      nodes.append(LinkedAtomGraph(atom=extracted, depends_on=atom.depends_on))
  ```

---

## Execution Protocol

```xml
<execution_protocol>
    <phase_1_models_and_dtos>
        <step id="1.1">
            <action>Update TDAAssertion in backend_v2/models/v2_core.py to include depends_on: list[CausalEdge] = Field(default_factory=list)</action>
            <constraint invariant="pydantic_strictness">ConfigDict(strict=True, extra="forbid") must be preserved.</constraint>
        </step>
        <step id="1.2">
            <action>Update FlattenedAtom in backend_v2/models/dtos/engine.py to include depends_on: list[CausalEdge] = Field(default_factory=list)</action>
            <constraint invariant="pydantic_strictness">ConfigDict(strict=True, frozen=True, extra="forbid") must be preserved.</constraint>
        </step>
    </phase_1_models_and_dtos>

    <phase_2_hooks_and_engine>
        <step id="2.1">
            <action>Update atom_flattening.py hook to propagate depends_on from TDAAssertion into FlattenedAtom</action>
            <constraint invariant="zero_duct_tape">Do not use getattr or silent fallback; extract depends_on directly from typed models.</constraint>
        </step>
        <step id="2.2">
            <action>Update TDAEngine.execute() matrix branch to construct LinkedAtomGraph(atom=extracted, depends_on=atom.depends_on)</action>
            <constraint invariant="topological_invariants">Preserve TopologicalEvaluator wave execution and Kahn's algorithm short-circuiting.</constraint>
        </step>
    </phase_2_hooks_and_engine>

    <phase_3_verification>
        <step id="3.1">
            <action>Write unit test in backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine_causal_matrix.py verifying that a FAILED parent assertion causes dependent child assertion to short-circuit to N_A</action>
        </step>
        <step id="3.2">
            <action>Run backend audit loop: uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test</action>
        </step>
    </phase_3_verification>
</execution_protocol>
```

---

## Verification Plan

### Automated Tests
1. **Unit Test (New)**: `backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine_causal_matrix.py`
   - Provide two matrix assertions: A (Root) and B (Depends on A, `expected_status=PASSED`).
   - Mock the sensor so that A returns `ExecutionStatus.FAILED`.
   - Verify that `TDAEngine.execute()` returns `FAILED` for A and `ExecutionStatus.N_A` for B, and that B's `short_circuit_reason_tda_ids == [A.tda_id]`.
2. **Full Subsystem Audit**:
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test
   ```
