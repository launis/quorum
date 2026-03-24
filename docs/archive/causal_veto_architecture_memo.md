# Architectural Memo: The Dangers of a Naive Causal Veto

## 1. The Core Philosophical Dilemma
The user raised an essential question: **What happens if the final product is actually excellent (it does exactly what the reflection claims), but the explicit `CHAT_LOG` doesn't show the user directly asking for it? And what happens when complex external files are involved?**

A blind implementation of a "Fail-Fast Zero Score" (`final_score` = 0.0) based purely on a mismatch between the `CHAT_LOG` and the `REFLECTION_TEXT` introduces significant risks in a modern, context-rich environment like Cognitive Quorum.

## 2. Analysis of the Edge Cases

### Edge Case A: "Good Artifact, Fake Genesis" (The Accidental Genius)
*   **Scenario:** The user types "Tee eepos" (Make an epic). The AI, relying on system prompts and training, generates a masterpiece. The user's reflection claims: *"I carefully steered the AI using Socratic questioning and iterative feedback loops to shape this epic."*
*   **The Problem:** The final output is genuinely a masterpiece. However, the user is lying about *how* it was achieved (Post-Hoc Rationalization).
*   **The V2 Architecture View:** Cognitive Quorum is designed for **Process Integrity**, not just Output Quality. If an audit framework allows a user to claim credit for a process they didn't execute, the audit is flawed.
*   **Conclusion:** The deception *should* be heavily penalized, but completely nullifying a brilliant artifact (0.0) might destroy faith in the system. A "Truth Penalty" (-50%) might be more appropriate than a "Fatal Veto".

### Edge Case B: The Multi-File Causality (The Silent Context)
*   **Scenario:** The user uploads a dense 50-page PDF (`Sitra_Megatrends.pdf`), a JSON API spec, and says in chat: "Apply the framework to the data." The AI executes perfectly. The user's reflection states: *"I guided the logic applying the Arrow-Indicator paradigm from the Sitra report."*
*   **The Problem:** The Causal Analyst agent looks at the `CHAT_LOG` = "Apply the framework to the data." It looks at the `REFLECTION_TEXT` = "I guided the logic applying the Arrow-Indicator paradigm." A strict Causal Analyst will flag this as a **LIE** (Post-Hoc Rationalization) because the words "Arrow-Indicator" aren't in the chat log.
*   **The Truth:** The user isn't lying. The causality existed in the **ambient context** (the injected files/RAG data), not in the explicit conversational utterances.
*   **Conclusion:** If we implement a hard 0.0 Veto without arming the `Causal Analyst` with the ability to read and comprehend *every single injected file* as part of the causal chain, we will generate massive amounts of **False Positives** (punishing honest users for implicit context dependencies).

## 3. Recommendations & Path Forward

Before changing a single line of code in `backend_v2/hooks/scoring.py` or altering the scoring math, we must address the Intelligence tier:

1.  **Do Not Implement the 0.0 Veto Yet:** It is too brittle. In a real-world scenario with multiple RAG files, the `Causal Analyst` will unfairly penalize implicit context usage.
2.  **Redefine the Penalty (The "Integrity Tax"):** Instead of a Veto, we should retain `settings.scoring_post_hoc_penalty` (e.g., a 30% drop). This sends a signal ("We doubt your claimed methodology") without destroying the value of a potentially good final artifact.
3.  **Upgrade the Causal Analyst's Context:** If we ever want a true "Veto", the `Causal Analyst` prompt block in `seed_data.json` must be upgraded. It must be explicitly instructed: *"Before declaring a claim Post-Hoc, you MUST verify if the claimed logic could have originated from any provided input files (JSON, PDF, TXT), not just the raw chat log."*

Waiting for your thoughts on this philosophical and architectural framing.
