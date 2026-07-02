# EPIC 93 Phase 1: DTO Refactoring and Context Injection

## Source: Epic 93, Sections 0, 1, 3.1, and OSA 2.1

### Objective
Establish the headless Data Transfer Object (DTO) layer as the single source of truth. Refactor `ReportDataDto` and `ExecutionState` to be strictly typed and presentation-agnostic. Implement the `QuoteEvidenceDTO` with deterministic alias resolution using Pydantic's `ValidationInfo` and `@field_validator`, mapping failed aliases to `OpaqueID.UNVERIFIED`.

### Target Files (Modify)
- `backend_v2/models/dtos/report.py`
- `backend_v2/models/state.py`
- `backend_v2/models/dtos/quote_evidence.py` (NEW or update existing)

### Context Files (Read-Only)
- `backend_v2/seed/seed_data.json`
- `c:\src\quorum\.agents\rules\01-python-backend.md`

### Architectural Mandates (From `hardening.xml` & `01-python-backend.md`)
- **fail_fast_hydration_mandate**: All uncertain data flowing as dictionaries MUST be hydrated via `.model_validate()` IMMEDIATELY before processing.
- **strict_pydantic_v2_rust**: Force the Fail-Fast pipeline by using `.model_validate()`, Rust-based `.model_validate_json()`, `.model_dump()`, and `@field_validator`. Use `model_config = ConfigDict(extra='forbid', strict=True)`.
- **zero_legacy_fallback_hacks**: NEVER bypass Pydantic `extra='forbid'` strictness to accommodate dirty databases.
- **the_zero_compromise_pledge**: No fallback chains, shortcuts, or naked dict `.get()` loops. Let the system crash if data is malformed.
- **Epic Phase 0 Prerequisite**: Visual and semantic output must remain completely unchanged from the external perspective.

### Implementation Details
1.  **Refactor `ReportDataDto` and `ExecutionState`:**
    *   Strip out all Markdown, HTML, or UI tags from these models.
    *   Redefine them as headless, strongly-typed Pydantic models carrying only semantic data (e.g., `executive_summary: str`, `evidence_quotes: List[QuoteEvidenceDTO]`).
2.  **Create/Refactor `QuoteEvidenceDTO`:**
    *   Define `quote: str` and `source_alias: List[str]`.
    *   Implement a `mode='before'` `@field_validator` on `source_alias` to intercept strings like `"DOC-1, DOC-2"` and normalize them into a list `["DOC-1", "DOC-2"]` using regex `re.findall(r'DOC-\d+', v)`.
    *   Implement an after `@field_validator` on `source_alias` that takes `info: ValidationInfo`. It must access `info.context.get("alias_registry", {})`.
    *   Map each alias to its Opaque ID. If the alias is missing, map it strictly to the literal string `"OpaqueID.UNVERIFIED"`. No logging or side-effects inside the validator.

### Destructive Operation Inventory
- None in this phase.

### Bidirectional Integration Check
- **Producer:** LLM `chunk_worker.py` outputting `DOC-X`.
- **Consumer:** `QuoteEvidenceDTO` validation utilizing the context registry.

### Testing & Quality Gate Plan
1.  **Unit Tests:** Create `tests/unit/models/dtos/test_quote_evidence.py`. Test the `mode='before'` regex parsing of combined strings and the `ValidationInfo` alias mapping (including the `OpaqueID.UNVERIFIED` fallback).
2.  **Integration Tests:** None needed for this specific DTO tier yet.
3.  **Verification:** Execute `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/ --test`.

### Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/epic_93_tracker.md`
