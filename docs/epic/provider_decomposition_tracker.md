<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Master Decomposition Tracker: `backend_v2/llm/provider.py` (`LLMProvider`, `LiteLLMProvider`, `MockProvider`, `LLMFactory`)

- **Target Monolith**: `[DELETE] @[backend_v2/llm/provider.py]` (1,846 lines)
- **Target Domain Package**: `backend_v2/llm/provider/` (`< 430` lines per sub-module, `< 160` lines for `__init__.py` facade)
- **Symbol & Blast-Radius Map**: `@[docs/epic/tasks_provider/symbol_migration_map.md]`
- **Monolith Archetype**: **Archetype C / D Hybrid — External LLM Anti-Corruption Layer (ACL) & Micro-Concurrency Core** (Two-Tier Concurrency Dynamic RPM Semaphore, Adaptive `Retry-After` Tenacity Policy, Sequential Response/Telemetry Stage Separation, RFC 7807 Dual-Reporting & OpenTelemetry GenAI Semantic Span Parity)
- **Pre-Flight Test Baseline (`[BASELINE]`)**: **34 passed unit tests, 92% line coverage** (`785` statements, `66` missed across `test_provider.py`, `test_provider_httpx_client.py`, `test_provider_penalties.py`, `test_provider_retry_after.py`, `test_provider_telemetry.py`, and `test_provider_toolcalls.py`). Exceeds the `75%` minimum coverage gate (`Phase 0` skipped).

---

## Phase Execution Status

### Phase 1: Leaf Environment/Schema Utilities & Transient Retry Policy Extraction (Epoch 1 Leaf & Policy)
- **Plan:** @[docs/epic/tasks_provider/phase1_leaf_utils_and_retry_policy_extraction.md]
- [x] **[SKIPPED] Research:** Complete 4-Phase Strangler Fig Decomposition pre-researched in Tier 3
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_provider/phase1_leaf_utils_and_retry_policy_extraction.md] @[docs/epic/provider_decomposition_tracker.md]`
  - [x] Step 1: Create `[NEW] @[backend_v2/tests/unit/llm/provider/__init__.py]`, extend `is_boundary_exempt` in `@[scripts/_ast_guardrails.py#L98-L107]` to cover `backend_v2/llm/provider/`, and create `[NEW] @[backend_v2/llm/provider/env_and_schema_utils.py]` (`_safe_static_getattr`, `_safe_static_hasattr`, `_INTERNAL_NON_API_KEYS`, `resolve_env_variables`, `_normalize_mcp_tool_schema_for_llm`, `_sync_diagnostic_dump`) and `[NEW] @[backend_v2/llm/provider/transient_retry_policy.py]` (`_is_transient_llm_error`, `_RETRY_AFTER_REGEX`, `_extract_retry_after_seconds`, `_AdaptiveWaitWithRetryAfter`, `_format_attempt_error`) without creating `backend_v2/llm/provider/__init__.py`.
  - [x] Step 2: Update `[DELETE] @[backend_v2/llm/provider.py]` to re-export all Phase 1 symbols using explicit redundant aliases (`Symbol as Symbol`), and create `[NEW] @[backend_v2/tests/unit/llm/provider/test_env_and_schema_utils.py]` and `[NEW] @[backend_v2/tests/unit/llm/provider/test_transient_retry_policy.py]`.
  - [x] Step 3: Run `uv run python scripts/backend_audit_loop.py backend_v2/llm/provider/env_and_schema_utils.py --test --ast-strict`, `uv run python scripts/backend_audit_loop.py backend_v2/llm/provider/transient_retry_policy.py --test --ast-strict`, `uv run python scripts/backend_audit_loop.py scripts/_ast_guardrails.py --test --ast-strict`, and `uv run python scripts/backend_audit_loop.py backend_v2/llm/provider.py --test --ast-strict`.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_provider/phase1_leaf_utils_and_retry_policy_extraction.md] @[docs/epic/provider_decomposition_tracker.md]`

### Phase 2: Base Contract, LogfireShieldedClient, MockProvider & LLMFactory Extraction (Epoch 1 Contracts & Factory)
- **Plan:** @[docs/epic/tasks_provider/phase2_base_mock_and_factory_extraction.md]
- [x] **[SKIPPED] Research:** Complete 4-Phase Strangler Fig Decomposition pre-researched in Tier 3
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_provider/phase2_base_mock_and_factory_extraction.md] @[docs/epic/provider_decomposition_tracker.md]` (`0aa1db612`)
  - [x] Step 1: Create `[NEW] @[backend_v2/llm/provider/base_and_mock_provider.py]` (`LLMProvider`, `LogfireShieldedClient`, `MockProvider`) and `[NEW] @[backend_v2/llm/provider/provider_factory.py]` (`LLMFactory.create_provider`).
  - [x] Step 2: Update `[DELETE] @[backend_v2/llm/provider.py]` to re-export `LLMProvider`, `LogfireShieldedClient`, `MockProvider`, and `LLMFactory` using explicit redundant aliases (`Symbol as Symbol`), and create `[NEW] @[backend_v2/tests/unit/llm/provider/test_base_and_mock_provider.py]` and `[NEW] @[backend_v2/tests/unit/llm/provider/test_provider_factory.py]`.
  - [x] Step 3: Run `uv run python scripts/backend_audit_loop.py backend_v2/llm/provider/base_and_mock_provider.py --test --ast-strict`, `uv run python scripts/backend_audit_loop.py backend_v2/llm/provider/provider_factory.py --test --ast-strict`, and `uv run python scripts/backend_audit_loop.py backend_v2/llm/provider.py --test --ast-strict`.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_provider/phase2_base_mock_and_factory_extraction.md] @[docs/epic/provider_decomposition_tracker.md]`

### Phase 3: LiteLLM Response/Telemetry Stage & LiteLLMProvider Extraction (Epoch 1 Provider Core)
- **Plan:** @[docs/epic/tasks_provider/phase3_litellm_stages_and_provider_extraction.md]
- [x] **[SKIPPED] Research:** Complete 4-Phase Strangler Fig Decomposition pre-researched in Tier 3
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_provider/phase3_litellm_stages_and_provider_extraction.md] @[docs/epic/provider_decomposition_tracker.md]`
  - [x] Step 1: Create `[NEW] @[backend_v2/llm/provider/litellm_response_stage.py]` (`_truncate_for_debug`, `extract_litellm_content_and_usage`, `classify_and_raise_litellm_error`) and `[NEW] @[backend_v2/llm/provider/litellm_provider.py]` (`LiteLLMProvider`).
  - [x] Step 2: Update `[DELETE] @[backend_v2/llm/provider.py]` to re-export `LiteLLMProvider`, `_truncate_for_debug`, `extract_litellm_content_and_usage`, and `classify_and_raise_litellm_error` using explicit redundant aliases (`Symbol as Symbol`), and create `[NEW] @[backend_v2/tests/unit/llm/provider/test_litellm_response_stage.py]` and `[NEW] @[backend_v2/tests/unit/llm/provider/test_litellm_provider.py]`.
  - [x] Step 3: Run `uv run python scripts/backend_audit_loop.py backend_v2/llm/provider/litellm_response_stage.py --test --ast-strict`, `uv run python scripts/backend_audit_loop.py backend_v2/llm/provider/litellm_provider.py --test --ast-strict`, and `uv run python scripts/backend_audit_loop.py backend_v2/llm/provider.py --test --ast-strict`.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_provider/phase3_litellm_stages_and_provider_extraction.md] @[docs/epic/provider_decomposition_tracker.md]`

### Phase 4: Consumer Import Rewiring, Test Modularization, Atomic Package Cutover & QGR017 Lockdown (Epoch 1 Cutover)
- **Plan:** @[docs/epic/tasks_provider/phase4_package_cutover_and_guardrails.md]
- [x] **[SKIPPED] Research:** Complete 4-Phase Strangler Fig Decomposition pre-researched in Tier 3
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_provider/phase4_package_cutover_and_guardrails.md] @[docs/epic/provider_decomposition_tracker.md]`
  - [x] Step 1: Migrate all 16 unit tests from `[DELETE] @[backend_v2/tests/unit/llm/test_provider.py]` into `[NEW] @[backend_v2/tests/unit/llm/provider/test_provider_facade.py]` and the per-submodule test suites under `backend_v2/tests/unit/llm/provider/`, delete `[DELETE] @[backend_v2/tests/unit/llm/test_provider.py]`, and verify `@[backend_v2/tests/unit/llm/test_provider_httpx_client.py#L34-L99]`, `@[backend_v2/tests/unit/llm/test_provider_penalties.py#L14-L76]`, `@[backend_v2/tests/unit/llm/test_provider_retry_after.py#L49-L90]`, and `@[backend_v2/tests/unit/llm/test_provider_toolcalls.py#L11-L89]`.
  - [x] Step 2: Atomically create `[NEW] @[backend_v2/llm/provider/__init__.py]` (`< 160` lines), physically delete `[DELETE] @[backend_v2/llm/provider.py]`, and rewire 1-hop production callers (`@[backend_v2/llm/client.py#L46-L58]`, `@[backend_v2/llm/handler.py#L878-L1057]`, `@[backend_v2/services/mcp/generic_mcp_client.py#L447-L509]`).
  - [x] Step 3: Lock retired path `backend_v2/llm/provider.py` in `@[scripts/_ast_guardrails.py#L621-L680]` (`QGR017`), update `BOUNDARY_EXEMPTION_FILES` in `@[scripts/_ast_guardrails.py#L98-L109]` and `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1146-L1180]` to `"backend_v2/llm/provider/__init__.py"`, and synchronize `@[.agents/rules/04_directory_reference.md]`.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_provider/phase4_package_cutover_and_guardrails.md] @[docs/epic/provider_decomposition_tracker.md]`

### Post-Implementation Gates

- [ ] **[NOK] Tier 2 Hardening (Backend)** (`[NEW]` sub-modules & 1-hop callers): Run `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/epic/provider_decomposition_tracker.md]" --gate backend --model gemini-4-argon-medium`
  - [x] [NEW] @[backend_v2/llm/provider/env_and_schema_utils.py]
  - [ ] [NEW] @[backend_v2/llm/provider/transient_retry_policy.py]
  - [ ] [NEW] @[backend_v2/llm/provider/base_and_mock_provider.py]
  - [ ] [NEW] @[backend_v2/llm/provider/provider_factory.py]
  - [ ] [NEW] @[backend_v2/llm/provider/litellm_response_stage.py]
  - [ ] [NEW] @[backend_v2/llm/provider/litellm_provider.py]
  - [ ] [NEW] @[backend_v2/llm/provider/__init__.py]
  - [ ] `@[backend_v2/llm/client.py#L46-L58]`
  - [ ] `@[backend_v2/llm/handler.py#L878-L1057]`
  - [ ] `@[backend_v2/services/mcp/generic_mcp_client.py#L447-L509]`
- [x] **[SKIPPED] Tier 2 Hardening (Frontend)**: Pure backend Python decomposition with zero `.dart` changes.
- [ ] **[NOK] Pre-Delete Audit**: Verify `git status` and `grep_search` confirm physical removal of `[DELETE] @[backend_v2/llm/provider.py]` and `[DELETE] @[backend_v2/tests/unit/llm/test_provider.py]`, with `QGR017` blocking re-creation of `backend_v2/llm/provider.py`.
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Verify all 34 baseline unit tests pass across the modularized test suites (`[NEW] @[backend_v2/tests/unit/llm/provider/test_env_and_schema_utils.py]`, `[NEW] @[backend_v2/tests/unit/llm/provider/test_transient_retry_policy.py]`, `[NEW] @[backend_v2/tests/unit/llm/provider/test_base_and_mock_provider.py]`, `[NEW] @[backend_v2/tests/unit/llm/provider/test_provider_factory.py]`, `[NEW] @[backend_v2/tests/unit/llm/provider/test_litellm_response_stage.py]`, `[NEW] @[backend_v2/tests/unit/llm/provider/test_litellm_provider.py]`, `[NEW] @[backend_v2/tests/unit/llm/provider/test_provider_facade.py]`, `@[backend_v2/tests/unit/llm/test_provider_httpx_client.py#L34-L99]`, `@[backend_v2/tests/unit/llm/test_provider_penalties.py#L14-L76]`, `@[backend_v2/tests/unit/llm/test_provider_retry_after.py#L49-L90]`, and `@[backend_v2/tests/unit/llm/test_provider_toolcalls.py#L11-L89]`) with `>= 92%` line coverage.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Verify 100% symbol parity ($\mathcal{I}_{orig} \subseteq \bigcup \mathcal{I}_{sub}$) and execute `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py`, `uv run python scripts/audit_dict_eradication.py`, and `uv run python scripts/audit_clean_imports.py`.

#### Epoch 2: 12-Item Technical Debt Inventory (Target Scope for Tier 2 Hardening)
1. **Item 1 (`no_naked_dicts_in_state` & `QGR012` / `QGR018` Boundary Tightening)**: Audit `resolve_env_variables`, `_normalize_mcp_tool_schema_for_llm` in `[NEW] @[backend_v2/llm/provider/env_and_schema_utils.py]`, `LLMProvider.generate`, `MockProvider.generate` in `[NEW] @[backend_v2/llm/provider/base_and_mock_provider.py]`, `LiteLLMProvider.generate` in `[NEW] @[backend_v2/llm/provider/litellm_provider.py]`, and `extract_litellm_content_and_usage` in `[NEW] @[backend_v2/llm/provider/litellm_response_stage.py]`; tighten intermediate boundary payloads to typed DTOs or `JsonValue` where compatible while synchronizing 1-hop callers (`@[backend_v2/llm/client.py#L46-L58]`, `@[backend_v2/llm/handler.py#L878-L1057]`).
2. **Item 4 (`the_duct_tape_ban` / `QGR003` Exception Handling & DLP Audit)**: Audit broad `except Exception:` blocks in `_safe_static_getattr`, `_safe_static_hasattr`, `_sync_diagnostic_dump` (`[NEW] @[backend_v2/llm/provider/env_and_schema_utils.py]`), `_is_transient_llm_error`, `_extract_retry_after_seconds` (`[NEW] @[backend_v2/llm/provider/transient_retry_policy.py]`), and cost calculation in `[NEW] @[backend_v2/llm/provider/litellm_response_stage.py]` to narrow caught exception tuples (`AttributeError`, `TypeError`, `ValueError`, `KeyError`, `OSError`) and audit all OpenTelemetry `span.set_attribute` calls to ensure zero raw user prompt, API key, or PII leakage outside `development` mode.
3. **Item 6 (`python_314_modern_syntax`)**: Verify PEP 695 type aliases, `@override` decorators on `LiteLLMProvider.generate`, `MockProvider.generate`, and `_AdaptiveWaitWithRetryAfter.__call__`, and modern `except A, B:` exception syntax across all sub-modules in `backend_v2/llm/provider/`.
4. **Item 7 (`strict_configuration_segregation`)**: Verify all RPM thresholds, fallback retry bounds, and timeouts in `[NEW] @[backend_v2/llm/provider/litellm_provider.py]` and `[NEW] @[backend_v2/llm/provider/transient_retry_policy.py]` resolve from `backend_v2/settings.py`.
5. **Item 8 (`docstring_fail_fast_ban` & `pep257_google_style_docstrings`)**: Ensure all classes, methods, and functions across `backend_v2/llm/provider/` include complete PEP 257 Google-style docstrings with `Args:`, `Returns:`, and explicit `Raises:` error codes (`ConfigurationError`, `ContextWindowExceededError`, `UpstreamAuthenticationError`, `UpstreamRateLimitError`, `UpstreamTimeoutError`, `ContentPolicyViolationError`, `BadRequestError`, `UpstreamServiceError`).
6. **Item 10 (`anti_happy_path_mandate` — ISTQB Negative & Boundary Partitions)**: Add negative and boundary unit tests covering the 66 missed statements from baseline (`lines 67, 72, 76-77, 80, 88-99, 211, 215, 242, 269-271, 284-297, 307, 312, 349, 368-369, 384-386, 511, 753, 809-811, 822-823, 874, 892-894, 904, 933, 997, 1033-1041, 1049-1050, 1063, 1069, 1332, 1534-1536, 1544, 1728, 1834-1835` of `provider.py`) across `backend_v2/tests/unit/llm/provider/` to achieve `>= 97%` line coverage.

#### Architectural Documentation Synchronization
- [ ] **[NOK] As-Built Architectural Sync**: Run `/tier7-describe-architecture @[docs/epic/provider_decomposition_tracker.md] @[ki_god_code_prevention.md] @[ki_deterministic_hardening_state.md]`
  - **Target KIs to Synchronize**: `@[ki_god_code_prevention.md]`, `@[ki_deterministic_hardening_state.md]`
  - **Directory Reference Sync**: Verify `@[.agents/rules/04_directory_reference.md]` reflects `backend_v2/llm/provider/` and `backend_v2/tests/unit/llm/provider/`
  - **Pillar Documentation Sync**: Update LLM & Adapter documentation in `docs/architecture/` to reflect the modular `backend_v2/llm/provider/` package

### Final Epic Audit
- [ ] **[NOK] System 2 Red-Team Audit**: Run `/tier8-audit-plan @[docs/epic/tasks_provider/phase4_package_cutover_and_guardrails.md] @[docs/epic/provider_decomposition_tracker.md]` and verify 100% completion across all phases and gates.

## Instructions for the Execution Agent
1. **Strict Two-Epoch Firewall**: During Epoch 1 (Phases 1–4), perform ONLY pure structural lift-and-shift extraction, consumer import rewiring, test suite modularization, and atomic package cutover with **zero behavioral changes**. Do NOT mix Epoch 2 tech debt fixes into Epoch 1.
2. **Two-Phase Package Strangler Protocol**: Do NOT create `backend_v2/llm/provider/__init__.py` during Phases 1, 2, or 3 while `backend_v2/llm/provider.py` exists on disk. Create `__init__.py` and delete `provider.py` atomically in Phase 4 Step 2.
3. **Quality Gate Enforcement**: Run `uv run python scripts/backend_audit_loop.py <target> --test --ast-strict` after every phase step and create an atomic Conventional Commit before advancing to the next phase.

## Requirements Traceability Matrix

| Requirement ID | Architectural Requirement | Phase & Step Mapping | Verification Target |
| :--- | :--- | :--- | :--- |
| `REQ-PRV-01` | Create test package marker, extend `is_boundary_exempt` for `backend_v2/llm/provider/`, and extract leaf utilities (`env_and_schema_utils.py`) and transient retry policy (`transient_retry_policy.py`) | Phase 1, Step 1 | `[NEW] @[backend_v2/llm/provider/env_and_schema_utils.py]`, `[NEW] @[backend_v2/llm/provider/transient_retry_policy.py]` |
| `REQ-PRV-02` | Rewire Phase 1 explicit redundant re-exports in `provider.py` and add unit tests for leaf utilities and transient retry policy | Phase 1, Step 2 | `[NEW] @[backend_v2/tests/unit/llm/provider/test_env_and_schema_utils.py]`, `[NEW] @[backend_v2/tests/unit/llm/provider/test_transient_retry_policy.py]` |
| `REQ-PRV-03` | Verify Phase 1 extraction passes 10/10 backend audit gates and all 34 baseline unit tests | Phase 1, Step 3 | `[DELETE] @[backend_v2/llm/provider.py]` |
| `REQ-PRV-04` | Extract `LLMProvider`, `LogfireShieldedClient`, and `MockProvider` into `base_and_mock_provider.py` and `LLMFactory` into `provider_factory.py` | Phase 2, Step 1 | `[NEW] @[backend_v2/llm/provider/base_and_mock_provider.py]`, `[NEW] @[backend_v2/llm/provider/provider_factory.py]` |
| `REQ-PRV-05` | Rewire Phase 2 explicit redundant re-exports in `provider.py` and add unit tests for base/mock provider and factory | Phase 2, Step 2 | `[NEW] @[backend_v2/tests/unit/llm/provider/test_base_and_mock_provider.py]`, `[NEW] @[backend_v2/tests/unit/llm/provider/test_provider_factory.py]` |
| `REQ-PRV-06` | Verify Phase 2 extraction passes 10/10 backend audit gates and all 34 baseline unit tests | Phase 2, Step 3 | `[DELETE] @[backend_v2/llm/provider.py]` |
| `REQ-PRV-07` | Extract `_truncate_for_debug`, `extract_litellm_content_and_usage`, and `classify_and_raise_litellm_error` into `litellm_response_stage.py` and `LiteLLMProvider` into `litellm_provider.py` | Phase 3, Step 1 | `[NEW] @[backend_v2/llm/provider/litellm_response_stage.py]`, `[NEW] @[backend_v2/llm/provider/litellm_provider.py]` |
| `REQ-PRV-08` | Rewire Phase 3 explicit redundant re-exports in `provider.py` and add unit tests for response stage and `LiteLLMProvider` | Phase 3, Step 2 | `[NEW] @[backend_v2/tests/unit/llm/provider/test_litellm_response_stage.py]`, `[NEW] @[backend_v2/tests/unit/llm/provider/test_litellm_provider.py]` |
| `REQ-PRV-09` | Verify Phase 3 extraction passes 10/10 backend audit gates and all 34 baseline unit tests | Phase 3, Step 3 | `[DELETE] @[backend_v2/llm/provider.py]` |
| `REQ-PRV-10` | Split `test_provider.py` (1,153 lines, 16 tests) into modular unit test suites under `backend_v2/tests/unit/llm/provider/` and delete `test_provider.py` | Phase 4, Step 1 | `[NEW] @[backend_v2/tests/unit/llm/provider/test_provider_facade.py]` |
| `REQ-PRV-11` | Atomically replace `provider.py` with `provider/__init__.py` (`< 160` lines) and rewire 1-hop callers (`client.py`, `handler.py`, `generic_mcp_client.py`) | Phase 4, Step 2 | `[NEW] @[backend_v2/llm/provider/__init__.py]` |
| `REQ-PRV-12` | Lock retired `backend_v2/llm/provider.py` in `QGR017`, update `BOUNDARY_EXEMPTION_FILES` to `backend_v2/llm/provider/__init__.py`, and synchronize `04_directory_reference.md` | Phase 4, Step 3 | `@[scripts/_ast_guardrails.py#L621-L680]`, `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1146-L1180]` |

# Session Handover Context

## Achieved
- Completed Tier 3 God Code Decomposition pre-flight AST analysis of `[DELETE] @[backend_v2/llm/provider.py]` (1,846 lines, 24 AST symbols), test baseline verification (`34 passed, 92% line coverage` across 785 statements), and 1-hop caller blast-radius inventory (`@[docs/epic/tasks_provider/symbol_migration_map.md]`).
- Generated and boundary-audited all 4 Epoch 1 Strangler Fig implementation plans (`@[docs/epic/tasks_provider/phase1_leaf_utils_and_retry_policy_extraction.md]`, `@[docs/epic/tasks_provider/phase2_base_mock_and_factory_extraction.md]`, `@[docs/epic/tasks_provider/phase3_litellm_stages_and_provider_extraction.md]`, and `@[docs/epic/tasks_provider/phase4_package_cutover_and_guardrails.md]`).
- Generated the Master Two-Epoch Decomposition Tracker (`@[docs/epic/provider_decomposition_tracker.md]`) with complete Epoch 1 Phase Execution Status, Epoch 2 12-Item Technical Debt Inventory, Tier 2 Hardening checklist, and bidirectional Requirements Traceability Matrix.
- Executed Phase 1 (`@[docs/epic/tasks_provider/phase1_leaf_utils_and_retry_policy_extraction.md]`): created `[NEW] @[backend_v2/tests/unit/llm/provider/__init__.py]`, extended `is_boundary_exempt` in `@[scripts/_ast_guardrails.py#L98-L109]`, extracted `[NEW] @[backend_v2/llm/provider/env_and_schema_utils.py]` and `[NEW] @[backend_v2/llm/provider/transient_retry_policy.py]`, wired explicit redundant re-exports in `[DELETE] @[backend_v2/llm/provider.py]`, added unit test suites `[NEW] @[backend_v2/tests/unit/llm/provider/test_env_and_schema_utils.py]` and `[NEW] @[backend_v2/tests/unit/llm/provider/test_transient_retry_policy.py]`, and verified 10/10 Universal Quality Gates across all Phase 1 targets.
- Executed Phase 2 (`@[docs/epic/tasks_provider/phase2_base_mock_and_factory_extraction.md]`): extracted `LLMProvider`, `LogfireShieldedClient`, and `MockProvider` into `[NEW] @[backend_v2/llm/provider/base_and_mock_provider.py]` (335 lines, 99% unit coverage), extracted `LLMFactory` (`create_provider`) into `[NEW] @[backend_v2/llm/provider/provider_factory.py]` (235 lines, 98% unit coverage), wired explicit redundant re-exports in `[DELETE] @[backend_v2/llm/provider.py]`, created unit test suites `[NEW] @[backend_v2/tests/unit/llm/provider/test_base_and_mock_provider.py]` and `[NEW] @[backend_v2/tests/unit/llm/provider/test_provider_factory.py]`, and verified 10/10 Universal Quality Gates across all Phase 2 targets and all 34 baseline unit tests (95% coverage).
- Executed Phase 3 (`@[docs/epic/tasks_provider/phase3_litellm_stages_and_provider_extraction.md]`): extracted `_truncate_for_debug`, `extract_litellm_content_and_usage`, and `classify_and_raise_litellm_error` into `[NEW] @[backend_v2/llm/provider/litellm_response_stage.py]` (379 lines, `< 380` limit, 99% unit coverage), extracted `LiteLLMProvider` into `[NEW] @[backend_v2/llm/provider/litellm_provider.py]` (420 lines, `< 430` limit, 93% unit coverage), reduced `[DELETE] @[backend_v2/llm/provider.py]` to a 98-line explicit redundant re-export proxy (`< 160` limit, 100% coverage), created unit test suites `[NEW] @[backend_v2/tests/unit/llm/provider/test_litellm_response_stage.py]` and `[NEW] @[backend_v2/tests/unit/llm/provider/test_litellm_provider.py]`, and verified 10/10 Universal Quality Gates across all Phase 3 targets and all 34 baseline unit tests.
- Executed Phase 4 (`@[docs/epic/tasks_provider/phase4_package_cutover_and_guardrails.md]`): migrated all 16 unit test functions from `[DELETE] @[backend_v2/tests/unit/llm/test_provider.py]` into `[NEW] @[backend_v2/tests/unit/llm/provider/test_provider_facade.py]` (439 lines) and the submodule test suites under `backend_v2/tests/unit/llm/provider/` (all `< 450` lines), physically deleted `[DELETE] @[backend_v2/tests/unit/llm/test_provider.py]` and `[DELETE] @[backend_v2/llm/provider.py]`, created `[NEW] @[backend_v2/llm/provider/__init__.py]` (93 lines, `< 160` limit), rewired 1-hop callers (`@[backend_v2/llm/client.py#L46-L58]`, `@[backend_v2/llm/handler.py#L878-L1057]`, `@[backend_v2/services/mcp/generic_mcp_client.py#L447-L509]`), locked retired `backend_v2/llm/provider.py` under `QGR017` in `@[scripts/_ast_guardrails.py#L621-L680]`, updated `BOUNDARY_EXEMPTION_FILES` and `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1146-L1180]`, synchronized `@[.agents/rules/04_directory_reference.md]`, and verified 10/10 Universal Quality Gates (56 passed provider unit tests, 98% line coverage).

## Learned
- `"backend_v2/llm/provider.py"` is one of the 15 locked paths in `BOUNDARY_EXEMPTION_FILES` (`@[scripts/_ast_guardrails.py#L98-L109]`); extending `is_boundary_exempt` in Phase 1 to match `rel_posix.startswith("backend_v2/llm/provider/")` ensures all extracted sub-modules inherit boundary exemption during Epoch 1 lift-and-shift, while updating `BOUNDARY_EXEMPTION_FILES` to `"backend_v2/llm/provider/__init__.py"` in Phase 4 preserves the 15-element SSOT invariant enforced by `test_purged_boundary_exemption_files` and `test_boundary_exemption_files_contains_only_relative_paths`.
- When decomposing `backend_v2/llm/provider.py` into same-stem directory `backend_v2/llm/provider/` while withholding `backend_v2/llm/provider/__init__.py` during Phases 1–3 (`strangler_fig_mandate`), declaring `__path__: list[str] = [str(Path(__file__).resolve().with_suffix(""))]` in `backend_v2/llm/provider.py` before sub-module imports enables Python's `importlib` (PEP 302/451) to resolve `backend_v2.llm.provider.*` submodules cleanly without triggering MyPy duplicate-module errors.
- Existing unit and integration tests patch `apply_provider_pacing`, `get_settings`, `MockLLMService`, `LiteLLMProvider`, and `otel_trace.get_current_span` on the `backend_v2.llm.provider` module namespace at test execution time; resolving these collaborators via `sys.modules["backend_v2.llm.provider"]` when present in `MockProvider`, `LLMFactory`, `LiteLLMProvider`, and `litellm_response_stage` (comparing against `_ORIG_GET_SETTINGS`, `_ORIG_APPLY_PROVIDER_PACING`, `_ORIG_OTEL_TRACE`, `_ORIG_MOCK_LLM_SERVICE`, and `_ORIG_MOCK_PROVIDER` so both submodule-level and facade-level patches are honored without binding `ModuleType` as `self` on plain functions) preserves 100% test compatibility without `getattr` reflection (`QGR001`) or `.get()` calls (`QGR002`).
- In unit tests that verify OpenTelemetry GenAI attributes when `DUMP_PROMPTS_FILE` is set in `.env`, patching `provider_facade.otel_trace` with a scoped mock module (`monkeypatch.setattr(provider_facade, "otel_trace", mock_otel)`) rather than mutating `opentelemetry.trace.get_current_span` globally prevents Logfire's threadpool context propagation (`asyncio.to_thread`) from receiving a `MagicMock` span context during `format_trace_id`.
- Transitioning `backend_v2/llm/provider.py` to `backend_v2/llm/provider/__init__.py` via the Two-Phase Package Strangler Protocol preserves `from backend_v2.llm.provider import _is_transient_llm_error` for orchestrator callers (`dag_executor.py`, `enriched_dag_executor.py`, `extractive_sensor_service.py`) without mutating files governed by `orchestrator_god_object_fragility`.
- In `scripts/audit_warning_baseline.py`, Census `T` enforces zero `# type: ignore` comments across `backend_v2/` and `scripts/` (`CEILING = 0`); using a typed `_StatusError(Exception)` subclass with an optional `status_code: int | None` attribute in negative error-mapping tests avoids `err.status_code = ... # type: ignore[attr-defined]`.

## Resume Command
`/tier8-audit-plan @[docs/epic/tasks_provider/phase4_package_cutover_and_guardrails.md] @[docs/epic/provider_decomposition_tracker.md]`

## Remaining
- Audit Phase 4 (`/tier8-audit-plan @[docs/epic/tasks_provider/phase4_package_cutover_and_guardrails.md] @[docs/epic/provider_decomposition_tracker.md]`).
- Execute Epoch 2 Tier 2 Hardening and Final Decomposition Audit.
