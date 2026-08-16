# Phase 3: Matrix Explanation Service Hardening & Dual Reporting

**Overview:** Harden `matrix_explanation_service.py` to eliminate 12 legacy anti-patterns, implement Status-Aware Dual Reporting (`SUPPORTING EVIDENCE` + `UNMET CRITERIA / DEFICITS`) with Ranked Round-Robin curation, define `MatrixExplanationContextList = TypeAdapter(list[MatrixExplanationContextDTO])` to eliminate Double-Serialization in `worker.py`, integrate SSOT quote limits in `SynthesisPayloadCompressor`, update Knowledge Item documentation, and expand unit/contract test coverage with concrete typed fixtures.
**Target Files:**
- `[MODIFY]` @[backend_v2/models/dtos/synthesis.py#L1-L168]
- `[MODIFY]` @[backend_v2/worker.py#L905-L975]
- `[MODIFY]` @[backend_v2/services/orchestrator/matrix_explanation_service.py#L1-L173]
- `[MODIFY]` @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L1-L149]
- `[MODIFY]` @[ki_synthesis_payload_compression.md]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py#L1-L253]
- `[MODIFY]` @[backend_v2/tests/unit/test_epic93_contract_verification.py#L257-L315]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 1 and Phase 2. Verify ranked_round_robin utility and distiller wiring pass all tests.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/services/orchestrator/matrix_explanation_service.py#L1-L173], @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L1-L149], @[backend_v2/models/dtos/synthesis.py#L1-L168], @[backend_v2/worker.py#L905-L975], and test files.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_143_Synthesis_Matrix_Explanation_Fix.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [x] `MatrixExplanationService.assemble_matrices_to_explain` updated to mandatory `target_locale: str` without defaults.
    - [x] Global settings hoisted at method start (`max_synthesis_quote_length`, `max_synthesis_quotes_per_matrix`, `max_synthesis_unmet_criteria_per_matrix`).
    - [x] Legacy anti-patterns eliminated: duck-typing (`isinstance`, `hasattr`, `getattr`, `.get()`), raw `+` concatenation, and unhandled `LightweightMatrixOutput` / `LevelStatsDTO` validations.
    - [x] Status-Aware Dual Reporting implemented (`SUPPORTING EVIDENCE` for `PASSED` atoms and `UNMET CRITERIA / DEFICITS` for `FAILED` atoms).
    - [x] Ranked Round-Robin claim diversity implemented with per-matrix pre-deduplication hash set (`seen_matrix_quotes`), eliminating Single-Claim Starvation and Deduplication Starvation.
    - [x] Unmet criteria curated deterministically by ascending scale score order (Level 1 critical deficits first, alphabetical tie-break), eliminating Priority Inversion.
    - [x] Low-substance quote fragments (&lt; 15 characters) filtered from `SUPPORTING EVIDENCE`.
    - [x] `MatrixExplanationContextList = TypeAdapter(list[MatrixExplanationContextDTO])` defined in @[backend_v2/models/dtos/synthesis.py].
    - [x] Double-Serialization in @[backend_v2/worker.py] eliminated by replacing `json.dumps([m.model_dump(...) for m in ...])` with direct `MatrixExplanationContextList.dump_json(matrices_to_explain, indent=2, exclude_none=True).decode("utf-8")`.
    - [x] Hardcoded `[:300]` replaced with `settings.max_synthesis_quote_length` in @[backend_v2/services/orchestrator/synthesis_payload_compressor.py].
    - [x] @[ki_synthesis_payload_compression.md] updated with SSOT settings and round-robin curation.
    - [x] All 5 existing test cases in @[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py] updated with `target_locale="en"` and concrete `PromptBlock` fixtures; 6 new unit tests added.
    - [x] Call-site and assertion in @[backend_v2/tests/unit/test_epic93_contract_verification.py#L257-L315] updated with mandatory `target_locale="en"` and updated fallback justification string.
  </dod_checklist>

  <required_context_rules>
    - @[.agents/rules/00-antigravity-core.md]
    - @[.agents/rules/01-python-backend.md]
    - @[.agents/rules/05_llm_architecture.md]
    - @[ki_god_code_prevention.md]
    - @[ki_synthesis_payload_compression.md]
    - @[ki_matrix_boolean_evaluation_strictness.md]
    - @[ki_dual_axis_localization_architecture.md]
    - @[ki_tripartite_pipeline_architecture.md]
    - @[ki_sdui_matrix_synthesis.md]
    - @[ki_sdui_adapter_pattern.md]
    - @[ki_flat_polymorphic_pipeline.md]
    - @[ki_global_config_sovereignty.md]
    - @[ki_python_314_concurrency_strictness.md]
    - @[ki_ai_testing_standards.md]
    - @[ki_ast_guardrail_testing.md]
    - @[ki_dag_engine_dto_projection_rules.md]
    - @[ki_epic_lifecycle_workflow.md]
    - @[ki_context_enriched_decompose_verify.md]
    - @[ki_strict_sdui_serialization.md]
    - @[ki_llm_extraction_architecture.md]
    - @[ki_topological_engine.md]
    - @[ki_execution_engine_protocol.md]
    - @[ki_matrix_sensor_prompt_builder.md]
  </required_context_rules>

  <anti_targets>
    - Do NOT use duck-typing (`isinstance(item, dict)`, `hasattr()`, `getattr()`, `.get()`) on domain models or DTOs.
    - Do NOT use raw `+` string concatenation to build justification text.
    - Do NOT add optional fallback defaults (specifically: `target_locale: str = "en"`) to `assemble_matrices_to_explain`.
    - Do NOT use `json.dumps([m.model_dump(...) for m in ...])` for DTO list serialization in `worker.py` (Double-Serialization Ban).
    - Do NOT use loose `MagicMock(spec=PromptBlock)` in unit tests (Anti-Fake-Green Mandate); use concrete Pydantic fixtures.
    - Do NOT commit Step 3.1 without simultaneously committing Step 3.5 (atomic test migration).
  </anti_targets>

  <step id="1" name="Matrix Explanation Service Hardening &amp; Dual Reporting">
    <action>Modify @[backend_v2/services/orchestrator/matrix_explanation_service.py#L1-L173]:
1. Module imports: `import logging`, `logger = logging.getLogger(__name__)`, `from pydantic import ValidationError`, `from backend_v2.exceptions import ErrorCodes`, `from backend_v2.settings import get_settings` (global import), `from backend_v2.utils.ranked_round_robin import ranked_round_robin_select`, `from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO, LightweightMatrixOutput`, `from backend_v2.models.enums import ExecutionStatus, PromptBlockCategory`.
2. Signature: `def assemble_matrices_to_explain(available_dtos: list[StepOutputDTO], title_map: dict[str, str], blocks_by_id: dict[str, PromptBlock], target_locale: str) -> list[MatrixExplanationContextDTO]:`
3. Hoist settings at start: `settings_obj = get_settings()`, `max_quote_len = settings_obj.max_synthesis_quote_length`, `max_quotes_per_matrix = settings_obj.max_synthesis_quotes_per_matrix`, `max_unmet_criteria = settings_obj.max_synthesis_unmet_criteria_per_matrix`.
4. Extract `global_quotes_map`: validate dicts via `AtomResultDTO.model_validate(atom_dict, strict=False)`, catch `(ValidationError, ValueError)` with warning log (`ErrorCodes.INVALID_OUTPUT_SCHEMA.name`), guard nullable `source_quote` (`if atom_res.source_quote: cleaned = atom_res.source_quote.strip(); if len(cleaned) >= 15: quotes.append(cleaned[:max_quote_len])`).
5. Probe `LightweightMatrixOutput`: wrap `LightweightMatrixOutput.model_validate(payload_to_validate, strict=False)` in `try...except (ValidationError, ValueError) as e:` (PROBE BOUNDARY with `# REVIEWED EXCEPTION to the_duct_tape_ban:` comment), log warning on failure and `continue`.
6. Guard prompt block lookup: `if block_id not in blocks_by_id: continue`, `pb = blocks_by_id[block_id]`, `if pb.category_id != PromptBlockCategory.MATRIX: continue`.
7. Precompute `tda_to_claim` and `tda_to_scale` resolving claim text via `claim.label.resolve(target_locale)`.
8. Collect atom evaluations: pre-deduplicate quote candidates via `seen_matrix_quotes: set[str]`, track unmet claims in `unmet_claim_to_min_scale: dict[str, int]`.
9. Curate quotes via `ranked_round_robin_select` (group_key=claim_label, rank_key=quote length, max_items=max_quotes_per_matrix, reverse_rank=True).
10. Curate unmet criteria via deterministic sorting: `sorted_unmet_claims = sorted(unmet_claim_to_min_scale.keys(), key=lambda c: (unmet_claim_to_min_scale[c], c))[:max_unmet_criteria]`.
11. Guard `level_breakdown`: `if lw_matrix.level_breakdown:`, validate `LevelStatsDTO.model_validate(stats_raw, strict=False)` with `try...except (ValidationError, ValueError) as e:` PROBE BOUNDARY and warning logging, format via f-strings.
12. Resolve title map via explicit key check: `title_map[block_id.lower()] if block_id.lower() in title_map else block_id`.
13. Assemble `justification_text` using deterministic sections (`[DISTRIBUTION CONTEXT: ...]`, `SUPPORTING EVIDENCE:\n...`, `UNMET CRITERIA / DEFICITS:\n...`, or fallback `No direct evidence quotes or specific deficits recorded for this matrix.`).
    </action>
    <contract_freeze>
      <signature>def assemble_matrices_to_explain(available_dtos: list[StepOutputDTO], title_map: dict[str, str], blocks_by_id: dict[str, PromptBlock], target_locale: str) -> list[MatrixExplanationContextDTO]:</signature>
    </contract_freeze>
    <constraint invariant="the_zero_compromise_pledge">Eliminate all duck-typing, hasattr, and raw dict fallbacks.</constraint>
    <constraint invariant="naked_prompt_injection">All justification formatting must use f-strings and str.join() with strict structural boundaries.</constraint>
  </step>

  <step id="2" name="Synthesis Payload Compressor SSOT Alignment">
    <action>In @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L1-L149], replace hardcoded `[:300]` quote slice in line 119 with `settings.max_synthesis_quote_length`.</action>
    <constraint invariant="dry_composition_mandate">Consolidate quote length truncation into centralized Settings SSOT.</constraint>
  </step>

  <step id="3" name="TypeAdapter Definition &amp; Worker Direct Serialization (Double-Serialization Ban)">
    <action>In @[backend_v2/models/dtos/synthesis.py#L1-L168]:
1. Import `TypeAdapter` from `pydantic`.
2. Define `MatrixExplanationContextList = TypeAdapter(list[MatrixExplanationContextDTO])`.
    </action>
    <action>In @[backend_v2/worker.py#L905-L975]:
1. Import `MatrixExplanationContextList` from `backend_v2.models.dtos.synthesis`.
2. At line 922 (Executive Synthesis prompt assembly), replace:
   `json.dumps([m.model_dump(exclude_none=True) for m in matrices_to_explain], indent=2)`
   with:
   `MatrixExplanationContextList.dump_json(matrices_to_explain, indent=2, exclude_none=True).decode("utf-8")`
3. At line 964 (Matrix Row Explanations prompt assembly), replace:
   `json.dumps([m.model_dump(exclude_none=True) for m in matrices_to_explain], indent=2)`
   with:
   `MatrixExplanationContextList.dump_json(matrices_to_explain, indent=2, exclude_none=True).decode("utf-8")`
    </action>
    <constraint invariant="strict_sdui_polymorphic_serialization">Enforce direct C/Rust pydantic-core serialization and ban intermediate Python dict allocations (Double-Serialization Ban).</constraint>
  </step>

  <step id="4" name="Knowledge Base Alignment">
    <action>In @[ki_synthesis_payload_compression.md], update documentation to replace references to `ExtractiveSensorService` with the SSOT `MatrixExplanationService`, and document centralized settings (`max_synthesis_quote_length`, `max_synthesis_quotes_per_matrix`, `max_synthesis_unmet_criteria_per_matrix`), Ranked Round-Robin diversity curation, `MatrixExplanationContextList` TypeAdapter serialization, and mandatory `target_locale` parameter.</action>
  </step>

  <step id="5" name="Matrix Explanation Service Unit &amp; Contract Tests (Atomic Test Migration)">
    <action>Modify @[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py#L1-L253]:
1. Replace all `MagicMock(spec=PromptBlock)` with concrete, valid `PromptBlock` test fixtures using a typed `_create_matrix_block` helper function (with valid Stripe ID pattern, `I18nText`, `MatrixScale`, `MatrixClaim`, and `TDAAssertion`).
2. Update 5 existing test cases to pass `target_locale="en"` and assert updated Status-Aware headers (`SUPPORTING EVIDENCE:` and `UNMET CRITERIA / DEFICITS:`, or updated fallback string `"No direct evidence quotes or specific deficits recorded for this matrix."`).
3. Add 6 new unit tests:
   - `test_assemble_matrices_to_explain_round_robin_diversity`: verify alternating quote selection across claims up to max 5.
   - `test_assemble_matrices_to_explain_deduplication_starvation_prevention`: verify candidate pre-deduplication returns full quota of unique quotes.
   - `test_assemble_matrices_to_explain_unmet_criteria_severity_order`: verify Level 1 deficits prioritized over Level 5 aspirational misses.
   - `test_assemble_matrices_to_explain_short_quote_filtering`: verify quotes &lt; 15 chars are excluded.
   - `test_assemble_matrices_to_explain_multilingual_resolution`: verify `target_locale="fi"` resolves Finnish claim translations while `target_locale="en"` resolves English.
   - `test_assemble_matrices_to_explain_corrupt_level_stats_graceful_handling`: verify malformed level stats are logged and skipped without crashing.
    </action>
    <action>Modify @[backend_v2/tests/unit/test_epic93_contract_verification.py#L257-L315]:
1. Update call-site in `test_matrices_to_explain_assembly` at line 306 to pass mandatory `target_locale="en"`.
2. Update assertion at line 313 from `"No direct evidence quotes extracted for this matrix."` to `"No direct evidence quotes or specific deficits recorded for this matrix."`.
    </action>
    <test_contracts>
      <test name="test_assemble_matrices_to_explain_basic" category="positive">
        <input>dtos with evaluated_atoms passed and authentic source quotes, target_locale="en"</input>
        <expected>"SUPPORTING EVIDENCE:" present with verbatim quotes</expected>
      </test>
      <test name="test_assemble_matrices_to_explain_includes_failed_claims" category="positive">
        <input>dtos with mixed PASSED and FAILED atoms, target_locale="en"</input>
        <expected>both "SUPPORTING EVIDENCE:" and "UNMET CRITERIA / DEFICITS:" present simultaneously</expected>
      </test>
      <test name="test_assemble_matrices_to_explain_round_robin_diversity" category="positive">
        <input>Claim A with 4 quotes, Claim B with 4 quotes, max_quotes=5</input>
        <expected>selects 3 from A and 2 from B in alternating order</expected>
      </test>
      <test name="test_assemble_matrices_to_explain_deduplication_starvation_prevention" category="positive">
        <input>Claim A and B sharing duplicate quotes across TDAs</input>
        <expected>selects exactly 5 unique quotes without post-selection collapse</expected>
      </test>
      <test name="test_assemble_matrices_to_explain_unmet_criteria_severity_order" category="positive">
        <input>12 failed atoms across scale levels 1 to 5, max_unmet=5</input>
        <expected>justification contains exactly 5 Level 1/2 deficits, discarding Level 5</expected>
      </test>
      <test name="test_assemble_matrices_to_explain_multilingual_resolution" category="positive">
        <input>Matrix with I18nText labels in English and Finnish, target_locale="fi"</input>
        <expected>unmet criteria formatted using Finnish translations</expected>
      </test>
      <test name="test_assemble_matrices_to_explain_short_quote_filtering" category="boundary">
        <input>atom with quote="yes" (&lt; 15 characters)</input>
        <expected>quote excluded from SUPPORTING EVIDENCE</expected>
      </test>
      <test name="test_assemble_matrices_to_explain_no_matching_quotes" category="boundary">
        <input>step payload with normalized_score but no evaluated_atoms</input>
        <expected>returns matrix with fallback justification string without crash</expected>
      </test>
      <test name="test_assemble_matrices_to_explain_empty_quotes_list" category="boundary">
        <input>atom result with source_quote=None</input>
        <expected>returns matrix with fallback justification string</expected>
      </test>
      <test name="test_assemble_matrices_to_explain_deduplicates_by_block_id" category="boundary">
        <input>duplicate StepOutputDTOs with identical block_id</input>
        <expected>first step output wins, single MatrixExplanationContextDTO returned</expected>
      </test>
      <test name="test_assemble_matrices_to_explain_corrupt_level_stats_graceful_handling" category="error_path">
        <input>matrix with malformed level_breakdown dict</input>
        <expected>logs warning with INVALID_OUTPUT_SCHEMA and continues without crash</expected>
      </test>
      <test name="test_matrices_to_explain_assembly" category="positive">
        <input>test_epic93_contract_verification scenario with blk_m1 and blk_m2, target_locale="en"</input>
        <expected>blk_m1 has quotes, blk_m2 has updated fallback string</expected>
      </test>
    </test_contracts>
  </step>

  <validation_gate>
    Run automated unit tests and audit loop:
    `uv run pytest backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py`
    `uv run pytest backend_v2/tests/unit/test_epic93_contract_verification.py`
    `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test`
    `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/synthesis.py --test`
  </validation_gate>
</execution_protocol>
```
