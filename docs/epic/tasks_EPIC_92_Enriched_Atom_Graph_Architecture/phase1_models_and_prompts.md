# EPIC 92: Phase 1 - Pydantic Schema & Prompt Integration

## Goal
Implement the core Pydantic models (`EnrichedAtom`, `ClaimCondition`, `EnrichedAtomBatch`) required for the Enriched Atom Graph architecture, and update the prompt extraction logic to instruct the LLM on generating these structures.

**Source**: [EPIC_92_Enriched_Atom_Graph_Architecture.md](file:///c:/src/quorum/docs/epic/EPIC_92_Enriched_Atom_Graph_Architecture.md) Phase 1

## Scoping
**TARGET (Modify)**
- `c:\src\quorum\backend_v2\models\dtos\lightweight_matrix.py` (Add new Pydantic models here)
- `c:\src\quorum\backend_v2\extraction_schema_factory.py` (Update LLM prompt instructions)

**CONTEXT (Read-Only)**
- `c:\src\quorum\backend_v2\seed\seed_data.json`

## Architectural Invariants (Hardening Mandates)
You MUST strictly adhere to these rules during execution:
- **00-antigravity-core.md**: Fail-fast Pydantic V2 definitions.
- **Rule 1 (Zero-Compromise)**: No `.get("default")` fallbacks. Strict validation is mandatory.
- **Rule 2 (Strict Pydantic)**: All new classes must define `model_config = ConfigDict(strict=True, extra="forbid")`.
- **Rule 54, 55, 56 (PEP 257)**: All classes must possess PEP 257 compliant Google-style docstrings.
- **Epic-Specific Immutability**: `source_quote` inside `EnrichedAtom` MUST be `frozen=True` or explicitly documented as immutable.
- **Epic-Specific DFS Cycle Detection**: `EnrichedAtomBatch` must include the O(V+E) DFS cycle detection inside its `@model_validator(mode="after")`.

## Implementation Steps

### Step 1: Model Implementation
- Inside `lightweight_matrix.py`, define `ClaimCondition(BaseModel)`.
- Define `EnrichedAtom(BaseModel)` with `model_config = ConfigDict(extra="forbid", strict=True, frozen=True)`. Ensure `tda_id`, `resolved_claim`, `source_quote`, `source_id`, `conditions`, and `depends_on_tda_ids` map exactly to the Epic's spec.
- Define `EnrichedAtomBatch(BaseModel)` containing a `list[EnrichedAtom]`. 
- Define a separate `GlobalDAGValidator` class. This class must implement a static method `validate_step_dag(all_atoms: List[EnrichedAtom])` that performs both broken-link checking across ALL chunks and the graph coloring DFS algorithm for cycle detection.

### Step 2: AliasResolutionService (Generalized Alias Pattern)
- Extract the existing `alias_map` logic from `llm.py` (`_apply_alias_chunks_and_audit`), `quote_evidence.py` (`resolve_source_id`), and `lightweight_matrix.py` into a new unified service class `AliasResolutionService`.
- The service must support multiple alias domains:
  - `src_N` for source documents (existing behavior, preserved exactly)
  - `claim_N` for enriched atom claims (new, Epic 92)
- Provide a `generate_aliases(items: dict[str, str]) -> dict[str, str]` method that maps `opaque_id -> alias`.
- Provide a `resolve_alias(alias: str, domain: str) -> str` method used by Pydantic validators.
- Provide a `build_prompt_fragment(domain: str) -> str` method that generates the XML/prompt text for injection.
- Ensure `ValueError` is raised for hallucinated aliases (preserving existing behavior from `quote_evidence.py` line 49).
- **CRITICAL:** Existing `src_N` aliasing must continue to work identically. This is a refactor, not a rewrite.

### Step 3: Prompt Enrichment (Two-Pass Pipeline)
- Inside `extraction_schema_factory.py`, update the dynamic schema generation or prompt instructions.
- **Pass 1 (Extraction):** Ensure the instruction mandates that the LLM performs a "Resolution Pass" to resolve anaphora ("It" -> "The system") and isolate conditional wrappers into the new `conditions` field. No new separate LLM call is made; this is an inline prompt enrichment.
- **Pass 2 (Graph Resolution):** Add a new prompt template that takes the Pass 1 results (as `claim_N` aliases) and asks the LLM to identify `depends_on` relationships and inter-claim conditions. This is a separate, lightweight LLM call.
- The `AliasResolutionService` is used to inject `claim_N` aliases into the Pass 2 prompt and resolve them back in the Pydantic validator.

### Step 4: Documentation Update
- Append the new models and constraints to `c:\src\quorum\docs\architecture\domain\api_models_and_schemas.md`.

## Testing & Quality Gate Plan
- **UNIT TESTS**: Create/update `tests/unit/models/dtos/test_lightweight_matrix.py` to assert that:
  - `GlobalDAGValidator` successfully parses cross-chunk DAGs.
  - Broken cross-chunk DAG links trigger a `ValueError`.
  - Circular Dependencies (A->B->A) trigger a `ValueError` caught by the DFS logic.
- **QUALITY GATE**: You MUST run `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/lightweight_matrix.py --test` to verify code quality. Naked execution of `pytest` is forbidden.

---
## Session Handover
To execute this Epic iteratively, start a NEW chat session and run:
`/tier5-resume --target docs/epic/EPIC_92_tracker.md`
