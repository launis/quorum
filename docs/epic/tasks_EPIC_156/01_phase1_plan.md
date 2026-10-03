# Phase 1: Tooling Infrastructure, Blindspot Elimination & Scoped Boy Scout CI Enforcement

**Overview:** Implement QGR024 and QGR025 in `_ast_guardrails.py`, build the Clean Import smoke test tool, expand `backend_audit_loop.py` to an 8-stage mandatory pipeline with hardened Jinja Dumb Painter regex, eliminate 79 pre-existing domain fatal violations across 27 files, clean low-count warning violations (46 instances: QGR007, QGR023, QGR009, QGR008, QGR006, QGR011 across 19 files), clean 22 active tooling violations across 6 scripts, promote cleaned rules to FATAL severity, build the warning baseline ledger, and synchronize agentic workflows.

**Target Files:**
- `[MODIFY]` `@[scripts/_ast_guardrails.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`
- `[NEW]` `@[scripts/audit_clean_imports.py]`
- `[NEW]` `@[backend_v2/tests/unit/scripts/test_clean_imports.py]`
- `[MODIFY]` `@[scripts/backend_audit_loop.py]`
- `[MODIFY]` `@[backend_v2/templates/report_template.jinja2]`
- `[NEW]` `@[scripts/audit_warning_baseline.py]`
- `[MODIFY]` `@[scripts/audit_database_atoms.py]`
- `[MODIFY]` `@[scripts/reconcile_storage.py]`
- `[MODIFY]` `@[scripts/audit_rules_staleness.py]`
- `[MODIFY]` `@[scripts/audit_matrix_auto_filler.py]`
- `[MODIFY]` `@[scripts/audit_matrix_manager.py]`
- `[MODIFY]` `@[scripts/matrix_slice_engine.py]`
- `[MODIFY]` `@[backend_v2/run_worker.py]`
- `[MODIFY]` `@[backend_v2/database/wrapper.py]`
- `[MODIFY]` `@[backend_v2/hooks/llm.py]`
- `[MODIFY]` `@[backend_v2/llm/handler.py]`
- `[MODIFY]` `@[backend_v2/llm/ingress_pipeline.py]`
- `[MODIFY]` `@[backend_v2/hooks/source_verification_hook.py]`
- `[MODIFY]` `@[backend_v2/seed/run_seed.py]`
- `[MODIFY]` `@[backend_v2/database/repositories/knowledge.py]`
- `[MODIFY]` `@[backend_v2/database/repositories/audit.py]`
- `[MODIFY]` `@[backend_v2/database/repositories/base.py]`
- `[MODIFY]` `@[backend_v2/database/repositories/identity.py]`
- `[MODIFY]` `@[backend_v2/database/repositories/workflow.py]`
- `[MODIFY]` `@[backend_v2/llm/adapters/ai_studio_adapter.py]`
- `[MODIFY]` `@[backend_v2/llm/adapters/openai_adapter.py]`
- `[MODIFY]` `@[backend_v2/llm/adapters/vertex_adapter.py]`
- `[MODIFY]` `@[backend_v2/llm/mock.py]`
- `[MODIFY]` `@[backend_v2/models/domain/metrics.py]`
- `[MODIFY]` `@[backend_v2/models/domain/security.py]`
- `[MODIFY]` `@[backend_v2/models/domain/validation.py]`
- `[MODIFY]` `@[backend_v2/models/dtos/matrix_scorecard.py]`
- `[MODIFY]` `@[backend_v2/services/auth.py]`
- `[MODIFY]` `@[backend_v2/services/cache/typed_cache.py]`
- `[MODIFY]` `@[backend_v2/services/chat_normalizer.py]`
- `[MODIFY]` `@[backend_v2/services/drivers/gcs_file_driver.py]`
- `[MODIFY]` `@[backend_v2/services/execution/lifecycle_service.py]`
- `[MODIFY]` `@[backend_v2/services/execution/stream_service.py]`
- `[MODIFY]` `@[backend_v2/services/mcp/tavily_search_client.py]`
- `[MODIFY]` `@[backend_v2/core/hook_registry.py]`
- `[MODIFY]` `@[backend_v2/core/registry.py]`
- `[MODIFY]` `@[backend_v2/models/chunking.py]`
- `[MODIFY]` `@[backend_v2/models/domain/step.py]`
- `[MODIFY]` `@[backend_v2/models/dtos/trace.py]`
- `[MODIFY]` `@[backend_v2/hooks/integrity.py]`
- `[MODIFY]` `@[backend_v2/llm/schema_builder.py]`
- `[MODIFY]` `@[backend_v2/services/chat_parser.py]`
- `[MODIFY]` `@[backend_v2/services/execution/ingress_service.py]`
- `[MODIFY]` `@[backend_v2/services/ingress/pdf_chat_extractor.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/two_pass_atomizer.py]`
- `[MODIFY]` `@[backend_v2/workers/synthesis_reducers.py]`
- `[MODIFY]` `@[backend_v2/scripts/generate_openapi.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/mcp/test_mcp_tool_loop.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_tavily_search_client.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py]`
- `[MODIFY]` `@[AGENTS.md]`
- `[MODIFY]` `@[.agents/workflows/tier2-execute.md]`
- `[MODIFY]` `@[.agents/workflows/tier1-tracker-generator.md]`
- `[MODIFY]` `@[.agents/workflows/tier1-plan-tracker-generator.md]`
- `[MODIFY]` `@[.agents/workflows/tier8-audit-plan.md]`
- `[MODIFY]` `@[.agents/workflows/tier8-red-teaming-audit.md]`
- `[MODIFY]` `@[.agents/workflows/tier2-hardening-knowledge.md]`
- `[MODIFY]` `@[.agents/workflows/tier0-create-epic.md]`
- `[MODIFY]` `@[.agents/workflows/tier0-research-epic.md]`
- `[MODIFY]` `@[.agents/workflows/tier3-minify-customization.md]`
- `[MODIFY]` `@[.agents/workflows/tier3-database-reset.md]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[scripts/_ast_guardrails.py]` | String-quoted forward-reference annotations (QGR024), dynamic untyped dicts in `model_copy(update=...)` (QGR025), and permissive WARNING classifications for cleaned rules. | Enforce Python 3.14 PEP 649/749 deferred annotations without quotes (exempting `Literal[...]` slices and `Annotated[...]` descriptions); enforce typed dictionary literals in `model_copy(update={...})` for atomic progress; promote QGR007, QGR023, QGR009, QGR008, QGR006, QGR011, QGR024, QGR025 unconditionally to FATAL severity. | Pruned complex AST parser hierarchies or speculative visitor classes; implement direct `visit_AnnAssign`, `visit_FunctionDef`, and `visit_Call` branches inside existing `QuorumGuardrailVisitor`. | `uv run python scripts/_ast_guardrails.py scripts/_ast_guardrails.py --strict` |
| `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]` | Missing unit tests for rules QGR013 through QGR025; untested false-positive boundaries. | Comprehensive positive, boundary, and error partition test cases asserting exact FATAL severity violations for QGR013-QGR025; explicit false-positive defense assertions for `Literal[...]`, `Annotated[...]`, and concurrency progress dicts. | Pruned external test mocks; evaluate raw AST strings directly via `scan_source_code_for_guardrails()`. | `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py -v` |
| `[NEW] @[scripts/audit_clean_imports.py]` and `[NEW] @[backend_v2/tests/unit/scripts/test_clean_imports.py]` | Circular dependency deadlocks, eager module-level side effects, and unisolated module loading that breaks when modules are imported independently. | Deterministic scanner recursively importing every module across all 896 files in `backend_v2/` via `importlib.import_module()`; asserts zero `ImportError`, zero `AttributeError`, zero circular imports. | Pruned multi-process import sandboxes or OS subprocesses; execute in-process with clean module isolation and sys.modules rollbacks for synthetic unit tests. | `uv run python scripts/audit_clean_imports.py` and `uv run pytest backend_v2/tests/unit/scripts/test_clean_imports.py` |
| `@[scripts/backend_audit_loop.py]` and `@[backend_v2/templates/report_template.jinja2]` | Permissive 6-stage pipeline missing clean import smoke test and DTO parity verification; Jinja fallback expressions (`or ''`, `or []`, `or {}`) in lines 390, 391, 413, 421, 422, 440, 461. | Expand to 8 mandatory sequential stages (Stage 7: Clean Imports, Stage 8: DTO Parity); harden Stage 5 regex to detect all Jinja `or` fallback expressions; replace 7 template fallbacks with backend DTO-guaranteed non-None defaults; enforce Scoped Boy Scout strictness on touched targets. | Pruned parallel audit executors; maintain sovereign single deterministic pipeline. | `uv run python scripts/backend_audit_loop.py scripts/_ast_guardrails.py --test --ast-strict` |
| `@[backend_v2/seed/run_seed.py]` and `@[backend_v2/database/repositories/knowledge.py]` | Silent exception swallowing without `raise` (QGR003: 7 in `run_seed.py`, 4 in `knowledge.py`); `_fail_fast` calling `sys.exit(1)` instead of raising `AppException`; skipping corrupted records in `get_banned_phrases()` without re-raising. | Replace silent exception handlers with explicit RFC 7807 structured logging followed by `raise AppException(ErrorCodes.VALIDATION_FAILED)` per `universal_fail_fast` and two-phase seeder pre-flight validation. | Pruned ad-hoc error wrappers; bind canonical `ErrorCodes` enum directly from `backend_v2/exceptions.py`. | `uv run python scripts/_ast_guardrails.py backend_v2/seed/run_seed.py backend_v2/database/repositories/knowledge.py --strict` |
| `@[backend_v2/database/repositories/audit.py]`, `@[backend_v2/database/repositories/base.py]`, `@[backend_v2/database/repositories/identity.py]`, `@[backend_v2/database/repositories/workflow.py]` | Silent exception catching without `raise` (QGR003: 3 in `audit.py`, 1 in `base.py`, 2 in `identity.py`, 3 in `workflow.py`). | Enforce strict Repository Reconstitution Firewall: catch exceptions, log with RFC 7807 parameters, and re-raise typed `AppException(ErrorCodes.DATABASE_ERROR)` or domain-specific exceptions. | Pruned defensive `try...except` blocks that catch and return `None` or `[]`; let typed repository methods return guaranteed domain models or raise. | `uv run python scripts/_ast_guardrails.py backend_v2/database/repositories/ --strict` |
| `@[backend_v2/database/wrapper.py]`, `@[backend_v2/run_worker.py]`, `@[backend_v2/hooks/llm.py]`, `@[backend_v2/llm/handler.py]` | Silent exception swallowing without `raise` (QGR003: 5 in `wrapper.py`, 3 in `run_worker.py`, 2 in `hooks/llm.py`, 4 in `llm/handler.py`); unexempted dictionary `.get()` calls (QGR002: 2 in `wrapper.py`); hardcoded timeouts (QGR008: 3 in `wrapper.py`). | Enforce explicit re-raise or typed DLQ dispatch (`dlq_service.push()`); replace dictionary `.get()` with bracket indexing after positive membership checks; import timeouts from `backend_v2/settings.py`. | Pruned generic fallback return literals (`return None`, `return {}`); fail-fast loudly on missing data or operational failure. | `uv run python scripts/_ast_guardrails.py backend_v2/database/wrapper.py backend_v2/run_worker.py backend_v2/hooks/llm.py backend_v2/llm/handler.py --strict` |
| `@[backend_v2/llm/ingress_pipeline.py]`, `@[backend_v2/hooks/source_verification_hook.py]`, `@[backend_v2/llm/mock.py]` | Illegal `# noqa: QGR*` comment suppressions in domain code (QGR000: 4 in `ingress_pipeline.py`, 1 in `mock.py`); banned `isinstance(..., dict)` duck-typing (QGR012: 4 in `ingress_pipeline.py`, 1 in `mock.py`); banned type laundering via `TypeAdapter(dict)` (QGR018: 1 in `source_verification_hook.py`); silent exception swallowing (QGR003: 2 in `source_verification_hook.py`). | Remove `# noqa` comments; replace `isinstance(dict)` with native Pydantic V2 discriminated union validation; replace `TypeAdapter(dict)` with strongly typed DTO by defining [NEW] `SourceVerificationPayloadDTO`; re-raise typed `AppException` in exception handlers. | Pruned untyped dictionary adapters and ad-hoc inspection loops. | `uv run python scripts/_ast_guardrails.py backend_v2/llm/ingress_pipeline.py backend_v2/hooks/source_verification_hook.py backend_v2/llm/mock.py --strict` |
| `@[backend_v2/llm/adapters/ai_studio_adapter.py]`, `@[backend_v2/llm/adapters/openai_adapter.py]`, `@[backend_v2/llm/adapters/vertex_adapter.py]` | Unauthorized `# noqa: QGR*` comment suppressions (QGR000: 1 in `ai_studio`, 3 in `openai`, 1 in `vertex`); silent exception swallowing (QGR003: 1 in `ai_studio`, 1 in `openai`, 2 in `vertex`); duck-typing via `isinstance(..., dict)` (QGR012: 2 in `openai`); unexempted `.get()` (QGR002: 2 in `ai_studio`). | Remove `# noqa` comments; resolve underlying violations with typed DTO validation or re-raise typed `AppException`; replace `.get()` with bracket indexing after positive membership checks. | Pruned custom error suppressions in provider adapters; delegate model pricing and parameters strictly to LiteLLM model registry SSOT. | `uv run python scripts/_ast_guardrails.py backend_v2/llm/adapters/ --strict` |
| `@[backend_v2/models/domain/metrics.py]`, `@[backend_v2/models/domain/security.py]`, `@[backend_v2/models/domain/validation.py]`, `@[backend_v2/models/dtos/matrix_scorecard.py]`, `@[backend_v2/services/auth.py]`, `@[backend_v2/services/cache/typed_cache.py]`, `@[backend_v2/services/chat_normalizer.py]`, `@[backend_v2/services/drivers/gcs_file_driver.py]`, `@[backend_v2/services/execution/lifecycle_service.py]`, `@[backend_v2/services/execution/stream_service.py]`, `@[backend_v2/services/mcp/tavily_search_client.py]` | Type laundering via `TypeAdapter(dict)` (QGR018: 1 in `metrics.py`, 1 in `security.py`, 1 in `validation.py`); silent exception swallowing (QGR003: 1 in `matrix_scorecard.py`, 4 in `auth.py`, 2 in `typed_cache.py`, 2 in `chat_normalizer.py`, 1 in `gcs_file_driver.py`, 1 in `lifecycle_service.py`, 2 in `stream_service.py`); unshielded f-string XML prompt structure (QGR022: 1 in `tavily_search_client.py`). | Replace dictionary type laundering with `ExecutionInputsDTO` or typed Pydantic models; re-raise typed `AppException` in exception handlers; replace f-string XML prompt in `tavily_search_client.py` with structured `PromptBlock` or template string. | Pruned pseudo-classes wrapping dictionaries; use native Pydantic V2 DTOs. | `uv run python scripts/_ast_guardrails.py backend_v2/models/domain/metrics.py backend_v2/models/domain/security.py backend_v2/models/domain/validation.py backend_v2/models/dtos/matrix_scorecard.py backend_v2/services/auth.py backend_v2/services/cache/typed_cache.py backend_v2/services/chat_normalizer.py backend_v2/services/drivers/gcs_file_driver.py backend_v2/services/execution/lifecycle_service.py backend_v2/services/execution/stream_service.py backend_v2/services/mcp/tavily_search_client.py --strict` |
| `@[backend_v2/core/hook_registry.py]`, `@[backend_v2/core/registry.py]`, `@[backend_v2/models/chunking.py]`, `@[backend_v2/models/domain/step.py]`, `@[backend_v2/models/dtos/trace.py]` | Missing `model_config = ConfigDict(strict=True, extra="forbid")` (QGR007: 2 in `hook_registry.py`, 1 in `registry.py`, 2 in `chunking.py`, 1 in `step.py`, 1 in `trace.py`); mutable default argument (QGR011: 1 in `trace.py:50`). | Add explicit `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)` to Pydantic models; replace mutable default argument in `trace.py:50` with `= None` and factory initialization in method body. | Pruned loose model configurations; enforce universal Pydantic strictness. | `uv run python scripts/_ast_guardrails.py backend_v2/core/hook_registry.py backend_v2/core/registry.py backend_v2/models/chunking.py backend_v2/models/domain/step.py backend_v2/models/dtos/trace.py --strict` |
| `@[backend_v2/hooks/integrity.py]`, `@[backend_v2/llm/schema_builder.py]`, `@[backend_v2/services/chat_parser.py]`, `@[backend_v2/services/execution/ingress_service.py]`, `@[backend_v2/services/ingress/pdf_chat_extractor.py]`, `@[backend_v2/services/orchestrator/two_pass_atomizer.py]`, `@[backend_v2/workers/synthesis_reducers.py]` | Anonymous 3+ element tuples ('Tuple Hell') in returns and intermediate state (QGR023: 1 in `integrity.py`, 2 in `schema_builder.py`, 1 in `chat_parser.py`, 1 in `ingress_service.py`, 9 in `pdf_chat_extractor.py`, 2 in `two_pass_atomizer.py`, 5 in `synthesis_reducers.py`). | Encapsulate anonymous tuples in dedicated, immutable Pydantic V2 DTOs (`ChunkPacketDTO`, `SectionReductionDTO`, etc.) with `ConfigDict(strict=True, extra="forbid", frozen=True)`. | Pruned positional tuple unpacking; access properties via static dot-notation. | `uv run python scripts/_ast_guardrails.py backend_v2/hooks/integrity.py backend_v2/llm/schema_builder.py backend_v2/services/chat_parser.py backend_v2/services/execution/ingress_service.py backend_v2/services/ingress/pdf_chat_extractor.py backend_v2/services/orchestrator/two_pass_atomizer.py backend_v2/workers/synthesis_reducers.py --strict` |
| `@[backend_v2/scripts/generate_openapi.py]`, `@[backend_v2/tests/unit/services/mcp/test_mcp_tool_loop.py]`, `@[backend_v2/tests/unit/test_tavily_search_client.py]`, `@[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py]`, `@[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py]` | AppException instantiations missing canonical `ErrorCodes` enum (QGR009: 1 in `generate_openapi.py`, 7 in `ingress_service.py`, 1 in `test_mcp_tool_loop.py`, 2 in `test_tavily_search_client.py`); unguarded dictionary subscripting in tests (QGR006: 1 in `test_ai_studio_adapter.py`, 1 in `test_vertex_adapter.py`). | Bind canonical `ErrorCodes` enum members to `AppException`; guard dictionary indexing in test assertions with positive key membership or typed assertions. | Pruned ad-hoc string error codes and unverified dictionary indexing. | `uv run python scripts/_ast_guardrails.py backend_v2/scripts/generate_openapi.py backend_v2/tests/unit/services/mcp/test_mcp_tool_loop.py backend_v2/tests/unit/test_tavily_search_client.py backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py --strict` |
| `@[scripts/audit_database_atoms.py]`, `@[scripts/reconcile_storage.py]`, `@[scripts/audit_rules_staleness.py]`, `@[scripts/audit_matrix_auto_filler.py]`, `@[scripts/audit_matrix_manager.py]`, `@[scripts/matrix_slice_engine.py]` | Duck-typing via `isinstance(dict)` (QGR012: 12 in `audit_database_atoms.py`); missing `ConfigDict(strict=True, extra="forbid")` (QGR007: 2 in `reconcile_storage.py`); `hasattr` reflection and exception swallowing (QGR001, QGR003: 2 in `audit_rules_staleness.py`); `.get()` lookups (QGR002: 2 in `audit_matrix_auto_filler.py`, 2 in `matrix_slice_engine.py`); `vars()` reflection (QGR001: 2 in `audit_matrix_manager.py`). | Replace `isinstance(dict)` with typed schema validation; exempt illustrative prompt examples per `05_llm_architecture.md`; enforce fail-fast exit on structural defects when `--strict` is enabled; add explicit ConfigDict; replace reflection and `.get()` with typed dot-notation and bracket indexing. | Pruned ad-hoc dict inspections in tooling; use native Pydantic V2 DTOs. | `uv run python scripts/_ast_guardrails.py scripts/audit_database_atoms.py scripts/reconcile_storage.py scripts/audit_rules_staleness.py scripts/audit_matrix_auto_filler.py scripts/audit_matrix_manager.py scripts/matrix_slice_engine.py --strict` |
| `[NEW] @[scripts/audit_warning_baseline.py]` | Unmonitored warning drift, silent re-introduction of fatal violations, and lack of mathematical proof that warning count decreases monotonically. | Deterministic ledger script asserting exactly 0 FATAL violations across all 896 `backend_v2/` files and verifying total warnings never exceed the 1,208 warning ceiling; provides `--verify-zero` flag for Phase 4 completion gate. | Pruned heavy database storage; lightweight deterministic AST runner reading stdout into structured Pydantic V2 DTOs. | `uv run python scripts/audit_warning_baseline.py` |
| `@[AGENTS.md]`, `@[.agents/workflows/tier2-execute.md]`, `@[.agents/workflows/tier1-tracker-generator.md]`, `@[.agents/workflows/tier1-plan-tracker-generator.md]`, `@[.agents/workflows/tier8-audit-plan.md]`, `@[.agents/workflows/tier8-red-teaming-audit.md]`, `@[.agents/workflows/tier2-hardening-knowledge.md]`, `@[.agents/workflows/tier0-create-epic.md]`, `@[.agents/workflows/tier0-research-epic.md]`, `@[.agents/workflows/tier3-minify-customization.md]`, `@[.agents/workflows/tier3-database-reset.md]` | Permissive audit loop calls lacking `--ast-strict`; fragmented testing gates ("Fake Green"); vague database reset instructions; un-integrated audit tools (`audit_plan_tracker_parity.py`, `audit_rules_staleness.py`, `audit_epic_coverage.py`, `audit_markdown_boundaries.py`). | Mandate `--ast-strict` by default in `AGENTS.md` and `tier2-execute.md`; enforce Two-Stage Testing Pipeline (localized tests during steps; global completion gate `backend_audit_loop.py backend_v2/ --test` and `flutter_audit_loop.py client_app_v2/ --build` before closing any phase); integrate specialized audit tools into workflow verification gates; bind explicit commands in `tier3-database-reset.md`. | Pruned redundant manual instructions; enforce automated script gates. | `uv run python scripts/audit_rules_staleness.py` and `uv run python scripts/audit_plan_tracker_parity.py --plan docs/epic/tasks_EPIC_156/01_phase1_plan.md --tracker docs/epic/EPIC_156_tracker.md` |

## Phase 1: Pre-Implementation Cleanups

All technical debt identified across touched files and 1-hop callers is quarantined and queued for pre-implementation resolution:
1. **Silent Exception Handlers (53 instances of QGR003)**: Handlers in repositories, seeders, and worker wrappers catching exceptions and continuing without `raise` or typed DLQ dispatch. Cleaned in Step 1.6.
2. **Comment Suppressions (10 instances of QGR000)**: Illegal `# noqa: QGR*` comment suppressions in domain code (`ingress_pipeline.py`, `mock.py`, `vertex_adapter.py`, `openai_adapter.py`, `ai_studio_adapter.py`). Cleaned in Step 1.6.
3. **Duck-Typing Inspections (7 instances of QGR012)**: `isinstance(..., dict)` checks in domain code (`ingress_pipeline.py`, `openai_adapter.py`, `mock.py`). Cleaned in Step 1.6.
4. **Type Laundering (4 instances of QGR018)**: `TypeAdapter(dict)` instances in `source_verification_hook.py`, `metrics.py`, `security.py`, `validation.py`. Cleaned in Step 1.6.
5. **Prompt F-String Interpolation (1 instance of QGR022)**: Unshielded f-string XML prompt structure in `tavily_search_client.py:285`. Cleaned in Step 1.6.
6. **Jinja Dumb Painter Fallbacks (7 instances)**: Fallback expressions (`or ''`, `or []`, `or {}`) in `report_template.jinja2` lines 390, 391, 413, 421, 422, 440, 461. Cleaned in Step 1.5.
7. **Missing Model Strictness (7 instances of QGR007)**: Pydantic models lacking `ConfigDict(strict=True, extra="forbid")` in `hook_registry.py`, `registry.py`, `chunking.py`, `step.py`, `trace.py`. Cleaned in Step 1.7.
8. **Tuple Hell State Transit (22 instances of QGR023)**: Methods returning 3+ element tuples across `pdf_chat_extractor.py`, `synthesis_reducers.py`, `two_pass_atomizer.py`, `schema_builder.py`, `ingress_service.py`, `chat_parser.py`, `integrity.py`, `base.py`. Cleaned in Step 1.7.
9. **Active Tooling Script Debt (22 instances)**: Duck typing, reflection, and `.get()` lookups across `audit_database_atoms.py`, `reconcile_storage.py`, `audit_rules_staleness.py`, `audit_matrix_auto_filler.py`, `audit_matrix_manager.py`, `matrix_slice_engine.py`. Cleaned in Step 1.8.

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state. Verify baseline violation count across 896 backend files (79 FATAL, 1,254 WARNING) and 26 tooling scripts.</action>
    <action>Look forward: Verify that adding QGR024, QGR025, Clean Imports, and 8-stage audit loop provides the foundation for subsequent zero-warning eradication without destabilizing offline diagnostic suites.</action>
    <constraint>If alignment is broken or baseline diverges unexpectedly, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_156_Universal_AST_Strictness_and_Advisory_Warning_Eradication.md]) and the Tracker document (@[docs/epic/EPIC_156_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_156/01_phase1_plan.md] @[docs/epic/EPIC_156_tracker.md] --full-auto`.</directive>
  </step>

  <dod_checklist>
    <item>QGR024 implemented in scripts/_ast_guardrails.py banning string-quoted annotations while exempting Literal[...] slices and Annotated[...] metadata arguments.</item>
    <item>QGR025 implemented in scripts/_ast_guardrails.py banning untyped dictionaries in model_copy(update=...) while permitting static typed dictionary literals.</item>
    <item>Comprehensive unit test suite for QGR013 through QGR025 implemented in backend_v2/tests/unit/scripts/test_ast_guardrails.py.</item>
    <item>Clean import verification tool scripts/audit_clean_imports.py and test backend_v2/tests/unit/scripts/test_clean_imports.py implemented.</item>
    <item>Expanded 8-stage backend_audit_loop.py pipeline functional with Clean Imports (Stage 7) and DTO Parity (Stage 8), hardened Jinja Dumb Painter regex, and 7 Jinja template fallbacks eradicated.</item>
    <item>All 79 pre-existing domain fatal violations in backend_v2 eradicated.</item>
    <item>Low-count advisory warning violations (46 instances: QGR007, QGR023, QGR009, QGR008, QGR006, QGR011) eradicated in domain code.</item>
    <item>Active tooling script violations (22 instances across 6 scripts) eradicated.</item>
    <item>Rules QGR007, QGR023, QGR009, QGR008, QGR006, QGR011, QGR024, and QGR025 promoted to FATAL severity in scripts/_ast_guardrails.py.</item>
    <item>Warning baseline ledger script scripts/audit_warning_baseline.py implemented asserting warning counts do not exceed 1,208 warnings and 0 fatals.</item>
    <item>Agentic workflows in AGENTS.md and .agents/workflows/ synchronized with mandatory strict quality gates, plan-tracker parity, and rule staleness auditing.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Offline statistical research suites: scripts/diff_executions.py (3,260 LOC) and scripts/run_e2e_variance_test.py (2,108 LOC) are quarantined under _is_domain_code = False.</anti_target>
    <anti_target>Test suite repository mocks under QGR014 (quarantined strictly for Phase 2).</anti_target>
    <anti_target>Broad domain .get() lookups under QGR002 and duck-typing under QGR012 (quarantined strictly for Phase 3).</anti_target>
    <anti_target>Third-party mutation frameworks (mutmut, cosmic-ray) - banned per Axis 4.</anti_target>
  </anti_targets>

  <touched_artifacts>
    <backend>@[scripts/_ast_guardrails.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]</backend>
    <backend>[NEW] @[scripts/audit_clean_imports.py]</backend>
    <backend>[NEW] @[backend_v2/tests/unit/scripts/test_clean_imports.py]</backend>
    <backend>@[scripts/backend_audit_loop.py]</backend>
    <backend>@[backend_v2/templates/report_template.jinja2]</backend>
    <backend>[NEW] @[scripts/audit_warning_baseline.py]</backend>
    <backend>@[scripts/audit_database_atoms.py]</backend>
    <backend>@[scripts/reconcile_storage.py]</backend>
    <backend>@[scripts/audit_rules_staleness.py]</backend>
    <backend>@[scripts/audit_matrix_auto_filler.py]</backend>
    <backend>@[scripts/audit_matrix_manager.py]</backend>
    <backend>@[scripts/matrix_slice_engine.py]</backend>
    <backend>@[backend_v2/run_worker.py]</backend>
    <backend>@[backend_v2/database/wrapper.py]</backend>
    <backend>@[backend_v2/hooks/llm.py]</backend>
    <backend>@[backend_v2/llm/handler.py]</backend>
    <backend>@[backend_v2/llm/ingress_pipeline.py]</backend>
    <backend>@[backend_v2/hooks/source_verification_hook.py]</backend>
    <backend>@[backend_v2/seed/run_seed.py]</backend>
    <backend>@[backend_v2/database/repositories/knowledge.py]</backend>
    <backend>@[backend_v2/database/repositories/audit.py]</backend>
    <backend>@[backend_v2/database/repositories/base.py]</backend>
    <backend>@[backend_v2/database/repositories/identity.py]</backend>
    <backend>@[backend_v2/database/repositories/workflow.py]</backend>
    <backend>@[backend_v2/llm/adapters/ai_studio_adapter.py]</backend>
    <backend>@[backend_v2/llm/adapters/openai_adapter.py]</backend>
    <backend>@[backend_v2/llm/adapters/vertex_adapter.py]</backend>
    <backend>@[backend_v2/llm/mock.py]</backend>
    <backend>@[backend_v2/models/domain/metrics.py]</backend>
    <backend>@[backend_v2/models/domain/security.py]</backend>
    <backend>@[backend_v2/models/domain/validation.py]</backend>
    <backend>@[backend_v2/models/dtos/matrix_scorecard.py]</backend>
    <backend>@[backend_v2/services/auth.py]</backend>
    <backend>@[backend_v2/services/cache/typed_cache.py]</backend>
    <backend>@[backend_v2/services/chat_normalizer.py]</backend>
    <backend>@[backend_v2/services/drivers/gcs_file_driver.py]</backend>
    <backend>@[backend_v2/services/execution/lifecycle_service.py]</backend>
    <backend>@[backend_v2/services/execution/stream_service.py]</backend>
    <backend>@[backend_v2/services/mcp/tavily_search_client.py]</backend>
    <backend>@[backend_v2/core/hook_registry.py]</backend>
    <backend>@[backend_v2/core/registry.py]</backend>
    <backend>@[backend_v2/models/chunking.py]</backend>
    <backend>@[backend_v2/models/domain/step.py]</backend>
    <backend>@[backend_v2/models/dtos/trace.py]</backend>
    <backend>@[backend_v2/hooks/integrity.py]</backend>
    <backend>@[backend_v2/llm/schema_builder.py]</backend>
    <backend>@[backend_v2/services/chat_parser.py]</backend>
    <backend>@[backend_v2/services/execution/ingress_service.py]</backend>
    <backend>@[backend_v2/services/ingress/pdf_chat_extractor.py]</backend>
    <backend>@[backend_v2/services/orchestrator/two_pass_atomizer.py]</backend>
    <backend>@[backend_v2/workers/synthesis_reducers.py]</backend>
    <backend>@[backend_v2/scripts/generate_openapi.py]</backend>
    <backend>@[backend_v2/tests/unit/services/mcp/test_mcp_tool_loop.py]</backend>
    <backend>@[backend_v2/tests/unit/test_tavily_search_client.py]</backend>
    <backend>@[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py]</backend>
    <backend>@[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py]</backend>
  </touched_artifacts>

  <step id="1.1" name="Implement QGR024 (String-Quoted Annotation Ban)">
    <action>In `@[scripts/_ast_guardrails.py]`, add AST visitor inspection for `ast.AnnAssign` and `FunctionDef.returns` detecting string literal constants (`ast.Constant` with string value) used as type annotations.</action>
    <action>Enforce False-Positive Defense: The AST visitor MUST explicitly exclude string constants that are slice arguments to `Literal[...]` (specifically: `Literal['development', 'production']`) or metadata arguments to `Annotated[T, 'Description']` and `Annotated[T, Field(description='...')]`.</action>
    <constraint invariant="deferred_annotations_and_typing">Python 3.14 natively compiles annotations into lazy annotate functions evaluated on-demand via annotationlib; string quotation forward-reference hacks are strictly prohibited.</constraint>
  </step>

  <step id="1.2" name="Implement QGR025 (Untyped Dict in model_copy Ban)">
    <action>In `@[scripts/_ast_guardrails.py]`, add AST visitor inspection for calls to `model_copy(update=...)`.</action>
    <action>Flag calls passing dynamic dictionary variables, function return calls, or unvalidated dictionary unpacking.</action>
    <action>Enforce Concurrency Progress Defense: The AST visitor MUST explicitly permit dictionary literals (`ast.Dict`) whose keys and values are statically known and typed (specifically: `{'status': ExecutionStatus.RUNNING, 'progress': 100}`), preserving atomic progress tracking within `async with _update_lock:`.</action>
    <constraint invariant="safe_model_copy_concurrency_boundary">Untyped dictionary state injection is banned; progress dictionary literals with statically known keys are explicitly permitted.</constraint>
  </step>

  <step id="1.3" name="Comprehensive Unit Tests for AST Engine">
    <action>In `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`, add explicit positive and negative test cases for every rule from QGR013 through QGR025.</action>
    <action>Include explicit false-positive defense assertions for QGR024 verifying `Literal['a', 'b']` and `Annotated[T, 'desc']` pass with zero violations.</action>
    <action>Include explicit false-positive defense assertions for QGR025 verifying typed dictionary literals in `model_copy(update={'status': ExecutionStatus.RUNNING})` pass with zero violations.</action>
    <constraint invariant="zero_tolerance_audit_loop">100% unit test coverage for the AST engine is mandatory.</constraint>
  </step>

  <step id="1.4" name="Implement Clean Import Smoke Test Tool">
    <action>Create [NEW] `@[scripts/audit_clean_imports.py]` implementing a deterministic scanner that recursively imports every module across all 896 files in `backend_v2/` via `importlib.import_module()`.</action>
    <action>Create [NEW] `@[backend_v2/tests/unit/scripts/test_clean_imports.py]` to test the clean import scanner with synthetic isolated modules.</action>
    <action>Assert zero `ImportError`, zero `AttributeError`, and zero circular dependency deadlocks.</action>
    <constraint invariant="the_no_legacy_mandate">Module imports must be side-effect free and pass cleanly in isolation.</constraint>
  </step>

  <step id="1.5" name="Expand backend_audit_loop.py to 8-Stage Mandatory Pipeline">
    <action>In `@[scripts/backend_audit_loop.py]`, integrate Stage 7/8 executing `scripts/audit_clean_imports.py`.</action>
    <action>In `@[scripts/backend_audit_loop.py]`, integrate Stage 8/8 executing `scripts/audit_dto_parity.py`.</action>
    <action>In `@[scripts/backend_audit_loop.py]`, expand Stage 5/8 Jinja Dumb Painter regex to detect fallback expressions (`or ''`, `or []`, `or {}`).</action>
    <action>In `@[backend_v2/templates/report_template.jinja2]`, eliminate 7 Jinja fallback violations (specifically: lines 390, 391, 413, 421, 422, 440, 461) by replacing `or ''`, `or []`, and `or {}` expressions with backend DTO-guaranteed non-None defaults.</action>
    <action>Equip `backend_audit_loop.py` with Scoped Boy Scout strictness: fail-fast if any actively touched target contains unsuppressed warnings.</action>
    <constraint invariant="single_pipeline_invariant_mandate">Quality gates execute sovereignly through exactly one deterministic pipeline.</constraint>
  </step>

  <step id="1.6" name="Eradicate Pre-Existing Domain FATAL Violations">
    <action>In `@[backend_v2/seed/run_seed.py]` (7 instances of QGR003): Refactor `_fail_fast()` to raise `AppException(ErrorCodes.VALIDATION_FAILED)` instead of `sys.exit(1)`, and replace module-level empty exception handlers with structured logging and re-raise.</action>
    <action>In `@[backend_v2/database/repositories/knowledge.py]` (4 instances of QGR003): In `get_banned_phrases()`, eliminate silent skipping of validation errors; log RFC 7807 error and re-raise typed `AppException(ErrorCodes.VALIDATION_FAILED)` per universal fail-fast.</action>
    <action>In `@[backend_v2/database/repositories/audit.py]` (3 instances of QGR003), `@[backend_v2/database/repositories/base.py]` (1 instance of QGR003), `@[backend_v2/database/repositories/identity.py]` (2 instances of QGR003), and `@[backend_v2/database/repositories/workflow.py]` (3 instances of QGR003): Replace silent exception swallowing with structured logging and `raise AppException(ErrorCodes.DATABASE_ERROR)`.</action>
    <action>In `@[backend_v2/database/wrapper.py]` (5 instances of QGR003, 2 instances of QGR002): Re-raise caught exceptions as typed `AppException`; replace unexempted dictionary `.get()` calls with bracket indexing after positive membership validation; import timeouts from `backend_v2/settings.py`.</action>
    <action>In `@[backend_v2/run_worker.py]` (3 instances of QGR003), `@[backend_v2/hooks/llm.py]` (2 instances of QGR003), and `@[backend_v2/llm/handler.py]` (4 instances of QGR003): Replace silent exception handlers with explicit `raise` or typed DLQ dispatch (`dlq_service.push()`).</action>
    <action>In `@[backend_v2/llm/ingress_pipeline.py]` (4 instances of QGR000, 4 instances of QGR012): Remove `# noqa: QGR*` comment suppressions; replace `isinstance(..., dict)` duck-typing checks with native Pydantic V2 discriminated union validation.</action>
    <action>In `@[backend_v2/hooks/source_verification_hook.py]` (1 instance of QGR018, 2 instances of QGR003): Replace banned `TypeAdapter(dict)` type laundering by defining [NEW] `SourceVerificationPayloadDTO`; re-raise typed `AppException` in exception handlers.</action>
    <action>In `@[backend_v2/llm/mock.py]` (1 instance of QGR000, 1 instance of QGR012): Remove `# noqa: QGR012` suppression; replace `isinstance(..., dict)` with typed schema validation.</action>
    <action>In `@[backend_v2/llm/adapters/ai_studio_adapter.py]` (1 instance of QGR000, 1 instance of QGR003, 2 instances of QGR002), `@[backend_v2/llm/adapters/openai_adapter.py]` (3 instances of QGR000, 1 instance of QGR003, 2 instances of QGR012), and `@[backend_v2/llm/adapters/vertex_adapter.py]` (1 instance of QGR000, 2 instances of QGR003): Remove `# noqa` comments; resolve underlying violations by re-raising typed `AppException` and replacing `isinstance(dict)` with typed DTO validation.</action>
    <action>In `@[backend_v2/models/domain/metrics.py]` (1 instance of QGR018), `@[backend_v2/models/domain/security.py]` (1 instance of QGR018), and `@[backend_v2/models/domain/validation.py]` (1 instance of QGR018): Replace banned `_dict_adapter = TypeAdapter(dict[str, Any])` type laundering with `ExecutionInputsDTO` or typed Pydantic V2 models.</action>
    <action>In `@[backend_v2/models/dtos/matrix_scorecard.py]` (1 instance of QGR003), `@[backend_v2/services/auth.py]` (4 instances of QGR003), `@[backend_v2/services/cache/typed_cache.py]` (2 instances of QGR003), `@[backend_v2/services/chat_normalizer.py]` (2 instances of QGR003), `@[backend_v2/services/drivers/gcs_file_driver.py]` (1 instance of QGR003), `@[backend_v2/services/execution/lifecycle_service.py]` (1 instance of QGR003), and `@[backend_v2/services/execution/stream_service.py]` (2 instances of QGR003): Eliminate silent exception swallowing; replace with structured RFC 7807 logging and re-raise typed `AppException`.</action>
    <action>In `@[backend_v2/services/mcp/tavily_search_client.py]` (1 instance of QGR022): At line 285, replace unshielded f-string XML prompt structure with structured PromptBlock assembly or template string.</action>
    <constraint invariant="universal_fail_fast">Zero tolerance for silent bypasses or fatal AST errors in domain code.</constraint>
  </step>

  <step id="1.7" name="Eradicate Low-Count Advisory Warning Violations">
    <action>In `@[backend_v2/core/hook_registry.py]` (2 instances of QGR007), `@[backend_v2/core/registry.py]` (1 instance of QGR007), `@[backend_v2/models/chunking.py]` (2 instances of QGR007), `@[backend_v2/models/domain/step.py]` (1 instance of QGR007), and `@[backend_v2/models/dtos/trace.py]` (1 instance of QGR007): Add explicit `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)` to Pydantic models.</action>
    <action>In `@[backend_v2/models/dtos/trace.py]` (1 instance of QGR011): At line 50, replace mutable default argument in method definition with `= None` and factory initialization in the method body.</action>
    <action>In `@[backend_v2/hooks/integrity.py]` (1 instance of QGR023), `@[backend_v2/llm/schema_builder.py]` (2 instances of QGR023), `@[backend_v2/services/chat_parser.py]` (1 instance of QGR023), `@[backend_v2/services/execution/ingress_service.py]` (1 instance of QGR023), `@[backend_v2/services/ingress/pdf_chat_extractor.py]` (9 instances of QGR023), `@[backend_v2/services/orchestrator/two_pass_atomizer.py]` (2 instances of QGR023), and `@[backend_v2/workers/synthesis_reducers.py]` (5 instances of QGR023): Refactor methods returning 3+ element tuples to return dedicated, immutable Pydantic V2 DTOs (specifically: defining `ChunkPacketDTO`, `SectionReductionDTO`).</action>
    <action>In `@[backend_v2/scripts/generate_openapi.py]` (1 instance of QGR009), `@[backend_v2/services/execution/ingress_service.py]` (7 instances of QGR009), `@[backend_v2/tests/unit/services/mcp/test_mcp_tool_loop.py]` (1 instance of QGR009), and `@[backend_v2/tests/unit/test_tavily_search_client.py]` (2 instances of QGR009): Bind canonical `ErrorCodes` enum members from `@[backend_v2/models/enums.py]` to all `AppException` instantiations.</action>
    <action>In `@[backend_v2/database/wrapper.py]` (3 instances of QGR008): Import timeouts and retry intervals centrally from `backend_v2/settings.py` instead of hardcoded numbers.</action>
    <action>In `@[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py]` (1 instance of QGR006) and `@[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py]` (1 instance of QGR006): Replace unguarded dictionary subscripting in test assertions with positive membership checks or typed assertions.</action>
    <constraint invariant="the_zero_compromise_pledge">Enforce strict Pydantic V2 schemas and eliminate tuple state transit.</constraint>
  </step>

  <step id="1.8" name="Eradicate Advisory Warnings in Active Tooling &amp; Audit Scripts">
    <action>In `@[scripts/audit_database_atoms.py]` (12 instances of QGR012): Replace `isinstance(..., dict)` duck-typing with typed schema validation; update prompt ambiguity inspection to exempt illustrative examples per `@[.agents/rules/05_llm_architecture.md]`; enforce fail-fast exit on structural defects when `--strict` is enabled.</action>
    <action>In `@[scripts/reconcile_storage.py]` (2 instances of QGR007): Add explicit `model_config = ConfigDict(strict=True, extra="forbid")` to `TraceEventContent` and `TraceEventHeader`.</action>
    <action>In `@[scripts/audit_rules_staleness.py]` (2 instances): Replace `hasattr()` with typed attribute access and replace broad exception swallowing with structured logging and re-raise.</action>
    <action>In `@[scripts/audit_matrix_auto_filler.py]` (2 instances of QGR002): Replace `.get()` calls with typed dictionary key indexing.</action>
    <action>In `@[scripts/audit_matrix_manager.py]` (2 instances of QGR001): Replace `vars()` reflection with `.model_dump()` or explicit attribute mapping.</action>
    <action>In `@[scripts/matrix_slice_engine.py]` (2 instances of QGR002): Replace `.get()` calls with bracket indexing.</action>
    <constraint invariant="ssot_reusability_mandate">Active audit scripts must pass strict quality gates without warnings.</constraint>
  </step>

  <step id="1.9" name="Promote Cleaned Rules to FATAL Severity &amp; Build Baseline Ledger">
    <action>In `@[scripts/_ast_guardrails.py]`, update visitor methods for QGR007, QGR023, QGR009, QGR008, QGR006, QGR011, QGR024, and QGR025 to unconditionally assign FATAL severity.</action>
    <action>Create [NEW] `@[scripts/audit_warning_baseline.py]` to record the exact warning count per rule code and assert total warnings never exceed 1,208 warnings and 0 fatals.</action>
    <action>Run full AST scan across backend_v2: verify 0 FATAL violations (down from 79 to 0) and total warnings reduced from 1,254 to 1,208.</action>
    <constraint invariant="neuro_symbolic_grounding_mandate">Rely on deterministic audit scripts to mathematically prove zero fatal regressions.</constraint>
  </step>

  <step id="1.10" name="Synchronize Agentic Workflows &amp; Quality Gate Alignment">
    <action>In `@[AGENTS.md]` and `@[.agents/workflows/tier2-execute.md]`, mandate strict AST mode by default (`uv run python scripts/backend_audit_loop.py <target_path> --test --ast-strict`) and enforce the Two-Stage Testing Pipeline (localized tests during steps; global completion gate `backend_audit_loop.py backend_v2/ --test` and `flutter_audit_loop.py client_app_v2/ --build` before closing any phase).</action>
    <action>Integrate `@[scripts/audit_plan_tracker_parity.py]` as a mandatory verification gate in `@[.agents/workflows/tier1-tracker-generator.md]`, `@[.agents/workflows/tier1-plan-tracker-generator.md]`, and `@[.agents/workflows/tier8-audit-plan.md]`.</action>
    <action>Integrate `@[scripts/audit_rules_staleness.py]` as a mandatory verification gate in `@[.agents/workflows/tier8-red-teaming-audit.md]` and `@[.agents/workflows/tier2-hardening-knowledge.md]`.</action>
    <action>Integrate `@[scripts/audit_epic_coverage.py]` as a mandatory verification gate in `@[.agents/workflows/tier0-create-epic.md]` and `@[.agents/workflows/tier0-research-epic.md]`.</action>
    <action>Integrate `@[scripts/audit_markdown_boundaries.py]` as a mandatory verification gate in `@[.agents/workflows/tier3-minify-customization.md]`.</action>
    <action>In `@[.agents/workflows/tier3-database-reset.md]`, replace vague audit commands with explicit executable commands: `uv run python backend_v2/seed/run_seed.py local` followed by `uv run python scripts/backend_audit_loop.py backend_v2/seed/ --test`.</action>
    <constraint invariant="universal_quality_gates">Zero tolerance for permissive workflow bypasses or orphaned audit scripts.</constraint>
  </step>

  <test_contracts>
    <test name="test_qgr024_string_quoted_annotation_raises_fatal" category="positive">
      <input>Source code with target: "StepOutputDTO"</input>
      <expected>QuorumGuardrailVisitor emits FATAL violation for QGR024</expected>
    </test>
    <test name="test_qgr024_literal_string_slice_permitted" category="boundary">
      <input>Source code with env: Literal['development', 'production']</input>
      <expected>QuorumGuardrailVisitor emits zero violations for QGR024</expected>
    </test>
    <test name="test_qgr024_annotated_metadata_description_permitted" category="boundary">
      <input>Source code with field: Annotated[int, 'Description string']</input>
      <expected>QuorumGuardrailVisitor emits zero violations for QGR024</expected>
    </test>
    <test name="test_qgr025_dynamic_dict_in_model_copy_raises_fatal" category="positive">
      <input>Source code with model.model_copy(update=untyped_dict)</input>
      <expected>QuorumGuardrailVisitor emits FATAL violation for QGR025</expected>
    </test>
    <test name="test_qgr025_typed_literal_dict_in_model_copy_permitted" category="boundary">
      <input>Source code with model.model_copy(update={'status': ExecutionStatus.RUNNING})</input>
      <expected>QuorumGuardrailVisitor emits zero violations for QGR025</expected>
    </test>
    <test name="test_clean_imports_detects_circular_dependency" category="error_path">
      <input>Two synthetic modules importing each other at top level</input>
      <expected>scripts/audit_clean_imports.py exits with non-zero code reporting circular import</expected>
    </test>
    <test name="test_backend_audit_loop_runs_all_8_stages" category="positive">
      <input>Run backend_audit_loop.py with target scripts/_ast_guardrails.py</input>
      <expected>Stages 1 through 8 execute sequentially and return exit code 0</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute AST guardrails on AST engine: `uv run python scripts/_ast_guardrails.py scripts/_ast_guardrails.py --strict`</action>
    <action>Execute AST unit tests: `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py`</action>
    <action>Execute clean import scanner test: `uv run pytest backend_v2/tests/unit/scripts/test_clean_imports.py`</action>
    <action>Execute clean import verification across all 896 modules: `uv run python scripts/audit_clean_imports.py`</action>
    <action>Execute warning baseline ledger: `uv run python scripts/audit_warning_baseline.py` (Assert: 0 FATAL errors, total warnings &lt;= 1,208)</action>
    <action>Execute active tooling AST check: `uv run python scripts/_ast_guardrails.py scripts/audit_database_atoms.py scripts/reconcile_storage.py scripts/audit_rules_staleness.py scripts/audit_matrix_auto_filler.py scripts/audit_matrix_manager.py scripts/matrix_slice_engine.py --strict`</action>
    <action>Execute 8-stage audit loop on touched tools: `uv run python scripts/backend_audit_loop.py scripts/_ast_guardrails.py --test`</action>
  </validation_gate>
</execution_protocol>
```
