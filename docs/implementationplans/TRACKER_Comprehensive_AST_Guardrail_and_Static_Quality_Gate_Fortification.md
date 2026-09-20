# Tracker: Comprehensive AST Guardrail & Static Quality Gate Fortification (Python & Dart)
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Comprehensive_AST_Guardrail_and_Static_Quality_Gate_Fortification.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
</required_context_rules>

## Step Execution Status
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Comprehensive_AST_Guardrail_and_Static_Quality_Gate_Fortification.md]
- [x] **Execution:** `/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_Comprehensive_AST_Guardrail_and_Static_Quality_Gate_Fortification.md] @[docs/implementationplans/TRACKER_Comprehensive_AST_Guardrail_and_Static_Quality_Gate_Fortification.md]`
  - [x] Step 1: PRE-IMPLEMENTATION TECHNICAL DEBT CLEANUP
  - [x] Step 2: EXPAND AST GUARDRAILS ENGINE (PYTHON BACKEND)
  - [x] Step 3: DEVELOP DART GUARDRAILS ENGINE (FLUTTER CLIENT)
  - [x] Step 4: INTEGRATE QUALITY GATES INTO AUDIT SCRIPTS
  - [x] Step 5: ISTQB UNIT TEST SUITE EXPANSION & FALSE-POSITIVE IMMUNITY
  - [x] Step 6: KNOWLEDGE BASE SYNCHRONIZATION
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Comprehensive_AST_Guardrail_and_Static_Quality_Gate_Fortification.md] @[docs/implementationplans/TRACKER_Comprehensive_AST_Guardrail_and_Static_Quality_Gate_Fortification.md]`
  - Audit Artifact: `@[red_team_audit_comprehensive_ast_guardrail_and_static_quality_gate_fortification.md]`
  - Verdict: ✅ PASSED (All 17 core requirements physically verified; 5 minor unparenthesized `except E1, E2:` syntax items fully resolved and parenthesized across `_ast_guardrails.py`, `_dart_guardrails.py`, and `flutter_audit_loop.py`).

### Post-Implementation Gates
- [x] **[OK] Golden Master & Test Restoration Audit**: Ensured no @pytest.mark.skip or commented-out tests remain in modified domains (123/123 tests passing).
- [x] **[OK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified @-referenced production backend files:
  - [x] @[scripts/_ast_guardrails.py]
  - [x] @[scripts/_dart_guardrails.py]
  - [x] @[scripts/backend_audit_loop.py]
  - [x] @[scripts/flutter_audit_loop.py]
- [x] **[OK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified @-referenced production Flutter files:
  - (No production Dart files modified in this plan; client migrations deferred to EPIC 152 Phase 4)
- [x] **[OK] Pre-Delete Audit**: Verified no orphaned symbols or dependencies remain.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verified line coverage >90% for modified business logic (92% total coverage).

### Documentation & Knowledge Item Update
- [x] **[OK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to anchor physical implementation in `docs/architecture/` (scoped to relevant documents), update relevant Knowledge Items, and synchronize `.agents/rules/04_directory_reference.md`.
  - [x] Knowledge Item Updated: @[ki_zero_permissive_typing.md] (Record QGR000, QGR001, QGR002, QGR003, QGR018, DGR001-DGR004, and boundary exemption invariants)
  - [x] Architecture Rule Synchronized: @[.agents/rules/04_directory_reference.md]

### Final Plan Audit
- [x] **[OK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Comprehensive_AST_Guardrail_and_Static_Quality_Gate_Fortification.md] @[docs/implementationplans/TRACKER_Comprehensive_AST_Guardrail_and_Static_Quality_Gate_Fortification.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent
- **Atomic Commit Mandate**: After each successful quality gate verification, commit changes atomically with strict Conventional Commits syntax (`<type>(<scope>): <summary>`). List all staged files explicitly.
- **Seeding Environment**: If database re-seeding is required, execute `uv run python backend_v2/seed/run_seed.py local`.
- **Quality Gates**:
  - For Python changes: `uv run python scripts/backend_audit_loop.py <target_path> --test`
  - For Flutter changes: `uv run python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build`
- **Execution Mode**: Supports Step-by-Step (default pause per step) and Continuous Full-Auto Mode (invoked via `/tier2-execute --full-auto`).
- **Context Budget Watchdog**: In Continuous Mode, proactively trigger `/tier5-session-handover` when context budget limit is reached: >8 turns, 3 atomic commits, or >5 modified complex files.
- **Workflow Loop**: `/tier2-execute @[plan] @[tracker]` -> `/tier8-audit-plan @[plan] @[tracker]` -> Post-Implementation Hardening Gates (`/tier2-hardening-backend`, `/tier2-hardening-frontend`) -> `/tier7-describe-architecture`.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-01 | Rectify Python 2 comma exception syntax in `_ast_guardrails.py` and `backend_audit_loop.py` | Step 1 | [x] |
| REQ-02 | Replace dynamic `hasattr` reflection in `flutter_audit_loop.py` with concrete `isinstance(sys.stdout, io.TextIOWrapper)` type narrowing | Step 1 | [x] |
| REQ-03 | Translate Finnish console strings in `flutter_audit_loop.py` to professional English, normalize relative paths, and remove legacy phase references | Step 1 | [x] |
| REQ-04 | Resolve workspace root path before `os.chdir` in `flutter_audit_loop.py` for deterministic helper script execution | Step 1 | [x] |
| REQ-05 | Implement Rule QGR000 in `CommentSuppressor` to emit FATAL violations on `# noqa: QGR*` comment suppressions in domain code | Step 2 | [x] |
| REQ-06 | Expand Rule QGR001 to ban `vars()`, `__dict__`, and `operator.attrgetter` in domain code and test files | Step 2 | [x] |
| REQ-07 | Fortify Rule QGR002 to eliminate 1-argument and 2-argument dictionary `.get()` lookups with strict client/ContextVar exemptions | Step 2 | [x] |
| REQ-08 | Fortify Rule QGR003 to eliminate silent exception swallowing in domain code lacking `raise` or typed DLQ dispatch | Step 2 | [x] |
| REQ-09 | Implement Rule QGR018 banning dictionary type laundering via Pydantic `TypeAdapter(dict[...])` | Step 2 | [x] |
| REQ-10 | Strictly maintain `BOUNDARY_EXEMPTION_FILES` contract locked to the 4 physical boundary files | Step 2 | [x] |
| REQ-11 | Implement `scripts/_dart_guardrails.py` enforcing DGR001 (Map returns), DGR002 (SizedBox.shrink), DGR003 (hardcoded strings), and DGR004 (lint suppressions) | Step 3 | [x] |
| REQ-12 | Ensure 100% generated file immunity (`*.freezed.dart`, `*.g.dart`) and CLI table reporting with `--strict` escalation in `_dart_guardrails.py` | Step 3 | [x] |
| REQ-13 | Integrate FATAL enforcement of QGR000, QGR001, QGR002, QGR003, and QGR018 into `scripts/backend_audit_loop.py` | Step 4 | [x] |
| REQ-14 | Integrate `_dart_guardrails.py` automated gate into `scripts/flutter_audit_loop.py` following code generation | Step 4 | [x] |
| REQ-15 | Expand `backend_v2/tests/unit/scripts/test_ast_guardrails.py` with ISTQB boundary partitions for all updated Python rules and exemptions | Step 5 | [x] |
| REQ-16 | Create comprehensive unit test suite `backend_v2/tests/unit/scripts/test_dart_guardrails.py` for Dart analyzer and generated code immunity | Step 5 | [x] |
| REQ-17 | Synchronize `ki_zero_permissive_typing.md` with new guardrail rules, zero-tolerance invariants, and boundary contracts | Step 6 | [x] |

# Session Handover Context
## Achieved
- Plan thoroughly researched and red-teamed via `/tier0-research-plan` with 5-Column Directives and adversarial failure mode analysis.
- Implementation plan anchored at `@[docs/implementationplans/IMPLEMENTATION_PLAN_Comprehensive_AST_Guardrail_and_Static_Quality_Gate_Fortification.md]`.
- Double-entry bookkeeping tracker created at `@[docs/implementationplans/TRACKER_Comprehensive_AST_Guardrail_and_Static_Quality_Gate_Fortification.md]`.
- Step 1 Completed: Modernized Python 2 comma exception tuples in `_ast_guardrails.py` and `backend_audit_loop.py`; replaced reflection with `isinstance` type narrowing, normalized relative paths, and translated console output to English in `flutter_audit_loop.py`. Verified with `py_compile`, pytest, and `backend_audit_loop.py` (0 errors).
- Step 2 Completed: Expanded Python AST guardrails with QGR000 (domain suppression fatal ban), QGR001 (`vars()`, `.__dict__`, `operator.attrgetter`), QGR002 (discriminated 1-arg and 2-arg `.get()` eradication with closed receiver exclusions), QGR003 (silent exception swallowing eradication), and QGR018 (`TypeAdapter(dict)` type laundering ban). Preserved 4-driver physical boundary exemption.
- Step 3 Completed: Developed client-side `scripts/_dart_guardrails.py` enforcing DGR001 (loose Map returns), DGR002 (`SizedBox.shrink()` concealment), DGR003 (hardcoded UI string literals), and DGR004 (Dart lint suppressions), with 100% generated file immunity (`*.freezed.dart`, `*.g.dart`) and `--strict` escalation.
- Step 4 Completed: Integrated expanded guardrails into `scripts/backend_audit_loop.py` (fatal enforcement of QGR000-QGR003, QGR018) and `scripts/flutter_audit_loop.py` (automated Dart gate following code generation and before formatting).
- Step 5 Completed: Expanded ISTQB unit test suites across `backend_v2/tests/unit/scripts/test_ast_guardrails.py` (96 tests) and `backend_v2/tests/unit/scripts/test_dart_guardrails.py` (27 tests), achieving 100% pass rate (123/123 tests) and 92% combined code coverage (>90% threshold satisfied).
- Step 6 Completed: Synchronized `ki_zero_permissive_typing.md` with QGR000-QGR003, QGR018, DGR001-DGR004, and boundary exemption invariants, updated `zero_permissive_typing/metadata.json`, and anchored `_dart_guardrails.py` in `@[.agents/rules/04_directory_reference.md]`.
- Audit Follow-Up Completed: Parenthesized all 5 unparenthesized comma-separated exception statements in `_ast_guardrails.py` (lines 40 & 193), `_dart_guardrails.py` (line 36), and `flutter_audit_loop.py` (lines 26 & 31). Verified 123/123 tests passing with 92% coverage and clean audit loops.
- Tier 2 Backend Hardening Completed: Fully audited and hardened all 4 target scripts (`_ast_guardrails.py`, `_dart_guardrails.py`, `backend_audit_loop.py`, `flutter_audit_loop.py`). Enforced explicit `__all__ = [...]` encapsulation and Google-style docstrings across all modules. Developed 15 new hermetically isolated ISTQB unit tests in `test_flutter_audit_loop.py` (98% line coverage). Successfully generated and validated strict Neuro-Symbolic Audit Matrices (177/177 rules) across all 4 targets via `audit_matrix_manager.py`. Verified 100% clean passes on all 6 stages of `backend_audit_loop.py` with strict AST guardrails (366/366 tests passing).

## Learned
- **Python 2 Comma Syntax:** Target files `_ast_guardrails.py` and `backend_audit_loop.py` contain legacy comma syntax in `except` blocks that must be modernized to parenthesized tuples in Step 1.
- **Parenthesized Exception Syntax:** Replaced all legacy comma-separated exception types with parenthesized tuples across target scripts, satisfying PEP 3110 / PEP 8 standards.
- **Ruff Format Python 3.14 Simplification:** Under Ruff 0.15.20 with `target-version = "py314"`, multi-exception syntax in `except A, B:` without parentheses is canonicalized automatically without errors.
- **Reflection Elimination:** Dynamic `hasattr(sys.stdout, "reconfigure")` in `flutter_audit_loop.py` must be replaced with concrete `isinstance(sys.stdout, io.TextIOWrapper)` type narrowing.
- **Dart Rule Severity Calibration:** Rules DGR001–DGR004 must emit WARNING severity in default baseline audits to prevent crashing CI before Phase 4 client migrations (27 `SizedBox.shrink()` usages and 49 loose Map returns), escalating to FATAL strictly under `--strict`.
- **Domain Suppression Partitioning:** Unit tests for comment suppressions in `test_ast_guardrails.py` must be explicitly partitioned between domain code (where QGR000 is always FATAL) and non-domain test fakes (where valid reasons pass).
- **Working Directory Traversal:** `flutter_audit_loop.py` must resolve workspace root before `os.chdir(client_app_dir)` to invoke Python helper scripts in `scripts/`.
- **TypeAdapter AST Matching:** TypeAdapter detection (QGR018) must use structural AST node matching rather than substring searching to avoid false positives on class names containing "dict".
- **Module Encapsulation & Test Discovery:** All standalone scripts must declare explicit `__all__ = [...]` exports, and `backend_audit_loop.py` must correctly resolve fallback test paths for scripts targeting `backend_v2/tests/unit/scripts/`.

## Remaining
- As-Built Documentation Sync (`/tier7-describe-architecture`)

## Resume Command
```powershell
/tier7-describe-architecture
```
