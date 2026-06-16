# Implementation Plan: Epic 1 - Phase D & E (Seed Data & Routing)

**Source**: `epic_structured_prompting.md` (Phase D & E)
**Epic Phase**: Seed Data ja Kognitiiviset Protokollat & Schema-Driven Override ja Determinismi

## 1. Goal
Purge legacy formatting instructions from the Seed Data to prevent "Cognitive Schizophrenia" between prompt text and JSON schema structure. Implement "Dual Static Schemas" (`StepDTOStrict` and `StepDTOSemantic`) to route zero-trust checks safely without causing Schema Leaks or memory bloat.

## 2. Files
**TARGET (Modify):**
- `c:\src\quorum\backend_v2\seed\seed_data.json`
- `c:\src\quorum\backend_v2\models\dtos\evaluation_steps.py` (New or Existing file for the schema)
- `c:\src\quorum\backend_v2\api\chunk_worker.py`

**CONTEXT (Read-Only):**
- `c:\src\quorum\.agents\rules\00-antigravity-core.md`
- `c:\src\quorum\.agents\rules\03_seed_vault.md`

## 3. Implementation Steps

### 3.1. Cognitive Schizophrenia Prevention (seed_data.json)
- **Migration:** Find all instances of *"TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log"* in the TDA descriptions.
- Replace them explicitly with: *"TRACE REQUIREMENT: Follow the explicit step-by-step cognitive sequence defined in the provided JSON schema."*
- Create new protocols `blk_8b4c2e1f9a0d3765` and `blk_f23a9b1c7d4e5082`.

### 3.2. Dual Static Schemas (Models)
- Create `ParsingLogSteps` model. Ensure `reasoning_steps` comes BEFORE `decision: bool` and `contextual_override: bool` (Cognitive Buffering).
- Make `ParsingLogSteps` agnostic (e.g. `list[StepDTO]`).
- Create **two static models**:
  1. `StepDTOStrict`: No override fields whatsoever.
  2. `StepDTOSemantic`: Includes `contextual_override: bool` and `override_reason: str`.

### 3.3. Proactive Routing (chunk_worker.py)
- Remove any existing reactive Python-level `AND` logic that checks `strictness==100` *after* the LLM call.
- Check permissions *before* the LLM call: If `strictness == 100` or rule denies override, pass `StepDTOStrict` to Vertex AI. Otherwise, pass `StepDTOSemantic`.
- This fully prevents the LLM from hallucinating overrides (Schema Leak) without triggering Rust memory leaks via `create_model`.
- Remove Track B gateway from `evaluate_extraction()`.

## 4. Testing & Quality Gate Plan
- **Verification:** Run `uv run python backend_v2/seed/run_seed.py local` to flash the database with the new sanitized Seed Data.
- **Unit Tests:** Write tests for the `chunk_worker.py` proactive routing.
- **Hardening:** Run the Universal Quality Gate on the modified files:
  `uv run python scripts/backend_audit_loop.py c:\src\quorum\backend_v2\api`
  `uv run python scripts/backend_audit_loop.py c:\src\quorum\backend_v2\models`

---
### Session Handover
To execute this phase iteratively, start a NEW chat session and run:
`/tier2-execute --target docs/epic/tasks_structured_prompting/phase_d_and_e_seed_data_and_routing.md`
