# Implementation Plan - Phase 1: TDA Rule Hardening & Seeding

This sub-plan focuses on rewriting the 5 unstable TDA assertions identified in `mismatch_traces_raw.md` within the `backend_v2/seed/seed_data.json` database configuration. The qualitative assessments are replaced with strict syntactic anchors, explicit step-by-step logic, and the ambiguity protocol.

## Architectural Rules Applied
- **Rule 1 (Direct Database Mutation Ban)**: Never modify the live database `data/db_v2.json` directly. We must mutate the source of truth `backend_v2/seed/seed_data.json` and then execute `run_seed.py`.
- **Rule 2 (Opaque Stripe ID Mandate)**: Preserve the exact opaque identifiers `tda_c74c4367acc028cf`, `tda_d204baf0bdf74ff7`, `tda_3d3f1162d2ff1558`, `tda_d0b6789c895808eb`, and `tda_8d049ce6e39a465c`.
- **Rule 3 (No Legacy Mandate)**: Do not maintain backward compatibility with loose, vague qualitative phrases. Transition completely to syntactic rules.

## Proposed Changes

### Component: Database Seeding & Metadata

#### [MODIFY] [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json)

We will locate and update the five specific assertions inside the JSON file.

##### Milestone 1.1: Harden `tda_c74c4367acc028cf` (Blind Faith / Passive Acceptance of Methodology)
- **Source**: Epic Phase 1, Step 1
- **File Range**: `seed_data.json` around line 1453
- **Change**: Replace the `ai_rule_description` for `tda_c74c4367acc028cf` with the following hardened value:
  ```json
  "ai_rule_description": "REQUIRED TARGET: Scan ONLY user prompts. STEP 1 (Syntactic Anchor): Find explicit user phrases of blind procedural surrender (must be one of: 'proceed with that approach', 'do what you suggested', 'let us use your structure', 'use your steps'). STEP 2 (Negative Condition): Reject if the user introduces at least one custom business rule, custom constraint, or alternative categorization model (e.g., 'supermegatrends') in the same message. AMBIGUITY PROTOCOL: If the exact surrender phrase is absent, or if it is followed by custom constraints, you MUST return JSON null. Speculation is strictly banned."
  ```

##### Milestone 1.2: Harden `tda_d204baf0bdf74ff7` (Key Limitations / Methodological Constraints)
- **Source**: Epic Phase 1, Step 1
- **File Range**: `seed_data.json` around line 6705
- **Change**: Replace the fuzzy list extraction `ai_rule_description` for `tda_d204baf0bdf74ff7` with the step-by-step semantic anchor rule:
  ```json
  "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find explicit boundary setting markers or key constraint phrases (must be one of: 'this does not apply to', 'a key constraint is', 'our analysis is limited to', 'rajoituksena on'). STEP 2 (Extraction Condition): Extract the exact quote containing the physical anchor. AMBIGUITY PROTOCOL: If the physical anchors are absent or vague, you MUST return JSON null. Speculation is strictly banned."
  ```

##### Milestone 1.3: Harden `tda_3d3f1162d2ff1558` (Marginal Critique / Limitation Dismissal)
- **Source**: Epic Phase 1, Step 1
- **File Range**: `seed_data.json` around line 6584
- **Change**: Replace the `ai_rule_description` for `tda_3d3f1162d2ff1558` with the step-by-step syntactic chain and strict ambiguity protocol:
  ```json
  "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find an explicit limitation acknowledgment phrase (must be one of: 'a limitation is', 'rajoituksena on', 'puutteena on', 'heikkoutena on'). STEP 2 (Syntactic Chain): Verify if it is immediately followed (within two sentences) by a dismissive logical transition word (must be one of: 'however', 'regardless', 'kuitenkin', 'silti') that rationalizes away the limitation. AMBIGUITY PROTOCOL: If the limitation anchor is absent, or if the dismissive marker is missing, or if new empirical data is cited to solve the limitation, you MUST return JSON null. Do not rationalize or excuse missing evidence."
  ```

##### Milestone 1.4: Harden `tda_d0b6789c895808eb` (Binary Reduction / Oversimplification)
- **Source**: Epic Phase 1, Step 1
- **File Range**: `seed_data.json` around line 712
- **Change**: Replace the `ai_rule_description` for `tda_d0b6789c895808eb` with:
  ```json
  "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find explicit binary reduction words in the text (must be one of: 'either', 'or', 'simply boils down to', 'joko', 'tai', 'pelkistyy'). STEP 2 (Extraction Condition): Verify if the text explicitly frames a multi-dimensional system or complex strategic situation into exactly two opposing options without acknowledging any middle ground or other alternatives. AMBIGUITY PROTOCOL: If the binary reduction anchors are absent, or if there is any nuance or mention of alternative paths in the paragraph, you MUST return JSON null. Speculation is strictly banned."
  ```

##### Milestone 1.5: Harden `tda_8d049ce6e39a465c` (Superficial Deceleration / Kahneman Transition)
- **Source**: Epic Phase 1, Step 1
- **File Range**: `seed_data.json` around line 1150
- **Change**: Replace the `ai_rule_description` for `tda_8d049ce6e39a465c` with:
  ```json
  "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find explicit transitional doubt words (must be one of: 'however', 'might seem', 'initially', 'kuitenkin', 'aluksi', 'vaikuttaisi'). STEP 2 (Syntactic Chain): Check if this doubt is immediately dismissed (within the same paragraph) to reaffirm the initial automatic conclusion without introducing any new empirical proof, metrics, or citations. AMBIGUITY PROTOCOL: If the doubt anchors are absent, or if the doubt leads to a new productive hypothesis, or if it is supported by new empirical evidence, you MUST return JSON null."
  ```

##### Milestone 1.6: Execute TinyDB Database Seeding Rebuild
- **Source**: Epic Phase 1, Step 3
- **Action**: Ask the user to run the seed script to reset the TinyDB:
  ```powershell
  uv run python backend_v2/seed/run_seed.py
  ```

---

## Verification Plan

### Automated Verification
1. We will check the syntax of `seed_data.json` to make sure it remains a valid JSON.
2. Run database integrity test:
   ```powershell
   uv run pytest backend_v2/tests/unit/test_matrix_data_integrity.py
   ```

---

## Session Handover
To execute this sub-plan after approval:
1. Open a fresh context window.
2. Run command: `/tier2-execute --target docs/epic/tasks_EPIC_61/phase1_tda_hardening.md`
