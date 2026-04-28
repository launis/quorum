# Epic: 100% Map-Reduce Matrix Synthesis Architecture (The "Mute Evaluator" Pattern)

## 1. Executive Summary
**Objective:** Transition the Quorum V2 reporting pipeline to a strict Map-Reduce architecture for **Matrix Justifications**. 
Currently, the LLM evaluates atoms and writes justifications simultaneously during the "Map" phase. For massive matrices (like Toulmin), this requires chunking, resulting in disjointed "Frankenstein" text when chunks are concatenated. 
This Epic decouples the evaluation math from the narrative writing. The atomic evaluators will become "Mute" (returning only math and booleans), and the "Chief Editor" (Synthesis Hook) will write all final matrix justifications in a single pass based on the calculated hit rates.

## 2. Business Value
* **Eliminates Chunking Artifacts:** No more glued-together, contradictory sentences.
* **Maximizes Accuracy:** Allows `LLM_MAX_CHUNK_SIZE` to be lowered (e.g., 60) for extremely rigorous analytical precision without breaking the text flow.
* **Enforces Zero-Trust:** The text is explicitly written *after* the backend has calculated the immutable, objective score (e.g., 2.1 / 5.0), guaranteeing perfect synchronization between the narrative and the math.

## 3. Implementation Phases

### Phase 1: The "Mute Evaluator" (Map Phase Adjustments)
* **Objective:** Stop the worker LLM from wasting tokens generating long narrative justifications during the atomic evaluation loops.
* **Tasks:**
  * Update `PromptCompiler` to instruct the LLM to omit `evaluation_notes` (or keep it strictly as internal scratchpad bullet points).
  * Enforce that the atom evaluation phase returns *only* the `true/false` arrays and required XAI extensions (like citations and risk flags).

### Phase 2: The Math Bridge (Scoring Hook)
* **Objective:** Ensure the exact mathematical reality is packaged cleanly for the Synthesis LLM.
* **Tasks:**
  * The `waterfall_scoring_hook` already calculates the score (e.g., 2.1) and hit rates (e.g., "Level 1: 40%").
  * Ensure this data (the calculated score and the level distribution) is cleanly exposed in the state dictionary so the `text_consolidation_hook` can read it.

### Phase 3: The Chief Editor Expansion (Reduce Phase)
* **Objective:** Expand the `text_consolidation_hook` to write matrix justifications.
* **Tasks:**
  * Update `SynthesisOutputDTO` in `backend_v2/models/dtos/synthesis.py` to include a new field: `matrix_justifications: list[MatrixJustificationItem]`.
  * Update the Synthesis LLM System Prompt. Instruct the "Chief Editor" to review the hit rates and scores calculated by the backend for each matrix, and write **one cohesive, professional justification paragraph** explaining the result.

### Phase 4: Blueprint & Frontend Alignment
* **Objective:** Stitch the synthesized justifications into the final UI payload.
* **Tasks:**
  * In `blueprint.py`, during the matrix extraction loop, intercept the `justification` field.
  * Instead of pulling it from the raw atomized `ext_dict`, pull it directly from the `matrix_justifications` map provided by the `xai_highlights_cache`.
  * Ensure the Flutter UI and PDF engine render this synthesized text exactly as they did the old one.

## 4. Risks & Mitigation
* **Risk:** The Synthesis LLM's context window gets overloaded if there are 20+ matrices.
  * **Mitigation:** Gemini 2.5 Pro has a massive context window and handles synthesis extremely well. We can pass only the mathematical distributions and core bullet points, keeping the prompt lean.
* **Risk:** Latency increases due to a heavier Synthesis prompt.
  * **Mitigation:** The atomic evaluation (Map) phase becomes significantly faster and cheaper because the LLM no longer needs to generate long paragraphs for every chunk. The time saved in the Map phase easily offsets the heavier Reduce phase.
