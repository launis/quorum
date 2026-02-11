# Cognitive Quorum: Structured Cognitive Architecture (V2.9)

## Abstract

**Cognitive Quorum V2026** is a data-driven cognitive architecture designed to produce deterministic, high-fidelity reasoning from stochastic LLMs. It separates the **Cognitive Strategy** (JSON-defined logic) from the **Execution Spine** (Python-defined flow).

The V2.9 iteration enforces a **Unidirectional Data Flow** where the "DNA" of the system (Evaluation Matrices, Prompts) is immutable code, seeded into the database to drive execution.

---

## 1. The Core Architecture

### A. The "Spine" (Execution Layer)
*   **Role**: Orchestration, State Management, and Type Enforcement.
*   **Implementation**: `backend/core/engine.py`, `backend/models/state.py`.
*   **Key Feature**: **Strict Object Mode**. Data is passed between agents as strictly typed Pydantic V2 models (`EvaluationResult`, `XAIReport`), never as loose dictionaries.

### B. The "Mind" (Cognitive Layer)
*   **Role**: Reasoning Strategy and Criteria.
*   **Implementation**: `seed_data.json` -> Database -> Agents.
*   **Components**:
    *   **Mandates**: "Thou shalt not hallucinate."
    *   **Matrices (BARS)**: "What is a score of 4 vs 1?"
    *   **Prompts**: "You are a ruthless prosecutor."

---

## 2. Dynamic Evaluation System (BARS)

The system uses **Behaviorally Anchored Rating Scales (BARS)** to decouple the *definition* of quality from the *code* that measures it.

### Dynamic Matrix Injection (Strict BARS)
 The `JudgeAgent` utilizes the **MatrixFormatter** service (`backend/services/matrix_formatter.py`) to convert abstract JSON criteria into high-fidelity Markdown BARS (Behaviorally Anchored Rating Scales).
 
 1.  **Reads** the `matrix_id` from the config.
 2.  **Fetches** the Matrix Component.
 3.  **Formats** the component into a detailed Markdown rubric with explicit Anchors (1-5) and specific Criteria.
 4.  **Injects** this immutable rubric into the System Prompt.

> **Strict Scale Enforcement**: The Judge Agent enforces the specific min/max scale defined in the DB. If the LLM generates a score outside this range, the agent effectively crashes (fail-fast) rather than guessing.

### Autonomous Evidence Discovery
The Judge does not need to know *who* produced the evidence. It uses a **Configuration-Driven Discovery** protocol:
*   It scans the `WorkflowState` for keys defined in `monitored_steps` (e.g., `step_falsifier`, `step_profiler`).
*   It aggregates all found evidence into a "Courtroom Dossier" prompt.
*   **Benefit**: You can swap out the entire line of critics (e.g., replace `Falsifier` with a `CodeReviewer`) without changing a single line of the Judge's code.

---

## 3. Hybrid State Architecture
 
 The `WorkflowState` (`backend/models/state.py`) implements a **Hybrid State Model**:
 
 ### A. Event Log (Truth)
 *   **Execution Trace**: An append-only log of `TraceEvent` objects. This provides a perfect audit trail of every thought and decision.
 
 ### B. Blackboard Snapshot (Performance)
 *   **Context Variables**: A mutable projection of the current state.
 *   **Benefit**: Agents can read `{{PREVIOUS_STEP_OUTPUTS}}` instantly without replaying the entire history.

### Reasoning Continuity (The "Hot Potato")
To solve the statelessness of LLMs, we implement **Reasoning Trace Continuity**:
1.  **Generation**: Agent N generates a hidden `thought` or `reasoning_trace`.
2.  **Storage**: The engine encrypts/stores this trace in `state.reasoning_context`.
3.  **Transfer**: The engine passes the *previous agent's* trace to Agent N+1.
4.  **Result**: The next agent "wakes up" knowing exactly *why* the previous agent made its decision.

---

## 4. The Cognitive Assembly Line

The standard `Courtroom 2.0` workflow consists of:

### I. The Guardians (Input Processing)
*   **Vartija (Guard)**: Regex/LLM hybrid for PII stripping and Prompt Injection defense.
*   **Analyytikko (Analyst)**: Structuring raw text into an `EvidenceMap`.

### II. The Critics (Parallel Processing)
*   **Profiloija (Profiler)**: Bias detection (Sycophancy, Confirmation Bias).
*   **Loogikko (Logician)**: Toulmin Argument mapping (Claim/Warrant/Backing).
*   **Falsifioija (Falsifier)**: Popperian stress-testing of claims.
*   **Valvoja (Overseer)**: Fact-checking against Google Search results.

### III. The Synthesis (Judgement)
*   **Tuomari (Judge)**: The matrix-driven decision engine. Synthesizes critic outputs into a strict `EvaluationResult`.
*   **Valmentaja (Coach)**: Pedagogical feedback generator. Translates scores into actionable advice.

### IV. The Reporter (Output)
*   **XAI Raportoija**: Generates the human-readable explanation. It is **Matrix-Agnostic**—it simply renders whatever dimensions the Judge scored.

---

## 5. Verification Protocols

The architecture is self-verifying via:
1.  **Pydantic Validation**: Every step output is validated against a strict schema.
2.  **Fail Fast**: The system prefers to crash (raising a clear error) rather than guessing at malformed data.
3.  **Retry Loop**: Infrastructure (Tenacity) handles transient failures, but logic errors are fatal.