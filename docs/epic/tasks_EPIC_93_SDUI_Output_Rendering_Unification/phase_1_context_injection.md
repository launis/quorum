# Phase 1: SDUI Mapper Service & Context Injection

## Goal Description
Refactor the DTO layer to completely separate from presentation logic and introduce the `sdui_mapper_service.py` to translate semantic data into `SduiComponent` models. This enforces the "Fail-Fast" principle and Dual-Reporting for hallucinations within the BFF (Backend-For-Frontend) layer.

## Target & Context
- **TARGET (Modify)**: 
  - `backend_v2/models/dtos/report/atoms.py` (QuoteEvidenceDTO equivalent if present, or `quote_evidence.py` if that's the exact file)
  - `backend_v2/models/dtos/quote_evidence.py`
  - `backend_v2/services/pdf_generator.py`
  - `backend_v2/services/sdui_mapper_service.py` [NEW]
- **CONTEXT (Read-Only)**:
  - `backend_v2/models/view/sdui.py`
  - `backend_v2/models/dtos/report/root.py`

## Proposed Changes

### `backend_v2/models/dtos/`
#### [MODIFY] [quote_evidence.py](file:///c:/src/quorum/backend_v2/models/dtos/quote_evidence.py) (and/or atoms.py)
- Refactor `QuoteEvidenceDTO` to include `@model_validator(mode='before')` that resolves aliases using `info.context.get("alias_registry")`.
- Implement `verified_source_ids`, `unverified_aliases`, and `is_verified` attributes.
- Ensure strict Pydantic V2 definitions with no side-effects in validators (e.g., no telemetry logging in DTOs).

### `backend_v2/services/`
#### [MODIFY] [pdf_generator.py](file:///c:/src/quorum/backend_v2/services/pdf_generator.py)
- Enforce `jinja2.StrictUndefined` on the Jinja environment to trigger Fail-Fast if a key is missing.
- Note: Requires ensuring the Jinja templates handle `N_A` (Optional) correctly with explicit `if/elif` statements.

#### [NEW] [sdui_mapper_service.py](file:///c:/src/quorum/backend_v2/services/sdui_mapper_service.py)
- Implement `map_evidence_to_sdui()` and `map_report_to_sdui()`.
- The mapper is responsible for Telemetry logging (Dual-Reporting) when hallucinations are detected.
- Returns strict `SduiComponent` derivatives (e.g., `SduiWarningCard`, `SduiQuoteCard`).

## Architecture Rules Addressed
- **Zero-Service Layer Fallbacks**: No `.get("key", default)` inside the UI mappers. If the DTO lacks it, fail fast.
- **Fail-Fast Hydration Mandate**: DTOs validate rigidly.

## Verification Plan
### Automated Tests
- `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/ --test`
- `uv run python scripts/backend_audit_loop.py backend_v2/services/sdui_mapper_service.py --test`
- `uv run python scripts/backend_audit_loop.py backend_v2/services/pdf_generator.py --test`

## Session Handover
To execute this Epic iteratively, start a NEW chat session and run the `/tier5-resume` command found at the bottom of your tracker.
