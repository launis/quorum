# EPIC 150: SYSTEM 2 RESEARCH & RED-TEAMING AUDIT REPORT

**Target Document**: `@[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md]`  
**Auditor**: Principal Enterprise Architect & System Red Team  
**Audit Protocol**: `/tier0-research-epic` (System 2 First-Principles Deconstruction & In-Place Hardening)  
**Date**: 2026-08-31  

---

## 1. Executive Summary & Verification Matrix

The objective of Epic 150 is to achieve **absolute mathematical zero** permissive typing patterns across the entire Quorum backend codebase. This audit evaluated the Epic against the **5-Axis System 2 Architecture**, **5-Tier Regression Defense**, the **Quorum 2026 Modernity Invariants**, and all relevant Knowledge Items.

### Boundary Audit Status
- `audit_markdown_boundaries.py` check: **PASSED (0 findings, 100% compliant)**
- Context & KI Coverage: **5 Rules verified, 8 KIs verified**

---

## 2. Five-Axis System 2 Deconstruction

### Axis 1: TARGET SCOPE & BOUNDARY (Scope Inquisitor)
- **Blast Radius Analysis**: The Epic touches ~94 files across 4 distinct execution phases. It cleanly isolates internal persistence boundaries (102 exempt `dict[str, Any]` annotations in database drivers/interfaces) from the domain/service layers.
- **Scope Creep Elimination**: Deferred monolithic decomposition of `worker.py` (1,497 LOC) to a dedicated God Code Epic, focusing Phase 2 purely on surgical typing, QGR suppression eradication, and typed telemetry envelopes.

### Axis 2: ERADICATED DUCT-TAPE (Duct-Tape Prosecutor)
- **Eliminated Patterns**:
  1. `list[dict[str, Any]]` message arrays in `CompiledPrompt` and LLM adapters.
  2. `.get("role")`, `.get("content")` dictionary access fallbacks.
  3. `isinstance(..., dict)` duck-typing across 152 locations.
  4. 130 `# noqa: QGR` inline suppressions.
  5. Unhandled Pydantic `ValidationError` bubbling into generic 500 HTTP responses.
  6. Standard `.model_dump()` null-field leakage (`"tool_calls": None`, `"tool_call_id": None`) that causes 400 Bad Request errors on Gemini 3.7 and Claude 3.7.
  7. Pre-mature `drop_tables()` in `run_seed.py` before in-memory collection validation.

### Axis 3: APPROVED BEST PRACTICE (Type Constitutionalist)
- **Target Invariants**:
  1. `LLMMessageDTO`, `PromptMetadataDTO`, `ProviderMetadataDTO`, `TaskMetadataDTO`, and `ProviderExtraParamsDTO` locked with `ConfigDict(strict=True, extra="forbid", frozen=True)`.
  2. Outer egress serialization enforced via `[m.model_dump(mode="json", exclude_none=True) if isinstance(m, BaseModel) else m for m in messages]`.
  3. Two-Phase Pre-Flight In-Memory Validation pattern in `run_seed.py`.
  4. 3-Tiered Anti-Duck-Typing Protocol: (1) Direct DTO dot-notation, (2) Guarded `TypeAdapter` validation with RFC-7807 `AppException(VALIDATION_FAILED)`, (3) Discriminated Unions for polymorphic DAG states.

### Axis 4: PRUNED OVER-ENGINEERING (Complexity Slayer)
- **30% Deletion Test Applied**:
  - Rejected creating a generic monolithic `SimulationResultDTO`. Directly reuses established SSOT models from `backend_v2/models/dtos/studio.py` (`WorkflowSimulationResponse`, `StepSimulationResponse`, `PromptBlockSimulationResponse`).
  - Purged obsolete `Workflow.ui_schema` and `Step.output_schema` without creating redundant replacement fields.
  - Co-located `PromptMetadataDTO` in `models/prompt.py` and `TaskMetadataDTO` in `core/registry.py` to prevent single-class file sprawl.

### Axis 5: FAIL-FAST PROOF ANCHOR (Incorruptible Judge)
- **Proof Mechanisms**:
  - AST Guardrails (`QGR001`, `QGR002`, `QGR012`) upgraded to universal `FATAL` severity for non-exempt files.
  - Multi-Category Exemption Register locked with exact mathematical counts (102 persistence annotations, 6 stdlib logging reflection calls, 1 transport boundary).
  - Explicit ISTQB negative boundary partition test specifications for all new DTOs and Seeder pre-flight validation.

---

## 3. Panel of Architects Evaluation

| Perspective | Verdict | Findings & Hardening Applied |
| :--- | :--- | :--- |
| **Global System Architect** | **APPROVED** | Enforces zero backward compatibility, zero fallback chains, and clean-slate seeding. Adheres to Single Source of Truth (SSOT). |
| **Backend/Data Architect** | **APPROVED** | Verified Multi-Category Exemption Register. Confirmed that persistence drivers retain raw dictionaries internally while repositories act as the typed reconstitution firewall. |
| **SDUI & Frontend Architect** | **APPROVED** | Verified decoupling between internal `ProgressState` and SSE `ExecutionRecord` transport. Guaranteed zero `FormatException` or `CheckedFromJsonException` in Flutter client. |
| **AI & Orchestration Architect** | **APPROVED** | Locked prompt compilation to `LLMMessageDTO` with O(1) static prefix context caching (`ki_provider_agnostic_caching.md`) and verified `exclude_none=True` parameter sanitization. |

---

## 4. Falsification & Plausible Failure Modes (Anti-Happy-Path)

### Failure Mode 1: LiteLLM / Provider 400 Bad Request via Null-Field Injection
- **Scenario**: When converting `LLMMessageDTO` to dictionaries for third-party SDK calls (`litellm.acompletion`), default `.model_dump()` emits `"tool_calls": None` and `"tool_call_id": None`. Strict providers like Anthropic Claude 3.7 or Vertex AI Gemini 3.7 reject requests containing explicit null fields for tool parameters with HTTP 400 Bad Request.
- **Epic Defense**: Mandates `[m.model_dump(mode="json", exclude_none=True) if isinstance(m, BaseModel) else m for m in messages]` across all adapter callsites and includes an explicit ISTQB negative test partition asserting zero null keys in dumped payloads.

### Failure Mode 2: Seeder Boot Crash on Corrupted Seed Data
- **Scenario**: If a developer introduces invalid schema entries into `seed_data.json`, standard seeding scripts that execute `drop_tables()` before validating all models wipe the database and then crash on hydration, leaving the local developer environment in an unrecoverable dead state.
- **Epic Defense**: Enforces Two-Phase Commit in `run_seed.py`: Phase 1 parses and validates 100% of all items in memory across all collections in `STANDARD_REGISTRY`. Phase 2 executes `drop_tables()` and database inserts only if Phase 1 passes with zero errors.

---

## 5. 5-Column Architectural Directive Table (Consolidated)

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape | 3. Approved Best Practice | 4. Pruned Over-Engineering | 5. Verification & Fail-Fast |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 1: LLM Prompt & Adapter Core**<br>`backend_v2/models/prompt.py`<br>`backend_v2/models/llm.py`<br>`backend_v2/llm/adapters/`<br>`backend_v2/llm/caching_service.py`<br>`backend_v2/seed/seed_registry.py`<br>`backend_v2/seed/run_seed.py`<br>20+ test files | Banned `list[dict[str, Any]]`, `.get("role")`, `isinstance(dict)` in adapters, and dropping DB before validation. | `LLMMessageDTO` & `PromptMetadataDTO` with `ConfigDict(strict=True, extra="forbid", frozen=True)`. List comprehension with `exclude_none=True` at LiteLLM boundary. | Pruned transitional union types. Co-locate metadata DTOs without class sprawl. | `backend_audit_loop.py` on Phase 1 targets.<br>ISTQB null-omission tests.<br>`test_run_seed.py` pre-flight verification. |
| **Phase 2: Service & Seed Models**<br>`backend_v2/services/progress.py`<br>`backend_v2/core/registry.py`<br>`backend_v2/services/studio/`<br>`backend_v2/models/v2_core.py`<br>`backend_v2/seed/seed_data.json`<br>`backend_v2/worker.py` | Banned `dict[str, Any]` in `ProgressState`, `Workflow.ui_schema`, `Step.output_schema`, `ModelProfile.additional_params`, and orphan `"step_blueprints": []`. | Strongly typed `ProgressState`, `TaskMetadataDTO`, `ProviderExtraParamsDTO`. Sanitized vault via `sanitize_seed_vault.py`. | Pruned generic `SimulationResultDTO`; directly reuse SSOT studio DTOs. Pruned obsolete schemas. | `backend_audit_loop.py` on Phase 2 targets.<br>`sanitize_seed_vault.py --reseed --test`<br>`audit_database_atoms.py --strict` |
| **Phase 3: Hooks & Orchestrator**<br>`backend_v2/hooks/`<br>`backend_v2/services/orchestrator/`<br>`backend_v2/database/repositories/` | Banned all 130 `# noqa: QGR` suppressions, duck-typing `isinstance(dict)`, and unhandled validation 500 errors. | 3-Tiered Anti-Duck-Typing Protocol: (1) Direct DTO access, (2) Guarded `TypeAdapter` hydration with RFC-7807 `AppException(VALIDATION_FAILED)`, (3) Discriminated Unions. | Pruned monomorphic model validation on heterogeneous DAG states. | `_ast_guardrails.py --strict` on hooks, orchestrator, and repositories. |
| **Phase 4: AST Hardening & KI**<br>`scripts/_ast_guardrails.py`<br>`.agents/rules/01-python-backend.md`<br>`.agents/rules/03_seed_vault.md`<br>`ki_zero_permissive_typing.md` | Banned all non-exempt `QGR001`, `QGR002`, `QGR012` violations across codebase. | Universal `FATAL` severity on AST guardrails with explicit 102-count persistence exemption register. | Unified AST scanner in Stage 4 of audit loop. | Zero-violation verification:<br>`_ast_guardrails.py backend_v2/ --strict`<br>`backend_audit_loop.py backend_v2/ --test` |

---

## 6. Conclusion & Readiness Recommendation

Epic 150 has been thoroughly audited and hardened in-place. All boundary checks pass, technical debt is properly partitioned into Phase 1 pre-implementation cleanups, and the four execution phases are structured as **Subsystem-Atomic Vertical Slices** to prevent CI Pipeline Deadlocks.

**Recommendation**: The Epic is **100% READY** for phased execution breakdown via `/tier1-planner`.
