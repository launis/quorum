# Phase 3: Backend Domain & Synthesis Payload Compression Hardening

**Overview:** Hardens SynthesisPayloadCompressor with unbounded mode and deterministic prioritized stratification, upgrades MatrixExplanationService with profile-level config overrides and candidate pre-deduplication, filters synthesis source steps in synthesis_distiller_hook, and enforces system core protection in StudioWorkflowService.
**Source:** @[docs/epic/EPIC_145_Workflow_Context_Governance_and_Studio_UX.md#L140-L192] Phase 3: Backend Domain & Synthesis Payload Compression Hardening
**Target Files:**
- `[MODIFY]` @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L17-L163]
- `[MODIFY]` @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L20-L163]
- `[MODIFY]` @[backend_v2/services/orchestrator/synthesis_distiller.py#L171-L344]
- `[MODIFY]` @[backend_v2/services/orchestrator/matrix_explanation_service.py#L25-L224]
- `[MODIFY]` @[backend_v2/services/orchestrator/matrix_explanation_service.py#L28-L224]
- `[MODIFY]` @[backend_v2/services/studio/workflow_service.py#L448-L479]
- `[MODIFY]` @[backend_v2/services/studio/workflow_service.py#L481-L504]
- `[MODIFY]` @[backend_v2/api/routers/studio/steps.py#L100-L119]
- `[MODIFY]` @[backend_v2/api/routers/studio/steps.py#L122-L142]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_studio.py#L238-L252]
- `[MODIFY]` @[backend_v2/tests/unit/test_synthesis_payload_compression.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 2. Verify that seed data and Step models are fully migrated.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true for synthesis payload compression and matrix explanation services.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_145_Workflow_Context_Governance_and_Studio_UX.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] `SynthesisPayloadCompressor` exports explicit `__all__ = ["SynthesisPayloadCompressor"]` and instantiates module-level logger.
    - [ ] `SynthesisPayloadCompressor._strip_heavy_keys` strips `hydrated_references`, `shuffled_atoms`, `atom_quotes`, `_step_metadata`, `_audit_signature`, `_evaluative_matrices` using `.pop(key, None)`.
    - [ ] `SynthesisPayloadCompressor` re-validates evaluations via `DistilledEvaluation.model_validate()` referencing `settings.max_synthesis_reasoning_length` without `model_copy(update={...})` or magic number `[:300]`.
    - [ ] `SynthesisPayloadCompressor` implements Unbounded Mode (`max_synthesis_evaluations == 0`) and Deterministic Prioritized Stratification with compound sort `(-len(exact_quotes), atom_id)` and final canonical `atom_id` sort when limit > 0.
    - [ ] `SynthesisPayloadCompressor` validates all 4 ISTQB heterogeneous payload partitions (`dict`, `list`, `str`, scalar/empty) and raises `AppException(VALIDATION_FAILED)` with RFC-7807 logging on invalid schemas or empty evaluation results.
    - [ ] `synthesis_distiller_hook` in `synthesis_distiller.py` declares `__all__ = ["synthesis_distiller_hook"]`, filters `valid_source_dtos` using `StepRule.is_synthesis_source`, and forwards `output_profile.synthesis` to `MatrixExplanationService`.
    - [ ] `MatrixExplanationService` in `matrix_explanation_service.py` declares `__all__ = ["MatrixExplanationService"]`, accepts `synthesis_config: SynthesisConfigDTO | None`, resolves limits via Tripartite Configuration Resolution, catches specific `(KeyError, AttributeError)` in label resolution, and accesses `tda_to_scale[tda_id]` directly.
    - [ ] `StudioWorkflowService` in `workflow_service.py` declares `__all__ = ["StudioWorkflowService"]` and raises `AppException(SYSTEM_PROTECTED_RESOURCE)` on deletion or system-core mutation of protected steps.
    - [ ] Unit tests in `test_synthesis_payload_compression.py`, `test_matrix_explanation_service.py`, and `test_studio.py` cover all positive, negative, and ISTQB equivalence partitions with >90% branch coverage.
    - [ ] Backend quality gate passes: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/synthesis_payload_compressor.py --test`.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <ki>@[ki_synthesis_payload_compression.md]</ki>
    <ki>@[ki_sdui_matrix_synthesis.md]</ki>
    <ki>@[ki_tripartite_pipeline_architecture.md]</ki>
    <ki>@[ki_god_code_prevention.md]</ki>
    <ki>@[ki_dual_axis_localization_architecture.md]</ki>
    <ki>@[ki_strict_sdui_serialization.md]</ki>
    <ki>@[ki_python_314_concurrency_strictness.md]</ki>
    <ki>@[ki_global_config_sovereignty.md]</ki>
    <ki>@[ki_matrix_boolean_evaluation_strictness.md]</ki>
    <ki>@[ki_ai_testing_standards.md]</ki>
    <ki>@[ki_dag_engine_dto_projection_rules.md]</ki>
    <ki>@[ki_neuro_symbolic_agentic_workflow.md]</ki>
    <ki>@[ki_flat_polymorphic_pipeline.md]</ki>
    <ki>@[ki_sdui_adapter_pattern.md]</ki>
  </required_context_rules>

  <touched_artifacts>
    <backend>@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]</backend>
    <backend>@[backend_v2/services/orchestrator/synthesis_distiller.py]</backend>
    <backend>@[backend_v2/services/orchestrator/matrix_explanation_service.py]</backend>
    <backend>@[backend_v2/services/studio/workflow_service.py]</backend>
    <backend>@[backend_v2/api/routers/studio/steps.py]</backend>
    <backend>@[backend_v2/tests/unit/test_synthesis_payload_compression.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/test_studio.py]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT modify Flutter frontend UI widgets in Phase 3.
    - Do NOT use raw dicts or duck-typing in compressor logic.
    - Do NOT use model_copy(update={...}) or magic number [:300].
    - Do NOT introduce fallback chains on validated mandatory keys.
  </anti_targets>

  <step id="1" name="Synthesis Payload Compressor Hardening">
    <action>In @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L17-L163], add `__all__ = ["SynthesisPayloadCompressor"]`, `import logging`, `logger = logging.getLogger(__name__)`, and `from pydantic import ValidationError`.</action>
    <action>In @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L17-L163] and @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L20-L163], upgrade `_strip_heavy_keys`:
      1. Strip keys using `obj.pop(key, None)` for `"shuffled_atoms"`, `"atom_quotes"`, `"hydrated_references"`, `"_step_metadata"`, `"_audit_signature"`, `"_evaluative_matrices"`.
      2. Implement `_normalize_result_item(item: dict[str, Any]) -> dict[str, Any]` with routing discriminator: if `"exact_quotes"` in item, route to `DistilledEvaluation.model_validate()`; otherwise apply field whitelisting (`{"output_text", "status", "atom_id"}`).
      3. Process `"evaluations"` and `"results"` as dual explicit distillation paths without fallback chains.
      4. Re-validate evaluations via `DistilledEvaluation.model_validate(lite_ev_obj.model_dump(exclude_unset=True) | {"exact_quotes": [q[: settings.max_synthesis_quote_length] for q in valid_quotes], "semantic_reasoning": str(lite_ev_obj.semantic_reasoning)[: settings.max_synthesis_reasoning_length] if lite_ev_obj.semantic_reasoning else None})`.
      5. Replace `except Exception as e:` with `except (ValidationError, ValueError) as e:` and log RFC-7807 structured error before raising `AppException(status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})`.
      6. Implement Token Shield Prioritized Stratification via `_prune_and_stratify_evaluations(evals, limit)`:
         - When `settings.max_synthesis_evaluations == 0`: Unbounded Mode (no truncation).
         - When `settings.max_synthesis_evaluations > 0` and `len(lite_evals) > settings.max_synthesis_evaluations`:
           - Partition into Deficits/Failures (`status in ("FAILED", "UNMET", "NON_COMPLIANT")` or `is_unmet: True`) and Strengths/Passes.
           - Sort both partitions by `(-len(exact_quotes), atom_id)`.
           - Allocate 70% deficit budget with dynamic spillover.
           - Combine and canonically sort by `atom_id` for deterministic JSON serialization.
           - Emit structured `logger.warning("Token Shield: Prioritized stratification applied", extra={"original_count": len(evals), "limit": limit, "deficits_retained": deficit_budget, "strengths_retained": strength_budget, "dropped_count": len(evals) - len(selected)})`.
      7. Enforce Fail-Fast on empty evaluations list (`AppException(VALIDATION_FAILED)`).</action>
    <demolish>REMOVE: lite_ev_obj.model_copy(update={...}) at @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L17-L163] and @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L20-L163]. REPLACE WITH: DistilledEvaluation.model_validate().</demolish>
    <demolish>REMOVE: hardcoded magic number [:300] at @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L17-L163] and @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L20-L163]. REPLACE WITH: settings.max_synthesis_reasoning_length.</demolish>
    <demolish>REMOVE: broad catch-all except Exception as e: at @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L17-L163]. REPLACE WITH: except (ValidationError, ValueError) as e: with RFC-7807 logging.</demolish>
    <constraint invariant="anti_god_file_dumping">Keep compressor logic clean, modular, and single-responsibility.</constraint>
  </step>

  <step id="2" name="Synthesis Distiller Hook Source Step Filtering">
    <action>In @[backend_v2/services/orchestrator/synthesis_distiller.py#L171-L344], add `__all__ = ["synthesis_distiller_hook"]`.</action>
    <action>In `synthesis_distiller_hook`, map `workflow_data.steps` by step ID to determine `StepRule.is_synthesis_source`.</action>
    <action>Filter `valid_source_dtos` to include only steps where `StepRule.is_synthesis_source == True`, excluding unselected steps (specifically Input Processing raw documents) from `<source>` prompt assembly.</action>
    <action>Forward `output_profile.synthesis` into `MatrixExplanationService.assemble_matrices_to_explain(available_dtos, title_map, blocks_by_id, target_locale=target_locale, synthesis_config=output_profile.synthesis)`.</action>
    <constraint invariant="execution_synthesis_tier_decoupling">Strictly filter data based on target blocks and synthesis source flags.</constraint>
  </step>

  <step id="3" name="Matrix Explanation Service Profile Overrides & Probe Boundaries">
    <action>In @[backend_v2/services/orchestrator/matrix_explanation_service.py#L25-L224], add `__all__ = ["MatrixExplanationService"]`.</action>
    <action>Accept `synthesis_config: SynthesisConfigDTO | None = None` in `assemble_matrices_to_explain()`.</action>
    <action>Resolve `max_quotes_per_matrix` and `max_unmet_criteria` using Tripartite Configuration Resolution:
      - `max_quotes_per_matrix = synthesis_config.max_quotes_per_matrix if synthesis_config and synthesis_config.max_quotes_per_matrix is not None else settings_obj.max_synthesis_quotes_per_matrix`
      - `max_unmet_criteria = synthesis_config.max_unmet_criteria if synthesis_config and synthesis_config.max_unmet_criteria is not None else settings_obj.max_synthesis_unmet_criteria_per_matrix`.</action>
    <action>Verify `seen_matrix_quotes: set[str]` pre-deduplication pattern operates before `ranked_round_robin_select`.</action>
    <action>In claim label resolution at @[backend_v2/services/orchestrator/matrix_explanation_service.py#L28-L224], replace `except Exception:` with specific `(KeyError, AttributeError)`.</action>
    <action>At line 152, replace `tda_to_scale.get(tda_id, 999)` with direct typed access `tda_to_scale[tda_id]`.</action>
    <action>Ensure probe boundary logging on `LevelStatsDTO.model_validate` and `AtomResultDTO.model_validate` includes `extra={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.name, "details": str(e)}`.</action>
    <demolish>REMOVE: except Exception: at @[backend_v2/services/orchestrator/matrix_explanation_service.py#L28-L224]. REPLACE WITH: except (KeyError, AttributeError):.</demolish>
    <demolish>REMOVE: tda_to_scale.get(tda_id, 999) at @[backend_v2/services/orchestrator/matrix_explanation_service.py#L25-L224]. REPLACE WITH: tda_to_scale[tda_id].</demolish>
    <constraint invariant="zero_service_layer_fallbacks">No magic defaults or silent error swallowing in service logic.</constraint>
  </step>

  <step id="4" name="Studio Workflow Service System Core Protection">
    <action>In @[backend_v2/services/studio/workflow_service.py#L448-L479] and @[backend_v2/services/studio/workflow_service.py#L481-L504], add `__all__ = ["StudioWorkflowService"]`.</action>
    <action>In `save_step`: fetch existing step if exists. If `existing.is_system_core` is True, enforce that `data.slug == existing.slug` and `data.is_system_core == existing.is_system_core` (or raise `AppException(message=f"Cannot mutate protected system core step {id}.", status_code=403, details={"error_code": ErrorCodes.SYSTEM_PROTECTED_RESOURCE.value})`).</action>
    <action>In `delete_step`: if `step.is_system_core` is True, raise `AppException(message=f"Cannot delete protected system core step {id}.", status_code=403, details={"error_code": ErrorCodes.SYSTEM_PROTECTED_RESOURCE.value})`.</action>
    <action>Ensure router endpoints in @[backend_v2/api/routers/studio/steps.py#L100-L119] and @[backend_v2/api/routers/studio/steps.py#L122-L142] cleanly delegate to service methods.</action>
    <constraint invariant="universal_fail_fast">Fail-Fast loudly when protected system resources are illegally modified.</constraint>
  </step>

  <step id="5" name="Unit & Regression Test Expansion">
    <action>In @[backend_v2/tests/unit/test_synthesis_payload_compression.py] and @[backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py], implement tests:
      - `test_compress_payload_unbounded_when_zero_evaluations_limit`
      - `test_compress_payload_prioritized_stratification_retains_critical_deficits_over_passes`
      - `test_compress_payload_stratification_is_100_percent_deterministic_with_tiebreakers`
      - `test_compress_payload_strips_hydrated_references_and_heavy_keys`
      - `test_compress_payload_with_results_only_no_evaluations`
      - `test_compress_payload_evaluations_empty_after_compression_fails_fast`
      - `test_compress_payload_heterogeneous_dag_types` (testing all 4 ISTQB partitions: dict, list, str, scalar/empty).</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py], add test verifying `synthesis_config` profile overrides for `max_quotes_per_matrix` and `max_unmet_criteria`.</action>
    <action>In @[backend_v2/tests/unit/services/test_studio.py#L238-L252], add `test_delete_step_protected_system_core_fails_fast` verifying `AppException(SYSTEM_PROTECTED_RESOURCE)` on system core step deletion.</action>
    <constraint invariant="anti_happy_path_mandate">Cover both positive paths and negative AppException paths per ISTQB standards.</constraint>
  </step>

  <validation_gate>
    <action>Execute Compressor Unit Tests: `uv run pytest backend_v2/tests/unit/test_synthesis_payload_compression.py -v`</action>
    <action>Execute Matrix Explanation Service Tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py -v`</action>
    <action>Execute Synthesis Distiller Wiring Tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py -v`</action>
    <action>Execute Studio Service Tests: `uv run pytest backend_v2/tests/unit/services/test_studio.py#L238-L252 -v`</action>
    <action>Execute Backend Audit Loop: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/synthesis_payload_compressor.py --test`</action>
    <action>Execute Full Backend Audit: `uv run python scripts/backend_audit_loop.py backend_v2 --test`</action>
  </validation_gate>
</execution_protocol>
```

