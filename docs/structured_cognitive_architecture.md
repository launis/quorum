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

## 2. Two-Level Architecture (Hybrid Rubric)
 
 The system implements a **Hybrid Rubric** designed to manage the tension between Reliability and Validity (The "Measurement Paradox"):
 
 ### Level 1: Analytical (Cognitive Assessment Matrix)
 *   **Goal**: Reliability.
 *   **Mechanism**: **BARS** (Behaviorally Anchored Rating Scales) rooted in Bloom's Taxonomy and Toulmin's Argumentation.
 *   **Focus**: The logical validity of the *process* and *artifact*.
 
 ### Level 2: Holistic (Cognitive Quorum)
 *   **Goal**: Validity (Mastery).
 *   **Mechanism**: **Multi-Agent System (MAS)** where specialized agents (Critics) challenge the consensus.
 *   **Focus**: Strategic guidance (`Agency`) and genuine insight that may break rules.
 
 ## 3. Dynamic Evaluation System (BARS)

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
    *   **Architectural Decision: Parallel Audit**: The Guard is designed as a "Sidecar Auditor" rather than a sequential filter.
    *   **Mechanism**: It returns a security status (`DATA_CHECKED_AND_SECURED`) instead of echoing the full text. This prevents "Prompt Injection Mirroring" (where an LLM inadvertently executes the attack while repeating it) and halves token costs.
    *   **Circuit Breaker**: If `threat_detected=True`, the Workflow Engine halts execution immediately via `FatalInterruption`.
*   **Tiedonhakija (Context Retrieval)**: RAG Agent executing the **Sidebar Pattern**.
    *   **Architectural Decision**: Fetches external context *before* analysis but is **NOT** connected to the Analyst.
    *   **Rationale ("Hallucination Masking")**: If the Analyst sees the "Truth" (RAG) before the "Claim" (User Input), it risks auto-correcting user errors. We keep the Analyst "blind" to ensure it captures the user's *actual* argument, enabling the Falsifier to spot discrepancies later.
    *   **Consumer**: Context is routed directly to the **Overseer** and **Judge** for fact-checking.
*   **Analyytikko (Analyst)**: Structuring raw text into an `EvidenceMap`.

### II. The Critics (Parallel Processing)
*   **Profiloija (Profiler)**: Bias detection (Sycophancy, Confirmation Bias).
*   **Loogikko (Logician)**: Toulmin Argument mapping (Claim/Warrant/Backing).
*   **Falsifioija (Falsifier)**: Popperian stress-testing of claims.
*   **Valvoja (Overseer)**: Fact-checking against Google Search results.

### III. The Synthesis (Judgement)
*   **Tuomari (Judge)**: The matrix-driven decision engine. Synthesizes critic outputs into a strict `EvaluationResult`.
    *   **Deterministic Penalty ("Passiveness Cutter")**: Implements `OP_RULE_4`. If the user is rated as a "Passenger" (Scale Minimum) in *any* dimension, the Total Score is automatically capped at the **Lower Third** of the scale.
        *   *Formula*: `Cap = Min + ((Max - Min) / 3)`.
        *   *Rationale*: A "Passenger" performance cannot mathematically exceed the "Driver" threshold (Level 3 equivalent), regardless of the scoring scale used (1-4, 1-100, etc.).
*   **Valmentaja (Coach)**: Pedagogical feedback generator. Translates scores into actionable advice.

### IV. The Reporter (Output)
*   **XAI Raportoija**: Generates the human-readable explanation. It is **Matrix-Agnostic**—it simply renders whatever dimensions the Judge scored.

---

## 5. Verification Protocols

The architecture is self-verifying via:
1.  **Pydantic Validation**: Every step output is validated against a strict schema.
2.  **Fail Fast**: The system prefers to crash (raising a clear error) rather than guessing at malformed data.
3.  **Retry Loop**: Infrastructure (Tenacity) handles transient failures, but logic errors are fatal.