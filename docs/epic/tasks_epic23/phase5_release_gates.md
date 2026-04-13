# TIER 2 EXECUTION PLAN: Phase 5 - Release the Gates (Seeding & Validation)

## Objective
Finalize Epic 23 by removing the artificial `STRATIFIED_3` limitations globally from the DAG/Config structure. With the Map-Reduce ChunkingService and Calibrated DINA Math fully operational, the system can now safely ingest unbounded LLM questions (`ALL (0)`) without facing timeout crashes or mathematical cascading zero scores. Validate the entire architecture end-to-end to confirm the Mega Epic success.

## Target & Context Files
- **TARGET (Modify):** `backend_v2/seed/seed_data.json` (or database equivalent payload schema to alter `STRATIFIED_3` limits to `ALL (0)`).
- **CONTEXT (Read-Only):** `backend_v2/services/orchestrator/dag_executor.py`, `.agents/rules/00-antigravity-core.md`, `.agents/rules/01-python-backend.md`

## Architectural Sequence
1. **Dependencies:** Seed payload must adhere to the latest exact schema.
2. **Pydantic/Data Update:** Modify `backend_v2/seed/seed_data.json` to configure the matrix evaluation step's parameters to parse infinite elements.
3. **Seeding Protocol:** Run the database seed payload script safely (with user confirmation explicitly).
4. **End-to-End Validation:** Perform a comprehensive architecture test triggering the new chunking Map-Reduce flow and calculating the Calibrated DINA floor scores natively.

## Strict Constraints
- **Direct Database Mutation Ban:** We MUST NOT modify the live `db_v2.json` directly. We MUST mutate `backend_v2/seed/seed_data.json` and ask the User to execute `run_seed.py`.
- **Zero Legacy Fallback Hacks:** Do not insert optional dict fallback types into configuration models to compensate for parsing seed anomalies if they occur.
- **Fail-Fast Observation:** During testing, errors must crash immediately via AppError/RFC 7807 instead of silently skipping questions.

## Verification & Quality Gate Plan
- The User will be instructed to execute the Tier 3 Database Reset protocol `uv run python backend_v2\seed\run_seed.py local`.
- Run comprehensive End-to-End tests simulating 500+ questions. Ensure the Arq worker successfully map-reduces and the Flutter client retrieves a fully formed matrix structure without 429 Rate Limits or Timeout HTTP limits.
- Complete the hand-off workflow.
