# Epic 47 - Phase 2: Orchestration & Virtual System Steps

## Objective
Implement anomaly hooks, real-time UX feedback (SSE), robust XAI i18n, and Arq Virtual System Steps for transparent backend operations.

## TARGET (Modify)
- `backend_v2/hooks/validation.py`
- `backend_v2/services/orchestrator/`
- `backend_v2/api/routers/system/telemetry.py`
- `backend_v2/utils/scoring/*_engine.py`
- `backend_v2/models/dtos/`
- `backend_v2/worker.py`
- `backend_v2/api/routers/execution/executions.py`
- `backend_v2/models/v2_core.py`
- `backend_v2/models/dtos/output_profile.py`
- `backend_v2/hooks/scoring.py`

## CONTEXT (Read-Only)
- `client_app_v2/lib/features/execution/views/dynamic_start_screen.dart` (For SSE context)

## Architectural Invariants (From .agents/rules/)
- **Rule 1: The Duct Tape Ban:** Do not catch all errors with `except Exception: pass`. Never swallow LLM failures silently with god blocks.
- **Rule 2: Circuit Breaker Protocol:** Retries MUST have explicit max limits (e.g. 2), managed in state, not global vars. 
- **Rule 3: Strict Pydantic V2:** Parse dictionary data into `OutputProfile` immediately using `.model_validate()`. `dict.get(key, default)` hacks are strictly banned.
- **Rule 4: Schema-Driven Routing:** No natural language magic strings allowed in Python code. 
- **Rule 5: No Naked Dicts:** State payloads must use structured envelopes.

## [x] Task 6: Arkkitehtuuri - LLM-virheiden korjaus (Anomaly Hook & Circuit Breaker)
Target files: `backend_v2/hooks/validation.py`, `backend_v2/services/orchestrator/`

Implement a pre-scoring `LLMAnomalyDetectionHook` to catch Guttman logic failures (e.g., L1=0%, L3=100%).

New logic requirements:
1. If a logical anomaly is detected in the matrix, trigger an LLM Self-Correction loop via the Orchestrator.
2. Implement the Circuit Breaker explicitly: Store `retry_count` in the Orchestrator's internal node state (NO global variables). 
3. Set the maximum retries to 2.
4. If max retries are exceeded, swallow the anomaly, set `anomaly_unresolved=True` in the state payload, and proceed gracefully to mathematical scoring without crashing the workflow.
5. **Agent Rule Compliance**: Must comply with `c:\src\quorum\.agents\rules\05_llm_architecture.md` for Circuit Breaker implementation and `c:\src\quorum\.agents\rules\01-python-backend.md` for the Duct Tape Ban (all retry loops and LLM failures must be explicitly logged, never silently swallowed with god blocks).

## [x] Task 7 (Backend): UX/XAI - Asynkroninen UX-palaute (SSE)
Target files: `backend_v2/api/routers/system/telemetry.py`

Implement a real-time UX feedback mechanism for the LLM Anomaly Retry loop.

New logic requirements:
1. Backend: When the Orchestrator triggers an anomaly retry, dispatch a specific Server-Sent Event (SSE) to the client: `{"status": "processing", "message_code": "event_llm_anomaly_retry"}`.

## [x] Task 8: XAI:n Inhimillistäminen (Strict i18n & Debug Erottelu)
Target files: `backend_v2/utils/scoring/*_engine.py`, `backend_v2/models/dtos/`

Refactor XAI logging to support global localization and maintain developer debuggability.

New logic requirements:
1. DO NOT hardcode Finnish or English natural language explanations in the backend Python code. This violates i18n principles.
2. Refactor the `calculation_log` into a structured DTO: `XAILogDto` with two fields: `pedagogical_key: str` and `engine_debug_trace: dict`.
3. Return ONLY translation keys (e.g., `xai_soft_waterfall_penalty`) to the frontend for the pedagogical explanation.
4. Place raw math details, thresholds, and multipliers strictly inside the `engine_debug_trace` dictionary for admins and developers.
5. **Agent Rule Compliance**: Must adhere to `c:\src\quorum\.agents\rules\01-python-backend.md` (Schema-Driven Routing). No natural language magic strings allowed in Python code.

## [x] Task 9: Backend - Yleinen Arq-työnkulkujen Hallintamenetelmä (Virtual Steps) & Tulostemallikohtainen Matematiikka
Target files: `backend_v2/worker.py`, `backend_v2/api/routers/execution/executions.py`, `backend_v2/models/v2_core.py`, `backend_v2/models/dtos/output_profile.py`, `backend_v2/hooks/scoring.py`

Refactor scoring logic to detach `strictness_level` and `scoring_strategy` from the Execution phase and bind them to the Output Profile phase (Arq Worker).

New logic requirements:
1. Data Models: Remove `strictness_level` and `scoring_strategy` from `ExecutionCreate` and `ExecutionRecord`. Add them to `OutputProfile`, `EmbeddedOutputProfile`, and `OutputLayoutBlock`. Add them as defaults to the `Workflow` model (which will cascade them via `default_profile_id`).
2. Execution Hook: Refactor `matrix_scoring_hook`. It must no longer calculate the mathematical score or use `dampening_score`. It should ONLY aggregate the raw hit/miss boolean counts (`evaluated_atoms`, `true_atoms_count`) into the Frozen Context.
3. Arq Background Method - Trigger: When `execute_workflow` finishes (or when On-Demand endpoint `POST /{execution_id}/render_pdf` is called), the system injects a Virtual Step (e.g. `sys_render_X`) into `ExecutionRecord.steps` with `status="running"`. If On-Demand, it forces the execution status back to `RUNNING` from `COMPLETED`. Send an SSE immediately.
4. Report Generation Phase (Inside Arq): The Arq-worker (`render_profile_job`) takes over. It loads the `Frozen Context` raw atoms, dynamically runs the math (`get_scoring_engine`) using the selected Output Profile's `strictness_level` and `scoring_strategy`, feeds the scores to LLM synthesis, and caches the `ReportDataDTO`.
5. Arq Background Method - Completion: On success (`status="completed"`) or failure (`status="failed"`), update the `sys_render_<profile>` step state in the DB. In both cases, ensure the overall `ExecutionRecord` status is returned to `COMPLETED`.
6. Taaksepäin Yhteensopivuus ja Zero-Trust: Uudet virtuaaliset askeleet tunnistetaan selkeästi `sys_` -etuliitteellä, jotta ne erotetaan aidoista AI-arviointiasteleista. SSOT säilyy tietokannassa. Kaikkien päivitysten on tapahduttava keskitetysti `repository.update_execution()` -metodin kautta atomisesti.
7. **Agent Rule Compliance**: CRITICAL. Enforce `c:\src\quorum\.agents\rules\01-python-backend.md` (Fail-Fast Hydration Mandate). Parse dictionary data into `OutputProfile` immediately using `.model_validate()`. Follow `c:\src\quorum\.agents\rules\00-antigravity-core.md` Zero-Legacy standard (no `dict.get(key, default)` hacks in logic layers).

## [x] Documentation Update
Update `c:\src\quorum\docs\architecture\` detailing Virtual System Steps and strict decoupled scoring models.
Täydennä myös `c:\src\quorum\.agents\rules\04_directory_reference.md` tiedostoa tehtyjen muutosten osalta.

## Testing & Quality Gate Plan
1. **INTEGRATION TESTS**: Update `tests/backend_v2/worker/test_render_profile_job.py` or equivalent to test Virtual Steps injection.
2. **UNIT TESTS**: Test Pydantic model validation with strictness rules.
3. Run `uv run python scripts/backend_audit_loop.py` on all modified paths, utilizing `--openapi` flag if Pydantic schemas or routers are touched. Ensure tests pass.
