# Cognitive Quorum: A Data-Driven Architecture for Robust Multi-Agent Reasoning (V2.0)

## Abstract

This document outlines the **Cognitive Quorum**, a structured cognitive architecture designed to resolve the fundamental tension between the stochastic, generative nature of Large Language Models (LLMs) and the deterministic, reliable requirements of production software. The architecture achieves this by separating cognitive logic ("The Mind") from procedural execution ("The Spine").

## Architectural Principles

### The Mind (Dynamic Layer)
*   **Source:** `seed_data.json` / Database.
*   **Components:** Prompts, Mandates (`MANDATE_1`), Methods (`METHOD_1`).
*   **Role:** Defines the *strategy* of reasoning. Configurable without code changes.

### The Spine (Static Layer)
*   **Source:** Python Code (`backend/agents/`, `backend/models/`).
*   **Components:** Agent Classes, Pydantic V2 Models (`typing.Annotated`).
*   **Role:** Defines the *structure* of data and execution. Enforces type safety.

## The Cognitive Assembly Line (`sequential_audit_chain`)

The system processes information through a pipeline of specialized agents:

### 1. Vartija (Guard Agent)
**Role:** Security Gateway.
Mitigates prompt injection and ensures PII privacy via `Presidio` hooks.

### 2. Analyytikko (Analyst Agent)
**Role:** Data Structuring.
Transforms raw input into a grounded `EvidenceMap`, mitigating hallucination via "Chain of Trust".

### 3. Arkistonhoitaja (Archivist Agent)
**Role:** Context Retrieval.
Connects the current case to historical precedents via Vector RAG Search.

### 4. Loogikko (Logician Agent)
**Role:** Argument Mapping.
Constructs Toulmin arguments (Claim, Data, Warrant) to expose logical structure.

### 5. Falsifioija (Falsifier Agent)
**Role:** Stress Testing.
Acts as "Devil's Advocate" (Popperian Falsification) to find internal contradictions.

### 6. Kausaalinen Analyytikko (Causal Agent)
**Role:** Causal Inference.
Distinguishes correlation from causation using `DoWhy` refutation tests.

### 7. Performatiivisuuden Tunnistaja (Detector Agent)
**Role:** Anti-Gaming.
Detects manipulative rhetoric or "fluff" designed to bias the system.

### 8. Valvoja (Overseer Agent)
**Role:** Fact & Ethics.
Verifies factual accuracy (Google Search) and ethical alignment.

### 9. Paneeli (Panel Agent)
**Role:** Synthesis & Optimization.
Simulates a simultaneous review by multiple experts (Logic, Causal, Ethics) for efficiency.

### 10. Tuomari (Judge Agent)
**Role:** Adjudication.
Synthesizes all critiques into a final Verdict using a strict scoring matrix (`BARS_MATRIX`).

### 11. Valmentaja (Coach Agent)
**Role:** Pedagogical Feedback.
Provides actionable advice to the user on improving their reasoning.

### 12. XAI-Raportoija (XAI Reporter)
**Role:** Transparency.
Generates a human-readable, explainable report documenting the entire decision chain.

## Reasoning Continuity Architecture

To maintain high-level cognitive coherence across multiple agent turns, the system implements a **Reasoning Trace** mechanism.

### The Challenge: Statelessness vs. Context
LLMs are inherently stateless. When `AnalystAgent` finishes and `JudgeAgent` begins, the specific "train of thought" that led to the analysis is typically lost, leaving only the final JSON output. This "Information Loss" degrades the quality of subsequent judgments.

### Solution: Explicit Chain-of-Thought (CoT) Transfer
Cognitive Quorum implements a **Hot Potato** state mechanism for reasoning:

1.  **Generation:** Every agent is instructed to produce a `reasoning_trace` (a step-by-step internal monologue) *before* generating its final structured output.
2.  **Capture:** The `BaseAgent` infrastructure automatically extracts this trace from either:
    *   **Native Metadata:** Provider-specific fields (e.g., `reasoning_token` for reasoning models).
    *   **Structured Payload:** The `reasoning_trace` field within the JSON response (for standard models like Gemini 1.5/3).
3.  **Transient Storage:** The trace is stored in `state.last_reasoning_trace`.
4.  **Injection:** The next agent in the pipeline receives this trace in its system prompt: *"The previous agent's internal reasoning was: [TRACE]"*.

### Trade-off: Explicit Trace vs. Native Thought Signatures
While models like Gemini 3 offer "Thought Signatures" (encrypted opaque tokens representing internal state), Cognitive Quorum prioritizes **Explicit Textual Traces** because:
*   **Model Agnostic:** Works across OpenAI, Google, and Anthropic models seamlessly.
*   **Auditable:** The reasoning is human-readable and logged for XAI purposes.
*   **Cross-Role Compatible:** `AnalystAgent` (Gemini) can pass reasoning to `JudgeAgent` (GPT-4) without compatibility issues.

This explicit mechanism ensures that the "Mind" of the system maintains a coherent stream of consciousness throughout the "Assembly Line".

## Verification & Self-Correction

The system employs a **Monolithic Validation Loop**:

1.  **Schema Injection:** The engine injects the Pydantic V2 JSON Schema into the prompt.
2.  **Hard Validation:** LLM output is parsed against the strict `Annotated` model.
3.  **Self-Correction:** Validation errors trigger an automatic retry, forcing the LLM to fix its own formatting mistakes.

This guarantees that the input to Step N+1 is always valid data produced by Step N.