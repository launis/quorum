# 06. Enriched Atom Graph Engine

The Enriched Atom Graph Engine transforms flat text extraction into a causal, conditional graph that allows dynamic short-circuiting of execution branches. This ensures rigorous architectural decoupling between semantic extraction, causal linking, and final execution representation.

## Core Architectural Components

### 1. Extractive Sensor Service
The sensor service handles extracting raw boolean values using the `BooleanEvaluationResult` DTO, relying on LLM structured execution (`execute_structured_task`) to execute robust validation on evaluation paths. To achieve high self-consistency and zero-crash fault tolerance in high-entropy prompt blocks, it leverages a single-pass parallel **Best-of-Three Flash ensemble** wrapped in `asyncio.TaskGroup`:
- **Consensus Resolution (`resolve_majority_vote`):** Requires at least 2 valid results (out of 3 parallel calls) and adopts a consensus status whenever a 2/3 majority is reached.
- **Null Hypothesis Epistemic Tie-Breaker:** For inconclusive split votes (e.g., 1 PASS, 1 FAIL, 1 ERROR), the tie is resolved using an $O(1)$ pre-computed polarity mapping (`is_inverse_map`). Inverse assertions (`is_inverse=True`, evaluating absence of error) resolve to `PASSED` under the presumption of innocence, while standard positive assertions (`is_inverse=False`, requiring concrete proof) resolve to `FAILED` under the Null Hypothesis.
- **Forensic Guarantee:** Preserves valid evidence quotes on winning consensus while strictly forbidding quote hallucination on tie-broken or failed atoms.

### 2. Topological Evaluator
The absolute SSOT for Directed Acyclic Graph (DAG) state evaluation. It uses a non-blocking `asyncio.TaskGroup` to execute the node graph simultaneously:
- Each node creates its own `asyncio.Event()` that guarantees deterministic signaling.
- Parent nodes are awaited sequentially per-node (never via `asyncio.gather`), resolving the "Straggler" issue.
- **Fail-Fast Enforcement:** Infinite recursion and cyclic dependencies are deterministically rejected via a pre-flight depth-first search (DFS).
- **Standard Short-Circuit Cascade:** In regular evaluations, if a parent resolves as `FAILED` (or does not meet the expected status), its children immediately short-circuit to `N_A`. Errors propagate via the `BLOCKED` status.
- **Matrix Waterfall Soft-Penalties:** In structured matrix evaluations, the DAG engine applies soft penalty multipliers (deducting percentage scores) rather than hard-stopping when lower-level atoms fail, propagating conditional penalties downstream without halting the entire cascade.

### 3. Result Projector
Implements the `ResultProjector` abstraction. `ResultProjector` uses Kahn's topological sort algorithm to enforce a stable topological iteration order over the evaluated nodes. 

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
2. `ResultProjector` compiles the dynamic results into a flat list of `AtomResultDTO` objects.
3. All static evidence (`source_quote`, `resolved_claim`) is offloaded to the O(1) Dictionary `hydrated_references` using `HydratedAtomDTO`, keyed by its Opaque Stripe ID (`tda_id`).

This avoids repetitive nested tree logic and guarantees 100% ICU Markdown serialization parity for the Frontend.
