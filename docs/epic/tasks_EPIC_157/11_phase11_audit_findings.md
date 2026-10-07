# Architectural Audit Findings: Dict Eradication Anti-Patterns in Phase 11

**Document ID:** `11_phase11_audit_findings`  
**Target Epic:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]  
**Target Plan:** @[docs/epic/tasks_EPIC_157/11_phase11_plan.md]  
**Target Tracker:** @[docs/epic/EPIC_157_tracker.md]  
**Status:** MANDATORY HARDENING DIRECTIVE  
**Date:** 2026-10-07  

---

## 1. Executive Summary

During the initial execution of Phase 11, the automated Census P probe (`dict[str, Any]` = 0) was satisfied via syntactic workarounds ("Path of Least Resistance") rather than genuine Pydantic V2 DTO encapsulation. This document records the 12 discovered evasion and fallback patterns that MUST be systematically eradicated during the Phase 11 re-planning and hardened execution.

---

## 2. The 12 Evasion Anti-Patterns Discovered in the Codebase

### Anti-Pattern 1: Open-JSON Camouflage (`dict[str, Any]` -> `dict[str, JsonValue]`)
* **Mechanism:** Substituted `Any` with `JsonValue` in ~150 test fixture annotations and scripts.
* **Why it was an evasion:** `_is_naked_dict_subscript` only matched `Any` and `object`. Metric 11 (`unauthorized_open_json_annotations`) was restricted by `if self.is_domain_or_service:`, exempting `tests/` and `scripts/`. It avoided instantiating valid `Workflow`, `OutputProfile`, or `StepOutputDTO` models.
* **Remediation:** Replace mock fixture returns with concrete Pydantic models (specifically: `def _get_base_workflow() -> Workflow`). For negative validation tests, pass unannotated raw dict literals.

### Anti-Pattern 2: Primitive Obsession Bypass (`list[dict]` -> `Sequence[Mapping[str, JsonValue]]`)
* **Mechanism:** Retyped lists of dicts to `Sequence[Mapping[str, JsonValue]]`.
* **Discovered Evidence:** Explicitly admitted in tracker learnings: *"Changing list[dict[str, Any]] to Sequence[Mapping[str, JsonValue]] completely avoids primitive_obsession_nested_dicts and naked_dict_annotations without requiring throwaway DTOs."*
* **Remediation:** Ban `Mapping` in `_find_nested_dict_subscript`. Use concrete collections of DTOs (`list[PromptBlock]`, `list[Step]`, `list[ScaleDTO]`).

### Anti-Pattern 3: Inner Dict Disguise (`dict[str, dict]` -> `dict[str, Mapping[str, JsonValue]]`)
* **Mechanism:** Retyped nested dicts to `dict[str, Mapping[str, JsonValue]]` (specifically in `test_matrix_anchoring_rules.py`).
* **Discovered Evidence:** Admitted in tracker learnings: *"satisfies AST guardrails because Mapping is not dict/Dict, and JsonValue is strictly typed."*
* **Remediation:** Expand AST nested dict inspection to flag `Mapping` and `MutableMapping`. Encapsulate inner records in dedicated DTOs (specifically: `dict[str, AtomDefinitionDTO]`).

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
* **Remediation:** Introduce typed Pydantic models or use explicit in-memory fakes.

### Anti-Pattern 6: Chameleon Dictionary Dataclasses (`def __getitem__`)
* **Mechanism:** In `backend_v2/tests/unit/hooks/test_matrix_hook.py`, wrapped mock containers in a dataclass with `def __getitem__(self, key: str)` so that legacy bracket indexing (`matrix_setup["mock_repo"]`) still functioned.
* **Remediation:** Refactor tests to use pure dot notation (`matrix_setup.mock_repo`) and eradicate `__getitem__` dictionary emulation.

### Anti-Pattern 7: Mega-Union Ingress Dicts (`DomainInputValue`)
* **Mechanism:** In `backend_v2/models/domain/inputs.py`, `DomainInputValue` contains `dict[str, str] | dict[str, float] | dict[str, HydratedAtomDTO]`.
* **Remediation:** Narrow `DomainInputValue` to strictly typed Pydantic models and primitive scalar types, eradicating open `dict[str, str]` and `dict[str, float]`.

### Anti-Pattern 8: Raw `object` or `Any` Assigned Dict Literals (`: Any = {` / `: object = {`)
* **Mechanism:** Annotating variable targets as `Any` or `object` while assigning dictionary literals directly, evading `_is_naked_dict_subscript` because the AST annotation node lacks a subscript.
* **Discovered Evidence:** `backend_v2/llm/client.py:102` (`adapter_schema: Any = {"type": "json_schema"}`), `backend_v2/tests/unit/services/test_blueprint.py:1807` (`workflow_steps: Any = {`), and line 1815 (`mcp_audit_map: Any = {...}`).
* **Remediation:** Retype `adapter_schema` to `dict[str, JsonValue]` in `client.py` and replace test mock dictionaries with validated Pydantic models (`dict[str, StepRule]`, `dict[str, MCPAuditTrace]`).

### Anti-Pattern 9: Anonymous Tuple State Packing ("Tuple Hell")
* **Mechanism:** Packing multi-value states or key-value structures into anonymous tuples (specifically `tuple[dict, dict]` or `list[tuple[str, object]]`) to avoid explicit dictionary syntax while retaining loose associative access.
* **Remediation:** Enforce rule `ban_anonymous_state_tuples` repo-wide. Multi-value state transitions must be encapsulated in dedicated immutable Pydantic V2 DTOs (`ConfigDict(strict=True, extra="forbid", frozen=True)`).

### Anti-Pattern 10: Dynamic `json.loads` Deserialization Bypassing Schemas
* **Mechanism:** Calling `json.loads(raw_text)` in execution paths or legacy helper pipelines, followed by manual dictionary subscription or `cast(dict[str, JsonValue])`, evading Pydantic schema validation.
* **Discovered Evidence:** `backend_v2/llm/ingress_pipeline.py:394` (`cast(dict[str, JsonValue], json.loads(raw_stripped))`) and dead `UniversalIngress` import in `backend_v2/llm/client.py:23`.
* **Remediation:** Purge dead `UniversalIngress` import from `client.py` and enforce native Pydantic V2 Structured Outputs (`run_structured_task`) without manual syntactic repair fallbacks.

### Anti-Pattern 11: `SimpleNamespace` Chameleon Container Mocks
* **Mechanism:** Importing `types.SimpleNamespace` in test suites to construct unvalidated mock objects with arbitrary attributes, evading Pydantic DTO contracts while mimicking object attribute access (`obj.attr`).
* **Discovered Evidence:** `backend_v2/tests/unit/services/test_blueprint.py` across 10 sites (lines 1713, 1724, 1735, 1808, 1815, 1919, 1926, 1948, 2366, 2892).
* **Remediation:** Eradicate all `SimpleNamespace` imports and usages repo-wide. Instantiate valid Pydantic models (`Workflow`, `StepRule`, `StepOutputDTO`, `MCPAuditTrace`) with required attributes.

### Anti-Pattern 12: `model_construct()` Validation Bypassing in Fixtures
* **Mechanism:** Using `Model.model_construct(...)` in test fixtures instead of `Model(...)` or `Model.model_validate(...)`, bypassing schema validation and allowing malformed dictionaries or mismatched types to bypass testing gates.
* **Remediation:** Ensure test fixture factories construct valid domain models through full Pydantic validation (`model_validate`), ensuring test suites exercise real validation invariants.

---

## 3. Mandatory AST Guardrail Hardening (Pre-Conditions)

Before re-executing Phase 11 code changes, the following AST rules in `scripts/` MUST be updated:
1. **Expand `_is_dict_type_node` (QGR018)** in `scripts/_ast_guardrails.py` to match `Mapping` and `MutableMapping`.
2. **Expand `_find_nested_dict_subscript`** in `scripts/audit_dict_eradication.py` and `scripts/_ast_guardrails.py` to match `Mapping` and `MutableMapping` in both outer and inner positions.
3. **Extend Metric 11 (`unauthorized_open_json_annotations`)** in `scripts/audit_dict_eradication.py` to inspect `FunctionDef.returns` and `AsyncFunctionDef.returns` in test files, forbidding `def _get_base_*() -> dict[..., JsonValue]`.
4. **Audit and Eradicate Anti-Patterns 8-12**:
   - Retype `adapter_schema` in `backend_v2/llm/client.py` and purge dead `UniversalIngress` import.
   - Eradicate `SimpleNamespace` and `: Any = {` from `backend_v2/tests/unit/services/test_blueprint.py`.
5. **Verify Monotonic Ceilings**: Ensure Census P=0, Census M=0, and verify zero unauthorized open-JSON annotations across production and test suites.

