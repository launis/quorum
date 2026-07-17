# Quorum Core Architecture & Invariants

## 1. Executive Summary
The Quorum Compound AI System operates as a high-precision, strict "Zero-Compromise" orchestration engine designed for deep semantic contract, regulatory, and policy analysis. The architecture operates at the bleeding edge of enterprise AI, eschewing traditional flat-text retrieval (standard RAG) in favor of a deterministic, causal graph evaluation pipeline backed by infinite context caching. The system is designed under the philosophy that AI should act as a rigorous reasoning engine rather than a probabilistic chatbot, ensuring 100% auditable and forensic outputs.

## 2. Core Architectural Principles (The Invariants)

### 2.1 The Zero-Compromise Pledge & Universal Fail-Fast
- **Strict Boundaries:** All data entering or leaving the system boundary must be strictly validated against immutable, strictly typed schemas. 
- **SSOT Model Location Sovereignty:** All domain structures and strict data models (e.g., data payloads, blackboards) MUST reside exclusively in dedicated domain modeling modules. Inline model definitions within orchestration layers are strictly banned to preserve the Single Source of Truth (SSOT).
- **Fail-Fast & Dual-Reporting:** The system strictly prohibits "duct-tape" programming, silent error absorption, or returning empty/null values to mask failures. If an expected logical state is not reached, the system MUST first emit a structured forensic log (The Dual-Reporting Protocol) to capture the exact failure context, and then crash immediately to preserve forensic sovereignty and prevent data corruption.
- **The DLQ Isolation Exception (Transient Failures):** The system strictly distinguishes between rigid logical data schema violations (which MUST Fail-Fast and crash immediately) and transient network/LLM latency issues. Raising a naked exception for a transient failure inside a parallel execution block would catastrophically cancel all sibling tasks, destroying hours of valid LLM processing. Therefore, transient network/LLM failures in background workers MUST be caught and securely routed to a Dead Letter Queue (DLQ). This DLQ routing is explicitly exempt from the duct-tape prohibition, as it preserves forensic evidence without tearing down the entire execution DAG.

### 2.2 Global Configuration Sovereignty & Model Multiplexing
- **Tripartite Configuration Architecture:** Execution limits, API timeouts, and token constraints are NOT governed by a vague master layer. They MUST be explicitly segregated using a Tripartite structure (rigid state logic, operational thresholds, and structural data shapes). This ensures absolute segregation between environmental, operational, and business parameters.
- **Model Agnosticism & Unified Multiplexing:** The underlying AI models are entirely decoupled from the business logic. Developers are STRICTLY BANNED from making direct provider SDK integrations. Execution strategies MUST request logical capabilities via a centralized multiplexer (using mapped strategies from the primary configuration database), allowing the system to hot-swap AI providers seamlessly without structural changes.

### 2.3 Strict Physical Anchoring (Zero Hallucination) & The Null Hypothesis
- **Deterministic Anchoring:** Generative AI responses must be structurally mapped to explicit, verbatim quotes. The engine verifies the existence of this quote via a strict, deterministic physical anchoring algorithm against the original document. Fuzzy matching is strictly banned as it permits hallucinations to bypass the quality gate.
- **Evidence Sovereignty:** If an AI-generated quote is hallucinated or modified by even a single character, the engine rejects the entire logical claim as a Semantic Evidence Error.
- **The Null Hypothesis Rule:** While physical anchoring is strict, the system acknowledges that some facts are deduced purely logically (e.g., "The contract does not mention X"). In these cases, the AI is permitted to invoke a logical deduction flag, which intentionally forces the quote to a null state, indicating a deduced state rather than a physically quoted state.

## 3. Cognitive Orchestration & The RAG Pipeline

The execution architecture abandons arbitrary vector embeddings and semantic chunk retrieval in favor of a highly optimized **Dual-Input Synthesis Pipeline**.

### 3.1 Phase 1: The Global Extraction Node (Pre-Flight Analysis)
Before any individual analysis or evaluation step begins, the system processes the raw document once globally to establish a baseline truth:
- **Two-Pass Atomization:** The document is systematically parsed to extract "Atoms" (independent, self-contained claims and rules). This atomization MUST occur exclusively via structured execution blocks to strictly eradicate legacy syntactic self-healing extraction loops. 
- **Sliding Window Linker:** The system establishes causal dependencies (edges) between these atoms, resolving linguistic anaphoras (e.g., pronouns referencing prior entities) and creating a comprehensive **Enriched Causal Graph**.
- **The Knowledge Blackboard:** The extracted, causally linked atoms are locked into an immutable state model known as the Knowledge Blackboard. This serves as the absolute, centralized fact repository for the duration of the execution. The Blackboard guarantees mutation-proof execution, with payloads deliberately constrained to fit within standard embedded database limits (preventing the need for complex external cloud storage offloading during state iterations).
- **Virtual Step Runtime Injection:** To maintain UI liveliness during heavy global processing without polluting the persisted admin configuration, the orchestrator injects ephemeral Virtual Steps directly into the runtime state. This follows established patterns and ensures the Presentation Layer has a valid rendering target without altering the underlying blueprint.

### 3.2 Pre-Hydrated Synthesis Strategy & Ephemeral Caching Topology
- **Dual-Input Context:** When individual analytical evaluation steps trigger, they no longer scan the raw text. The AI prompt is populated strictly with the distilled factual map from the Knowledge Blackboard. Simultaneously, the complete, raw original document remains dormant in the AI provider's **Native Context Cache** (The Encyclopedia).
- **Ephemeral Caching Topology:** To prevent cache busting and FinOps cost explosions, the prompt MUST adhere strictly to the Ephemeral Caching Topology: The System Prompt must be 100% static. All dynamic variables (e.g., the specific user query or extracted atoms) MUST be appended exclusively at the absolute end. This guarantees maximum cache hit survival across consecutive steps.
- **O(1) Execution Efficiency:** By feeding a mathematically clean graph to the AI, the system slashes the required number of concurrent AI calls by over 85%. This completely eliminates provider rate-limiting bottlenecks while maintaining 100% contextual depth and nuance.

## 4. Execution Graph & Topological Evaluation

### 4.1 The Topological Evaluator
The Topological Evaluator acts as the singular source of truth for traversing and resolving the Directed Acyclic Graph (DAG) of the extracted contract logic:
- **Structured Concurrency:** The evaluator strictly mandates Structured Concurrency paradigms for parallel node evaluation. Ambiguous "fire-and-forget" event loops or detached promises without fail-fast cancellation are strictly banned. Because a worker crash inside a concurrent block normally cancels the entire DAG execution, the system enforces strict Dead Letter Queue (DLQ) routing to safely isolate failures. Circular dependencies and infinite loops are detected and rejected deterministically via a pre-flight mathematical depth-first search.
- **Conditional Short-Circuiting (The N/A Cascade):** If a parent requirement is evaluated as mathematically `FAILED` (the condition is not met in the text), all dependent child nodes immediately short-circuit to a `Not Applicable` state. This prevents the system from wasting computational resources analyzing clauses that are logically irrelevant based on prior conditions.

### 4.3 Best-Of-Three Flash Consensus
For highly sensitive, binary boolean evaluations (e.g., "Is this clause compliant?"), the system dynamically escalates from a single prompt to a **Best-of-Three (Bo3) Consensus Architecture**. Three lightweight, parallel AI instances cast independent votes. A deterministic 2/3 majority is required to finalize the logical status.
- **Ensemble Parallel Evaluation Mandate:** Launching 3 parallel instances dynamically inside a global macro-limit pool causes catastrophic queue deadlocks if resources are constrained. To prevent this, the Best-of-Three ensemble MUST enforce a dedicated, micro-level concurrency lock per ensemble evaluation, ensuring atomic execution of the consensus block.

## 5. Memory Management & Output Representation

### 5.1 Semantic Attention Anchoring (Opaque ID Hydration)
To prevent the AI from suffering token bloat and hallucinating large database UUIDs:
- **Alias Masking:** The engine strips heavy database identifiers out of the context and replaces them with lightweight, semantic Attention Anchors.
- **Post-Hydration:** The core engine deterministically translates these anchors back to their true physical database identifiers before routing the final payload to the presentation layer. This semantic anchoring is hard-linked strictly to the centralized aliasing engine boundary to permanently prevent disparate custom extraction implementations.

### 5.2 The De-Generator Paradigm & Server-Driven UI (SDUI)
- **Agnostic Workflows:** End-users do not interact with the AI via open-ended chat prompts. Administrators define workflows using rigid matrices, which the system dynamically compiles into deterministic system prompts.
- **XML Structural Sovereignty:** Developers are STRICTLY BANNED from using raw, unstructured string interpolation to assemble LLM instructions. All generated prompts must be compiled into rigid, deterministic semantic boundaries. This structural sovereignty prevents prompt injection and is required to maintain the Ephemeral Caching Topology.
- **Hybrid Sanitization:** Interceptors sanitize all AI output to strip conversational artifacts, ensuring the payload conforms strictly to the Server-Driven UI data contracts. Backend Presentation UI generation (e.g., injecting presentation formatting styles into backend strings) is EXPLICITLY BANNED. The backend must strictly pass clean structured data objects for the Client to render.
- **Cross-Language Enumeration Parity:** Any modification to Backend Enumerations or Literal types MUST be synchronously mirrored in the corresponding Client data models. Because the UI enforces strict key validation, drifting API contracts cause catastrophic app-level validation crashes.

### 5.3 Result Projection (Flat Adjacency Lists)
To support infinite scalability in the user interface without nested tree complexities:
- **Flattened State:** The dynamic runtime states (e.g., Passed, Failed, Short-Circuited) are decoupled from the heavy text payloads. 
- **Relational Integrity:** The system outputs a flat adjacency list referencing static dictionary objects. This relational structure guarantees identical presentation logic for the core Desktop-Class Pro Tool, reporting generators, and spreadsheet exports without recursive recalculation.
