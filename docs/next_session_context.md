# Next Session Context: Hardening the Cognitive Quorum Evaluators

**Goal of Next Session:**
To address the "Lenient Evaluator Problem." In recent tests, evaluating agents (Judge, Profiler, Logician) awarded perfect scores (100.0) based solely on the user's *claims* in the `REFLECTION_TEXT`, ignoring the actual low quality of the explicit `CHAT_LOG`. We need to figure out why the "judges let the user off too easily" and how to fix it without destroying the system's ability to recognize genuinely good outputs derived from complex RAG data.

---

## 1. The Triggering Event ("The Accidental Genius Fraud")
*   **The Setup:** The user provided a deliberately sparse chat log ("Write an epic") but a highly sophisticated, false reflection ("I used advanced Socratic methods...").
*   **The Result:** The system generated a great output based on system prompts, but the user lied about their process.
*   **Agent Behavior:**
    *   **Failed (Too Lenient):** `Judge`, `Profiler`, and `Logician` gave full points because they were easily manipulated by the eloquent reflection. They lacked skepticism.
    *   **Succeeded (Critical):** The `Causal Analyst` correctly caught the post-hoc rationalization and gave a failing grade (33.3) because the claimed logic didn't exist in the chat log.
*   **The Problem:** The final score was still high (70.4) because the naive mathematical average (`scoring.py`) masked the single critical failure.

## 2. Key Files & Components to Bring Over

### A. The Prompts (`backend_v2/seed/seed_data.json`)
The leniency problem is fundamentally a prompt engineering issue. We need to examine the specific `PromptBlock` definitions for the evaluating agents:
*   `promptblock_matrix_judge`
*   `promptblock_matrix_bloom`
*   `promptblock_matrix_toulmin`
*   `promptblock_matrix_profiler`
*   *Why?* Because currently, these prompts likely lack explicit instructions like: *"Be skeptical of claims. Verify that the user's claimed strategy actually matches their explicit commands."*

### B. The Scoring Logic (`backend_v2/hooks/scoring.py`)
*   *Why?* We need to refer to how the `apply_scoring_logic_hook` calculates the "Commensurate Average" across the 5 matrices.

### C. The Philosophical Memo (`docs/causal_veto_architecture_memo.md`)
*   *Why?* We just wrote this. It explains the danger of a strict "0.0 Veto" and why we distinguish between "Output Quality" (the epic is good) and "Process Integrity" (the user lied about how they made it).

## 3. Initial Questions to Launch the Next Session
1.  **Prompt Hardening vs. System Hardening:** Should we fix the leniency by making every single Judge prompt more skeptical ("Prompt Hardening"), or should we fix it structurally by weighting the Causal Analyst heavier in `scoring.py` ("System Hardening")?
2.  **The RAG Blindspot:** How do we train the evaluating agents to distinguish between "The user is lying about their process" and "The user is silently relying on a 50-page PDF context"?
3.  **BARS Scaling Limits:** Are the evaluating agents defaulting to `10.0` or `100.0` because the prompt doesn't give them a clear enough "Reason to Penalize"?

---
*Copy-paste the contents of this file into the first prompt of your new context window.*
