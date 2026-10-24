<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
</required_context_rules>

# Phase 4: Consumer Import Rewiring, Test Modularization, Atomic Package Cutover & QGR017 Lockdown (`phase4_package_cutover_and_guardrails.md`)

## 1. Objective
Execute the final Epoch 1 Cutover of the `AnchorValidationService` decomposition:
1. Split the monolithic unit test files `[DELETE] @[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py]` (998 lines, 53 tests) and `[DELETE] @[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_atom_result.py]` (145 lines, 6 tests) into five modular unit test suites (`< 450` lines each) under `backend_v2/tests/unit/services/orchestrator/anchor_validation/`:
   - `[NEW] @[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_lexical_normalizer.py]`
   - `[NEW] @[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_lexical_matcher.py]`
   - `[NEW] @[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_evidence_validator.py]`
   - `[NEW] @[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_atom_evaluation_processor.py]`
   - `[NEW] @[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_anchor_validation_facade.py]`
2. Atomically replace `[DELETE] @[backend_v2/services/orchestrator/anchor_validation_service.py]` with the domain package facade `[NEW] @[backend_v2/services/orchestrator/anchor_validation/__init__.py]` (`< 150` lines) and rewire all 1-hop consumer imports across production backend services, CLI scripts, and test suites to import from `backend_v2.services.orchestrator.anchor_validation`.
3. Register the retired module `backend_v2.services.orchestrator.anchor_validation_service` in `@[scripts/_ast_guardrails.py#L1865-L1923]` (`visit_Import`) and `@[scripts/_ast_guardrails.py#L1925-L2047]` (`visit_ImportFrom`) under `QGR017`, and synchronize `@[.agents/rules/04_directory_reference.md]`.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/services/orchestrator/anchor_validation/__init__.py]` | Canonical package facade (`< 150` lines) exporting `AnchorValidationService`, constants, and sub-module functions with explicit `__all__` and redundant aliases |
| `[DELETE]` | `[DELETE] @[backend_v2/services/orchestrator/anchor_validation_service.py]` | Delete legacy monolith/proxy file atomically when creating `[NEW] @[backend_v2/services/orchestrator/anchor_validation/__init__.py]` |
| `[MODIFY]` | `@[backend_v2/services/orchestrator/extractive_sensor_service.py#L176-L761]` | Rewire `AnchorValidationService` import (line 48, used in `_fuzzy_match` `@[backend_v2/services/orchestrator/extractive_sensor_service.py#L182-L207]`) to `backend_v2.services.orchestrator.anchor_validation` |
| `[MODIFY]` | `@[backend_v2/services/mcp/mcp_tool_loop.py#L150-L476]` | Rewire `AnchorValidationService` import (line 40, used in `execute_mcp_retrieval` `@[backend_v2/services/mcp/mcp_tool_loop.py#L150-L476]`) to `backend_v2.services.orchestrator.anchor_validation` |
| `[MODIFY]` | `@[backend_v2/hooks/integrity.py#L118-L138]` | Rewire `AnchorValidationService` import (line 25, used in `_is_hallucinated` `@[backend_v2/hooks/integrity.py#L118-L138]` and `verify_citation_integrity_hook` `@[backend_v2/hooks/integrity.py#L213-L304]`) to `backend_v2.services.orchestrator.anchor_validation` |
| `[MODIFY]` | `@[scripts/ablation_live_executor.py#L624-L1089]` | Rewire `AnchorValidationService` import (line 36, used in `_validate_quote_lexically` `@[scripts/ablation_live_executor.py#L710-L761]`) to `backend_v2.services.orchestrator.anchor_validation` |
| `[MODIFY]` | `@[scripts/audit_manifest_generator.py#L233-L331]` | Rewire `AnchorValidationService` import in `load_physical_execution_items` (`@[scripts/audit_manifest_generator.py#L233-L331]`) to `backend_v2.services.orchestrator.anchor_validation` |
| `[MODIFY]` | `@[scripts/run_ablation_benchmark.py#L490-L1143]` | Rewire `AnchorValidationService` import (line 57, used in `evaluate_atom_with_config` `@[scripts/run_ablation_benchmark.py#L678-L811]`) to `backend_v2.services.orchestrator.anchor_validation` |
| `[MODIFY]` | `@[scripts/run_e2e_variance_test.py#L955-L1065]` | Rewire `AnchorValidationService` import (line 111, used in `validate_execution_kelvollisuus` `@[scripts/run_e2e_variance_test.py#L955-L1065]`) to `backend_v2.services.orchestrator.anchor_validation` |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/test_multi_segment_quote_foundation.py#L129-L142]` | Rewire `AnchorValidationService` import (line 13, used by `test_anchor_validation_symmetric_index_resolution_exact` `#L129-L142` and `test_anchor_validation_symmetric_index_resolution_fuzzy` `#L145-L159`) to `backend_v2.services.orchestrator.anchor_validation` |
| `[MODIFY]` | `@[backend_v2/tests/unit/hooks/test_integrity.py#L379-L385]` | Update `patch` target in `test_is_hallucinated_empty_normalized` (`@[backend_v2/tests/unit/hooks/test_integrity.py#L379-L385]`) to `"backend_v2.services.orchestrator.anchor_validation.AnchorValidationService.normalize_text_with_mapping"` |
| `[MODIFY]` | `@[backend_v2/tests/integration/test_multi_segment_causal_e2e.py#L52-L76]` | Rewire `AnchorValidationService` import (line 28, used by `#L52-L76`, `#L155-L181`, and `#L281-L303`) to `backend_v2.services.orchestrator.anchor_validation` |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_lexical_normalizer.py]` | Unit tests for `lexical_normalizer.py` (`normalize_text_with_mapping`, `strict_match`, `calculate_fuzzy_score`) |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_lexical_matcher.py]` | Unit tests for `lexical_matcher.py` (`is_lexically_valid` across Gate 0, Gate 1, Gate 2, and Gate 3) |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_evidence_validator.py]` | Unit tests for `evidence_validator.py` (`validate_evidence` provenance, syntactic anchors, and multi-document slicing) |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_atom_evaluation_processor.py]` | Unit tests for `atom_evaluation_processor.py` (`process_atom_evaluation` across `AtomResultDTO`, `AtomDefinitionDTO`, and `AssertionEvaluationDTO`) |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_anchor_validation_facade.py]` | Unit tests for `AnchorValidationService` package facade (`__init__.py`) |
| `[DELETE]` | `[DELETE] @[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py]` | Delete monolithic 998-line test file after migrating all 53 tests into the modular test suite |
| `[DELETE]` | `[DELETE] @[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_atom_result.py]` | Delete legacy 145-line atom result test file after migrating all 6 tests into `test_atom_evaluation_processor.py` |
| `[MODIFY]` | `@[scripts/_ast_guardrails.py#L1865-L1923]` | Add `backend_v2.services.orchestrator.anchor_validation_service` to `QGR017` banned imports in `visit_Import` |
| `[MODIFY]` | `@[scripts/_ast_guardrails.py#L1925-L2047]` | Add `backend_v2.services.orchestrator.anchor_validation_service` to `QGR017` banned imports in `visit_ImportFrom` |
| `[MODIFY]` | `@[.agents/rules/04_directory_reference.md]` | Update Pillar 6 (`backend_v2/services/`) directory reference from `anchor_validation_service.py` to `anchor_validation/` |

## 3. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Modularize Unit Test Suite under anchor_validation/">
    <constraint invariant="test_directory_isolation">All unit tests for backend_v2/services/orchestrator/anchor_validation/ MUST reside under backend_v2/tests/unit/services/orchestrator/anchor_validation/ with < 450 lines per test file.</constraint>
    <action>
      1. Split all 53 unit tests from `[DELETE] @[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py]` and all 6 unit tests from `[DELETE] @[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_atom_result.py]` into five modular test files (`< 450` lines each):
         - `[NEW] @[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_lexical_normalizer.py]`
         - `[NEW] @[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_lexical_matcher.py]`
         - `[NEW] @[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_evidence_validator.py]`
         - `[NEW] @[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_atom_evaluation_processor.py]`
         - `[NEW] @[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_anchor_validation_facade.py]`
      2. Delete `[DELETE] @[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py]` and `[DELETE] @[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_atom_result.py]`.
    </action>
  </step>

  <step id="2" name="Execute Atomic Package Cutover and Rewire 1-Hop Callers">
    <constraint invariant="strangler_fig_mandate">Delete backend_v2/services/orchestrator/anchor_validation_service.py and create backend_v2/services/orchestrator/anchor_validation/__init__.py in a single atomic step.</constraint>
    <constraint invariant="explicit_reexport_mandate">Declare __all__ and explicit redundant import aliases (from module import Symbol as Symbol) in backend_v2/services/orchestrator/anchor_validation/__init__.py.</constraint>
    <action>
      1. Create `[NEW] @[backend_v2/services/orchestrator/anchor_validation/__init__.py]` (`< 150` lines) containing `AnchorValidationService` (delegating `normalize_text_with_mapping`, `strict_match`, `calculate_fuzzy_score`, `_is_lexically_valid`, `validate_evidence`, and `process_atom_evaluation`) and explicit redundant re-exports with `__all__ = ["AnchorValidationService", "MAX_CITATION_SPAN_CHARS", "MIN_ENTROPY_GATE_CHARS", "MIN_MULTI_SEGMENT_FLOOR_CHARS", "calculate_fuzzy_score", "is_lexically_valid", "normalize_text_with_mapping", "process_atom_evaluation", "strict_match", "validate_evidence"]`.
      2. Physically delete `[DELETE] @[backend_v2/services/orchestrator/anchor_validation_service.py]`.
      3. Rewire all 1-hop production, script, and test callers to import `AnchorValidationService` from `backend_v2.services.orchestrator.anchor_validation`:
         - `@[backend_v2/services/orchestrator/extractive_sensor_service.py#L176-L761]` (`_fuzzy_match` `@[backend_v2/services/orchestrator/extractive_sensor_service.py#L182-L207]`)
         - `@[backend_v2/services/mcp/mcp_tool_loop.py#L150-L476]` (`execute_mcp_retrieval`)
         - `@[backend_v2/hooks/integrity.py#L118-L138]` (`_is_hallucinated` and `verify_citation_integrity_hook` `@[backend_v2/hooks/integrity.py#L213-L304]`)
         - `@[scripts/ablation_live_executor.py#L624-L1089]` (`_validate_quote_lexically` `@[scripts/ablation_live_executor.py#L710-L761]`)
         - `@[scripts/audit_manifest_generator.py#L233-L331]` (`load_physical_execution_items`)
         - `@[scripts/run_ablation_benchmark.py#L490-L1143]` (`evaluate_atom_with_config` `@[scripts/run_ablation_benchmark.py#L678-L811]`)
         - `@[scripts/run_e2e_variance_test.py#L955-L1065]` (`validate_execution_kelvollisuus`)
         - `@[backend_v2/tests/unit/services/orchestrator/test_multi_segment_quote_foundation.py#L129-L142]` and `@[backend_v2/tests/unit/services/orchestrator/test_multi_segment_quote_foundation.py#L145-L159]`
         - `@[backend_v2/tests/unit/hooks/test_integrity.py#L379-L385]` (`test_is_hallucinated_empty_normalized` patch path)
         - `@[backend_v2/tests/integration/test_multi_segment_causal_e2e.py#L52-L76]`, `@[backend_v2/tests/integration/test_multi_segment_causal_e2e.py#L155-L181]`, and `@[backend_v2/tests/integration/test_multi_segment_causal_e2e.py#L281-L303]`
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation/ --test --ast-strict`, `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/extractive_sensor_service.py --test --ast-strict`, `uv run python scripts/backend_audit_loop.py backend_v2/services/mcp/mcp_tool_loop.py --test --ast-strict`, and `uv run python scripts/backend_audit_loop.py backend_v2/hooks/integrity.py --test --ast-strict`.</verification>
  </step>

  <step id="3" name="Lock Retired Path in QGR017 AST Guardrails and Synchronize Directory Reference">
    <constraint invariant="ast_guardrail_mandate">Retired monolith paths MUST be permanently banned under QGR017 in scripts/_ast_guardrails.py.</constraint>
    <action>
      1. Modify `@[scripts/_ast_guardrails.py#L1865-L1923]` (`visit_Import`) and `@[scripts/_ast_guardrails.py#L1925-L2047]` (`visit_ImportFrom`) to ban imports of `backend_v2.services.orchestrator.anchor_validation_service` and `from backend_v2.services.orchestrator import anchor_validation_service` under `QGR017`, instructing callers to import from `backend_v2.services.orchestrator.anchor_validation`.
      2. Modify `@[.agents/rules/04_directory_reference.md]` under Pillar 6 (`backend_v2/services/`) to replace `anchor_validation_service.py` with `anchor_validation/ (lexical_normalizer.py, lexical_matcher.py, evidence_validator.py, atom_evaluation_processor.py, __init__.py facade)`.
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation/ --test --ast-strict`, `uv run pytest backend_v2/tests/integration/test_multi_segment_causal_e2e.py`, and `uv run python backend_v2/seed/run_seed.py local`.</verification>
  </step>

  <test_contracts>
    <contract type="regression" name="test_anchor_validation_facade_full_parity">
      Verifies that importing AnchorValidationService from backend_v2.services.orchestrator.anchor_validation preserves 100% identical outputs across all 6 static methods.
    </contract>
    <contract type="positive" name="test_is_hallucinated_empty_normalized">
      Verifies that 1-hop caller backend_v2/hooks/integrity.py resolves AnchorValidationService from backend_v2.services.orchestrator.anchor_validation.
    </contract>
    <contract type="negative" name="test_qgr017_bans_legacy_anchor_validation_service_import">
      Verifies that AST guardrail QGR017 flags any import from backend_v2.services.orchestrator.anchor_validation_service.
    </contract>
  </test_contracts>
</execution_protocol>
```
