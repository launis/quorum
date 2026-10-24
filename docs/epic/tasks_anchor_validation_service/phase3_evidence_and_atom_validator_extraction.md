<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
</required_context_rules>

# Phase 3: Evidence Validator & Atom Evaluation Processor Extraction (`phase3_evidence_and_atom_validator_extraction.md`)

## 1. Objective
Execute Phase 3 of the Two-Epoch Strangler Fig decomposition for `@[backend_v2/services/orchestrator/anchor_validation_service.py#L32-L855]`:
1. Extract `AnchorValidationService.validate_evidence` (`@[backend_v2/services/orchestrator/anchor_validation_service.py#L427-L740]`) into `[NEW] @[backend_v2/services/orchestrator/anchor_validation/evidence_validator.py]` (~330 lines).
2. Extract `AnchorValidationService.process_atom_evaluation` (`@[backend_v2/services/orchestrator/anchor_validation_service.py#L742-L855]`) into `[NEW] @[backend_v2/services/orchestrator/anchor_validation/atom_evaluation_processor.py]` (~130 lines), promoting `from backend_v2.utils.alias_engine import AliasEngine` to a top-level import to satisfy `inline_imports_ban` (`QGR009`).
3. Retain 1-line delegations in `AnchorValidationService.validate_evidence` and `AnchorValidationService.process_atom_evaluation` inside `@[backend_v2/services/orchestrator/anchor_validation_service.py#L32-L855]` so all existing callers and unit tests pass 100% unchanged.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/services/orchestrator/anchor_validation/evidence_validator.py]` | Forensic evidence validator (`validate_evidence`) enforcing reasoning trace contradiction gates, syntactic anchor verification, speaker provenance (`TargetSpeaker`), and physical quote slicing |
| `[NEW]` | `[NEW] @[backend_v2/services/orchestrator/anchor_validation/atom_evaluation_processor.py]` | Atom evaluation post-processor (`process_atom_evaluation`) validating `AtomDefinitionDTO`, `AssertionEvaluationDTO`, and `AtomResultDTO` quotes across `SourceDocumentContext` and `mcp_source_texts` and hydrating aliases via `AliasEngine` |
| `[MODIFY]` | `@[backend_v2/services/orchestrator/anchor_validation_service.py#L32-L855]` | Delegate `validate_evidence` (`#L427-L740`) and `process_atom_evaluation` (`#L742-L855`) to the new sub-modules with explicit redundant re-exports |

## 3. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Create Evidence Validator and Atom Evaluation Processor Sub-Modules">
    <constraint invariant="topological_leaf_first_extraction_mandate">Neither evidence_validator.py nor atom_evaluation_processor.py may exceed 350 lines or import from anchor_validation_service.py.</constraint>
    <constraint invariant="inline_imports_ban">Declare AliasEngine at the top level of atom_evaluation_processor.py rather than inside process_atom_evaluation.</constraint>
    <action>
      1. Create `[NEW] @[backend_v2/services/orchestrator/anchor_validation/evidence_validator.py]` (~330 lines, all lines `<= 120` chars) with `__all__ = ["validate_evidence"]`:
         - Import `normalize_text_with_mapping` from `backend_v2.services.orchestrator.anchor_validation.lexical_normalizer` and `is_lexically_valid` from `backend_v2.services.orchestrator.anchor_validation.lexical_matcher`.
         - Import `SemanticEvidenceError` from `backend_v2.exceptions`, `QuoteEvidenceDTO`, `SourceDocumentContext` from `backend_v2.models.dtos.quote_evidence`, and `TargetSpeaker`, `VerificationState` from `backend_v2.models.enums`.
         - Relocate `validate_evidence` verbatim from `@[backend_v2/services/orchestrator/anchor_validation_service.py#L427-L740]`, calling `normalize_text_with_mapping` and `is_lexically_valid` directly.
      2. Create `[NEW] @[backend_v2/services/orchestrator/anchor_validation/atom_evaluation_processor.py]` (~130 lines, all lines `<= 120` chars) with `__all__ = ["process_atom_evaluation"]`:
         - Import `is_lexically_valid` from `backend_v2.services.orchestrator.anchor_validation.lexical_matcher` and `AliasEngine` from `backend_v2.utils.alias_engine` at top level.
         - Import `AtomResultDTO` from `backend_v2.models.dtos.atom_result`, `SourceDocumentContext` from `backend_v2.models.dtos.quote_evidence`, `AssertionEvaluationDTO`, `AtomDefinitionDTO` from `backend_v2.models.dtos.sensor`, and `EvaluationStatus`, `ExecutionStatus` from `backend_v2.models.enums`.
         - Relocate `process_atom_evaluation` verbatim from `@[backend_v2/services/orchestrator/anchor_validation_service.py#L742-L855]`, calling `is_lexically_valid` directly.
    </action>
  </step>

  <step id="2" name="Wire Proxy Delegations in AnchorValidationService">
    <constraint invariant="explicit_reexport_mandate">Re-export validate_evidence and process_atom_evaluation in anchor_validation_service.py using explicit redundant aliases.</constraint>
    <action>
      1. Update `@[backend_v2/services/orchestrator/anchor_validation_service.py#L32-L855]` to import:
         - `from backend_v2.services.orchestrator.anchor_validation.evidence_validator import validate_evidence as validate_evidence`
         - `from backend_v2.services.orchestrator.anchor_validation.atom_evaluation_processor import process_atom_evaluation as process_atom_evaluation`
      2. Replace the bodies of `AnchorValidationService.validate_evidence` (`@[backend_v2/services/orchestrator/anchor_validation_service.py#L427-L740]`) and `AnchorValidationService.process_atom_evaluation` (`@[backend_v2/services/orchestrator/anchor_validation_service.py#L742-L855]`) with 1-line delegations to `validate_evidence(...)` and `process_atom_evaluation(...)`.
    </action>
  </step>

  <step id="3" name="Run Phase 3 Verification and Quality Gate">
    <constraint invariant="zero_tolerance_audit_loop">Run backend_audit_loop.py with --test --ast-strict on both new sub-modules and the proxy monolith.</constraint>
    <action>
      1. Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation/evidence_validator.py --test --ast-strict`, `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation/atom_evaluation_processor.py --test --ast-strict`, and `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation_service.py --test --ast-strict`.
      2. Execute `uv run pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_atom_result.py` and `uv run pytest backend_v2/tests/integration/test_multi_segment_causal_e2e.py` to confirm 100% behavioral parity.
    </action>
  </step>

  <test_contracts>
    <contract type="regression" name="test_process_atom_evaluation_with_atom_result_dto">
      Verifies that process_atom_evaluation validates AtomResultDTO quotes against SourceDocumentContext and hydrates document aliases via AliasEngine.
    </contract>
    <contract type="positive" name="test_multi_segment_causal_e2e_dag_execution">
      Verifies that validate_evidence anchors multi-segment quotes across multi-document contexts and returns physical slices.
    </contract>
    <contract type="negative" name="test_anchor_validation_provenance_user_rejects_ai_text">
      Verifies that validate_evidence raises SemanticEvidenceError with PROVENANCE_VIOLATION when a USER-scoped claim quotes AI draft context.
    </contract>
  </test_contracts>
</execution_protocol>
```
