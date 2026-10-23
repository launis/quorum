<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
</required_context_rules>

# Phase 1: Stage DTOs & Distribution Formatter Extraction (`phase1_leaf_and_formatter_extraction.md`)

## 1. Objective
Execute Epoch 1 Phase 1A (Bottom-Up Leaf-First Extraction) of the `MatrixDomainParser` decomposition:
1. Define immutable Pydantic V2 stage DTOs (`[NEW]` `MatrixScaleProjectionDTO`, `[NEW]` `MatrixAtomHydrationResultDTO`, and `[NEW]` `MatrixContextTargetResultDTO`) inside `@[backend_v2/models/dtos/matrix_parser.py#L75-L98]` with `ConfigDict(strict=True, extra="forbid", frozen=True)` so no stage returns anonymous multi-value state tuples (`ban_anonymous_state_tuples`) and no Pydantic models are declared inside `backend_v2/services/` (`strict_model_location`).
2. Extract leaf distribution and explanation formatting functions (`format_level_distribution`, `clean_hallucinated_numbers`, `format_level_breakdown`, `resolve_row_explanation`) into `[NEW] @[backend_v2/services/matrix_parser/distribution_formatter.py]` without creating `backend_v2/services/matrix_parser/__init__.py` (Two-Phase Package Strangler Protocol).
3. Delegate `MatrixDomainParser._format_level_distribution` (`@[backend_v2/services/matrix_domain_parser.py#L40-L90]`), `MatrixDomainParser._clean_hallucinated_numbers` (`@[backend_v2/services/matrix_domain_parser.py#L92-L116]`), and the level breakdown and row explanation sections of `MatrixDomainParser.parse_matrices` (`@[backend_v2/services/matrix_domain_parser.py#L118-L732]`) to `[NEW] @[backend_v2/services/matrix_parser/distribution_formatter.py]` with 100% identical runtime behavior.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[MODIFY]` | `@[backend_v2/models/dtos/matrix_parser.py#L75-L98]` | Define `[NEW]` `MatrixScaleProjectionDTO`, `[NEW]` `MatrixAtomHydrationResultDTO`, and `[NEW]` `MatrixContextTargetResultDTO` with `ConfigDict(strict=True, extra="forbid", frozen=True)` |
| `[NEW]` | `[NEW] @[backend_v2/services/matrix_parser/distribution_formatter.py]` | Leaf formatter functions: `format_level_distribution`, `clean_hallucinated_numbers`, `format_level_breakdown`, and `resolve_row_explanation` |
| `[MODIFY]` | `@[backend_v2/services/matrix_domain_parser.py#L40-L90]` | Delegate `MatrixDomainParser._format_level_distribution` to `format_level_distribution` |
| `[MODIFY]` | `@[backend_v2/services/matrix_domain_parser.py#L92-L116]` | Delegate `MatrixDomainParser._clean_hallucinated_numbers` to `clean_hallucinated_numbers` |
| `[MODIFY]` | `@[backend_v2/services/matrix_domain_parser.py#L118-L732]` | Delegate level breakdown and row explanation formatting in `MatrixDomainParser.parse_matrices` to `format_level_breakdown` and `resolve_row_explanation` |
| `[CONTEXT]` | `@[docs/epic/tasks_matrix_domain_parser/symbol_migration_map.md]` | Canonical symbol and stage migration reference |
| `[CONTEXT]` | `@[backend_v2/tests/unit/services/test_matrix_domain_parser.py]` | Existing 34-test unit suite verifying 100% behavioral parity |

## 3. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Define Immutable Stage DTOs in backend_v2/models/dtos/matrix_parser.py">
    <constraint invariant="strict_model_location">All Pydantic V2 DTOs MUST reside in backend_v2/models/dtos/matrix_parser.py; zero BaseModel subclasses are permitted inside backend_v2/services/.</constraint>
    <constraint invariant="ban_anonymous_state_tuples">All multi-field stage outputs MUST be encapsulated in immutable Pydantic V2 DTOs with ConfigDict(strict=True, extra="forbid", frozen=True) and PEP 593 Annotated fields.</constraint>
    <action>Modify `@[backend_v2/models/dtos/matrix_parser.py#L75-L98]` to export and define `[NEW]` `MatrixScaleProjectionDTO`, `[NEW]` `MatrixAtomHydrationResultDTO`, and `[NEW]` `MatrixContextTargetResultDTO`:
      1. Define `[NEW]` `MatrixScaleProjectionDTO(V2CoreBase)` with `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)` and PEP 593 `Annotated` fields:
         - `true_atoms: Annotated[int | None, Field(default=None, description="Count of passed TDA atoms")] = None`
         - `total_atoms: Annotated[int | None, Field(default=None, description="Count of non-N_A TDA atoms")] = None`
         - `raw_score: Annotated[float | None, Field(default=None, description="Computed or payload raw score")] = None`
         - `norm_score: Annotated[float | None, Field(default=None, description="Computed or payload normalized score")] = None`
         - `math_min: Annotated[float, Field(description="Minimum mathematical scale boundary from PromptBlock")]`
         - `math_max: Annotated[float, Field(description="Maximum mathematical scale boundary from PromptBlock")]`
         - `display_scale_min: Annotated[float, Field(description="Resolved UI display scale minimum")]`
         - `display_scale_max: Annotated[float, Field(description="Resolved UI display scale maximum")]`
         - `score_float: Annotated[float | None, Field(default=None, description="Projected UI display score")] = None`
         - `score_display_label: Annotated[str, Field(description="Formatted UI score label string")]`
         - `ui_plot_ratio: Annotated[float | None, Field(default=None, description="Normalized 0.0 to 1.0 plot ratio")] = None`
         - `level_names: Annotated[dict[str, str], Field(default_factory=dict, description="Mapping of scale level key to localized scale label")]`
         - `ui_boundary_labels: Annotated[dict[str, str], Field(default_factory=dict, description="Mapping of 0.0 and 1.0 plot boundaries to localized scale labels")]`
      2. Define `[NEW]` `MatrixAtomHydrationResultDTO(V2CoreBase)` with `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)` and PEP 593 `Annotated` fields:
         - `evaluated_atoms: Annotated[list[ScorecardAtomDTO], Field(default_factory=list, description="Ordered list of hydrated ScorecardAtomDTO items for the row")]`
         - `clustered_row_sources: Annotated[list[MCPAuditTrace], Field(default_factory=list, description="Clustered MCP audit trace sources for the row")]`
      3. Define `[NEW]` `MatrixContextTargetResultDTO(V2CoreBase)` with `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)` and PEP 593 `Annotated` fields:
         - `context_target: Annotated[str | None, Field(default=None, description="Resolved deterministic input target key")] = None`
         - `context_target_label: Annotated[I18nText | None, Field(default=None, description="Resolved localized label for the context target")] = None`
      4. Add `"MatrixAtomHydrationResultDTO"`, `"MatrixContextTargetResultDTO"`, and `"MatrixScaleProjectionDTO"` to `__all__` in `@[backend_v2/models/dtos/matrix_parser.py#L75-L98]`.
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/matrix_parser.py --test --ast-strict`.</verification>
  </step>

  <step id="2" name="Create Leaf Formatter Module backend_v2/services/matrix_parser/distribution_formatter.py">
    <constraint invariant="strangler_fig_mandate">Do NOT create backend_v2/services/matrix_parser/__init__.py in Phase 1 while backend_v2/services/matrix_domain_parser.py still exists on disk.</constraint>
    <constraint invariant="rfc7807_dual_reporting_mandate">Preserve exact structured logger.error calls with ErrorCodes.VALIDATION_FAILED and ErrorCodes.CONFIGURATION_ERROR preceding every AppException.</constraint>
    <action>Create `[NEW] @[backend_v2/services/matrix_parser/distribution_formatter.py]` containing four pure functions relocated verbatim from `@[backend_v2/services/matrix_domain_parser.py#L37-L732]`:
      1. `format_level_distribution(lvl_data: LevelStatsDTO, locale: str) -> str`: Relocate exact logic from `MatrixDomainParser._format_level_distribution` (`@[backend_v2/services/matrix_domain_parser.py#L40-L90]`).
      2. `clean_hallucinated_numbers(text: str) -> str`: Relocate exact regex sentence filtering logic from `MatrixDomainParser._clean_hallucinated_numbers` (`@[backend_v2/services/matrix_domain_parser.py#L92-L116]`).
      3. `format_level_breakdown(raw_breakdown: dict[str, LevelStatsDTO] | None, locale: str, block_id: str) -> dict[str, str] | None`: Relocate lines 366-393 of `MatrixDomainParser.parse_matrices` (`@[backend_v2/services/matrix_domain_parser.py#L118-L732]`), preserving the `ValueError` catch block logging `ErrorCodes.VALIDATION_FAILED.name` with `exc_info=True` and raising `AppException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})`.
      4. `resolve_row_explanation(block_id: str, profile: OutputProfile, row_explanations_cache: dict[str, str], has_synthesis_cache: bool, execution: Any = None) -> str`: Relocate lines 396-421 and line 561 of `MatrixDomainParser.parse_matrices` (`@[backend_v2/services/matrix_domain_parser.py#L118-L732]`), checking `synthesis_expected` and `is_data_starved`, raising `AppException` with `ErrorCodes.CONFIGURATION_ERROR` when `block_id not in row_explanations_cache`, and returning `clean_hallucinated_numbers(final_explanation)`.
      5. Declare `__all__ = ["clean_hallucinated_numbers", "format_level_breakdown", "format_level_distribution", "resolve_row_explanation"]`.
    </action>
  </step>

  <step id="3" name="Wire Proxy Delegations in backend_v2/services/matrix_domain_parser.py">
    <constraint invariant="two_epoch_separation_mandate">Maintain 100% identical method signatures, exception messages, and return values on MatrixDomainParser during Epoch 1.</constraint>
    <action>Modify `@[backend_v2/services/matrix_domain_parser.py#L40-L90]`, `@[backend_v2/services/matrix_domain_parser.py#L92-L116]`, and `@[backend_v2/services/matrix_domain_parser.py#L118-L732]`:
      1. Import `clean_hallucinated_numbers`, `format_level_breakdown`, `format_level_distribution`, and `resolve_row_explanation` from `backend_v2.services.matrix_parser.distribution_formatter`.
      2. Delegate `MatrixDomainParser._format_level_distribution(lvl_data: LevelStatsDTO, locale: str) -> str` (`@[backend_v2/services/matrix_domain_parser.py#L40-L90]`) to `return format_level_distribution(lvl_data, locale)`.
      3. Delegate `MatrixDomainParser._clean_hallucinated_numbers(text: str) -> str` (`@[backend_v2/services/matrix_domain_parser.py#L92-L116]`) to `return clean_hallucinated_numbers(text)`.
      4. In `MatrixDomainParser.parse_matrices` (`@[backend_v2/services/matrix_domain_parser.py#L118-L732]`), replace inline level breakdown formatting (lines 366-393) with `axis_level_breakdown = format_level_breakdown(matrix_payload.level_breakdown, locale, b_id)` and replace inline row explanation resolution and cleaning (lines 396-421 and line 561) with `cleaned_explanation = resolve_row_explanation(block_id=b_id, profile=profile, row_explanations_cache=row_explanations_cache, has_synthesis_cache=has_synthesis_cache, execution=execution)`.
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/matrix_domain_parser.py --test --ast-strict` and `uv run pytest backend_v2/tests/unit/services/orchestrator/test_tier4_matrix_distribution_regression.py`.</verification>
  </step>

  <test_contracts>
    <contract type="regression" name="test_matrix_domain_parser_formats_float_level_stats_as_clean_integers">
      Verifies that float-valued LevelStatsDTO counts (hits=2.0, total=3.0) and integer-equivalent level keys ("1.0", "2.0") format into clean integer strings ("2/3") without ".0" suffixes.
    </contract>
    <contract type="positive" name="test_hybrid_and_capability_level_formatting">
      Verifies Model B Pure Capability ("3/4 skills" / "3/4 taitoa"), Pure Error Radar ("purity 2/3 (⚠️ 1 defect)"), and Hybrid level formatting across 'en' and 'fi' locales.
    </contract>
    <contract type="negative" name="test_matrix_domain_parser_rejects_invalid_level_key">
      Verifies that non-numeric level keys ("level_one") in level_breakdown log ErrorCodes.VALIDATION_FAILED and raise AppException(HTTP 500).
    </contract>
    <contract type="negative" name="test_parse_matrices_missing_explanation_in_cache_fails_fast">
      Verifies that missing row_explanations_cache entry when profile.requires_row_explanations=True and has_synthesis_cache=True logs ErrorCodes.CONFIGURATION_ERROR and raises AppException(HTTP 500).
    </contract>
  </test_contracts>
</execution_protocol>
```
