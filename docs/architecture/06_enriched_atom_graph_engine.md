# 06. Enriched Atom Graph Engine

The Enriched Atom Graph Engine transforms flat text extraction into a causal, conditional graph that allows dynamic short-circuiting of execution branches. This ensures rigorous architectural decoupling between semantic extraction, causal linking, and final execution representation.

## Core Architectural Components

### 1. Extractive Sensor Service
The sensor service handles extracting raw boolean values using the `BooleanEvaluationResult` DTO, relying on LLM structured execution. It uses `execute_structured_task` to execute robust boolean validation on evaluation paths.

### 2. Topological Evaluator
The absolute SSOT for Directed Acyclic Graph (DAG) state evaluation. It uses a non-blocking `asyncio.TaskGroup` to execute the node graph simultaneously:
- Each node creates its own `asyncio.Event()` that guarantees deterministic signaling.
- Parent nodes are awaited sequentially per-node (never via `asyncio.gather`), resolving the "Straggler" issue.
- **Fail-Fast Enforcement:** Infinite recursion and cyclic dependencies are deterministically rejected via a pre-flight depth-first search (DFS).
- **Short-Circuit Cascade:** If a parent resolves as `FAILED` (or does not meet the expected status), its children immediately short-circuit to `N_A`. Errors propagate via the `BLOCKED` status.

### 3. Result Projector
Implements the `ResultProjector` abstraction. `EnrichedResultProjector` uses Python's `graphlib.TopologicalSorter` to enforce a stable topological iteration order over the evaluated nodes. 

### 4. Sliding Window Linker
Connects extracted atoms into a causal graph using an output-aware sliding window strategy. To prevent LLM output truncation (8192 token ceiling), windows are dynamically bounded by the strict limit, pre-subdividing oversized chunks and maintaining deterministic edge mapping.

### 5. Chat Parser
Transforms raw conversational interactions into structured analytical events. By parsing unstructured dialogue, it feeds contextual triggers directly into the graph engine, ensuring that human-in-the-loop interactions can dynamically alter evaluation paths without bypassing strict structural validation.

### 6. Anchor Validation Service
Acts as the authoritative validator for data provenance within the graph. It ensures that any extracted atom or causal link is strictly backed by traceable evidence, preventing hallucinations from contaminating the DAG state and providing a verified audit trail for all evaluations.

### 7. Context-Enriched Pipeline (Dual-Path TDA)
Supports two distinct execution paths: Regular TDA and Matrix Assertion TDA. 
- **Matrix Path**: When assertions are predefined in a structured matrix, original UUIDs (`tda_id`) are preserved. The `SlidingWindowLinker` is bypassed because matrix assertions are independent. The structured claims are mapped directly into independent graph nodes.
- **Enriched Context**: To prevent context drift and ensure O(1) Cache Survival, a static-first `<context>` block is constructed containing all enriched facts and raw source text. The topological executor inherits this enriched global context uniformly across parallel evaluations.

## DTO Lifecycle & Output Boundary

The engine strictly decouples logical graph execution from server-driven UI elements.
1. The engine produces a `dict[str, AtomExecutionState]`.
2. `EnrichedResultProjector` compiles the dynamic results into a flat list of `AtomResultDTO` objects.
3. All static evidence (`source_quote`, `resolved_claim`) is offloaded to the O(1) Dictionary `hydrated_references` using `HydratedAtomDTO`, keyed by its Opaque Stripe ID (`tda_id`).

This avoids repetitive nested tree logic and guarantees 100% ICU Markdown serialization parity for the Frontend.
