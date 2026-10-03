<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
  <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
  <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
  <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
  <knowledge_item>@[ki_synthesis_payload_compression.md]</knowledge_item>
  <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
</required_context_rules>

# Implementation Plan - Domain Orchestrators Mutation Testing and Invariance Verification

> [!NOTE]
> **Scientific and Industrial Foundation (ISTQB & Mutation Testing Invariance)**
> Standard line and branch coverage metrics evaluate exclusively whether code paths were traversed during test execution; they fail to verify whether the assertions in the test suite actively detect logic faults or regressions. Empirical mutation testing generates deliberate AST-level semantic faults ("mutants") to evaluate the fault-detection efficacy of unit tests. When unit tests execute against stateful in-memory repository fakes, mutation testing provides mathematical proof that every state transition, criteria evaluation, DAG dependency resolution, and Fail-Fast exception branch is strictly asserted.

---

## User Review Required

> [!IMPORTANT]
> **Targeted Mutation Operators vs. Brute-Force Testing:**
> To eliminate execution latency and combinatorial explosion across complex orchestrators, mutation testing executes targeted architectural mutation operators (specifically and exhaustively: Branch Inversion, State Transitions, Threshold Bounds, Collection/Return Alterations, and Exception Bypasses) rather than unconstrained brute-force mutations.
>
> **In-Memory Fakes Pre-requisite:**
> This implementation plan relies directly on the stateful in-memory repository fakes (`InMemoryExecutionRepository`, `InMemoryWorkflowRepository`) established during persistence mock eradication. Tests execute purely in memory in sub-50ms cycles without external network or file I/O delays.
>
> **Minimum Kill Rate Gate:**
> Every domain orchestrator test suite must achieve a minimum mutation kill rate of 85% on its targeted mutant population, with 100% kill rate mandated on state transition and exception handling branches.

---

## 1. Scope & Impact Analysis

### 1.1 Target Files

| Action | Relative File Path | Responsibility & Component Scope |
| :--- | :--- | :--- |
| `[NEW]` | `@[scripts/audit_mutation_coverage.py]` | Unified AST mutation testing engine supporting targeted orchestrator profiles and kill-rate auditing |
| `[NEW]` | `@[scripts/mutation_baseline.json]` | Mathematical kill-rate baseline ledger tracking per-orchestrator regression thresholds |
| `[NEW]` | `@[backend_v2/tests/unit/scripts/test_mutation_orchestrator.py]` | Comprehensive unit test suite for the mutation engine AST visitor and mutant runner |
| `[MODIFY]` | `@[scripts/backend_audit_loop.py]` | Add `--mutation-strict` flag and optional Stage 9 mutation invariance verification gate |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py]` | Fortify unit tests for `TDAEngine` to eliminate surviving mutants |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]` | Fortify unit tests for `SynthesisEngine` to eliminate surviving mutants |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py]` | Fortify unit tests for `PromptEngine` to eliminate surviving mutants |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]` | Fortify unit tests for `DAGExecutor` and `NodeExecutor` to eliminate surviving mutants |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/test_enriched_dag_executor.py]` | Fortify unit tests for `EnrichedDagExecutor` to eliminate surviving mutants |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/test_dag_compiler.py]` | Fortify unit tests for `DAGCompilerService` to eliminate surviving mutants |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py]` | Fortify unit tests for `ExtractiveSensorService` to eliminate surviving mutants |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py]` | Fortify unit tests for `SlidingWindowLinker` to eliminate surviving mutants |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py]` | Fortify unit tests for `TwoPassAtomizer` to eliminate surviving mutants |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py]` | Fortify unit tests for `AnchorValidationService` to eliminate surviving mutants |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py]` | Fortify unit tests for `PromptCompiler` to eliminate surviving mutants |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/test_context_router.py]` | Fortify unit tests for `ContextRouter` to eliminate surviving mutants |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/test_rag_preflight_service.py]` | Fortify unit tests for `RAGPreflightService` to eliminate surviving mutants |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py]` | Fortify unit tests for `synthesis_distiller_hook` to eliminate surviving mutants |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py]` | Fortify unit tests for `SynthesisPayloadCompressor` to eliminate surviving mutants |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py]` | Fortify unit tests for `MatrixExplanationService` to eliminate surviving mutants |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/test_state_reducer.py]` | Fortify unit tests for `merge_execution_inputs` and `reduce_hook_delta` to eliminate surviving mutants |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/test_matrix_reducer.py]` | Fortify unit tests for `MatrixReducer` to eliminate surviving mutants |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/execution/test_facade.py]` | Fortify unit tests for `ExecutionService` facade to eliminate surviving mutants |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/execution/test_ingress_service.py]` | Fortify unit tests for `ExecutionIngressService` to eliminate surviving mutants |
| `[NEW]` | `@[backend_v2/tests/unit/services/execution/test_lifecycle_service.py]` | Create unit test suite for `ExecutionLifecycleService` and achieve >= 85% mutation kill rate |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/execution/test_override_service.py]` | Fortify unit tests for `ExecutionOverrideService` to eliminate surviving mutants |
| `[MODIFY]` | `@[backend_v2/tests/unit/workers/test_execution_worker.py]` | Fortify unit tests for `execute_workflow_job` to eliminate surviving mutants |
| `[MODIFY]` | `@[backend_v2/tests/unit/workers/test_report_worker.py]` | Fortify unit tests for `generate_report_artifact_job` and `render_profile_job` to eliminate surviving mutants |
| `[MODIFY]` | `@[backend_v2/tests/unit/workers/test_synthesis_worker.py]` | Fortify unit tests for `generate_profile_synthesis_and_pdf_task` to eliminate surviving mutants |

### 1.2 Context Files (Read-Only SSOT)

- `@[backend_v2/services/orchestrator/engines/tda_engine.py]`
- `@[backend_v2/services/orchestrator/engines/synthesis_engine.py]`
- `@[backend_v2/services/orchestrator/engines/prompt_engine.py]`
- `@[backend_v2/services/orchestrator/dag_executor.py]`
- `@[backend_v2/services/orchestrator/enriched_dag_executor.py]`
- `@[backend_v2/services/orchestrator/dag_compiler.py]`
- `@[backend_v2/services/orchestrator/extractive_sensor_service.py]`
- `@[backend_v2/services/orchestrator/sliding_window_linker.py]`
- `@[backend_v2/services/orchestrator/two_pass_atomizer.py]`
- `@[backend_v2/services/orchestrator/anchor_validation_service.py]`
- `@[backend_v2/services/orchestrator/prompt_compiler.py]`
- `@[backend_v2/services/orchestrator/context_router.py]`
- `@[backend_v2/services/orchestrator/rag_preflight_service.py]`
- `@[backend_v2/services/orchestrator/synthesis_distiller.py]`
- `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]`
- `@[backend_v2/services/orchestrator/matrix_explanation_service.py]`
- `@[backend_v2/services/orchestrator/state_reducer.py]`
- `@[backend_v2/services/orchestrator/matrix_reducer.py]`
- `@[backend_v2/services/execution/facade.py]`
- `@[backend_v2/services/execution/ingress_service.py]`
- `@[backend_v2/services/execution/lifecycle_service.py]`
- `@[backend_v2/services/execution/override_service.py]`
- `@[backend_v2/workers/execution_worker.py]`
- `@[backend_v2/workers/report_worker.py]`
- `@[backend_v2/workers/synthesis_worker.py]`

---

## 2. Technical Debt Pre-Flight Sweep

Pre-flight inspection across the target orchestrators confirms that:
1. Target test files exist in `backend_v2/tests/unit/` but primarily assert happy paths and call counts rather than edge-case boundary mutations.
2. Handlers and reducers contain boundary checks (specifically: checking `not items`, status equality, and score threshold bounds) where mutating relational or equality operators currently leaves tests green.
3. Exception paths raising `AppException` are tested in isolated negative tests, but mutating `raise AppException(...)` to a default return object in certain helper methods does not cause downstream test failure.

Phase 1 establishes the automated mutation engine, and subsequent phases systematically eliminate surviving mutants per orchestrator tier.

---

## 3. Phased Execution Protocol

```xml
<execution_protocol>
  <phase id="1" name="Mutation Testing Engine and Architectural Operators">
    <step id="1.1" name="Build Targeted AST Mutation Engine">
      <action>Create [NEW] @[scripts/audit_mutation_coverage.py] implementing AST-based mutant generation and test execution.</action>
      <action>Implement 5 targeted architectural mutation operators:
        1. Branch Inversion: mutate if test to not test, True, or False.
        2. State Transitions: mutate ExecutionStatus enum assignments (for instance: COMPLETED to FAILED or RUNNING).
        3. Threshold and Relational Bounds: mutate comparison operators (&lt; to &lt;=, &gt; to &gt;=, == to !=).
        4. Return Alterations: mutate return statements to return None or empty collections.
        5. Exception Bypasses: mutate raise AppException statements into pass or return None.</action>
      <action>Equip CLI with arguments: --target-module, --test-suite, --profile, --min-kill-rate (default: 85), and --baseline-ledger.</action>
      <constraint invariant="zero_permissive_typing">CLI options and report data structures must use strict Pydantic V2 DTOs with extra='forbid'.</constraint>
    </step>

    <step id="1.2" name="Unit Tests for Mutation Engine">
      <action>Create [NEW] @[backend_v2/tests/unit/scripts/test_mutation_orchestrator.py] verifying that the mutation engine accurately parses AST nodes, generates valid mutants, executes sub-process test runs, and computes kill-rate metrics without false positives.</action>
    </step>

    <step id="1.3" name="Initialize Mutation Baseline Ledger">
      <action>Create [NEW] @[scripts/mutation_baseline.json] capturing the initial kill-rate baseline across all 25 orchestrator targets, initializing minimum threshold to 85%.</action>
    </step>
  </phase>

  <phase id="2" name="Core Execution Engines Invariance Verification">
    <step id="2.1" name="TDAEngine Mutation Hardening">
      <action>Execute mutation audit against @[backend_v2/services/orchestrator/engines/tda_engine.py] targeting @[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py].</action>
      <action>Identify surviving mutants in criteria evaluation, passivity penalty invocation, and shuffled_atoms validation.</action>
      <action>Modify @[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py] adding concrete assertions to kill all surviving mutants, achieving &gt;= 85% kill rate.</action>
    </step>

    <step id="2.2" name="SynthesisEngine Mutation Hardening">
      <action>Execute mutation audit against @[backend_v2/services/orchestrator/engines/synthesis_engine.py] targeting @[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py].</action>
      <action>Identify surviving mutants in perspective distillation, token budget distribution, and cross-step aggregation.</action>
      <action>Modify @[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py] adding assertions to achieve &gt;= 85% kill rate.</action>
    </step>

    <step id="2.3" name="PromptEngine Mutation Hardening">
      <action>Execute mutation audit against @[backend_v2/services/orchestrator/engines/prompt_engine.py] targeting @[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py].</action>
      <action>Identify surviving mutants in prompt dispatch, schema enforcement, and non-matrix instruction execution.</action>
      <action>Modify @[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py] adding assertions to achieve &gt;= 85% kill rate.</action>
    </step>
  </phase>

  <phase id="3" name="DAG Orchestrators and Compilers Invariance Verification">
    <step id="3.1" name="DAGExecutor and NodeExecutor Mutation Hardening">
      <action>Execute mutation audit against @[backend_v2/services/orchestrator/dag_executor.py] targeting @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py].</action>
      <action>Identify surviving mutants in semaphore acquisition, step state transitions, wave-based node execution, and exception propagation.</action>
      <action>Modify @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py] adding assertions to achieve &gt;= 85% kill rate.</action>
    </step>

    <step id="3.2" name="EnrichedDagExecutor Mutation Hardening">
      <action>Execute mutation audit against @[backend_v2/services/orchestrator/enriched_dag_executor.py] targeting @[backend_v2/tests/unit/services/orchestrator/test_enriched_dag_executor.py].</action>
      <action>Identify surviving mutants in sliding window linking, paragraph decomposition, and enriched context injection.</action>
      <action>Modify @[backend_v2/tests/unit/services/orchestrator/test_enriched_dag_executor.py] adding assertions to achieve &gt;= 85% kill rate.</action>
    </step>

    <step id="3.3" name="DAGCompilerService Mutation Hardening">
      <action>Execute mutation audit against @[backend_v2/services/orchestrator/dag_compiler.py] targeting @[backend_v2/tests/unit/services/orchestrator/test_dag_compiler.py].</action>
      <action>Identify surviving mutants in topological dependency graph building, cycle detection, and step validation.</action>
      <action>Modify @[backend_v2/tests/unit/services/orchestrator/test_dag_compiler.py] adding assertions to achieve &gt;= 85% kill rate.</action>
    </step>
  </phase>

  <phase id="4" name="Atom Graph and Sensor Orchestrators Invariance Verification">
    <step id="4.1" name="ExtractiveSensorService Mutation Hardening">
      <action>Execute mutation audit against @[backend_v2/services/orchestrator/extractive_sensor_service.py] targeting @[backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py].</action>
      <action>Identify surviving mutants in boolean evaluation parsing, pre-flight checks, batch sensor chunking, and quote verification.</action>
      <action>Modify @[backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py] adding assertions to achieve &gt;= 85% kill rate.</action>
    </step>

    <step id="4.2" name="SlidingWindowLinker Mutation Hardening">
      <action>Execute mutation audit against @[backend_v2/services/orchestrator/sliding_window_linker.py] targeting @[backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py].</action>
      <action>Identify surviving mutants in causal edge creation, dependency sorting, and inter-paragraph window overlapping.</action>
      <action>Modify @[backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py] adding assertions to achieve &gt;= 85% kill rate.</action>
    </step>

    <step id="4.3" name="TwoPassAtomizer and AnchorValidationService Mutation Hardening">
      <action>Execute mutation audit against @[backend_v2/services/orchestrator/two_pass_atomizer.py] targeting @[backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py].</action>
      <action>Execute mutation audit against @[backend_v2/services/orchestrator/anchor_validation_service.py] targeting @[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py].</action>
      <action>Modify test files adding assertions on text normalization, anchor boundary offsets, and exact lexical quote matches to achieve &gt;= 85% kill rate.</action>
    </step>
  </phase>

  <phase id="5" name="Prompt, Context and Reducer Orchestrators Invariance Verification">
    <step id="5.1" name="PromptCompiler and ContextRouter Mutation Hardening">
      <action>Execute mutation audit against @[backend_v2/services/orchestrator/prompt_compiler.py] and @[backend_v2/services/orchestrator/context_router.py].</action>
      <action>Modify @[backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py] and @[backend_v2/tests/unit/services/orchestrator/test_context_router.py] adding assertions on XML section framing, token budgeting, and deliverable context delivery to achieve &gt;= 85% kill rate.</action>
    </step>

    <step id="5.2" name="RAGPreflightService and SynthesisDistiller Mutation Hardening">
      <action>Execute mutation audit against @[backend_v2/services/orchestrator/rag_preflight_service.py] and @[backend_v2/services/orchestrator/synthesis_distiller.py].</action>
      <action>Modify @[backend_v2/tests/unit/services/orchestrator/test_rag_preflight_service.py] and @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py] to achieve &gt;= 85% kill rate.</action>
    </step>

    <step id="5.3" name="StateReducer and MatrixReducer Mutation Hardening">
      <action>Execute mutation audit against @[backend_v2/services/orchestrator/state_reducer.py] and @[backend_v2/services/orchestrator/matrix_reducer.py].</action>
      <action>Modify @[backend_v2/tests/unit/services/orchestrator/test_state_reducer.py] and @[backend_v2/tests/unit/services/orchestrator/test_matrix_reducer.py] adding assertions on delta reduction, step state accumulation, and variance metrics to achieve &gt;= 85% kill rate.</action>
    </step>
  </phase>

  <phase id="6" name="Execution Lifecycle Facades and Background Workers Invariance Verification">
    <step id="6.1" name="Execution Service Facades Mutation Hardening">
      <action>Execute mutation audit against @[backend_v2/services/execution/facade.py], @[backend_v2/services/execution/ingress_service.py], @[backend_v2/services/execution/lifecycle_service.py], and @[backend_v2/services/execution/override_service.py].</action>
      <action>Modify test files in @[backend_v2/tests/unit/services/execution/] adding assertions on execution creation, resumption guards, human overrides, and state cancellation to achieve &gt;= 85% kill rate.</action>
    </step>

    <step id="6.2" name="Background Workers Mutation Hardening">
      <action>Execute mutation audit against @[backend_v2/workers/execution_worker.py], @[backend_v2/workers/report_worker.py], and @[backend_v2/workers/synthesis_worker.py].</action>
      <action>Modify test files in @[backend_v2/tests/unit/workers/] adding assertions on job execution, dead-letter queue failure dispatch, and profile cache compilation to achieve &gt;= 85% kill rate.</action>
    </step>
  </phase>

  <phase id="7" name="CI/CD Quality Gate Integration and Permanent Baseline Locking">
    <step id="7.1" name="Integrate Mutation Verification Gate in backend_audit_loop.py">
      <action>Update @[scripts/backend_audit_loop.py] to support --mutation-strict flag.</action>
      <action>Add optional Stage 9 gate executing uv run python scripts/audit_mutation_coverage.py --baseline-ledger scripts/mutation_baseline.json to enforce that no orchestrator kill rate regresses below its baseline.</action>
    </step>

    <step id="7.2" name="Full Suite Audit Gate Verification">
      <action>Execute full repository quality gate in strict mode: uv run python scripts/backend_audit_loop.py backend_v2 --test.</action>
      <action>Verify all 25 target orchestrator suites pass with 100% green test status and kill rate &gt;= 85%.</action>
    </step>
  </phase>
</execution_protocol>
```

---

## 4. Architectural Safeguards & Verification Plan

### 4.1 Unit & Integration Test Verification
- Run mutation verification across all orchestrator tiers:
  ```powershell
  uv run python scripts/audit_mutation_coverage.py --baseline-ledger scripts/mutation_baseline.json
  ```
- Run standard backend audit loop across touched files:
  ```powershell
  uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/ --test
  uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/execution/ --test
  uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/workers/ --test
  ```

### 4.2 Mandatory Final E2E REST API Verification Gate
- Windows PowerShell:
  ```powershell
  $env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
  ```
- Unix Bash:
  ```bash
  RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
  ```

---

## 5. Definition of Done (DoD)

1. `[NEW] @[scripts/audit_mutation_coverage.py]` is fully implemented and passes all unit tests in `[NEW] @[backend_v2/tests/unit/scripts/test_mutation_orchestrator.py]`.
2. Every domain orchestrator (all 25 targets across `backend_v2/services/orchestrator/`, `backend_v2/services/execution/`, and `backend_v2/workers/`) achieves a minimum mutation kill rate of 85% on targeted mutants.
3. 100% of state transition mutations (`ExecutionStatus`) and exception bypass mutations (`raise AppException`) are detected and killed by tests.
4. `[NEW] @[scripts/mutation_baseline.json]` is committed with mathematical kill-rate thresholds for all orchestrator modules.
5. `@[scripts/backend_audit_loop.py]` supports `--mutation-strict` and enforces the baseline ledger.
6. The entire backend test suite passes cleanly through all 8 stages of `backend_audit_loop.py`.
