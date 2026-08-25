```xml
<required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_context_enriched_decompose_verify.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_polymorphic_rule_routing.md]</knowledge_item>
    <knowledge_item>@[ki_matrix_boolean_evaluation_strictness.md]</knowledge_item>
</required_context_rules>
```

# Implementation Plan - Matrix Causal DAG Integration

Integrates Quorum's evaluation matrices (`tda_assertions` inside `MatrixPromptBlock` / `request.shuffled_atoms`) directly into the system's topological causal engine (`TopologicalEvaluator`). This allows matrix criteria to form logical dependency hierarchies (`depends_on: tuple[CausalEdge, ...]`), enabling failed root preconditions to deterministically short-circuit child assertions (`ExecutionStatus.N_A`) without redundant LLM evaluation calls.

---

## User Review Required

> [!IMPORTANT]
> **Database & Schema Extension (`seed_data.json` & `TDAAssertion`):**
> Adds `depends_on: tuple[CausalEdge, ...] = Field(default_factory=tuple)` to the matrix rule schema. In accordance with `the_no_legacy_mandate` and `the_zero_compromise_pledge`, zero backwards compatibility or fallback shims are provided for previous execution runs or legacy historical traces. Strict Fail-Fast Pydantic validation is enforced across all engine boundaries.
>
> **Opaque ID Invariance & Transitive Dependency Closure (`ki_context_enriched_decompose_verify.md`):**
> Matrix atom identifiers (`tda_id`) are NEVER prefixed or dynamically renamed during flattening (`matrix_tda_uuid_preservation` invariant). To prevent dangling references (`UNRESOLVED_DEPENDENCY`) when Stratified Sampling (`matrix_sampling_strategy > 0`) is enabled, `atom_flattening.py` enforces Transitive Causal Closure: when a child atom with causal preconditions is sampled, all its upstream ancestor atoms (`CausalEdge.tda_id`) are deterministically retained in the flattened set.
>
> **God Code Prevention & Preventative Decomposition (`ki_god_code_prevention.md`):**
> 1. *Anti-God-File Dumping*: No new private helpers or unbounded logic dumped into `tda_engine.py` (which is already 273 lines). Logic modifications are strictly scoped to routing existing `depends_on` structures.
> 2. *Domain Model Purity*: Models remain pure immutable DTOs (`frozen=True, strict=True, extra="forbid"`), containing zero database lookups, business logic branching, or mutable collection state.
> 3. *AST Boundary Verification*: Class boundaries and method bounds are parsed deterministically before modifications.
>
> **Tripartite Pipeline Decoupling & Pure DTO Transit (`ki_tripartite_pipeline_architecture.md`):**
> Execution (Phase 1), Synthesis (Phase 2), and SDUI (Phase 3) remain 100% decoupled. Matrix DAG dependency evaluation executes exclusively within Phase 1 (`TopologicalEvaluator`). Downstream DTO projection (`ResultProjector.project()`) maps graph states to strict `AtomResultDTO` envelopes (`depends_on_tda_ids`, `short_circuit_reason_tda_ids`) so Presentation/SDUI adapters remain pure "Dumb Painters".
>
> **Polymorphic Rule Routing & Schema Strictness (`ki_polymorphic_rule_routing.md`):**
> Preserves `TypeAdapter(AnyPromptBlock)` Discriminated Union integrity in `atom_flattening.py`. Fails fast on invalid block structures (`ValidationError` / `AppException(VALIDATION_FAILED)`) with zero chameleon classes or duck-typing fallbacks.
>
> **Matrix Boolean Evaluation Strictness (`ki_matrix_boolean_evaluation_strictness.md`):**
> Strict `ExecutionStatus` enum parsing is maintained across all DAG evaluation paths. When an atom short-circuits (`ExecutionStatus.N_A`), `source_quote` is omitted, and parent failure reason is attributed deterministically without breaking Null Hypothesis validation rules.
>
> **Clean Architecture & Circular Import Prevention:**
> `v2_core.py` isolates `CausalEdge` behind `if TYPE_CHECKING:` to prevent circular module resolution traps and preserve dependency direction (DTO -> Core). Runtime schema resolution is handled deterministically via deferred `TDAAssertion.model_rebuild(_types_namespace={"CausalEdge": CausalEdge})` at the bottom of `v2_core.py`.
>
> **Cross-Domain Frontend Parity (`client_app_v2`):**
> Adds `CausalEdgeDTO` to `client_app_v2/lib/features/studio/models/prompt_block.dart` and extends `TDAAssertion` with `@Default([]) @JsonKey(name: 'depends_on') List<CausalEdgeDTO> dependsOn`. Ensures strict JSON serialization parity between Python backend and Flutter client.
>
> **Frozen Immutability (`frozen=True`):**
> Both `TDAAssertion` (via `V2CoreBase`) and `FlattenedAtom` enforce `frozen=True`. The causal dependency list is strictly typed as an immutable `tuple[CausalEdge, ...]` rather than a mutable `list`.
>
> **Touched Scope Technical Debt Cleanups:**
> In accordance with `touched_scope_tech_debt_mandate`, Phase 1 explicitly removes generic `except Exception:` catch-all handlers in `atom_flattening.py` in favor of strict `pydantic.ValidationError` handling, replaces raw dict unpacking in `tda_engine.py`, and synchronizes data starvation short-circuit logic.

---

## Proposed Changes

### Layer 1: Technical Debt Remediation & Domain Models / DTOs

#### `[MODIFY]` [atom_flattening.py](file:///c:/src/quorum/backend_v2/hooks/atom_flattening.py)
- **Pre-requisite Technical Debt Cleanup**: Replace generic `except Exception as e:` on `PromptBlockAdapter.validate_python` (`L107–112`) with explicit `(ValidationError, ValueError)` handling and Fail-Fast `AppException(VALIDATION_FAILED)`.
- Extract `TDAAssertion.depends_on` as `tuple[CausalEdge, ...]` and populate `FlattenedAtom.depends_on`.
- Enforce Transitive Causal Closure during Stratified Sampling:
  1. Index all available matrix assertions by `tda_id` before sampling.
  2. For any sampled atom, recursively resolve and include all ancestor parent atoms (`edge.tda_id`) in the final atom collection to prevent phantom edges and `UNRESOLVED_DEPENDENCY` crashes.

#### `[MODIFY]` [v2_core.py](file:///c:/src/quorum/backend_v2/models/v2_core.py)
- In `if TYPE_CHECKING:`, import `CausalEdge` from `backend_v2.models.dtos.dag_models`.
- Add field to `TDAAssertion`:
  ```python
  depends_on: Annotated[
      tuple[CausalEdge, ...],
      Field(
          default_factory=tuple,
          description="Causal preconditions required for this assertion.",
      ),
  ]
  ```
- At the bottom of `backend_v2/models/v2_core.py` (in the deferred post-import section), import `CausalEdge` from `backend_v2.models.dtos.dag_models` and invoke:
  ```python
  TDAAssertion.model_rebuild(_types_namespace={"CausalEdge": CausalEdge})
  ```

#### `[MODIFY]` [engine.py](file:///c:/src/quorum/backend_v2/models/dtos/engine.py)
- Import `CausalEdge` from `backend_v2.models.dtos.dag_models`.
- Add field to `FlattenedAtom`:
  ```python
  depends_on: Annotated[
      tuple[CausalEdge, ...],
      Field(
          default_factory=tuple,
          description="Causal dependencies attached to this atom.",
      ),
  ]
  ```

#### `[MODIFY]` [prompt_block.dart](file:///c:/src/quorum/client_app_v2/lib/features/studio/models/prompt_block.dart)
- Add `CausalEdgeDTO` Freezed model:
  ```dart
  @Freezed(equal: false)
  abstract class CausalEdgeDTO with _$CausalEdgeDTO {
    const CausalEdgeDTO._();

    @JsonSerializable(disallowUnrecognizedKeys: true)
    const factory CausalEdgeDTO({
      @JsonKey(name: 'edge_reasoning') required String edgeReasoning,
      @JsonKey(name: 'tda_id') required String tdaId,
      @JsonKey(name: 'source_id') required String sourceId,
      @JsonKey(name: 'expected_status')
      @Default(ExecutionStatus.passed)
      ExecutionStatus expectedStatus,
    }) = _CausalEdgeDTO;

    factory CausalEdgeDTO.fromJson(Map<String, dynamic> json) =>
        _$CausalEdgeDTOFromJson(json);
  }
  ```
- Add field to `TDAAssertion`:
  ```dart
  @JsonKey(name: 'depends_on')
  @Default([])
  List<CausalEdgeDTO> dependsOn,
  ```
- Add `List<CausalEdgeDTO> dependsOn = const []` to `TDAAssertion.create` factory constructor and pass `dependsOn: dependsOn,`.

---

### Layer 2: Pipeline Hooks & Strategy Engines

#### `[MODIFY]` [tda_engine.py](file:///c:/src/quorum/backend_v2/services/orchestrator/engines/tda_engine.py)
- In `if is_starved:` data starvation circuit breaker (`L73–93`), ensure `LinkedAtomGraph` nodes propagate `depends_on=list(atom.depends_on)` consistently rather than hardcoded `[]`.
- In `if request.shuffled_atoms:` (`L157–169`), construct `LinkedAtomGraph` nodes using each atom's dependencies converted to list format for `LinkedAtomGraph.depends_on`:
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
      nodes.append(LinkedAtomGraph(atom=extracted, depends_on=list(atom.depends_on)))
  ```

---

## Execution Protocol

```xml
<execution_protocol>
    <phase_1_tech_debt_and_models>
        <step id="1.1">
            <action>Clean technical debt in backend_v2/hooks/atom_flattening.py: Replace generic except Exception on PromptBlockAdapter.validate_python with (ValidationError, ValueError) and Fail-Fast AppException(VALIDATION_FAILED).</action>
            <constraint invariant="the_duct_tape_ban">No generic catch-alls or silent exception swallowing.</constraint>
        </step>
        <step id="1.2">
            <action>Update backend_v2/models/v2_core.py: Add TYPE_CHECKING import for CausalEdge, add depends_on: Annotated[tuple[CausalEdge, ...], Field(default_factory=tuple)] (without duplicate `= ()` assignment) to TDAAssertion, and add deferred TDAAssertion.model_rebuild(_types_namespace={"CausalEdge": CausalEdge}) at the bottom of the file.</action>
            <constraint invariant="clean_architecture_and_pydantic_strictness">Zero top-level DTO imports in v2_core.py. ConfigDict(strict=True, extra="forbid") must be preserved.</constraint>
            <constraint invariant="pydantic_strict_tuple_coercion_safety">CRITICAL: TDAAssertion uses ConfigDict(strict=True). In strict mode, Pydantic rejects list-to-tuple coercion. This is safe ONLY because the database hydration boundary at atom_flattening.py L106 uses PromptBlockAdapter.validate_python(raw_block, strict=False), which allows list-to-tuple coercion. Future agents MUST NOT change this hydration to strict=True or add new strict hydration paths for MatrixPromptBlock without accounting for the tuple field.</constraint>
        </step>
        <step id="1.3">
            <action>Update backend_v2/models/dtos/engine.py: Import CausalEdge and add depends_on: Annotated[tuple[CausalEdge, ...], Field(default_factory=tuple)] (without duplicate `= ()` assignment) to FlattenedAtom.</action>
            <constraint invariant="frozen_immutability">ConfigDict(strict=True, frozen=True, extra="forbid") must be preserved with immutable tuple typing.</constraint>
        </step>
        <step id="1.4">
            <action>Update client_app_v2/lib/features/studio/models/prompt_block.dart: Add CausalEdgeDTO model, add depends_on field to TDAAssertion Dart model, and update TDAAssertion.create factory constructor. Run build_runner to regenerate Freezed and JsonSerializable code.</action>
            <constraint invariant="cross_language_enum_parity">Enforce strict 1:1 cross-domain DTO parity between Python and Flutter Freezed models.</constraint>
            <constraint invariant="dart_import_verification">CausalEdgeDTO uses ExecutionStatus enum. Verify that ExecutionStatus is importable in prompt_block.dart from client_app_v2/lib/core/models/enums.dart. If not already imported, add the import.</constraint>
        </step>
    </phase_1_tech_debt_and_models>

    <session_handover_gate>
        <instruction>After completing Phase 1 and passing the audit loop, perform an atomic git commit. Then execute /tier5-session-handover to start Phase 2 from a fresh context window. The 8+ files in this plan heavily saturate the context budget.</instruction>
    </session_handover_gate>

    <phase_2_hooks_and_engine>
        <step id="2.1">
            <action>Update backend_v2/hooks/atom_flattening.py: Propagate depends_on tuple from TDAAssertion into FlattenedAtom and implement Transitive Causal Closure for Stratified Sampling. STRUCTURAL SPECIFICATION: The scale collection tuple in scale_atoms and matrix_collected_atoms MUST be upgraded to a 6-tuple: `tuple[str, str, str, str, bool, tuple[CausalEdge, ...]]` containing `(aid, text, rule, anchor, is_inv, tda.depends_on)`. The intermediate dictionary `unique_atoms` (L102) MUST be updated to `dict[str, tuple[str, str, str, bool, tuple[CausalEdge, ...]]]`. The FlattenedAtom construction at L165-167 MUST then use `depends_on=val[4]`. The Transitive Causal Closure MUST operate globally AFTER per-scale sampling by iterating the sampled `matrix_collected_atoms` list with a queue/set and recursively adding any ancestor atom whose tda_id appears in a sampled atom's depends_on edges from an all_matrix_atoms lookup map.</action>
            <constraint invariant="zero_duct_tape">Do not use getattr or silent fallback; extract depends_on directly from typed models. Retain all Opaque Stripe IDs without prefix modification.</constraint>
        </step>
        <step id="2.2">
            <action>Update backend_v2/services/orchestrator/engines/tda_engine.py: Construct LinkedAtomGraph(atom=extracted, depends_on=list(atom.depends_on)) in both the matrix execution and data starvation paths.</action>
            <constraint invariant="topological_invariants">Preserve TopologicalEvaluator wave execution and Kahn's algorithm short-circuiting.</constraint>
        </step>
    </phase_2_hooks_and_engine>

    <phase_3_verification>
        <step id="3.1">
            <action>Update backend_v2/tests/unit/hooks/test_atom_flattening.py: Add tests for depends_on propagation and Transitive Causal Closure under Stratified Sampling.</action>
        </step>
        <step id="3.2">
            <action>Write comprehensive ISTQB test suite in backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine_causal_matrix.py covering all 5 negative/edge-case partitions.</action>
        </step>
        <step id="3.3">
            <action>Create AST guardrail test in backend_v2/tests/unit/guardrails/test_ast_causal_dag_guardrails.py to verify that TDAAssertion.depends_on remains strictly a tuple and no raw dictionaries or generic catch-alls are used in atom_flattening.py.</action>
        </step>
        <step id="3.4">
            <action>Run backend audit loop: uv run python scripts/backend_audit_loop.py backend_v2/models/ backend_v2/hooks/ backend_v2/services/orchestrator/ --test</action>
        </step>
        <step id="3.5">
            <action>Run Flutter audit loop: uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/prompt_block.dart --build</action>
        </step>
    </phase_3_verification>
</execution_protocol>
```

---

## Verification Plan

### Automated Tests

1. **Core Strictness & Deferred Rebuild Test**:
   ```powershell
   uv run pytest backend_v2/tests/unit/test_v2_core_strictness.py
   ```
   - Verifies `TDAAssertion` allows valid `depends_on: tuple[CausalEdge, ...]` and rejects invalid dictionary or scalar types.
   - Verifies `TDAAssertion.model_rebuild()` resolves forward reference cleanly without circular import crashes.

2. **Hook Causal Closure & Flattening Tests**:
   ```powershell
   uv run pytest backend_v2/tests/unit/hooks/test_atom_flattening.py
   ```
   - Verifies `depends_on` propagation from `TDAAssertion` to `FlattenedAtom`.
   - Verifies that `atom_flattening.py` raises `AppException(VALIDATION_FAILED)` when invalid block format is passed (Technical Debt verification).

3. **Causal DAG Matrix Comprehensive ISTQB Test Suite (New)**:
   File: `backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine_causal_matrix.py`
   - **ISTQB Partition 1 (Happy Path - Clean Short-Circuit)**: Root assertion $A$ evaluates to `FAILED`. Dependent child $B$ (`expected_status=PASSED`) is short-circuited to `ExecutionStatus.N_A` with `short_circuit_reason_tda_ids=[A.tda_id]`. Sensor is never called for $B$.
   - **ISTQB Partition 2 (Negative - Phantom Edge Isolation)**: Assertion $B$ specifies dependency on missing/unsampled parent `tda_missing_parent_id`. Verifies `TopologicalEvaluator` marks $B$ as `SYSTEM_ERROR` with reasoning `"UNRESOLVED_DEPENDENCY"` without crashing the engine.
   - **ISTQB Partition 3 (Negative - Cyclic Graph Isolation)**: Matrix assertions form circular dependency $A \to B \to A$. Verifies `TopologicalEvaluator` marks both as `SYSTEM_ERROR` with reasoning `"CYCLIC_DEPENDENCY_DETECTED"`, while independent assertion $C$ evaluates normally.
   - **ISTQB Partition 4 (Negative - Multi-Level Transitive Sampling Closure)**: Stratified Sampling limit $N=1$ with a 3-tier chain ($A \to B \to C$). When only $C$ is chosen by RNG, verifies `atom_flattening.py` retains $A$, $B$, and $C$ in the flattened payload so no dangling edges reach the evaluator.
   - **ISTQB Partition 5 (Negative - Multi-Parent Conflicting Dependencies)**: Child $C$ depends on Parent $A$ (`expected_status=PASSED`) and Parent $B$ (`expected_status=PASSED`). If $A$ evaluates to `PASSED` and $B$ evaluates to `FAILED`, verifies $C$ short-circuits to `ExecutionStatus.N_A` and attributes $B.tda_id$ as the short-circuit reason.

4. **AST Guardrail Verification**:
   ```powershell
   uv run pytest backend_v2/tests/unit/guardrails/test_ast_causal_dag_guardrails.py
   ```
   - Verifies AST structural compliance: `TDAAssertion.depends_on` is typed with immutable `tuple`, `FlattenedAtom.depends_on` is typed with immutable `tuple`, and `atom_flattening.py` contains zero generic `except Exception:` handlers.

5. **Flutter Client Parity & Build Runner**:
   ```powershell
   uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/prompt_block.dart --build
   ```
   - Verifies Freezed code generation for `CausalEdgeDTO` and `TDAAssertion.dependsOn`.
   - Runs client unit tests: `flutter test test/features/studio/models/prompt_block_test.dart`.

6. **Full Subsystem Audit Loop**:
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py backend_v2/models/dtos/engine.py backend_v2/hooks/atom_flattening.py backend_v2/services/orchestrator/engines/tda_engine.py --test
   ```

---

## Known Tech Debt (Out of Scope — Discovered During Research)

> [!NOTE]
> The following tech debt was discovered during Tier 0 analysis of touched files and their 1-hop dependencies. These items are **NOT blocking** this plan but should be tracked for a dedicated remediation task.

1. **`tda_engine.py` L62–66: Naked Dict Blackboard Pattern**
   - Uses `.get()` defaults and `isinstance(data, dict)` on `context_variables["__GLOBAL_ATOM_BLACKBOARD__"]`.
   - Violates: `no_naked_dicts_in_state`, `the_duct_tape_ban`, `the_zero_compromise_pledge`.
   - Root Cause: `StrategyContext.context_variables` is typed as `dict[str, Any]` — a broader architectural limitation.
   - Remediation: Requires dedicated refactoring of the context variables system to use typed Pydantic DTOs.

2. **`topological_evaluator.py`: `model_copy(update={...})` Pattern (7 call sites)**
   - Uses `model_copy(update={...})` on `AtomExecutionState` instead of mandated `Model.model_validate(event.model_dump() | {...})`.
   - Violates: `frozen_state_mutability`.
   - Risk Assessment: Low — `AtomExecutionState` has only primitive/Enum fields, so shallow copy bypass is functionally equivalent.
   - Remediation: Replace with `model_validate(state.model_dump() | {...})` pattern.
