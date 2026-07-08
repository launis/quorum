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
- **Enforcement:** The PromptCompiler MUST assemble LLM payloads using a strict "Static-First" topology. All static components (System Instructions, Knowledge Items, Performative Lexicons) are compiled and placed at the absolute beginning of the prompt. All highly dynamic variables (User Queries, Opaque IDs, short-lived tokens) are appended at the absolute end. This ensures prefix-matching cache survival, maintaining a >95% cache hit rate.

### 2.3. Unified Model Multiplexing
- **Law:** Business logic must never be hardcoded to a specific model version (e.g., `gemini-2.5-pro`).
- **Enforcement:** The orchestration engine routes all LLM requests through a dynamic Model Registry defined in `seed_data.json`. Operations request logical model tiers (e.g., "fast", "deep", "synthesis") rather than physical model names. This allows administrators to hot-swap models globally without altering a single line of Python code.

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

## 4. Physical Implementation Map (Auto-Generated)
> **Note:** This section is automatically maintained by the Tier 7 execution agent. Do not manually update physical file paths here.
- **Backend Entrypoints:** `backend_v2/services/orchestrator/prompt_compiler.py` (Static-First Assembly), `backend_v2/services/orchestrator/dag_compiler.py` & `backend_v2/services/orchestrator/dag_executor.py` (DAG Engine), `backend_v2/services/orchestrator/context_router.py` (Context Routing), `backend_v2/services/llm_task_executor.py` (Best-Of-Three Consensus), `backend_v2/llm/client.py` (Model Multiplexer), `backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py` (Dependency Injected Ontology Context), `backend_v2/services/mcp/mcp_tool_loop.py` & `backend_v2/services/mcp/dispatcher.py` (MCP Tool Execution Loop).
- **Frontend Consumers:** This capability is strictly backend-driven; the Frontend consumes synthesized results via `client_app_v2/lib/core/api/execution_client.dart`.
