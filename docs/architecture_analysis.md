# Technical Architecture Validation & Analysis (V2.9)

**Status:** V2.9 / V2026 Production Standard
**Architecture:** Modular Async Monolith (Python 3.14.2 + FastAPI + Arq)

This document validates the technical architecture of the Cognitive Quorum system against the **V2026 "Zero-Magic" Manifesto**, analyzing its core strengths, data flow, and safeguards.

---

## 1. Core Pattern: Modular Async Monolith

The system rejects microservices complexity in favor of a strictly typed, distributed monolith.

### The "Spine" (Execution Control)
*   **Framework:** FastAPI (HTTP) + Arq (Redis-based Async Workers).
*   **Concurrency:** Fully Async/Await (Python 3.14.2).
*   **State Management (Hybrid):** The system implements a **Hybrid State Architecture**:
    1.  **Event Sourcing (Truth):** `WorkflowState.execution_trace` is an append-only log of immutable `TraceEvent` objects. This provides a perfect audit trail and enables time-travel debugging.
    2.  **Blackboard Snapshot (Performance):** `WorkflowState.context_variables` maintains a mutable projection of the current state for high-performance read access by agents.
*   **Strict Object Mode:** The `GraphEngine` (`backend/core/engine.py`) enforces that all data passed between agents is a validated Pydantic Object, not a loose dictionary.

### The "Mind" (Cognitive Strategy)
*   **Separation of Concerns:** Logic is defined in JSON (`seed_data.json`), not Python code.
*   **Unidirectional Data Flow:** Configuration changes (e.g., new matrix criteria) flow from `seed_data.json` -> Database -> Runtime. The runtime never mutates the configuration.

---

## 2. Distributed Sync Loop

The system solves the "Long-Running AI" problem via a detached execution loop:

1.  **Ingest (API)**: `POST /execution` pushes a job to Redis and returns `202 Accepted` immediately.
2.  **Pickup (Worker)**: Arq Worker picks up the job.
3.  **Hydrate (Engine)**: `GraphEngine` loads the full `WorkflowState` from Firestore/TinyDB.
4.  **Execute (Agent)**: The Agent runs (taking 10s - 120s), calling the LLM.
5.  **Persist (DB)**: The Engine saves the updated state to the DB.
6.  **Polling (Client)**: The Flutter client polls the DB for changes, updating the UI in real-time.

> **Resilience:** If a Worker crashes, the state is safe in the DB. The job can be retried or resumed without data loss.

---

## 3. Cognitive Assembly Line (The Agents)

Agents are specialized processors in a deterministic graph.

| Agent | Responsibility | Output Schema |
| :--- | :--- | :--- |
| **Guard** | Security & PII Redaction | `TaintedData` -> `SafeData` |
| **Analyst** | Grounding & Evidence Extraction | `TodistusKartta` |
| **Retrieval** | Organizational Grounding (RAG) | `ContextData` |
| **Interaction** | User Agency Analysis | `InteractionAnalysis` |
| **Profiler** | Bias & Intent Profiling | `ProfilerAnalysis` |
| **Logician** | Argument Structure (Toulmin) | `ArgumentaatioAnalyysi` |
| **Causal** | Impact Verification (Counterfactuals) | `CausalAnalysis` |
| **Detector** | Illusion of Control (Goodhart) | `PerformativityAnalysis` |
| **Panel** | Unified Critics (Falsifier, Overseer) | `PanelOutput` |
| **Archivist** | Best Practices Audit | `ComplianceScore` |
| **Judge** | **BARS Scoring** & Verdict | `EvaluationResult` |
| **Coach** | Technical Remediation | `CoachingPlan` |
| **Reporter** | XAI Explanation | `XAIOutput` |

---

## 4. Advanced "Zero-Magic" Features

We explicitly avoid "Magic" frameworks (LangChain, AutoGPT) in favor of explicit, deterministic code.

### A. Centralized Hook Mapping
Instead of dynamic imports or "plugin discovery", all hooks are explicitly registered in `backend/core/engine.py:HOOK_MAPPING`.
*   *Benefit:* Readable, Grep-able, Debuggable.

### B. Reasoning Token Continuity
To solve LLM amnesia, we extract the "Hidden Thinking" tokens (Gemini 1.5 Thinking) and pass them explicitly to the next agent via `state.reasoning_context`.

### C. Instructor-Based Structured Output
The system abandons regex-based repair in favor of native Structured Output (LLM-enforced Schemas).
*   **Layer 1:** `instructor` library (wrapping LiteLLM) enforces Pydantic schemas at the API level.
*   **Layer 2:** `tenacity` handles transient network failures and rate limits.
*   **Layer 3:** Strict Validation (Agents fail fast if the output cannot be coerced to the schema).

### D. High-Fidelity Matrix Formatting
The `PromptBuilder` now enforces strict BARS formatting via `MatrixFormatter`. Evaluation Matrices are converted to detailed Markdown rubrics with explicit anchor-to-scale mapping logic, ensuring the LLM understands the grading criteria precisely.

---

## 5. Scalability & Performance Analysis

### Timeout Decoupling
Standard HTTP timeouts (60s) are incompatible with Deep Reasoning (10m+).
*   **Solution:** The Async Worker model allows jobs to run for 15 minutes (`job_timeout=900s`) without the client connection dropping.

### Horizontal Scaling
*   **Stateless Workers:** You can run 1 or 100 worker nodes. They simply pull from Redis.
*   **Database Bottleneck:** Minimized by "Optimistic Locking" (`version` field) and efficient updates.

---

## 6. Verification Strategy

*   **Backend:** `pytest` + `unittest.mock` (No network calls in tests).
*   **Frontend:** `flutter_test` + `mocktail` (No code generation).
*   **Philosophy:** "Fail Fast". If the DB schema doesn't match the Pydantic model, or if a Matrix cannot be formatted, the system crashes immediately rather than corrupting data.