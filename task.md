# Task Tracker: Automated AST Codebase Guardrails & Workflow Scripts Modernization

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_ast_guardrail_testing.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
</required_context_rules>

## Milestone A: Core Engine & Gatekeeper (Phases 1–4)

### Phase 1: Pre-requisite Gatekeeper Cleanup & Core AST Guardrail Engine
- [x] **Step 1.1**: Refactor `@[scripts/backend_audit_loop.py]` to eradicate all existing technical debt per `touched_scope_tech_debt_mandate`
- [x] **Step 1.2**: Implement `GuardrailSeverity`, `GuardrailViolation` DTO, `CommentSuppressor`, and `QuorumGuardrailVisitor` in `@[scripts/_ast_guardrails.py]`
- [x] **Step 1.3**: Implement `scan_files_for_guardrails` CLI engine in `@[scripts/_ast_guardrails.py]`

### Phase 2: ISTQB Unit Testing & Isolated Scanner Verification (TDD First)
- [x] **Step 2.1**: Implement ISTQB unit tests in `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]` covering 33+ partitions
- [x] **Step 2.2**: Refactor `DomainSecurityVisitor` in `@[backend_v2/tests/unit/test_ast_domain_security_guardrails.py]` to eliminate legacy `getattr()` calls
- [x] **Step 2.3**: Execute isolated Pytest run verifying 100% test pass and >90% coverage on `@[scripts/_ast_guardrails.py]`

### Phase 3: Backend Audit Loop Quality Gate Integration, CLI Testing & Self-Audit
- [x] **Step 3.1**: Integrate AST check into `@[scripts/backend_audit_loop.py]` main() as Step 4 with `--ast-strict` CLI flag support
- [x] **Step 3.2**: Implement hermetically isolated unit tests in `@[backend_v2/tests/unit/scripts/test_backend_audit_loop.py]`
- [x] **Step 3.3**: Execute Strict Self-Audit with `backend_audit_loop.py` on gatekeeper files with `--ast-strict`

### Phase 4: Knowledge Item Governance & Live E2E Verification
- [x] **Step 4.1**: Create Knowledge Item `@[ki_ast_guardrail_engine.md]` in `<appDataDir>\knowledge\ast_guardrail_engine\`
- [x] **Step 4.2**: Execute Final Live E2E REST API Verification Gate on `@[backend_v2/tests/integration/test_integration_real_llm.py]` with `RUN_LIVE_E2E="true"`
- [x] **Step 4.3**: Context Flush Checkpoint 1 (Mandatory Session Handover)

---

## Milestone B: Shared AST Utilities, Immediate Workflow Consumers & DTO Parity Modernization (Phase 5)

### Phase 5: Shared AST Utils, Immediate Workflow Consumers & DTO Parity
- [ ] **Step 5.1**: Refactor `@[scripts/_ast_boundary_utils.py]` with zero reflection and Pydantic V2 DTOs
- [ ] **Step 5.2**: Refactor `@[scripts/audit_dto_parity.py]` with zero reflection and Pydantic V2 DTOs
- [ ] **Step 5.3**: Migrate `@[scripts/audit_planner_output.py]` and `@[scripts/audit_epic_coverage.py]` to consume refactored DTOs
- [ ] **Step 5.4**: Implement unit tests `@[backend_v2/tests/unit/scripts/test_ast_boundary_utils.py]`, `@[backend_v2/tests/unit/scripts/test_audit_dto_parity.py]`, and migrated `@[backend_v2/tests/unit/scripts/test_audit_verification_scripts.py]`
- [ ] **Step 5.5**: Context Flush Checkpoint 2 (Mandatory Session Handover)

---

## Milestone C: Standalone Workflow Diagnostics, Evidence Engine & Production Dry-Run (Phases 6–7)

### Phase 6: Standalone Workflow Diagnostics & Remediation Standardization
- [ ] **Step 6.1**: Modernize `@[scripts/audit_markdown_boundaries.py]` with Pydantic V2 DTOs and AST inspection
- [ ] **Step 6.2**: Modernize `@[scripts/audit_tracker_output.py]` with Pydantic V2 DTOs and remediation guidance
- [ ] **Step 6.3**: Implement unit tests `@[backend_v2/tests/unit/scripts/test_audit_markdown_boundaries.py]` and `@[backend_v2/tests/unit/scripts/test_audit_tracker_output.py]`

### Phase 7: Neuro-Symbolic Matrix AST Evidence Engine Integration
- [ ] **Step 7.1**: Modernize `@[scripts/audit_matrix_manager.py]` with AST scan binding and Pydantic V2 schemas
- [ ] **Step 7.2**: Implement unit tests `@[backend_v2/tests/unit/scripts/test_audit_matrix_manager.py]`
- [ ] **Step 7.3**: Execute Final Production Dry-Run Scan Proof on top 3 largest production Python files

---

## Session Handover Context
- **Achieved**: Completed Milestone A (Phases 1–4). Implemented `scripts/_ast_guardrails.py` (QGR000–QGR010), refactored `scripts/backend_audit_loop.py` to integrate the AST gate with `--ast-strict`, implemented comprehensive unit tests with >90% coverage across all files, created Knowledge Item `ki_ast_guardrail_engine.md`, and passed full quality gate suites.
- **Learned**: AST comment suppression parsing directly via `tokenize` and structural pattern matching (`match/case`) avoids the Python `ast.NodeVisitor` reflection paradox. Gatekeepers achieve 100% self-compliance with 0 violations and 0 suppressions.
- **Remaining**: Milestone B: Shared AST Utilities & Immediate Consumers (Phase 5), Milestone C: Standalone Diagnostics & Neuro-Symbolic Matrix (Phases 6–7).
