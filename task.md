# Eradication of Lazy `.get()` and `getattr()` Calls Tracker

## Plan Context
- Source Plan: `@[docs/implementationplans/plan_lazy_get_getattr_eradication.md]`
- Status: In Progress (Continuous Full-Auto)

## Tasks Checklist

- [x] **Phase 1: Knowledge Item SSOT Synchronization, Pre-Implementation Cleanups & AST Guardrail Calibration**
  - [x] Update `ki_zero_permissive_typing.md` (lock 8 boundary files, router/redis exemptions, external ACL standard, 4 canonical patterns)
  - [x] Update `scripts/_ast_guardrails.py` (exempt wrapper.py, subrouters, Redis clients, _get_table)
  - [x] Update `scripts/audit_dict_eradication.py` (CLI --strict fix, expand is_domain_or_service to all non-test backend_v2, reflection visitor checks, receiver exemptions)
  - [x] Run quality gate: `uv run python scripts/_ast_guardrails.py backend_v2` and `uv run python scripts/audit_dict_eradication.py`
  - [x] Git commit Phase 1

- [x] **Phase 2: Models & DTO Validation Layer**
  - [x] Update `backend_v2/models/dtos/quote_evidence.py` (resolve_source_id & resolve_and_verify_aliases)
  - [x] Update `backend_v2/models/domain/mechanical_anchors.py` (from_context accepting LLMContextDataDTO | None, positive checks)
  - [x] Update `backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py` (pass llm_context_data directly)
  - [x] Update `backend_v2/tests/unit/models/domain/test_mechanical_anchors.py` (fixtures with LLMContextDataDTO)
  - [x] Update `backend_v2/models/dtos/evaluation_steps.py` (_sanitize_source_aliases)
  - [x] Run quality gate: `uv run pytest backend_v2/tests/unit/models/` and `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/quote_evidence.py --test`
  - [x] Git commit Phase 2

- [x] **Phase 3: Orchestration & Prompt Compilation Layer**
  - [x] Update `backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py` (Fail-Fast AppException on missing atom)
  - [x] Run quality gate: `uv run pytest backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py`
  - [x] Git commit Phase 3

- [x] **Phase 4: External Ingress & LLM Adapters Layer**
  - [x] Update `backend_v2/services/ingress/pdf_chat_extractor.py` (positive drawing dict checks)
  - [x] Update `backend_v2/llm/adapters/openai_adapter.py` (positive checks on info and schema)
  - [x] Update `backend_v2/llm/adapters/anthropic_adapter.py` (positive check on call_kwargs)
  - [x] Update `backend_v2/llm/adapters/base_adapter.py` (positive check on discriminator propertyName)
  - [x] Update `backend_v2/llm/ingress_pipeline.py` (positive checks on discriminator_field)
  - [x] Update `backend_v2/llm/client.py` (positive check on schema_err.details error_code)
  - [x] Update `backend_v2/llm/mock.py` (positive check on response_schema title)
  - [x] Run quality gate: `uv run pytest backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py backend_v2/tests/unit/llm/`
  - [x] Git commit Phase 4

- [ ] **Phase 5: Core Services & Infrastructure**
  - [ ] Update `backend_v2/services/auth.py` (positive check on sub and email)
  - [ ] Update `backend_v2/main.py` (positive check on id and trace path)
  - [ ] Run quality gate: `uv run pytest backend_v2/tests/unit/test_auth.py`
  - [ ] Git commit Phase 5

- [ ] **Phase 6: Test Suite Modernization (Eradicating `getattr()` Reflection)**
  - [ ] Modernize `backend_v2/tests/test_worker_models_used.py`
  - [ ] Modernize `backend_v2/tests/integration/test_epic_chain_e2e.py`
  - [ ] Modernize `backend_v2/tests/test_caching_schema_scrub_bug.py`
  - [ ] Modernize `backend_v2/tests/unit/llm/test_structured_retry.py`
  - [ ] Modernize `backend_v2/tests/unit/test_llm_task_executor.py`
  - [ ] Modernize `backend_v2/tests/unit/services/test_llm_task_executor.py`
  - [ ] Modernize `backend_v2/tests/unit/test_litellm_redis_timeout.py`
  - [ ] Modernize `backend_v2/tests/unit/test_epic66_multi_provider.py`
  - [ ] Modernize `backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py`
  - [ ] Run quality gate: `uv run pytest` on modernized test files
  - [ ] Git commit Phase 6

- [ ] **Phase 7: Codebase-Wide Verification & Quality Gates**
  - [ ] Run `uv run python scripts/_ast_guardrails.py backend_v2`
  - [ ] Run `uv run python scripts/audit_dict_eradication.py --strict`
  - [ ] Run full `uv run python scripts/backend_audit_loop.py backend_v2 --test`
  - [ ] Final audit reporting and session wrap-up
