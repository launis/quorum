# Epic 50: Output Profile Architecture & Parity Hardening

## 1. Context & Architectural Violations Identified
The V2026 architectural mandates strictly separate the **Execution Phase** (Raw evaluation, 1-5 scales, PromptBlocks) from the **Reporting/Display Phase** (Synthesis, normalized 0-100 scales, Output Profiles).

During a deep audit of `seed_data.json`, two massive bi-directional leaks were identified between these tiers:

### Leak A: PromptBlocks Contaminated with UI Logic
* **Issue:** `row_explanation_generator` was added to the execution layer as a `PromptBlock`. 
* **Violation:** It explicitly operates on a normalized `0-100` scale and contains UI-centric formatting rules (e.g., "Output exactly ONE punchy sentence"). PromptBlocks must ONLY evaluate raw data on their native scales (e.g., 1-5) and should not concern themselves with UI formatting.

### Leak B: OutputProfiles Contaminated with Execution Logic
* **Issue:** Multiple layout configurations (e.g., inside the `holistic_audit` profile) contain execution-tier prompts copy-pasted directly into their `synthesis.system_prompt` fields.
* **Violation:** Synthesis prompts contain directives like `"ROLE: ANTAGONISTIC PROSECUTOR"`, `"NULL HYPOTHESIS"`, and `"MANDATORY DIRECTIVE: Default all boolean claim evaluations to FALSE"`. This instructs the Synthesis LLM (which runs *after* execution) to attempt to re-evaluate the raw text rather than simply summarizing the execution results. This causes hallucinations, slows down generation, and breaks the Single Source of Truth.

---

## 2. Unused Fields & Schema Redundancy
* **Issue:** The `ReportLayoutDTO` / `OutputLayoutBlock` definitions in `seed_data.json` contain fields like `"synthesis_md": null`. 
* **Violation:** `synthesis_md` is a runtime container for the generated output, not a configuration parameter. Storing it as `null` in the seed data adds unnecessary bloat and confusion to the Output Profile definitions.

---

## 3. Implementation Plan (Refactor Steps)

### Phase 1: Seed Data Sanitization (The Purge)
1. [x] **Scrub Output Profiles:** Iterate through all `output_profiles` in `seed_data.json`. Strip all execution-specific terminology (`NULL HYPOTHESIS`, `FALSE/TRUE`, `ZERO-TRUST AUDITOR`) from `synthesis.system_prompt`. Rewrite them to focus purely on synthesizing the provided JSON data.
2. [x] **Delete UI Prompts from Execution:** Completely remove `row_explanation_generator` from the `prompt_blocks` list.
3. [x] **Remove Dead Fields:** Remove `"synthesis_md": null` from all layout block configurations in the seed data.

### Phase 2: DTO & Backend Engine Adjustments
1. **Migrate Row Explanations:** Add `row_explanation_prompt: str | None` to `SynthesisConfigDTO` in `backend_v2/models/v2_core.py`.
2. **Decouple Scoring Hook:** Remove the dynamic LLM explanation loop from `backend_v2/hooks/scoring.py`. The execution payload's `justification` field must remain the raw, unedited `step_3_logical_friction` output from the atomic evaluator (maintaining the 1-5 scale integrity).
3. **Hook Synthesis Tier:** Implement the ultra-short row explanation generation inside `backend_v2/hooks/synthesis.py`. The Synthesis Hook will read the new `row_explanation_prompt` from the active Output Profile, compress the raw justification, and cache the UI-friendly result in the `profile_syntheses` dict.

### Phase 3: Frontend & End-to-End Parity
1. **Output Profile UI:** Verify that the frontend `client_app_v2` (`OutputProfileCrudView`) correctly surfaces the new `row_explanation_prompt` field so admins can tweak the matrix UI explanation length directly from the Studio without touching Python code.
2. **Test Matrix Table:** Ensure `AtomMatrixTableWidget` correctly reads the synthesized UI explanation rather than falling back to the raw, verbose execution justification.

### Phase 4: Migration Tooling & Test Automation (Execution Protocol)
To ensure architectural integrity, NO manual editing of `seed_data.json` is permitted. The migration must be strictly automated and verified:
1. [x] **Pre-Flight Backup:** Before any scripts are executed, create a literal hard backup of the current database to `backend_v2/seed/backups/seed_data_pre_epic50.json`.
2. [x] **Migration Scripts:** Build dedicated Python tooling to mutate `seed_data.json`. The script will parse the JSON into Pydantic models, apply the purge logic, and re-serialize.
3. [x] **Before-and-After Dry Runs:** Execute multiple test runs of the migration script. The tool must output a detailed diff log to prove no data loss occurred outside the targeted purge fields.
4. [x] **Pydantic Validation Scans:** Verify the post-migration `seed_data.json` successfully loads back into all relevant Pydantic V2 databases without throwing validation errors.
4. [x] **Pytest Integration (Architectural Guardrails):** Once verified, the logic used in the dry runs must be converted into permanent `pytest` test cases. These tests will continually scan `seed_data.json` in CI/CD to assert that:
   - No `PromptBlock` contains UI keywords or 0-100 display scales.
   - No `OutputProfile` contains execution terminology (e.g., `NULL HYPOTHESIS`, `BOOLEAN`).
   This ensures we catch any future boundary leaks immediately.

### Phase 5: Documentation & Rule Hardening
To prevent this architectural regression from ever happening again, the precise roles and boundaries of the database components must be written into the mandated system rules:
1. [x] **Agent Rules Update:** Update the strict enforcement files in `c:\src\quorum\.agents\rules\` to explicitly define:
   - **PromptBlocks:** Exclusively for raw data evaluation (1-5 scales, `ZERO-TRUST AUDITOR` directives, atomic extraction). Zero formatting logic allowed.
   - **OutputProfiles:** Exclusively for presentation and UI formatting (0-100 scales, brevity constraints, tone). Zero boolean evaluation or hypothesis testing allowed.
2. [x] **Architecture Docs Sync:** Verify and update the official architecture documentation in `c:\src\quorum\docs\architecture\` (e.g., `02_domain_models.md`) to reflect these strict boundaries and the new `SynthesisConfigDTO` fields.

---
**Status:** Completed. Epic 50 finished.
