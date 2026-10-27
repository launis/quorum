# Implementation Plan: Systemic Prevention, AST Guardrail QGR030 & Test Fixture Fortification

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
</required_context_rules>

## Executive Summary & Direct Traceability Matrix to the 4 Systemic Improvements

During the PostgreSQL 19 final cutover, four systemic failure modes were identified. This plan physically implements the four concrete preventative countermeasures and confirms alignment with Osa 2 (Tracker & Requirements SSOT):

| Improvement Item | Identified Problem in Cutover | Concrete Architectural Solution in This Plan |
| :--- | :--- | :--- |
| **1. Zero-Bifurcation Mandate** | Coexistence of `STORAGE_BACKEND=LOCAL` (TinyDB) alongside `POSTGRES` allowed deprecated code and tests to hide in parallel execution paths. | **Phase 1, Phase 2 (`QGR030`) & Phase 4**: <br>1. Clean up residual `StorageBackend` branches in `backend_v2/settings.py` and `storage_backend="LOCAL"` in unit tests.<br>2. Implement `QGR030` (`FATAL`) banning deprecated backend references repo-wide.<br>3. Add `zero_compromise_cutover_mandate` to `.agents/rules/00-antigravity-core.md` prohibiting transitional coexistence or backward compatibility shims. |
| **2. Hermetic Test Isolation & Fixture Sovereignty** | Unit tests unrelated to persistence (specifically `test_token_service.py` and LLM provider unit tests) lazily instantiated `Settings(storage_backend="LOCAL")`, exploding when Fail-Fast was activated. | **Phase 1, Phase 2 (`QGR030`) & Phase 4**: <br>1. Remove `storage_backend="LOCAL"` from all LLM provider unit tests.<br>2. `QGR030` statically parses `Settings(...)` calls in tests and forbids deprecated backend keywords.<br>3. Add `hermetic_test_fixtures_mandate` to `.agents/rules/01-python-backend.md` requiring pure in-memory fakes (`InMemoryUnitOfWork`, `InMemoryEntityAdapter`). |
| **3. Pre-Flight Metatest & Exemption Mapping** | Deleting `tinydb_driver.py` and `wrapper.py` broke metatests (`test_ast_guardrails.py`, `test_scripts_cli_help.py`) because `BOUNDARY_EXEMPTION_FILES` was unmapped in the plan. | **Phase 2 & Phase 4**: <br>1. Add automated existence validation in `test_ast_guardrails.py` asserting physical file existence for all exemption sets (`BOUNDARY_EXEMPTION_FILES`, `OPEN_JSON_EXEMPTION_FILES`, `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES`, `RESIDUAL_FUTURE_PHASE_QGR028_FILES`).<br>2. Update `.agents/workflows/tier0-research-plan.md` to mandate pre-flight grep across `scripts/` and `tests/unit/scripts/` whenever files are marked `[DELETE]`. |
| **4. First-Class Script Strictness & Polyfactory** | `scripts/reconcile_storage.py` contained loose dicts, and tests used non-hex fake IDs (specifically and exhaustively: `exe_ghost1234567890`, `exe_disk9876543210`, `exe_test1234567890`, `exe_sdui1234567890`), breaking Pydantic V2 validation. | **Phase 1, Phase 3 & Phase 5**: <br>1. Include operational and guardrail scripts in `scripts/backend_audit_loop.py` and `scripts/audit_zero_orm_strictness.py`.<br>2. Expand Polyfactory definitions in `backend_v2/tests/factories/model_factories.py` and enforce regex `^([a-z]{2,5})_[a-fA-F0-9]{16,32}$` via `QGR030`. |
| **Osa 2: Tracker & Requirements Parity** | `TRACKER_PostgreSQL_Final_Cutover.md` and `POSTGRESQL_CUTOVER_REQUIREMENTS.md` needed 100% complete 5-KI alignment and unambiguous Tier 7 directives. | **Verified & Completed**: <br>1. Added `ki_seed_vault_verification_and_sanitization.md` establishing 5 KIs.<br>2. Formulated closed-list Tier 7 synchronization directives obeying `anti_ambiguity_mandate`. |

---

## 1. Scope & Target Boundaries

### 1.1 Complete Unified 18-Target Code & Hardening Scope

This unified list combines all 15 modified/created backend targets from the PostgreSQL 19 Final Cutover with the 3 code/script/test targets from this Systemic Prevention plan into a single authoritative hardening scope (18 files total). Running Tier 2 Hardening (`auto_hardening_runner.py`) against this unified list audits and hardens all cutover and systemic changes in a single comprehensive pass.

| # | Target File & AST Span | Origin & Role | Planned Action | Architectural Responsibility |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `@[backend_v2/database/driver.py]` | Cutover: Database Core | `[VERIFY/HARDEN]` | Abstract `DatabaseDriver` and `StorageDriver` contracts governing asynchronous persistence across repositories. |
| 2 | `@[backend_v2/database/factory.py]` | Cutover: Driver Factory | `[VERIFY/HARDEN]` | Authoritative database factory wiring `StorageBackend.POSTGRES` exclusively; raises `ConfigurationError` on legacy backends. |
| 3 | `@[backend_v2/database/interfaces.py]` | Cutover: Seeding Ports | `[VERIFY/HARDEN]` | `EntityPersistencePort` declaring `seed_collection_batch` and `verify_seed_table_counts` across all 10 PostgreSQL 19 tables. |
| 4 | `@[backend_v2/database/postgres/entity_adapter.py]` | Cutover: Adapter Implementation | `[VERIFY/HARDEN]` | Asynchronous PostgreSQL 19 entity adapter executing parameterized batch upserts with binary `\x01` JSONB wire codecs. |
| 5 | `@[backend_v2/database/postgres/pool.py]` | Cutover: Connection Pool | `[VERIFY/HARDEN]` | PostgreSQL 19 asyncpg connection pool manager with health check, retry semantics, and isolation level management. |
| 6 | `[NEW] @[backend_v2/database/postgres/storage_driver.py]` | Cutover: Sovereign Driver | `[VERIFY/HARDEN]` | Sovereign `PostgresStorageDriver` conforming to `StorageDriver` protocol over `PostgresPoolManager` for all 16 repositories. |
| 7 | `@[backend_v2/main.py]` | Cutover: Application Lifespan | `[VERIFY/HARDEN]` | FastAPI lifespan preflight checks verifying PostgreSQL 19 connectivity and table row counts at server startup. |
| 8 | `@[backend_v2/models/core_base.py]` | Cutover: Entity ID Authority | `[VERIFY/HARDEN]` | Monotonic RFC 9562 UUIDv7 opaque ID routing for operational entities (`exe_...`, `rep_...`, `nod_...`, `edg_...`). |
| 9 | `@[backend_v2/seed/run_seed.py]` | Cutover: Database Seeding | `[VERIFY/HARDEN]` | Authoritative database seeding pipeline ingesting `ValidatedSeedBufferDTO` directly into PostgreSQL 19 with count assertions. |
| 10 | `@[backend_v2/services/storage.py]` | Cutover: File Storage Router | `[VERIFY/HARDEN]` | File storage driver factory routing `StorageBackend.POSTGRES` to `LocalFileDriver` or cloud bucket storage. |
| 11 | `[MODIFY] @[backend_v2/settings.py#L803-L811]`, `@[backend_v2/settings.py#L983-L1000]` | Cutover: Centralized Settings | `[MODIFY/HARDEN]` | Centralized Pydantic `Settings` defaulting storage backend to `StorageBackend.POSTGRES` and governing local mock auth tokens with zero references to `StorageBackend.FIRESTORE` or `StorageBackend.LOCAL`. |
| 12 | `[MODIFY] @[scripts/_ast_guardrails.py#L523-L2582]` | Cutover & Systemic: AST Guardrails | `[MODIFY]` | Implement `QGR030` (`FATAL`) in `QuorumGuardrailVisitor` banning deprecated storage backend references (`LOCAL`, `FIRESTORE`) in function calls and test fixtures, and validate entity ID string literals against canonical hexadecimal format (`^([a-z]{2,5})_[a-fA-F0-9]{16,32}$`). |
| 13 | `[MODIFY] @[scripts/audit_zero_orm_strictness.py#L582-L634]` | Cutover & Systemic: Zero-ORM Strictness | `[MODIFY]` | Ensure `scripts/reconcile_storage.py` and all operational scripts are systematically verified under `ZORM001`–`ZORM006` Zero-ORM strictness. |
| 14 | `@[scripts/reconcile_storage.py]` | Cutover: Storage Reconciliation | `[VERIFY/HARDEN]` | Storage reconciliation utility operating on typed snapshots with strict Pydantic V2 models and zero naked dicts. |
| 15 | `@[scripts/run_e2e_variance_test.py]` | Cutover: End-to-End Variance | `[VERIFY/HARDEN]` | End-to-end variance test runner executing multi-model evaluations against PostgreSQL 19. |
| 16 | `[MODIFY] @[scripts/backend_audit_loop.py#L73-L356]`, `@[scripts/backend_audit_loop.py#L359-L593]` | Systemic: Quality Gate Script | `[MODIFY]` | Include operational and guardrail scripts in `scripts/` and `scripts/audit_zero_orm_strictness.py` as first-class audit targets in the global completion gate. |
| 17 | `[MODIFY] @[backend_v2/tests/factories/model_factories.py#L76-L121]`, `@[backend_v2/tests/factories/model_factories.py#L124-L161]`, `@[backend_v2/tests/factories/model_factories.py#L164-L226]`, `@[backend_v2/tests/factories/model_factories.py#L229-L289]`, `@[backend_v2/tests/factories/model_factories.py#L292-L316]`, `@[backend_v2/tests/factories/model_factories.py#L319-L392]`, `@[backend_v2/tests/factories/test_model_factories.py#L39-L46]` | Systemic: Polyfactory Models | `[MODIFY]` | Expand Polyfactory models (`ReportArtifactFactory`, `WorkflowFactory`, `SystemRulePromptBlockFactory`, `OutputProfileFactory`, `MatrixPromptBlockFactory`, `ExecutionStepFactory`, `ExecutionRecordFactory`) to guarantee all mock entity IDs adhere strictly to canonical regex hexadecimal format via `generate_opaque_id(EntityPrefix.<TYPE>)`. |
| 18 | `[MODIFY] @[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1924-L1934]`, `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2247-L2271]` | Systemic: AST Unit Tests | `[MODIFY]` | Add comprehensive unit tests for `QGR030` with >=2 positive violation detections and >=2 negative boundary cases, plus automated existence validation across all guardrail exemption sets (`BOUNDARY_EXEMPTION_FILES`, `OPEN_JSON_EXEMPTION_FILES`, `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES`, `RESIDUAL_FUTURE_PHASE_QGR028_FILES`). |

---

### 1.2 Governance & Workflow Invariant Rules (Step 4)

| Rule File & Section | Planned Action | Invariant Enforced |
| :--- | :--- | :--- |
| `[MODIFY] @[.agents/rules/01-python-backend.md#L10-L60]` | `[MODIFY]` | Formalize `hermetic_test_fixtures_mandate` banning live settings instantiation or storage backend overrides in domain unit tests. |
| `[MODIFY] @[.agents/rules/00-antigravity-core.md#L87-L105]` | `[MODIFY]` | Formalize `zero_compromise_cutover_mandate` banning transitional dual-backend states during platform migrations. |
| `[MODIFY] @[.agents/workflows/tier0-research-plan.md#L50-L53]` | `[MODIFY]` | Add `preflight_metatest_and_exemption_mapping_mandate` to research workflow requiring pre-flight grep on `scripts/` and `tests/unit/scripts/` when files are marked `[DELETE]`. |

---

### 1.3 5-Column Architectural Directives Table (Tier 0 System 2 Synthesis)

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 1 Pre-Implementation Cleanups**<br>`[MODIFY] @[backend_v2/settings.py#L803-L811]`<br>`[MODIFY] @[backend_v2/settings.py#L983-L1000]`<br>`[MODIFY] @[backend_v2/tests/unit/llm/provider/test_base_and_mock_provider.py#L108-L150]`<br>`[MODIFY] @[backend_v2/tests/unit/llm/provider/test_base_and_mock_provider.py#L153-L246]`<br>`[MODIFY] @[backend_v2/tests/unit/llm/provider/test_base_and_mock_provider.py#L291-L358]`<br>`[MODIFY] @[backend_v2/tests/unit/llm/provider/test_litellm_provider.py#L83-L126]`<br>`[MODIFY] @[backend_v2/tests/unit/llm/provider/test_litellm_provider.py#L267-L362]`<br>`[MODIFY] @[backend_v2/tests/unit/llm/provider/test_provider_factory.py#L19-L49]`<br>`[MODIFY] @[backend_v2/tests/unit/llm/provider/test_provider_factory.py#L52-L182]`<br>`[MODIFY] @[backend_v2/tests/unit/llm/provider/test_provider_factory.py#L185-L280]`<br>`[MODIFY] @[backend_v2/tests/unit/test_epic66_multi_provider.py#L23-L37]`<br>`[MODIFY] @[backend_v2/tests/unit/test_epic66_multi_provider.py#L40-L54]`<br>`[MODIFY] @[backend_v2/tests/unit/scripts/test_reconcile_storage.py#L292-L312]`<br>`[MODIFY] @[backend_v2/tests/unit/scripts/test_reconcile_storage.py#L315-L337]` | Passing `storage_backend="LOCAL"` to `Settings(...)` in LLM provider unit tests; dead `StorageBackend.FIRESTORE` and `StorageBackend.LOCAL` branches in `Settings.is_cloud_storage` and `Settings.allow_mock_tokens`; non-hexadecimal test IDs (`exe_test1234567890`, `exe_sdui1234567890`) in `test_reconcile_storage.py`. | Default `Settings(...)` strictly to sovereign `StorageBackend.POSTGRES`; evaluate `is_cloud_storage` strictly from `bool(self.storage_bucket_name)` and `allow_mock_tokens` strictly against `StorageBackend.POSTGRES`; use canonical 16-char hexadecimal IDs (`exe_1111222233334444`, `exe_5555666677778888`) in `test_reconcile_storage.py`. | Pruned custom test settings subclasses or wrapper fixtures; rely directly on `Settings` defaults and canonical hex literals. | `uv run pytest backend_v2/tests/unit/test_settings.py backend_v2/tests/unit/llm/provider/ backend_v2/tests/unit/test_epic66_multi_provider.py backend_v2/tests/unit/scripts/test_reconcile_storage.py` passes 100% with 0 `QGR030` violations. |
| **AST Guardrail QGR030 & Self-Verifying Exemption Sets**<br>`[MODIFY] @[scripts/_ast_guardrails.py#L523-L2582]`<br>`[MODIFY] @[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1924-L1934]`<br>`[MODIFY] @[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2247-L2271]` | Unchecked `Settings(storage_backend="LOCAL")` or `StorageBackend.FIRESTORE` calls in tests; non-hexadecimal pseudo-IDs (`exe_ghost1234567890`, `exe_disk9876543210`); stale deleted file paths lingering in `BOUNDARY_EXEMPTION_FILES` or residual exemption sets. | Implement `QGR030` (`FATAL` severity in `GuardrailSeverity`) inside `QuorumGuardrailVisitor.visit_Call` and `visit_Constant` (with `is_guardrail_self` exemption); assert physical disk existence `(REPO_ROOT / path).is_file()` across `BOUNDARY_EXEMPTION_FILES`, `OPEN_JSON_EXEMPTION_FILES`, `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES`, and `RESIDUAL_FUTURE_PHASE_QGR028_FILES`. | Pruned standalone regex scanner scripts; embedded `QGR030` directly into the single-pass `QuorumGuardrailVisitor` AST traversal with zero reflection. | `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py -k "qgr030 or boundary"` passes with >=2 positive violation tests and >=2 negative boundary cases. |
| **First-Class Script Quality Gate & Zero-ORM Strictness**<br>`[MODIFY] @[scripts/backend_audit_loop.py#L73-L356]`<br>`[MODIFY] @[scripts/backend_audit_loop.py#L359-L593]`<br>`[MODIFY] @[scripts/audit_zero_orm_strictness.py#L582-L634]` | Auditing only `backend_v2/` during the global completion gate while leaving operational scripts (`scripts/reconcile_storage.py`) outside `ZORM001`–`ZORM006` and macro quality gates. | Register `scripts/reconcile_storage.py` in default `resolved_targets` of `run_zero_orm_audit`; execute `scripts/audit_zero_orm_strictness.py` and audit authoritative operational/guardrail scripts in `scripts/backend_audit_loop.py` during the macro gate. | Pruned duplicate linter wrapper scripts; integrated directly into `scripts/backend_audit_loop.py` and `scripts/audit_zero_orm_strictness.py`. | `uv run python scripts/audit_zero_orm_strictness.py` and `uv run python scripts/backend_audit_loop.py scripts/reconcile_storage.py --test --ast-strict` exit with code 0. |
| **Governance & Pre-Flight Metatest Mapping Rules**<br>`[MODIFY] @[.agents/rules/01-python-backend.md#L10-L60]`<br>`[MODIFY] @[.agents/rules/00-antigravity-core.md#L87-L105]`<br>`[MODIFY] @[.agents/workflows/tier0-research-plan.md#L50-L53]` | Unmapped `[DELETE]` targets breaking metatests (`test_ast_guardrails.py`, `test_scripts_cli_help.py`); dual-backend transitional coexistence during cutovers; live `Settings()` backend overrides in domain unit tests. | Codify `hermetic_test_fixtures_mandate` in `@[.agents/rules/01-python-backend.md]`, `zero_compromise_cutover_mandate` in `@[.agents/rules/00-antigravity-core.md]`, and `preflight_metatest_and_exemption_mapping_mandate` in `@[.agents/workflows/tier0-research-plan.md]`. | Pruned verbose prose descriptions; codified concise, deterministic XML `<rule_block>` mandates. | Verified via `uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/IMPLEMENTATION_PLAN_Systemic_Prevention_and_AST_Guardrails.md` with 0 findings. |
| **Polyfactory SSOT & Hexadecimal Opaque ID Authority**<br>`[MODIFY] @[backend_v2/tests/factories/model_factories.py#L76-L121]`<br>`[MODIFY] @[backend_v2/tests/factories/model_factories.py#L124-L161]`<br>`[MODIFY] @[backend_v2/tests/factories/model_factories.py#L164-L226]`<br>`[MODIFY] @[backend_v2/tests/factories/model_factories.py#L229-L289]`<br>`[MODIFY] @[backend_v2/tests/factories/model_factories.py#L292-L316]`<br>`[MODIFY] @[backend_v2/tests/factories/model_factories.py#L319-L392]`<br>`[MODIFY] @[backend_v2/tests/factories/test_model_factories.py#L39-L46]` | Hardcoded non-hexadecimal `organization_id = "org_testorg123"` and legacy prefixes (`prof_...`, `st_...`, `exec_...`) in `model_factories.py`; missing `ReportArtifactFactory`. | Route all Polyfactory ID generation through `generate_opaque_id(EntityPrefix.<TYPE>)` (`EntityPrefix.WORKFLOW`, `EntityPrefix.OUTPUT_PROFILE`, `EntityPrefix.PROMPT_BLOCK`, `EntityPrefix.STEP`, `EntityPrefix.EXECUTION`, `EntityPrefix.REPORT`, `EntityPrefix.ORGANIZATION`); add `ReportArtifactFactory` for `ReportArtifact` and verify in `test_model_factories.py`. | Pruned ad-hoc `f"prefix_{uuid.uuid4().hex[:16]}"` string formatting across individual factory classes; delegated 100% to `generate_opaque_id`. | `uv run pytest backend_v2/tests/factories/test_model_factories.py` passes with 100% `OPAQUE_STRIPE_ID_REGEX` compliance and >=2 negative validation tests. |

---

## 2. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Phase 1: Pre-Implementation Cleanups (Touched-Scope Technical Debt &amp; Legacy Backend References)">
    <targets>
      <target>[MODIFY] @[backend_v2/settings.py#L803-L811]</target>
      <target>[MODIFY] @[backend_v2/settings.py#L983-L1000]</target>
      <target>[MODIFY] @[backend_v2/tests/unit/llm/provider/test_base_and_mock_provider.py#L108-L150]</target>
      <target>[MODIFY] @[backend_v2/tests/unit/llm/provider/test_base_and_mock_provider.py#L153-L246]</target>
      <target>[MODIFY] @[backend_v2/tests/unit/llm/provider/test_base_and_mock_provider.py#L291-L358]</target>
      <target>[MODIFY] @[backend_v2/tests/unit/llm/provider/test_litellm_provider.py#L83-L126]</target>
      <target>[MODIFY] @[backend_v2/tests/unit/llm/provider/test_litellm_provider.py#L267-L362]</target>
      <target>[MODIFY] @[backend_v2/tests/unit/llm/provider/test_provider_factory.py#L19-L49]</target>
      <target>[MODIFY] @[backend_v2/tests/unit/llm/provider/test_provider_factory.py#L52-L182]</target>
      <target>[MODIFY] @[backend_v2/tests/unit/llm/provider/test_provider_factory.py#L185-L280]</target>
      <target>[MODIFY] @[backend_v2/tests/unit/test_epic66_multi_provider.py#L23-L37]</target>
      <target>[MODIFY] @[backend_v2/tests/unit/test_epic66_multi_provider.py#L40-L54]</target>
      <target>[MODIFY] @[backend_v2/tests/unit/scripts/test_reconcile_storage.py#L292-L312]</target>
      <target>[MODIFY] @[backend_v2/tests/unit/scripts/test_reconcile_storage.py#L315-L337]</target>
    </targets>
    <action>
      Execute pre-implementation technical debt cleanups across `backend_v2/settings.py` and the 5 unit test files before activating `QGR030`:
      1. In `@[backend_v2/settings.py#L803-L811]` (`is_cloud_storage`) and `@[backend_v2/settings.py#L983-L1000]` (`allow_mock_tokens`), remove dead comparisons to `StorageBackend.FIRESTORE` and `StorageBackend.LOCAL` so `is_cloud_storage` returns `bool(self.storage_bucket_name)` and `allow_mock_tokens` checks `self.active_backend != StorageBackend.POSTGRES`.
      2. In `@[backend_v2/tests/unit/llm/provider/test_base_and_mock_provider.py#L108-L150]`, `@[backend_v2/tests/unit/llm/provider/test_base_and_mock_provider.py#L153-L246]`, `@[backend_v2/tests/unit/llm/provider/test_base_and_mock_provider.py#L291-L358]`, `@[backend_v2/tests/unit/llm/provider/test_litellm_provider.py#L83-L126]`, `@[backend_v2/tests/unit/llm/provider/test_litellm_provider.py#L267-L362]`, `@[backend_v2/tests/unit/llm/provider/test_provider_factory.py#L19-L49]`, `@[backend_v2/tests/unit/llm/provider/test_provider_factory.py#L52-L182]`, `@[backend_v2/tests/unit/llm/provider/test_provider_factory.py#L185-L280]`, `@[backend_v2/tests/unit/test_epic66_multi_provider.py#L23-L37]`, and `@[backend_v2/tests/unit/test_epic66_multi_provider.py#L40-L54]`, remove the deprecated `storage_backend="LOCAL"` keyword argument from `Settings(...)` instantiations.
      3. In `@[backend_v2/tests/unit/scripts/test_reconcile_storage.py#L292-L312]` and `@[backend_v2/tests/unit/scripts/test_reconcile_storage.py#L315-L337]`, replace non-hexadecimal test directory identifiers `"exe_test1234567890"` and `"exe_sdui1234567890"` with canonical 16-character hexadecimal IDs `"exe_1111222233334444"` and `"exe_5555666677778888"`, and ensure ISTQB negative test partitions (`test_*_invalid`, `test_*_error`) are present in both `test_reconcile_storage.py` and `test_epic66_multi_provider.py` (`TD_ISTQB_NEGATIVE`).
    </action>
    <constraint invariant="single_pipeline_invariant_mandate">
      Zero legacy storage_backend="LOCAL" keyword arguments or dead StorageBackend enum comparisons remain in backend_v2/.
    </constraint>
  </step>

  <step id="2" name="Phase 2: Implement AST Guardrail QGR030 &amp; Self-Verifying Exemption Lists (Improvements 1, 2, &amp; 3)">
    <targets>
      <target>[MODIFY] @[scripts/_ast_guardrails.py#L523-L2582]</target>
      <target>[MODIFY] @[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1924-L1934]</target>
      <target>[MODIFY] @[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2247-L2271]</target>
    </targets>
    <action>
      Implement `QGR030` (`FATAL`) in `QuorumGuardrailVisitor` inside `@[scripts/_ast_guardrails.py#L523-L2582]` (`visit_Call` and `visit_Constant`, exempting `self.is_guardrail_self`):
      1. **Improvement 1 &amp; 2 (Zero-Bifurcation &amp; Static Call Guard)**: Inspect `ast.Call` nodes where `keywords` specify `storage_backend="LOCAL"`, `storage_backend="FIRESTORE"`, `StorageBackend.LOCAL`, or `StorageBackend.FIRESTORE`, and inspect `ast.Attribute` references to `StorageBackend.LOCAL` or `StorageBackend.FIRESTORE` outside `backend_v2/models/enums.py`. Flag these immediately as FATAL `QGR030` violations.
      2. **Improvement 4 (Mock ID Regex Invariant)**: Inspect `ast.Constant` string literals matching `^([a-z]{2,5})_[a-zA-Z0-9]{14,32}$` for canonical entity prefixes (`exe`, `rep`, `tda`, `wf`, `stp`, `prf`, `blk`, `sys`, `usr`, `org`, `nod`, `edg`) where the 14-to-32 character suffix mixes digits (`[0-9]`) with non-hexadecimal letters (`[g-zG-Z]`), preventing non-hexadecimal mock ID strings (specifically and exhaustively: `exe_ghost1234567890`, `exe_disk9876543210`) from passing static analysis while preserving valid snake_case identifiers and short negative-test literals.
      3. **Improvement 3 (Self-Verifying Boundary Exemption Consistency)**: In `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1924-L1934]` and `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2247-L2271]`, add deterministic self-verification tests iterating `BOUNDARY_EXEMPTION_FILES`, `OPEN_JSON_EXEMPTION_FILES`, `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES`, and `RESIDUAL_FUTURE_PHASE_QGR028_FILES` asserting that every declared file physically exists on disk (`BOUNDARY_EXEMPTION_FILES contains deleted file: {path}`), plus unit tests for `QGR030` covering >=2 positive violation detections and >=2 negative boundary cases.
    </action>
    <constraint invariant="universal_fail_fast">
      QGR030 must exit with fatal code 1 on any violation.
    </constraint>
  </step>

  <step id="3" name="Phase 3: First-Class Scripts Quality Gate &amp; Zero-ORM Strictness Integration (Improvement 4)">
    <targets>
      <target>[MODIFY] @[scripts/backend_audit_loop.py#L73-L356]</target>
      <target>[MODIFY] @[scripts/backend_audit_loop.py#L359-L593]</target>
      <target>[MODIFY] @[scripts/audit_zero_orm_strictness.py#L582-L634]</target>
    </targets>
    <action>
      Update `@[scripts/backend_audit_loop.py#L73-L356]` and `@[scripts/backend_audit_loop.py#L359-L593]` so that running the macro completion gate (`backend_audit_loop.py backend_v2/ --test`) automatically audits authoritative operational and guardrail scripts in `scripts/` (specifically: `scripts/reconcile_storage.py`, `scripts/_ast_guardrails.py`, `scripts/audit_zero_orm_strictness.py`, `scripts/backend_audit_loop.py`, `scripts/audit_markdown_boundaries.py`, `scripts/audit_dict_eradication.py`, `scripts/audit_technical_debt.py`, and `scripts/_ast_boundary_utils.py`) across Ruff, MyPy `--strict`, and AST Guardrail checks, and invokes `scripts/audit_zero_orm_strictness.py`. Update `@[scripts/audit_zero_orm_strictness.py#L582-L634]` (`run_zero_orm_audit`) to include `_WORKSPACE_ROOT / "scripts" / "reconcile_storage.py"` in default `resolved_targets` so `ZORM001`–`ZORM006` are enforced on `scripts/reconcile_storage.py`.
    </action>
    <constraint invariant="the_zero_compromise_pledge">
      Zero permissive dictionaries or unannotated accumulators in operational scripts.
    </constraint>
  </step>

  <step id="4" name="Phase 4: Hermetic Test Fixtures &amp; Pre-Flight Metatest Mapping Mandate (Improvements 1, 2, &amp; 3)">
    <targets>
      <target>[MODIFY] @[.agents/rules/01-python-backend.md#L10-L60]</target>
      <target>[MODIFY] @[.agents/rules/00-antigravity-core.md#L87-L105]</target>
      <target>[MODIFY] @[.agents/workflows/tier0-research-plan.md#L50-L53]</target>
    </targets>
    <action>
      Update `@[.agents/rules/01-python-backend.md#L10-L60]` to add `hermetic_test_fixtures_mandate`:
      - Unit tests testing domain logic, token verification, SDUI rendering, or linguistics MUST NEVER instantiate concrete production `Settings()` instances with legacy storage backend overrides or configure live database backends.
      - Unit tests MUST use lightweight in-memory fakes (`InMemoryUnitOfWork`, `InMemoryEntityAdapter`) and Polyfactory models.
      Update `@[.agents/rules/00-antigravity-core.md#L87-L105]` to add `zero_compromise_cutover_mandate`:
      - Forbids transitional dual-backend states or legacy fallback branches during platform migrations.
      Update `@[.agents/workflows/tier0-research-plan.md#L50-L53]` to add `preflight_metatest_and_exemption_mapping_mandate`:
      - Whenever an implementation plan includes `[DELETE]` targets or removes symbols/drivers, pre-flight research MUST execute `grep_search` across `scripts/` and `tests/unit/scripts/` (specifically: `BOUNDARY_EXEMPTION_FILES`, `test_ast_guardrails.py`, and `test_scripts_cli_help.py`). Any discovered metatest files, exemption lists, or CLI help callers that reference the deleted symbols MUST be explicitly added to the plan's TARGET boundaries and updated synchronously during implementation.
    </action>
    <constraint invariant="single_pipeline_invariant_mandate">
      Zero bifurcated pipelines or legacy fallback modes permitted in rules or domain code.
    </constraint>
  </step>

  <step id="5" name="Phase 5: Polyfactory SSOT &amp; Hexadecimal ID Generation Expansion (Improvement 4)">
    <targets>
      <target>[MODIFY] @[backend_v2/tests/factories/model_factories.py#L76-L121]</target>
      <target>[MODIFY] @[backend_v2/tests/factories/model_factories.py#L124-L161]</target>
      <target>[MODIFY] @[backend_v2/tests/factories/model_factories.py#L164-L226]</target>
      <target>[MODIFY] @[backend_v2/tests/factories/model_factories.py#L229-L289]</target>
      <target>[MODIFY] @[backend_v2/tests/factories/model_factories.py#L292-L316]</target>
      <target>[MODIFY] @[backend_v2/tests/factories/model_factories.py#L319-L392]</target>
      <target>[MODIFY] @[backend_v2/tests/factories/test_model_factories.py#L39-L46]</target>
    </targets>
    <action>
      Update `@[backend_v2/tests/factories/model_factories.py#L76-L121]` (`WorkflowFactory`), `@[backend_v2/tests/factories/model_factories.py#L124-L161]` (`SystemRulePromptBlockFactory`), `@[backend_v2/tests/factories/model_factories.py#L164-L226]` (`OutputProfileFactory`), `@[backend_v2/tests/factories/model_factories.py#L229-L289]` (`MatrixPromptBlockFactory`), `@[backend_v2/tests/factories/model_factories.py#L292-L316]` (`ExecutionStepFactory`), and `@[backend_v2/tests/factories/model_factories.py#L319-L392]` (`ExecutionRecordFactory`), and add `ReportArtifactFactory` (`ReportArtifact`) so all factories generate strictly canonical hexadecimal Opaque Stripe IDs via `generate_opaque_id(EntityPrefix.<TYPE>)` (`EntityPrefix.WORKFLOW`, `EntityPrefix.OUTPUT_PROFILE`, `EntityPrefix.PROMPT_BLOCK`, `EntityPrefix.STEP`, `EntityPrefix.EXECUTION`, `EntityPrefix.REPORT`, `EntityPrefix.ORGANIZATION`), replacing `"org_testorg123"`, `"prof_..."`, `"st_..."`, and `"exec_..."`. Update `@[backend_v2/tests/factories/test_model_factories.py#L39-L46]` to register `ReportArtifactFactory` in `ALL_FACTORIES`, assert `OPAQUE_STRIPE_ID_REGEX` compliance across all generated IDs, and add >=2 ISTQB negative validation boundary tests (`test_polyfactory_invalid_id_error`, `test_polyfactory_invalid_extra_field_error` resolving `TD_ISTQB_NEGATIVE`).
    </action>
    <constraint invariant="id_backend_generation_authority_mandate">
      All mock IDs must match pattern ^([a-z]{2,5})_[a-fA-F0-9]{16,32}$.
    </constraint>
  </step>
</execution_protocol>
```

---

## 3. Verification & Quality Gates

To verify that these 4 systemic improvements and Osa 2 alignments are fully effective:
1. **Improvement 1 &amp; 2 Verification**: Run `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py -k "qgr030"` to verify static detection of deprecated backend strings in calls.
2. **Improvement 3 Verification**: Run `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py -k "boundary"` to verify automated physical existence testing of `BOUNDARY_EXEMPTION_FILES`.
3. **Improvement 4 Verification**: Run `uv run python scripts/audit_zero_orm_strictness.py` and `uv run python scripts/backend_audit_loop.py scripts/_ast_guardrails.py --ast-strict` to confirm all `scripts/` pass cleanly.
4. **Global Quality Gate**: Run `uv run python scripts/backend_audit_loop.py backend_v2/ --test` to confirm 100% pass across all stages.

### 3.1 Unified Post-Implementation Tier 2 Hardening (All 18 Targets)

Upon completing Steps 1–5, a single comprehensive Tier 2 Hardening run audits and hardens all 18 targets in parallel via `scripts/auto_hardening_runner.py`:

```markdown
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker "[NEW] @[docs/implementationplans/TRACKER_Systemic_Prevention_and_AST_Guardrails.md]" --gate backend --model gemini-4-argon-medium`.
  - [ ] @[backend_v2/database/driver.py]
  - [ ] @[backend_v2/database/factory.py]
  - [ ] @[backend_v2/database/interfaces.py]
  - [ ] @[backend_v2/database/postgres/entity_adapter.py]
  - [ ] @[backend_v2/database/postgres/pool.py]
  - [ ] [NEW] @[backend_v2/database/postgres/storage_driver.py]
  - [ ] @[backend_v2/main.py]
  - [ ] @[backend_v2/models/core_base.py]
  - [ ] @[backend_v2/seed/run_seed.py]
  - [ ] @[backend_v2/services/storage.py]
  - [ ] @[backend_v2/settings.py]
  - [ ] @[scripts/_ast_guardrails.py]
  - [ ] @[scripts/audit_zero_orm_strictness.py]
  - [ ] @[scripts/reconcile_storage.py]
  - [ ] @[scripts/run_e2e_variance_test.py]
  - [ ] @[scripts/backend_audit_loop.py]
  - [ ] @[backend_v2/tests/factories/model_factories.py]
  - [ ] @[backend_v2/tests/unit/scripts/test_ast_guardrails.py]
```
