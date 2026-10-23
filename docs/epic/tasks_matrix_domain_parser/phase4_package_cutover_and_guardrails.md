<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
</required_context_rules>

# Phase 4: Consumer Import Rewiring, Test Modularization, Atomic Package Cutover & QGR017 Lockdown (`phase4_package_cutover_and_guardrails.md`)

## 1. Objective
Execute the final Epoch 1 Cutover of the `MatrixDomainParser` decomposition:
1. Split the monolithic 1,297-line unit test file `[DELETE] @[backend_v2/tests/unit/services/test_matrix_domain_parser.py]` into four modular unit test suites under `backend_v2/tests/unit/services/matrix_parser/`: `[NEW] @[backend_v2/tests/unit/services/matrix_parser/test_distribution_formatter.py]`, `[NEW] @[backend_v2/tests/unit/services/matrix_parser/test_scale_and_atom_stage.py]`, `[NEW] @[backend_v2/tests/unit/services/matrix_parser/test_row_builder_stage.py]`, and `[NEW] @[backend_v2/tests/unit/services/matrix_parser/test_matrix_parser_facade.py]`.
2. Atomically replace `[DELETE] @[backend_v2/services/matrix_domain_parser.py]` with the domain package facade `[NEW] @[backend_v2/services/matrix_parser/__init__.py]` (`< 150` lines) and rewire all 1-hop consumer imports (`@[backend_v2/services/blueprint.py#L65-L669]`, `@[backend_v2/tests/unit/services/test_blueprint.py#L3302-L3397]`, `@[backend_v2/tests/unit/services/orchestrator/test_tier4_matrix_distribution_regression.py#L81-L160]`) to import `MatrixDomainParser` from `backend_v2.services.matrix_parser`.
3. Register the retired module `backend_v2.services.matrix_domain_parser` in `@[scripts/_ast_guardrails.py#L1865-L1897]` (`visit_Import`) and `@[scripts/_ast_guardrails.py#L1899-L1977]` (`visit_ImportFrom`) under `QGR017`, and synchronize `@[.agents/rules/04_directory_reference.md]`.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/services/matrix_parser/__init__.py]` | Canonical package facade (`< 150` lines) exporting `MatrixDomainParser` and stage functions with explicit `__all__` and redundant aliases |
| `[DELETE]` | `[DELETE] @[backend_v2/services/matrix_domain_parser.py]` | Delete legacy monolith/proxy file atomically when creating `[NEW] @[backend_v2/services/matrix_parser/__init__.py]` |
| `[MODIFY]` | `@[backend_v2/services/blueprint.py#L65-L669]` | Rewire 1-hop consumer import in `BlueprintTransformer` (`@[backend_v2/services/blueprint.py#L65-L669]` and `build_report_dto` `@[backend_v2/services/blueprint.py#L126-L669]`) from `backend_v2.services.matrix_domain_parser` to `backend_v2.services.matrix_parser` |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/test_blueprint.py#L3302-L3397]` | Rewire `MatrixDomainParser` imports (line 138 and inside `test_matrix_domain_parser_accepts_matrix_payload_with_atom_quotes` `@[backend_v2/tests/unit/services/test_blueprint.py#L3302-L3397]`) to `backend_v2.services.matrix_parser` |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/test_tier4_matrix_distribution_regression.py#L81-L160]` | Rewire `MatrixDomainParser` import (line 41, used by `@[backend_v2/tests/unit/services/orchestrator/test_tier4_matrix_distribution_regression.py#L81-L160]`) to `backend_v2.services.matrix_parser` |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/matrix_parser/test_distribution_formatter.py]` | Unit tests for `distribution_formatter.py` (`format_level_distribution`, `clean_hallucinated_numbers`, `format_level_breakdown`, `resolve_row_explanation`) |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/matrix_parser/test_scale_and_atom_stage.py]` | Unit tests for `scale_and_atom_stage.py` (`unpack_matrix_payload`, `compute_scale_and_score_projection`, `hydrate_step_scorecard_atoms`) |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/matrix_parser/test_row_builder_stage.py]` | Unit tests for `row_builder_stage.py` (`resolve_unique_axis_name`, `resolve_axis_description`, `resolve_context_target`, `build_matrix_scorecard_row`) |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/matrix_parser/test_matrix_parser_facade.py]` | End-to-end unit tests for `MatrixDomainParser` package facade (`__init__.py`) |
| `[DELETE]` | `[DELETE] @[backend_v2/tests/unit/services/test_matrix_domain_parser.py]` | Delete monolithic 1,297-line test file after migrating all 34 tests into the 4 modular test files |
| `[MODIFY]` | `@[scripts/_ast_guardrails.py#L1865-L1897]` | Add `backend_v2.services.matrix_domain_parser` to `QGR017` banned imports in `visit_Import` |
| `[MODIFY]` | `@[scripts/_ast_guardrails.py#L1899-L1977]` | Add `backend_v2.services.matrix_domain_parser` to `QGR017` banned imports in `visit_ImportFrom` |
| `[MODIFY]` | `@[.agents/rules/04_directory_reference.md]` | Update Pillar 6 (`backend_v2/services/`) directory reference from `matrix_domain_parser.py` to `matrix_parser/` |

## 3. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Modularize Unit Test Suite and Rewire 1-Hop Consumer Imports">
    <constraint invariant="test_directory_isolation">All unit tests for backend_v2/services/matrix_parser/ MUST reside under backend_v2/tests/unit/services/matrix_parser/ with < 500 lines per test file.</constraint>
    <action>
      1. Split all 34 unit tests from `[DELETE] @[backend_v2/tests/unit/services/test_matrix_domain_parser.py]` into four modular test files (< 450 lines each):
         - `[NEW] @[backend_v2/tests/unit/services/matrix_parser/test_distribution_formatter.py]`
         - `[NEW] @[backend_v2/tests/unit/services/matrix_parser/test_scale_and_atom_stage.py]`
         - `[NEW] @[backend_v2/tests/unit/services/matrix_parser/test_row_builder_stage.py]`
         - `[NEW] @[backend_v2/tests/unit/services/matrix_parser/test_matrix_parser_facade.py]`
      2. Delete `[DELETE] @[backend_v2/tests/unit/services/test_matrix_domain_parser.py]`.
    </action>
  </step>

  <step id="2" name="Execute Atomic Package Cutover and Rewire 1-Hop Callers">
    <constraint invariant="strangler_fig_mandate">Delete backend_v2/services/matrix_domain_parser.py and create backend_v2/services/matrix_parser/__init__.py in a single atomic operation so Python and MyPy never see duplicate module names.</constraint>
    <constraint invariant="explicit_reexport_mandate">Declare __all__ and explicit redundant import aliases (from module import Symbol as Symbol) in backend_v2/services/matrix_parser/__init__.py.</constraint>
    <action>
      1. Create `[NEW] @[backend_v2/services/matrix_parser/__init__.py]` (< 150 lines) containing `MatrixDomainParser` and explicit redundant re-exports of stage functions with `__all__ = ["MatrixDomainParser", "build_matrix_scorecard_row", "clean_hallucinated_numbers", "compute_scale_and_score_projection", "format_level_breakdown", "format_level_distribution", "hydrate_step_scorecard_atoms", "resolve_axis_description", "resolve_context_target", "resolve_row_explanation", "resolve_unique_axis_name", "unpack_matrix_payload"]`.
      2. Physically delete `[DELETE] @[backend_v2/services/matrix_domain_parser.py]`.
      3. Update `@[backend_v2/services/blueprint.py#L65-L669]` (`BlueprintTransformer` and `build_report_dto` `@[backend_v2/services/blueprint.py#L126-L669]`) to import `from backend_v2.services.matrix_parser import MatrixDomainParser`.
      4. Update `@[backend_v2/tests/unit/services/test_blueprint.py#L3302-L3397]` (line 138 and line 3309 inside `test_matrix_domain_parser_accepts_matrix_payload_with_atom_quotes`) to import `from backend_v2.services.matrix_parser import MatrixDomainParser`.
      5. Update `@[backend_v2/tests/unit/services/orchestrator/test_tier4_matrix_distribution_regression.py#L81-L160]` (line 41) to import `from backend_v2.services.matrix_parser import MatrixDomainParser`.
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/matrix_parser/ --test --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py --test --ast-strict`.</verification>
  </step>

  <step id="3" name="Lock Retired Path in QGR017 AST Guardrails and Synchronize Directory Reference">
    <constraint invariant="ast_guardrail_mandate">Retired monolith paths MUST be permanently banned under QGR017 in scripts/_ast_guardrails.py.</constraint>
    <action>
      1. Modify `@[scripts/_ast_guardrails.py#L1865-L1897]` (`visit_Import`) and `@[scripts/_ast_guardrails.py#L1899-L1977]` (`visit_ImportFrom`) to ban imports of `backend_v2.services.matrix_domain_parser` and `from backend_v2.services import matrix_domain_parser` under `QGR017`, instructing callers to import from `backend_v2.services.matrix_parser`.
      2. Modify `@[.agents/rules/04_directory_reference.md]` under Pillar 6 (`backend_v2/services/`) to replace `matrix_domain_parser.py` with `matrix_parser/ (distribution_formatter.py, scale_and_atom_stage.py, row_builder_stage.py, __init__.py facade)`.
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/matrix_parser/ --test --ast-strict`, `uv run pytest backend_v2/tests/unit/services/orchestrator/test_tier4_matrix_distribution_regression.py`, and `uv run python backend_v2/seed/run_seed.py local`.</verification>
  </step>

  <test_contracts>
    <contract type="regression" name="test_matrix_parser_facade_full_parse_matrices_parity">
      Verifies that importing MatrixDomainParser from backend_v2.services.matrix_parser preserves 100% identical ParsedMatricesResultDTO outputs across evaluative and informational matrices.
    </contract>
    <contract type="positive" name="test_blueprint_parse_matrix_trace_results_comprehensive">
      Verifies 1-hop caller BlueprintTransformer.build_report_dto integration with backend_v2.services.matrix_parser.MatrixDomainParser.
    </contract>
    <contract type="negative" name="test_blueprint_parse_matrix_trace_results_exceptions">
      Verifies that Fail-Fast AppException errors raised by backend_v2.services.matrix_parser propagate through BlueprintTransformer.build_report_dto.
    </contract>
    <contract type="negative" name="test_qgr017_bans_legacy_matrix_domain_parser_import">
      Verifies that AST guardrail QGR017 flags any import from backend_v2.services.matrix_domain_parser.
    </contract>
  </test_contracts>
</execution_protocol>
```
