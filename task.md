# Task Tracker: Zero-Knowledge Dynamic Workflow Ingress & Anti-Collision Architecture

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
</required_context_rules>

Implementation Plan: @[c:\Users\risto\.gemini\antigravity-ide\brain\55b2db83-ab64-40e5-8528-71e365fbbcda\implementation_plan.md]

## Pre-Flight Checklist (<constraint> tags)
- [x] Phase 1, Step 1.1 (`zero_service_layer_fallbacks`): Eradicate inline duck-typing and dictionary scraping in `start_execution`.
- [x] Phase 1, Step 1.2 (`anti_ambiguity_mandate`): Eradicate hardcoded domain keywords from test runner `run_e2e_variance_test.py`.
- [x] Phase 2, Step 2.1 (`zero_naked_dicts_and_permissive_typing`): Encapsulate all transit state in strict Pydantic V2 `ResolvedIngressDTO`.
- [x] Phase 2, Step 2.2 (`ki_god_code_prevention`): Extract `SmartIngressResolver` into isolated service file under 200 lines.
- [x] Phase 2, Step 2.2 (`rfc7807_dual_reporting_mandate`): Precede all raised AppExceptions with structured `logger.error`.
- [x] Phase 2, Step 2.3 (`explicit_reexport_mandate`): Explicitly re-export `SmartIngressResolver` in `__all__`.
- [x] Phase 2, Step 2.4 (`anti_happy_path_mandate`): Include at least 3 negative test cases covering boundary values.
- [ ] Phase 3, Step 3.1 (`universal_fail_fast`): Fail-Fast if inputs are invalid or profile cannot be resolved.
- [ ] Phase 3, Step 3.2 (`quality_gate_execution`): Run backend audit loop on modified tests.
- [ ] Phase 4, Step 4.1 (`anti_ambiguity_mandate`): Zero domain keywords in test runner.
- [ ] Phase 4, Step 4.3 (`pep257_google_style_docstrings`): Header documentation accurately mirrors runtime parameters and CLI syntax.

## Execution Tasks

- [x] **Phase 1: Pre-Implementation Debt Cleanup**
  - [x] Step 1.1: Audit Execution Service Tech Debt (`backend_v2/services/execution.py#L384-L641`)
  - [x] Step 1.2: Audit Test Harness Tech Debt (`scripts/run_e2e_variance_test.py#L111-L215, #L577-L661`)

- [x] **Phase 2: Ingress DTO and Resolver Implementation**
  - [x] Step 2.1: Create `ResolvedIngressDTO` (`backend_v2/models/dtos/ingress.py`)
  - [x] Step 2.2: Implement `SmartIngressResolver` (`backend_v2/services/ingress/smart_ingress_resolver.py`)
  - [x] Step 2.3: Expose `SmartIngressResolver` in `backend_v2/services/ingress/__init__.py`
  - [x] Step 2.4: Unit Test `SmartIngressResolver` (`backend_v2/tests/unit/services/ingress/test_smart_ingress_resolver.py`)

- [ ] **Phase 3: Execution Service Integration**
  - [ ] Step 3.1: Integrate Resolver in `ExecutionService.start_execution` (`backend_v2/services/execution.py`)
  - [ ] Step 3.2: Unit Test Execution Service Integration (`backend_v2/tests/unit/services/test_execution.py`)

- [ ] **Phase 4: Test Harness Zero-Knowledge Decoupling**
  - [ ] Step 4.1: Decouple `load_inputs_from_path` (`scripts/run_e2e_variance_test.py#L111-L215`)
  - [ ] Step 4.2: Decouple `trigger_execution` and `run_variance_test` (`scripts/run_e2e_variance_test.py#L577-L914`)
  - [ ] Step 4.3: Modernize Header Docstring and CLI Examples (`scripts/run_e2e_variance_test.py#L1-L38`)

- [ ] **Phase 5: Verification and Quality Gates**
  - [ ] Step 5.1: Run Backend Audit Gate (`backend_v2/services/execution.py`)
  - [ ] Step 5.2: Run Smart Ingress Resolver Audit (`backend_v2/services/ingress/smart_ingress_resolver.py`)
