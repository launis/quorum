# Agnostic Matrices & Semantic Routing

## Overview
Historically, evaluation matrices within the Quorum framework carried hardcoded execution restrictions mapping directly to specific prompt roles (e.g., `REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks.`). While this prevented the AI from analyzing its own output as evidence of human performance, it tightly coupled the evaluation logic (the "measuring stick") to a specific document format (`ai:` vs `user:` split chat logs).

## The Agnostic Matrix Pattern
Under the **Agnostic Matrices** architectural pattern, all hardcoded `target 'ai:' block` or `BANNED SOURCES: 'user:'` directives have been stripped from the actual assertions (atoms). The matrices are now purely objective measuring sticks detailing *what* constitutes compliance or cognitive value, divorced from *where* that evidence comes from.

## Semantic Routing via Output Profiles
To prevent collisions (e.g., scoring the AI's output instead of the human's), the routing and source-targeting logic is now handled exclusively at the **Input Configuration Level** via `ai_description`.

For example, when evaluating a **Chat Log** (`chat_log`), the system injects the following context-specific instruction, dynamically steering the Agnostic Matrices to only evaluate the human:

```text
--- AI INSTRUCTION FOR THIS SOURCE (chat_log) ---
PROCESS EVIDENCE DIRECTIVE: This artifact contains the chronological dialogue unspooled between the human operator and the AI system leading up to the final product. You must analyze this strictly for developmental trajectory, cognitive dependencies, prompt compliance, and the balance of intellectual labor. Do not treat this as the final product itself, but rather the scaffolding that built it.

MANDATE_HUMAN_EVALUATION: You must evaluate ONLY the human user's cognitive level, steering skills, and domain expertise. 

EXTRACTION_RULE: You MUST extract 'exact_quote' evidence STRICTLY from lines starting with "user:". 

CONTEXT_RULE: Text starting with "ai:" is strictly background context. NEVER use the AI's output, intelligence, or reasoning as evidence of the human's competence.
```

This ensures that:
1. Input files of any format (not just `user:`/`ai:` splits) can be evaluated.
2. The core evaluation matrices remain pure, reusable, and abstract.
3. Arkkitehtuuri ei joudu ristiriitaan itsensä kanssa, kun eri syötteillä on eri rakenne.

By treating the matrices as agnostic, Quorum allows Admin Studio to orchestrate complex evaluations cleanly.
