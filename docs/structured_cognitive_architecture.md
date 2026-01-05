# Cognitive Quorum: A Data-Driven Architecture for Robust Multi-Agent Reasoning (V2.5)

## Abstract

This document outlines the **Cognitive Quorum**, a structured cognitive architecture designed to resolve the fundamental tension between the stochastic, generative nature of Large Language Models (LLMs) and the deterministic, reliable requirements of production software. The architecture achieves this by separating cognitive logic ("The Mind") from procedural execution ("The Spine"), now enhanced with **Asynchronous Distributed Processing** in V2.5.

## Architectural Principles

### The Mind (Dynamic Layer)
*   **Source:** `seed_data.json` / Firetore.
*   **Components:** Prompts, Mandates (`MANDATE_1`), Methods (`METHOD_1`).
*   **Role:** Defines the *strategy* of reasoning. Configurable without code changes.

### The Spine (Static Layer)
*   **Source:** Python Code (`backend/agents/`, `backend/models/`).
*   **Components:** Agent Classes, Pydantic V2 Models (`typing.Annotated`), Arq Workers.
*   **Role:** Defines the *structure* of data and execution. Enforces type safety, manages async concurrency, and provides observability via **Logfire**.

## The Cognitive Assembly Line (`sequential_audit_chain`)

The system processes information through a pipeline of specialized agents:

### 1. Vartija (Guard Agent)
**Role:** Security Gateway.
Mitigates prompt injection and ensures PII privacy via `Presidio` hooks.

### 2. Analyytikko (Analyst Agent)
**Role:** Data Structuring.
Transforms raw input into a grounded `EvidenceMap`, mitigating hallucination via "Chain of Trust".

### 2.2. Vuorovaikutusanalysaattori (Interaction Analyst)
**Role:** Dynamic Control Assessment.
Determines if the user is a "Driver" (Active) or "Passenger" (Passive) in the process.

### 2.5. Profiloija (Profiler Agent)
**Role:** Cognitive Bias Detection.
Identifies psychological profiles and cognitive biases in the source text.

### 3. Loogikko (Logician Agent)
**Role:** Argument Mapping.
Constructs Toulmin arguments (Claim, Data, Warrant) to expose logical structure.

### 4. Falsifioija (Falsifier Agent)
**Role:** Stress Testing.
Acts as "Devil's Advocate" (Popperian Falsification) to find internal contradictions.

### 5. Valvoja (Overseer Agent)
**Role:** Fact & Ethics.
Verifies factual accuracy (Google Search) and ethical alignment.

### 6. Kausaalinen Analyytikko (Causal Agent)
**Role:** Causal Inference.
Distinguishes correlation from causation using `DoWhy` refutation tests.

### 7. Performatiivisuuden Tunnistaja (Detector Agent)
**Role:** Anti-Gaming.
Detects manipulative rhetoric or "fluff" designed to bias the system.

### 8. Arkistonhoitaja (Archivist Agent)
**Role:** Context Retrieval.
Connects the current case to historical precedents via Vector RAG Search.

### 8c. Valmentaja (Coach Agent)
**Role:** Pedagogical Feedback.
Provides actionable advice to the user on improving their reasoning.

### 9. Tuomari (Judge Agent)
**Role:** Adjudication.
Synthesizes all critiques into a final Verdict using a strict scoring matrix.

### 10. XAI-Raportoija (XAI Reporter)
**Role:** Transparency.
Generates a human-readable, explainable report documenting the entire decision chain.

## Reasoning Continuity Architecture (V2.5)

To maintain high-level cognitive coherence across multiple agent turns, the system implements a **Dual-Layer Reasoning Trace** mechanism.

### The Challenge: Statelessness vs. Context
LLMs are inherently stateless. When `AnalystAgent` finishes and `JudgeAgent` begins, the specific "train of thought" that led to the analysis is typically lost, leaving only the final JSON output.

### Solution: Thinking Tokens & Explicit Traces

1.  **Reasoning Models (Gemini 2.5 Thinking)**: 
    *   **Mechanism**: The model generates a "Show Your Work" trace (`thought` signature) alongside the JSON.
    *   **Persistence**: We capture this trace and store it in `WorkflowState.reasoning_context`.
    *   **Transfer**: It is passed to the next agent, allowing it to "see" the logic that led to the conclusion.

2.  **Standard Models (Gemini Flash/Pro)**:
    *   **Mechanism**: Explicit Chain-of-Thought (CoT) text generation via `thought` field in JSON.
    *   **Persistence**: Stored in `state.last_reasoning_trace`.
    *   **Transfer**: Injected into the next prompt as text.

This approach ensures transparency and high-fidelity reasoning transfer regardless of the underlying model capability.

## Verification & Self-Correction

The system employs a **Monolithic Validation Loop**:

1.  **Schema Injection**: The engine injects the Pydantic V2 JSON Schema into the prompt.
2.  **Hard Validation**: LLM output is parsed against the strict `Annotated` model.
3.  **Heuristic Repair**: If JSON is malformed, a lightweight regex repair is attempted.
4.  **Self-Correction**: If repair fails, validation errors trigger an automatic retry, forcing the LLM to fix its own formatting mistakes.

This guarantees that the input to Step N+1 is always valid data produced by Step N.