# Cognitive Orchestration Engine

## 1. Executive Summary
The **Cognitive Orchestration Engine** capability is the "Brain" of the Compound AI System. It is responsible for taking the static ontology from the database (PromptBlocks), combining it with user input, and executing it against external LLM providers (e.g., Google Vertex AI). This capability is heavily optimized for speed, deterministic output, and fault tolerance, utilizing parallel execution patterns and provider-agnostic caching topologies to eliminate the common pitfalls of naive LLM integration.

## 2. Core Architectural Invariants (The Laws)

These absolute rules (Knowledge Items) govern the global context and must NEVER be violated:

### 2.1. TDA Best-Of-Three Flash (Consensus Architecture)
- **Law:** The system forbids relying on a single, massive, slow "Pro" model call for critical reasoning or evaluation tasks due to high latency and failure rates.
- **Enforcement:** The engine utilizes a parallelized "Best-of-Three" consensus mechanism using fast, lightweight models (e.g., Gemini 2.5 Flash). Three identical prompts are dispatched concurrently. The system then aggregates the responses and enforces a strict 2/3 majority vote to determine the final output. This achieves 98%+ self-consistency while drastically reducing timeout crashes.

### 2.2. Provider-Agnostic Caching Topology (Static-First)
- **Law:** The system must maximize LLM Context Caching (Prompt Caching) hit rates to reduce token costs and latency, regardless of the underlying LLM provider (Anthropic, OpenAI, or Vertex AI).
- **Enforcement:** The PromptCompiler MUST assemble LLM payloads using a strict "Static-First" topology. All static components (System Instructions, Knowledge Items, Performative Lexicons) are compiled and placed at the absolute beginning of the prompt. All highly dynamic variables (User Queries, Opaque IDs, short-lived tokens) are appended at the absolute end. The caching layer generates deterministic **composite hash signatures** (SHA-256) of the static components to identify cache hits globally across the Orchestrator without relying on transient request IDs. Furthermore, cache lifecycle management (pre-caching and teardown) MUST be hoisted to the Orchestrator level (e.g., `EnrichedDagExecutor`) to prevent early cache destruction during parallel TaskGroup execution.

### 2.3. Unified Model Multiplexing
- **Law:** Business logic must never be hardcoded to a specific model version (e.g., `gemini-2.5-pro`).
- **Enforcement:** The orchestration engine routes all LLM requests through a dynamic Model Registry defined in the central static data vault. Operations request logical model tiers (e.g., "fast", "deep", "synthesis") rather than physical model names. This allows administrators to hot-swap models globally without altering a single line of Python code.

### 2.4. Data Ingestion & RAG Preflight
- **Law:** The engine must handle dynamic external context gracefully.
- **Enforcement:** The orchestrator utilizes a suite of Data Ingestion Providers (including Document Extraction, Web Fetching, File Drivers, and Flatteners) to acquire raw context. Before passing this context to the LLM, the system performs RAG Preflight Cache Pagination to optimize token usage and ensure context windows are not exceeded.

### 2.5. Two-Pass Atomization & Execution
- **Law:** Complex workflows require iterative decomposition and execution.
- **Enforcement:** The orchestrator employs Two-Pass Atomization to break down high-level tasks into atomic steps. These atomic units are then routed through a DAG (Directed Acyclic Graph) Engine, ensuring dependencies are resolved correctly before dispatching to the Cognitive Execution Engines (such as TDA and Synthesis engines).

### 2.6. Background Execution & Asynchronous Workers
- **Law:** Heavy cognitive executions must never block the synchronous HTTP request-response cycle.
- **Enforcement:** The system strictly decouples API entry points from LLM execution utilizing an asynchronous background worker. The synchronous FastAPI routes must instantly return an `Execution ID` or a `202 Accepted` status. The orchestration DAG, LLM multiplexing, and heavy synthesis are executed asynchronously by the worker pool, reporting state progression back via the `ExecutionStatus` enum.

### 2.7. Sensor Caching Parity (Matrix vs. Regular TDA)
- **Law:** Context Caching topology must remain intact and O(1) highly efficient even when evaluating disparate structures (Regular TDA vs. Matrix Assertion TDA).
- **Enforcement:** The `MatrixSensorPromptBuilder` enforces structural caching parity by compiling all global logic, Matrix Context, and the massive source document text into the static `build_caching_prefix()`. Highly dynamic, batch-specific data (e.g., matrix assertions wrapped in CDATA encapsulation) are strictly isolated into the dynamic execution parameters. This guarantees that parallel evaluations across the same document reliably hit the Context Cache, avoiding token waste and latency.

### 2.8. Synthesis Payload Compression & Explanation Synthesis
- **Law:** The orchestrator must never send raw, unfiltered DAG evaluation context or unstructured ingestion documents directly into text synthesis generation, nor generate biased or starved syntheses.
- **Enforcement:** Before data is passed to the Synthesis Phase, execution context is distilled into structured, compressed payloads. The pipeline purges heavy raw keys and internal runtime metadata blocks (such as hydrated references, atom quotes, and runtime execution signatures), truncates quotes and reasoning texts according to centralized configuration thresholds, and strictly validates distilled evaluation models. When evaluation ceilings are configured, the Token Shield protocol stratifies evaluations by allocating 70% of the budget to critical deficits and failed evaluations with exact evidentiary backing, allowing dynamic spillover for passed evaluations, and finalizing with a canonical sort for deterministic JSON serialization; when unbounded mode is configured, all valid evaluations are forwarded without truncation. In parallel, synthesis prompt distillation filters source steps according to declarative workflow step rules, preventing upstream raw document ingestion steps from polluting text synthesis prompts. Furthermore, claim curation employs ranked round-robin selection with candidate pre-deduplication to guarantee fair multi-category representation without category starvation, and resolves explanation thresholds via tripartite configuration resolution (output profile overrides taking precedence over global system defaults).

## 3. Logical Data Flow
```mermaid
flowchart TD
    A[Trigger / Workflow Step] --> B[PromptCompiler]
    B --> C[Fetch Static PromptBlocks & KIs]
    B --> D[Fetch Dynamic Variables]
    C --> E[Assemble Static-First Payload]
    D --> E
    E --> F{Model Multiplexer}
    F -- Logical Tier 'Fast' --> G[Parallel Dispatch x3]
    G --> H[Vertex AI / Gemini Flash]
    H --> I[Consensus Aggregator (2/3 Vote)]
    I --> J[Return Deterministic Result]
```


