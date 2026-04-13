# TIER 2 EXECUTION PLAN: Phase 2 - The Isolated Chunking Service (TDD)

## Objective
Implement Phase 2 of Epic 23. Construct an isolated `ChunkingService` that can split enormous loads (Prompt Blocks/Atoms) into manageable chunks before they are sent to the LLM. It must exclusively utilize the newly mandated Opaque Stripe IDs to track chunk lineage and output strictly as Pydantic structural schema, avoiding any raw dictionary handling.

## Target & Context Files
- **TARGET (New):** `backend_v2/services/orchestrator/chunking_service.py` 
- **TARGET (Modify):** `tests/backend_v2/services/orchestrator/test_chunking.py` (New file creation for TDD tests)
- **CONTEXT (Read-Only):** `.agents/rules/01-python-backend.md`, `backend_v2/models/enums.py`

## Architectural Sequence
1. **Dependencies:** Native python itertools, typed logic (`list[T]`). 
2. **Pydantic Models:** Define Chunk structures internally if they do not exist. Any schema must be defined in `models/` per `pydantic_namespace_collisions` constraint if it forms a public signature.
3. **API/Logic (Chunking Service):** Create a deterministic function that maps large arrays into smaller arrays, assigning a unique parent-child `chk_xxxx` Opaque Stripe ID to each sub-array or sub-invocation.
4. **No Side-Effects:** Service must have zero database access and zero LLM access (`T=0.0` isolated). Pure data-in, data-out.

## Strict Constraints
- **Opaque Stripe ID Mandate:** Chunk IDs must conform to `chk_xxxxxxxx`. Never use auto-incremented integers or slugs.
- **Fail-Fast Resilienssi:** Must throw `AppException` explicitly and `logger.error` if the chunker receives corrupt inputs rather than silent exceptions.
- **No Naked Dicts:** Input and output structures must be completely validated Pydantic models.

## Verification & Quality Gate Plan
- Build rigorous Unit Tests in `tests/backend_v2/services/orchestrator/test_chunking.py`.
- Run Pytest script: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/chunking_service.py` 
- Validate that lists perfectly divide into `N` chunks without losing trailing artifacts (Lossless map-reduce).
