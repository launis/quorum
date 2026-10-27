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
| **1. Zero-Bifurcation Mandate** | Coexistence of `STORAGE_BACKEND=LOCAL` (TinyDB) alongside `POSTGRES` allowed deprecated code and tests to hide in parallel execution paths. | **Phase 1 (`QGR030`) & Phase 3**: <br>1. Implement `QGR030` (`FATAL`) banning deprecated backend references repo-wide.<br>2. Add `zero_compromise_cutover_mandate` to `.agents/rules/00-antigravity-core.md` prohibiting transitional coexistence or backward compatibility shims. |
| **2. Hermetic Test Isolation & Fixture Sovereignty** | Unit tests unrelated to persistence (specifically `test_token_service.py`) lazily instantiated `Settings(storage_backend="LOCAL")`, exploding when Fail-Fast was activated. | **Phase 1 (`QGR030`) & Phase 3**: <br>1. `QGR030` statically parses `Settings(...)` calls in tests and forbids deprecated backend keywords.<br>2. Add `hermetic_test_fixtures_mandate` to `.agents/rules/01-python-backend.md` requiring pure in-memory fakes (`InMemoryUnitOfWork`, `InMemoryEntityAdapter`). |
| **3. Pre-Flight Metatest & Exemption Mapping** | Deleting `tinydb_driver.py` and `wrapper.py` broke metatests (`test_ast_guardrails.py`, `test_scripts_cli_help.py`) because `BOUNDARY_EXEMPTION_FILES` was unmapped in the plan. | **Phase 1 & Phase 3**: <br>1. Add automated existence validation in `test_ast_guardrails.py` asserting `Path(f).exists()` for all exemption entries.<br>2. Update `.agents/workflows/tier0-research-plan.md` to mandate pre-flight grep across `scripts/` and `tests/unit/scripts/` whenever files are marked `[DELETE]`. |
| **4. First-Class Script Strictness & Polyfactory** | `scripts/reconcile_storage.py` contained loose dicts, and tests used non-hex fake IDs (`exe_ghost1234567890`), breaking Pydantic V2 validation. | **Phase 2 & Phase 4**: <br>1. Include `scripts/` in `scripts/backend_audit_loop.py` and `scripts/audit_zero_orm_strictness.py`.<br>2. Expand Polyfactory definitions in `backend_v2/tests/factories/model_factories.py` and enforce regex `^([a-z]{2,5})_[a-fA-F0-9]{16,32}$` via `QGR030`. |
| **Osa 2: Tracker & Requirements Parity** | `TRACKER_PostgreSQL_Final_Cutover.md` and `POSTGRESQL_CUTOVER_REQUIREMENTS.md` needed 100% complete 5-KI alignment and unambiguous Tier 7 directives. | **Verified & Completed**: <br>1. Added `ki_seed_vault_verification_and_sanitization.md` establishing 5 KIs.<br>2. Formulated closed-list Tier 7 synchronization directives obeying `anti_ambiguity_mandate`. |

---

## 1. Scope & Target Boundaries

| Target File & AST Span | Planned Action | Architectural Responsibility |
| :--- | :--- | :--- |
| `[MODIFY] @[scripts/_ast_guardrails.py#L523-L2576]` | `[MODIFY]` | Implement `QGR030` (`FATAL`) in `QuorumGuardrailVisitor` banning deprecated storage backend references (`LOCAL`, `FIRESTORE`) in function calls and test fixtures, and validate entity ID string literals against canonical hexadecimal format (`^([a-z]{2,5})_[a-fA-F0-9]{16,32}$`). |
| `[MODIFY] @[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2247-L2271]` | `[MODIFY]` | Add comprehensive unit tests for `QGR030` with >=2 positive violation detections and >=2 negative boundary cases, plus automated existence validation for `BOUNDARY_EXEMPTION_FILES`. |
| `[MODIFY] @[scripts/backend_audit_loop.py#L73-L356]` | `[MODIFY]` | Include `scripts/` as an authoritative, first-class audit target for MyPy, AST guardrails, and test execution in the global completion gate. |
| `[MODIFY] @[scripts/audit_zero_orm_strictness.py#L581-L633]` | `[MODIFY]` | Ensure `scripts/reconcile_storage.py` and all operational scripts are systematically verified under `ZORM001`–`ZORM006` Zero-ORM strictness. |
| `[MODIFY] @[.agents/rules/01-python-backend.md#L10-L60]` | `[MODIFY]` | Formalize `hermetic_test_fixtures_mandate` banning live settings instantiation or storage backend overrides in domain unit tests. |
| `[MODIFY] @[.agents/rules/00-antigravity-core.md#L87-L105]` | `[MODIFY]` | Formalize `zero_compromise_cutover_mandate` banning transitional dual-backend states during platform migrations. |
| `[MODIFY] @[.agents/workflows/tier0-research-plan.md#L50-L53]` | `[MODIFY]` | Add `preflight_metatest_and_exemption_mapping_mandate` to research workflow requiring pre-flight grep on `scripts/` and `tests/unit/scripts/` when files are marked `[DELETE]`. |
| `[MODIFY] @[backend_v2/tests/factories/model_factories.py#L319-L392]` | `[MODIFY]` | Expand Polyfactory models to guarantee all mock entity IDs adhere strictly to canonical regex hexadecimal format. |

---

## 2. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Phase 1: Implement AST Guardrail QGR030 &amp; Self-Verifying Exemption Lists (Improvements 1, 2, &amp; 3)">
    <targets>
      <target>[MODIFY] @[scripts/_ast_guardrails.py#L523-L2576]</target>
      <target>[MODIFY] @[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2247-L2271]</target>
    </targets>
    <action>
      Implement `QGR030` (`FATAL`) in `QuorumGuardrailVisitor` inside `scripts/_ast_guardrails.py` (`visit_Call` and `visit_Constant`):
      1. **Improvement 1 &amp; 2 (Zero-Bifurcation &amp; Static Call Guard)**: Inspect `ast.Call` nodes matching `Settings(...)` or any function call where `keywords` specify `storage_backend="LOCAL"`, `storage_backend="FIRESTORE"`, `StorageBackend.LOCAL`, or `StorageBackend.FIRESTORE`. Flag these immediately as FATAL violations, transforming runtime crashes into compile-time AST blocks.
      2. **Improvement 4 (Mock ID Regex Invariant)**: Inspect `ast.Constant` string literals matching entity prefix patterns (`exe_...`, `rep_...`, `tda_...`) whose suffix contains non-hexadecimal characters (`[^a-fA-F0-9]`), preventing non-hexadecimal mock ID strings (specifically and exhaustively: `exe_ghost1234567890`, `exe_disk9876543210`) from passing static analysis.
      3. **Improvement 3 (Self-Verifying Boundary Exemption Consistency)**: In `backend_v2/tests/unit/scripts/test_ast_guardrails.py`, add a deterministic self-verification test iterating `BOUNDARY_EXEMPTION_FILES` asserting that every declared file physically exists on disk. If a file is deleted from version control without updating the exemption list, raise a crystal-clear assertion error: "BOUNDARY_EXEMPTION_FILES contains deleted file: {path}".
    </action>
    <constraint invariant="universal_fail_fast">
      QGR030 must exit with fatal code 1 on any violation.
    </constraint>
  </step>

  <step id="2" name="Phase 2: First-Class Scripts Quality Gate &amp; Zero-ORM Strictness Integration (Improvement 4)">
    <targets>
      <target>[MODIFY] @[scripts/backend_audit_loop.py#L73-L356]</target>
      <target>[MODIFY] @[scripts/audit_zero_orm_strictness.py#L581-L633]</target>
    </targets>
    <action>
      Update `scripts/backend_audit_loop.py` to eliminate script blind spots by registering `scripts/` as an official first-class target. When running `backend_audit_loop.py backend_v2/ --test`, the script must automatically include all `.py` files in `scripts/` in Ruff formatting, MyPy strict typing, and AST guardrail checks. Update `scripts/audit_zero_orm_strictness.py` to verify that all operational scripts touching domain models or database ports adhere to `ZORM001`–`ZORM006` with zero naked dicts.
    </action>
    <constraint invariant="the_zero_compromise_pledge">
      Zero permissive dictionaries or unannotated accumulators in scripts/.
    </constraint>
  </step>

  <step id="3" name="Phase 3: Hermetic Test Fixtures &amp; Pre-Flight Metatest Mapping Mandate (Improvements 1, 2, &amp; 3)">
    <targets>
      <target>[MODIFY] @[.agents/rules/01-python-backend.md#L10-L60]</target>
      <target>[MODIFY] @[.agents/rules/00-antigravity-core.md#L87-L105]</target>
      <target>[MODIFY] @[.agents/workflows/tier0-research-plan.md#L50-L53]</target>
    </targets>
    <action>
      Update `.agents/rules/01-python-backend.md` to add `hermetic_test_fixtures_mandate`:
      - Unit tests testing domain logic, token verification, SDUI rendering, or linguistics MUST NEVER instantiate concrete production `Settings()` instances or configure live database backends.
      - Unit tests MUST use lightweight in-memory fakes (`InMemoryUnitOfWork`, `InMemoryEntityAdapter`) and Polyfactory models.
      Update `.agents/rules/00-antigravity-core.md` to add `zero_compromise_cutover_mandate`:
      - Forbids transitional dual-backend states or legacy fallback branches during platform migrations.
      Update `.agents/workflows/tier0-research-plan.md` to add `preflight_metatest_and_exemption_mapping_mandate`:
      - Whenever an implementation plan includes `[DELETE]` targets or removes symbols/drivers, pre-flight research MUST execute `grep_search` across `scripts/` and `tests/unit/scripts/` (specifically: `BOUNDARY_EXEMPTION_FILES`, `test_ast_guardrails.py`, and `test_scripts_cli_help.py`). Any discovered metatest files, exemption lists, or CLI help callers that reference the deleted symbols MUST be explicitly added to the plan's TARGET boundaries and updated synchronously during implementation.
    </action>
    <constraint invariant="single_pipeline_invariant_mandate">
      Zero bifurcated pipelines or legacy fallback modes permitted in rules or domain code.
    </constraint>
  </step>

  <step id="4" name="Phase 4: Polyfactory SSOT &amp; Hexadecimal ID Generation Expansion (Improvement 4)">
    <targets>
      <target>[MODIFY] @[backend_v2/tests/factories/model_factories.py#L319-L392]</target>
    </targets>
    <action>
      Update `backend_v2/tests/factories/model_factories.py` to expand Polyfactory definitions across all core domain entities (including `ExecutionRecordFactory`, `ReportArtifactFactory`, `PromptBlockFactory`, `WorkflowFactory`). Ensure all factories generate strictly canonical hexadecimal IDs via `generate_opaque_id()` (RFC 9562 UUIDv7 for executions, reports, nodes, edges; UUIDv4 for static blocks). Validate that no factory produces non-hex characters.
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
