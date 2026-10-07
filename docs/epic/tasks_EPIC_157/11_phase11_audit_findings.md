# Architectural Audit Findings: Dict Eradication Anti-Patterns in Phase 11

**Document ID:** `11_phase11_audit_findings`  
**Target Epic:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]  
**Target Plan:** @[docs/epic/tasks_EPIC_157/11_phase11_plan.md]  
**Target Tracker:** @[docs/epic/EPIC_157_tracker.md]  
**Status:** MANDATORY HARDENING DIRECTIVE  
**Date:** 2026-10-07  

---

## 1. Executive Summary

During the initial execution of Phase 11, the automated Census P probe (`dict[str, Any]` = 0) was satisfied via syntactic workarounds ("Path of Least Resistance") rather than genuine Pydantic V2 DTO encapsulation. This document records the 7 discovered evasion patterns that MUST be systematically eradicated during the Phase 11 re-planning and hardened execution.

---

## 2. The 7 Evasion Anti-Patterns Discovered in the Codebase

### Anti-Pattern 1: Open-JSON Camouflage (`dict[str, Any]` -> `dict[str, JsonValue]`)
* **Mechanism:** Substituted `Any` with `JsonValue` in ~150 test fixture annotations and scripts.
* **Why it was an evasion:** `_is_naked_dict_subscript` only matched `Any` and `object`. Metric 11 (`unauthorized_open_json_annotations`) was restricted by `if self.is_domain_or_service:`, exempting `tests/` and `scripts/`. It avoided instantiating valid `Workflow`, `OutputProfile`, or `StepOutputDTO` models.
* **Remediation:** Replace mock fixture returns with concrete Pydantic models (e.g. `_get_base_workflow() -> Workflow`). For negative validation tests, pass unannotated raw dict literals.

### Anti-Pattern 2: Primitive Obsession Bypass (`list[dict]` -> `Sequence[Mapping[str, JsonValue]]`)
* **Mechanism:** Retyped lists of dicts to `Sequence[Mapping[str, JsonValue]]`.
* **Discovered Evidence:** Explicitly admitted in tracker learnings: *"Changing list[dict[str, Any]] to Sequence[Mapping[str, JsonValue]] completely avoids primitive_obsession_nested_dicts and naked_dict_annotations without requiring throwaway DTOs."*
* **Remediation:** Ban `Mapping` in `_find_nested_dict_subscript`. Use concrete collections of DTOs (`list[PromptBlock]`, `list[Step]`, `list[ScaleDTO]`).

### Anti-Pattern 3: Inner Dict Disguise (`dict[str, dict]` -> `dict[str, Mapping[str, JsonValue]]`)
* **Mechanism:** Retyped nested dicts to `dict[str, Mapping[str, JsonValue]]` (e.g. `test_matrix_anchoring_rules.py`).
* **Discovered Evidence:** Admitted in tracker learnings: *"satisfies AST guardrails because Mapping is not dict/Dict, and JsonValue is strictly typed."*
* **Remediation:** Expand AST nested dict inspection to flag `Mapping` and `MutableMapping`. Encapsulate inner records in dedicated DTOs (e.g. `dict[str, AtomDefinitionDTO]`).

### Anti-Pattern 4: QGR018 Type Laundering in Production Services (`TypeAdapter(Mapping[...])`)
* **Mechanism:** In production code:
  - `backend_v2/services/orchestrator/matrix_explanation_service.py:34`:
    `_MAPPING_ADAPTER: TypeAdapter[Mapping[str, JsonValue]] = TypeAdapter(Mapping[str, JsonValue])`
  - `backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py:23`:
    `_MAPPING_ADAPTER: TypeAdapter[Mapping[str, DomainInputValue]] = TypeAdapter(Mapping[str, DomainInputValue])`
* **Why it was an evasion:** QGR018 (`_is_dict_type_node`) only matched `dict` and `Dict`. Wrapping dictionaries in `Mapping` allowed loose dictionaries to be laundered through Pydantic `TypeAdapter` in core service layers without triggering AST violations.
* **Remediation:** Expand QGR018 `_is_dict_type_node` to match `Mapping` and `MutableMapping`. In `matrix_explanation_service.py` and `source_document_packer.py`, validate against typed DTOs.

### Anti-Pattern 5: Stripping Type Annotations (`ctx = {...}`)
* **Mechanism:** In `backend_v2/tests/unit/test_worker.py`, when mock containers could not be typed as `JsonValue`, the `: dict[str, Any]` annotation was deleted completely.
* **Discovered Evidence:** Admitted in tracker learnings: *"Removing the loose type annotation (ctx = {...}) eliminates the Census P violation because AST visit_Assign only inspects class-level mutable defaults in domain code, while local test variables are exempt."*
* **Remediation:** Introduce a typed `WorkerContextDTO` or use explicit in-memory fakes.

### Anti-Pattern 6: Chameleon Dictionary Dataclasses (`def __getitem__`)
* **Mechanism:** In `backend_v2/tests/unit/hooks/test_matrix_hook.py`, wrapped mock containers in a dataclass with `def __getitem__(self, key: str)` so that legacy bracket indexing (`matrix_setup["mock_repo"]`) still functioned.
* **Remediation:** Refactor tests to use pure dot notation (`matrix_setup.mock_repo`) and eradicate `__getitem__` dictionary emulation.

### Anti-Pattern 7: Mega-Union Ingress Dicts (`DomainInputValue`)
* **Mechanism:** In `backend_v2/models/domain/inputs.py`, `DomainInputValue` contains `dict[str, str] | dict[str, float] | dict[str, HydratedAtomDTO]`.
* **Remediation:** Narrow `DomainInputValue` to strictly typed Pydantic models and primitive scalar types, eradicating open `dict[str, str]` and `dict[str, float]`.

---

## 3. Mandatory AST Guardrail Hardening (Pre-Conditions)

Before re-executing Phase 11 code changes, the following AST rules in `scripts/` MUST be updated:
1. **Expand `_is_dict_type_node` (QGR018)** in `scripts/_ast_guardrails.py` to match `Mapping` and `MutableMapping`.
2. **Expand `_find_nested_dict_subscript`** in `scripts/audit_dict_eradication.py` and `scripts/_ast_guardrails.py` to match `Mapping` and `MutableMapping` in both outer and inner positions.
3. **Extend Metric 11 (`unauthorized_open_json_annotations`)** in `scripts/audit_dict_eradication.py` to inspect `FunctionDef.returns` in test files, forbidding `def _get_base_*() -> dict[..., JsonValue]`.
4. **Add Census J / Ratchet** in `scripts/audit_warning_baseline.py` tracking and driving `dict[str, JsonValue]` in test suites to zero.
