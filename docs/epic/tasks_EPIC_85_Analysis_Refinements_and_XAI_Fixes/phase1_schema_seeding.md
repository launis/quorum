# Implementation Plan - Phase 1: Schema Extension & Polymorphic Seeding

This implementation plan details the schema extension of output profiles to support dynamic style/tone instruction, and database seeding updates.

## User Review Required

> [!IMPORTANT]
> This change overrides the `pydantic_schema_freeze_mandate` (Rule 84) from `01-python-backend.md` as explicitly required by Epic 85 to support dynamic tone configurations.
>
> Relational collections in `seed_data.json` are modified, which requires executing a database re-seeding command locally:
> `uv run python backend_v2/seed/run_seed.py local`

## Proposed Changes

### Database & Schema Layer

#### [MODIFY] [v2_core.py](file:///c:/src/quorum/backend_v2/models/v2_core.py)
- **Source:** Epic §5, Fix 6 (Unified Dynamic Tone & Language Maintenance)
- **Changes:**
  - Add `tone_instruction: I18nText | None = Field(default=None, description="Dynamic tone instruction for synthesis.")` to:
    * `SynthesisConfigDTO` (around line 895)
    * `OutputProfile` (around line 1033)
    * `EmbeddedOutputProfile` (around line 1079)

#### [MODIFY] [output_profile.py](file:///c:/src/quorum/backend_v2/models/dtos/output_profile.py)
- **Source:** Epic §5, Fix 6 (Unified Dynamic Tone & Language Maintenance)
- **Changes:**
  - Add matching `tone_instruction` field to `OutputProfileCreateDTO` (around line 75), `OutputProfileUpdateDTO` (around line 134), and `OutputProfileResponseDTO` (around line 179).
  - Enforce `tone_instruction: I18nText | None = Field(default=None, description="Dynamic tone instruction for synthesis.")` parity across all creation, modification, and response models.

#### [MODIFY] [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json)
- **Source:** Epic §5, Fix 6 (Unified Dynamic Tone & Language Maintenance)
- **Changes:**
  - Seed dynamic `"tone_instruction"` fields in all output profiles defined under `output_profiles`.
  - For example, default profiles can map a standard tone instruction structure:
    ```json
    "tone_instruction": {
      "fi": "Käytä asiallista, neutraalia ja analyyttistä sävyä.",
      "en": "Use professional, neutral, and analytical tone."
    }
    ```

---

## Verification Plan

### Automated Tests
Run the backend verification loops to ensure Pydantic parsing matches openapi specifications:
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --openapi
uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/output_profile.py --openapi
```

### Manual Verification
Execute database re-seeding to ensure new attributes are correctly parsed and populated into TinyDB:
```powershell
uv run python backend_v2/seed/run_seed.py local
```

---

## Session Handover

To execute this plan iteratively, start a NEW chat session and run:
```powershell
/tier2-execute --target docs/epic/tasks_EPIC_85_Analysis_Refinements_and_XAI_Fixes/phase1_schema_seeding.md
```
