# 06. Enriched Atom Graph Engine

The Enriched Atom Graph Engine transforms flat text extraction into a causal, conditional graph that allows dynamic short-circuiting of execution branches. This ensures rigorous architectural decoupling between semantic extraction, causal linking, and final execution representation.

## Core Architectural Components

### 1. Extractive Sensor Service
**Path:** `backend_v2/services/orchestrator/extractive_sensor_service.py`
The sensor service handles extracting raw boolean values using the `BooleanEvaluationResult` DTO, relying on LLM structured execution. It uses `execute_structured_task` to execute robust boolean validation on evaluation paths.

### 2. Topological Evaluator
**Path:** `backend_v2/services/orchestrator/topological_evaluator.py`
The absolute SSOT for Directed Acyclic Graph (DAG) state evaluation. It uses a non-blocking `asyncio.TaskGroup` to execute the node graph simultaneously:
- Each node creates its own `asyncio.Event()` that guarantees deterministic signaling.
- Parent nodes are awaited sequentially per-node (never via `asyncio.gather`), resolving the "Straggler" issue.
- **Fail-Fast Enforcement:** Infinite recursion and cyclic dependencies are deterministically rejected via a pre-flight depth-first search (DFS).
- **Short-Circuit Cascade:** If a parent resolves as `FAILED` (or does not meet the expected status), its children immediately short-circuit to `N_A`. Errors propagate via the `BLOCKED` status.

### 3. Result Projector
**Path:** `backend_v2/services/orchestrator/result_projector.py`
Implements the `ResultProjector` abstraction. `EnrichedResultProjector` uses Python's `graphlib.TopologicalSorter` to enforce a stable topological iteration order over the evaluated nodes. 

## DTO Lifecycle & Output Boundary

Following the Universal DTO Bridge (Epic 91.5), the engine must strictly decouple logical graph execution from server-driven UI elements.
1. The engine produces a `dict[str, AtomExecutionState]`.
2. `EnrichedResultProjector` compiles the dynamic results into a flat list of `AtomResultDTO` objects.
3. All static evidence (`source_quote`, `resolved_claim`) is offloaded to the O(1) Dictionary `hydrated_references` using `HydratedAtomDTO`, keyed by its Opaque Stripe ID (`tda_id`).

This avoids repetitive nested tree logic and guarantees 100% ICU Markdown serialization parity for the Frontend.
