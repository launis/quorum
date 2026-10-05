<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# EPIC 157 Residual Ledger (Per-File Verification Census)

Baseline 2026-10-05. This ledger is the per-file allocation of the Residual Permissive Typing & Test Bypass Ledger in @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]. Census commands D, F, K, X, N, T, P, R, and S are defined in that section. Column `Phase` names the Eradicating Phase; every file listed under a phase whose Target Boundaries reference this ledger is part of that phase's target boundary. A phase gate passes only when the census command restricted to the phase file list returns 0.

## Census D: Keyword-Injected Repository Mocks
821 occurrences in 32 files.

| File | Occurrences | Phase |
| :--- | :--- | :--- |
| `backend_v2/tests/unit/hooks/test_validation.py` | 160 | 3 |
| `backend_v2/tests/unit/hooks/test_input_processing.py` | 56 | 3 |
| `backend_v2/tests/unit/test_metadata.py` | 48 | 3 |
| `backend_v2/tests/unit/test_input_processing.py` | 21 | 3 |
| `backend_v2/tests/unit/core/test_hook_registry.py` | 16 | 3 |
| `backend_v2/tests/unit/test_synthesis_distiller_hook.py` | 16 | 3 |
| `backend_v2/tests/unit/hooks/test_source_verification_hook.py` | 15 | 3 |
| `backend_v2/tests/unit/hooks/test_interaction_hook.py` | 14 | 3 |
| `backend_v2/tests/unit/hooks/test_linguistics.py` | 8 | 3 |
| `backend_v2/tests/unit/test_metrics.py` | 8 | 3 |
| `backend_v2/tests/unit/test_references.py` | 8 | 3 |
| `backend_v2/tests/unit/hooks/test_matrix_hook.py` | 5 | 3 |
| `backend_v2/tests/unit/llm/test_google_providers_separation.py` | 4 | 3 |
| `backend_v2/tests/unit/services/test_execution.py` | 182 | 4 |
| `backend_v2/tests/unit/test_security.py` | 80 | 4 |
| `backend_v2/tests/unit/services/execution/test_legacy_render_service.py` | 7 | 4 |
| `backend_v2/tests/unit/services/orchestrator/test_dag_executor.py` | 44 | 5 |
| `backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py` | 24 | 5 |
| `backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py` | 10 | 5 |
| `backend_v2/tests/unit/services/orchestrator/strategies/test_base.py` | 8 | 5 |
| `backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py` | 8 | 5 |
| `backend_v2/tests/unit/services/orchestrator/strategies/test_node_strategy_registry.py` | 8 | 5 |
| `backend_v2/tests/unit/services/orchestrator/strategies/test_registry.py` | 8 | 5 |
| `backend_v2/tests/unit/services/orchestrator/test_dag_executor_telemetry.py` | 8 | 5 |
| `backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py` | 8 | 5 |
| `backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py` | 8 | 5 |
| `backend_v2/tests/unit/test_dag_taskgroup.py` | 8 | 5 |
| `backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_audit.py` | 6 | 5 |
| `backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py` | 2 | 5 |
| `backend_v2/tests/unit/services/orchestrator/test_rag_preflight_chat_inflation.py` | 2 | 5 |
| `backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py` | 14 | 6 |
| `backend_v2/tests/integration/test_tavily_live.py` | 7 | 6 |
| **TOTAL** | 821 | |

## Census F: String-Target Repository Patches
50 occurrences in 6 files.

| File | Occurrences | Phase |
| :--- | :--- | :--- |
| `backend_v2/tests/unit/test_worker.py` | 22 | 6 |
| `backend_v2/tests/unit/test_worker_synthesis.py` | 16 | 6 |
| `backend_v2/tests/unit/workers/test_report_worker.py` | 4 | 6 |
| `backend_v2/tests/unit/workers/test_synthesis_worker.py` | 4 | 6 |
| `backend_v2/tests/unit/workers/test_synthesis_reducers.py` | 3 | 6 |
| `backend_v2/tests/unit/test_worker_synthesis_accumulation.py` | 1 | 6 |
| **TOTAL** | 50 | |

## Census K: Ad-Hoc Repository Classes
25 classes in 7 files.

| File | Classes | Phase | Class Names |
| :--- | :--- | :--- | :--- |
| `backend_v2/tests/unit/hooks/test_scoring.py` | 15 | 3 | `MockRepository`, `MockRepoTapa2`, `MockRepoWaterfall`, `MockRepoWaterfallMixed`, `MockRepoWaterfallInverse`, `MockRepoWaterfallInverse`, `MockRepoWaterfallInverseNoOverrides`, `MockRepoWaterfallNoOverrides`, `MockRepoWaterfallInverse`, `MockRepoWaterfallSimulation`, `MockOutputProfileRepoWaterfallPropagates`, `MockOutputProfileRepoWaterfallPropagates`, `MockOutputProfileRepoWaterfallPropagates`, `MockOutputProfileRepoWaterfallPropagates`, `MockRepoWaterfallStrict` |
| `backend_v2/tests/unit/hooks/test_input_processing.py` | 4 | 3 | `MockInputProcessingRepo`, `ChatWFRepo`, `SmoothWFRepo`, `EmptyDescWFRepo` |
| `backend_v2/tests/unit/test_input_processing.py` | 2 | 3 | `MockRepository`, `FeatureFlagMockRepository` |
| `backend_v2/tests/unit/hooks/test_dlq_guard.py` | 1 | 3 | `DummyRepository` |
| `backend_v2/tests/unit/hooks/test_metadata.py` | 1 | 3 | `MockRepository` |
| `backend_v2/tests/unit/hooks/test_references.py` | 1 | 3 | `MockRepository` |
| `backend_v2/tests/unit/hooks/test_security.py` | 1 | 3 | `MockRepository` |
| **TOTAL** | 25 | | |

## Census X: `cast(Any, ...)`
804 occurrences in 13 files.

| File | Occurrences | Phase |
| :--- | :--- | :--- |
| `backend_v2/tests/unit/hooks/test_scoring.py` | 688 | 3 |
| `backend_v2/tests/unit/hooks/test_security.py` | 41 | 3 |
| `backend_v2/tests/unit/hooks/test_metadata.py` | 25 | 3 |
| `backend_v2/tests/unit/hooks/test_references.py` | 25 | 3 |
| `backend_v2/tests/unit/hooks/test_input_processing.py` | 8 | 3 |
| `backend_v2/tests/integration/test_caching_integration.py` | 3 | 9 |
| `backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py` | 3 | 9 |
| `backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py` | 3 | 9 |
| `backend_v2/tests/unit/test_input_processing.py` | 3 | 3 |
| `backend_v2/tests/unit/hooks/test_passivity_hook.py` | 2 | 3 |
| `backend_v2/services/orchestrator/strategies/llm.py` | 1 | 9 |
| `backend_v2/tests/unit/services/orchestrator/test_rag_preflight_service.py` | 1 | 5 |
| `backend_v2/tests/unit/test_context_mapper.py` | 1 | 9 |
| **TOTAL** | 804 | |

## Census N: `# noqa` Comment Tokens
76 comment tokens in 30 files. Eradicating Phase 9 for every row.

| File | Tokens | Phase | Codes |
| :--- | :--- | :--- | :--- |
| `backend_v2/llm/provider.py` | 27 | 9 | `QGR001` 20, `QGR012` 5, `QGR001+QGR012` 2 |
| `backend_v2/llm/adapters/base_adapter.py` | 5 | 9 | `QGR012` 5 |
| `backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py` | 5 | 9 | `E501` 5 |
| `backend_v2/tests/unit/services/test_blueprint.py` | 5 | 9 | `E501` 4, `F403+F401` 1 |
| `backend_v2/tests/unit/test_executions.py` | 3 | 9 | `E501` 3 |
| `backend_v2/tests/unit/test_metrics.py` | 3 | 9 | `E501` 3 |
| `backend_v2/tests/conftest.py` | 2 | 9 | `F401` 2 |
| `backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py` | 2 | 9 | `QGR001` 2 |
| `backend_v2/tests/unit/test_bug_synthesis_hook.py` | 2 | 9 | `F401` 2 |
| `backend_v2/tests/unit/test_dag_taskgroup.py` | 2 | 9 | `E501` 2 |
| `backend_v2/database/firestore_driver.py` | 1 | 9 | `QGR012` 1 |
| `backend_v2/database/tinydb_driver.py` | 1 | 9 | `QGR012` 1 |
| `backend_v2/logging_config.py` | 1 | 9 | `QGR012` 1 |
| `backend_v2/main.py` | 1 | 9 | `F401` 1 |
| `backend_v2/tests/fakes/in_memory_repositories.py` | 1 | 9 | `QGR001` 1 |
| `backend_v2/tests/integration/test_e2e_orchestration.py` | 1 | 9 | `E501` 1 |
| `backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py` | 1 | 9 | `E402` 1 |
| `backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py` | 1 | 9 | `E402` 1 |
| `backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py` | 1 | 9 | `E501` 1 |
| `backend_v2/tests/unit/services/orchestrator/strategies/test_strategies_init.py` | 1 | 9 | `F401` 1 |
| `backend_v2/tests/unit/services/sdui/adapters/test_matrix_graphs_adapter.py` | 1 | 9 | `F401` 1 |
| `backend_v2/tests/unit/services/sdui/adapters/test_matrix_summary_table_adapter.py` | 1 | 9 | `F401` 1 |
| `backend_v2/tests/unit/services/test_matrix_domain_parser.py` | 1 | 9 | `F401` 1 |
| `backend_v2/tests/unit/services/test_output_profile_studio_parity.py` | 1 | 9 | `F401` 1 |
| `backend_v2/tests/unit/test_dag_executor_prompt_blocks.py` | 1 | 9 | `E501` 1 |
| `backend_v2/tests/unit/test_web_fetcher.py` | 1 | 9 | `E501` 1 |
| `backend_v2/tests/unit/test_xai_extensions.py` | 1 | 9 | `E501` 1 |
| `backend_v2/tests/unit/workers/test_synthesis_worker.py` | 1 | 9 | `F403` 1 |
| `scripts/audit_epic_coverage.py` | 1 | 9 | `E402` 1 |
| `scripts/audit_planner_output.py` | 1 | 9 | `E402` 1 |
| **TOTAL** | 76 | | |

## Census T: `# type: ignore`
409 lines in 155 files. Batch 10.1 = production and `scripts/`; Batch 10.2 = tests.

| File | Lines | Batch |
| :--- | :--- | :--- |
| `backend_v2/settings.py` | 18 | 10.1 |
| `backend_v2/models/dtos/context_variables.py` | 6 | 10.1 |
| `backend_v2/services/orchestrator/strategies/llm.py` | 4 | 10.1 |
| `backend_v2/utils/redis_patcher.py` | 4 | 10.1 |
| `backend_v2/core/registry.py` | 3 | 10.1 |
| `backend_v2/database/firestore_driver.py` | 3 | 10.1 |
| `backend_v2/utils/alias_engine.py` | 3 | 10.1 |
| `backend_v2/database/wrapper.py` | 2 | 10.1 |
| `backend_v2/llm/handler.py` | 2 | 10.1 |
| `backend_v2/logging_config.py` | 2 | 10.1 |
| `backend_v2/models/domain/overseer.py` | 2 | 10.1 |
| `backend_v2/models/state.py` | 2 | 10.1 |
| `backend_v2/services/orchestrator/matrix_explanation_service.py` | 2 | 10.1 |
| `backend_v2/services/orchestrator/strategies/logic.py` | 2 | 10.1 |
| `backend_v2/utils/static_charts.py` | 2 | 10.1 |
| `scripts/audit_dto_parity.py` | 2 | 10.1 |
| `backend_v2/database/factory.py` | 1 | 10.1 |
| `backend_v2/llm/client.py` | 1 | 10.1 |
| `backend_v2/llm/provider.py` | 1 | 10.1 |
| `backend_v2/models/dtos/prompt.py` | 1 | 10.1 |
| `backend_v2/models/dtos/render.py` | 1 | 10.1 |
| `backend_v2/services/matrix_domain_parser.py` | 1 | 10.1 |
| `backend_v2/services/orchestrator/dag_executor.py` | 1 | 10.1 |
| `backend_v2/services/orchestrator/state_reducer.py` | 1 | 10.1 |
| `backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py` | 1 | 10.1 |
| `backend_v2/services/pdf_generator.py` | 1 | 10.1 |
| `scripts/audit_matrix_auto_filler.py` | 1 | 10.1 |
| `scripts/audit_matrix_manager.py` | 1 | 10.1 |
| `backend_v2/tests/unit/test_xai_extensions.py` | 15 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_synthesis.py` | 12 | 10.2 (tests) |
| `backend_v2/tests/unit/services/test_execution.py` | 10 | 10.2 (tests) |
| `backend_v2/tests/unit/services/orchestrator/strategies/test_base.py` | 9 | 10.2 (tests) |
| `backend_v2/tests/unit/hooks/test_dlq_guard.py` | 8 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_atom_result.py` | 8 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_lightweight_matrix.py` | 8 | 10.2 (tests) |
| `backend_v2/tests/unit/models/domain/test_inputs.py` | 7 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_hook_delta.py` | 7 | 10.2 (tests) |
| `backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py` | 7 | 10.2 (tests) |
| `backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py` | 7 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_finops.py` | 6 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_mcp.py` | 6 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_sensor.py` | 6 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_studio.py` | 6 | 10.2 (tests) |
| `backend_v2/tests/unit/test_usage.py` | 6 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_context_variables.py` | 5 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_flattened_atom.py` | 5 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_node_execution.py` | 5 | 10.2 (tests) |
| `backend_v2/tests/unit/models/test_v2_core.py` | 5 | 10.2 (tests) |
| `backend_v2/tests/conftest.py` | 4 | 10.2 (tests) |
| `backend_v2/tests/unit/hooks/test_scoring.py` | 4 | 10.2 (tests) |
| `backend_v2/tests/unit/models/domain/test_execution.py` | 4 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_base.py` | 4 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_dag_models.py` | 4 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_hook_state.py` | 4 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_schema_manifest.py` | 4 | 10.2 (tests) |
| `backend_v2/tests/unit/models/test_contrastive_pair_dto.py` | 4 | 10.2 (tests) |
| `backend_v2/tests/unit/models/test_prompt.py` | 4 | 10.2 (tests) |
| `backend_v2/tests/unit/services/ingress/test_smart_ingress_resolver.py` | 4 | 10.2 (tests) |
| `backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py` | 4 | 10.2 (tests) |
| `backend_v2/tests/unit/services/sdui/adapters/test_base_adapter.py` | 4 | 10.2 (tests) |
| `backend_v2/tests/unit/utils/scoring/test_variance_engine.py` | 4 | 10.2 (tests) |
| `backend_v2/tests/unit/core/test_hook_registry.py` | 3 | 10.2 (tests) |
| `backend_v2/tests/unit/core/test_registry.py` | 3 | 10.2 (tests) |
| `backend_v2/tests/unit/database/repositories/test_base.py` | 3 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_engine.py` | 3 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_ingress.py` | 3 | 10.2 (tests) |
| `backend_v2/tests/unit/models/test_state.py` | 3 | 10.2 (tests) |
| `backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_execution_time_resolver.py` | 3 | 10.2 (tests) |
| `backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py` | 3 | 10.2 (tests) |
| `backend_v2/tests/unit/test_judge.py` | 3 | 10.2 (tests) |
| `backend_v2/tests/integration/test_caching_integration.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/unit/core/test_template_processor.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/unit/hooks/test_source_verification_hook.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/unit/models/domain/test_report_artifact.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_flat_record.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_matrix_parser.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_render.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_sdui_rules.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_system.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_trace.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/unit/models/test_core_base.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/unit/services/orchestrator/test_context_router.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/unit/services/orchestrator/test_dag_executor.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_audit.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/unit/services/test_llm_task_executor.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/unit/services/test_matrix_domain_parser.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/unit/test_metadata.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/unit/test_progress.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/unit/test_references.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/unit/test_security.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/unit/utils/scoring/test_unified_engine.py` | 2 | 10.2 (tests) |
| `backend_v2/tests/test_vertex_adapter_caching_system_role.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/core/test_rate_limit.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/database/repositories/components/test_agent.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/database/repositories/components/test_prompt_block.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/database/repositories/components/test_task_blueprint.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/hooks/test_archival.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/hooks/test_context_mapper.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/hooks/test_interaction_hook.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/hooks/test_linguistics.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/hooks/test_llm.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/hooks/test_matrix_hook.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/hooks/test_security.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/llm/test_provider_retry_after.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/models/domain/test_matrix.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/models/domain/test_synthesis.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/models/domain/test_xai.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_global_context.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_inputs.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_output_profile.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_prompt.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_report_data.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_schema_bounds.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_step_telemetry.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_theory_manifest.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/models/dtos/test_variance.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/scripts/test_audit_database_atoms.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/scripts/test_matrix_hardening_generator.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/scripts/test_matrix_hardening_loop.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/scripts/test_sanitize_seed_vault.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/services/execution/test_ingress_service.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/services/execution/test_legacy_render_service.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/services/ingress/test_multi_channel_ingress_service.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_source_document_packer.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/services/orchestrator/strategies/test_node_strategy_registry.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/services/orchestrator/strategies/test_registry.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/services/orchestrator/test_localization_compiler.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/services/orchestrator/test_prompt_compiler_adapter.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/services/orchestrator/test_semantic_entailment_guardrails.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/services/sdui/adapters/test_xai_highlights_adapter.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/services/studio/test_workflow_service.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/services/test_blueprint.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/test_core_base.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/test_epic93_contract_verification.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/test_exceptions.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/test_localization.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/test_organizations.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/test_prompt_blocks.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/test_tier4_bug_fixes.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/test_users.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/test_v2_core_strictness.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/utils/test_normalization.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/utils/test_ranked_round_robin.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/workers/test_synthesis_reducers.py` | 1 | 10.2 (tests) |
| `backend_v2/tests/unit/workers/test_variance_synthesis.py` | 1 | 10.2 (tests) |
| **TOTAL** | 409 | |

## Census P: `dict[str, Any]` / `dict[str, object]` in Tests and `scripts/`
390 lines in 89 files. Eradicating Phase 11 for every row except files deleted in Phase 1.

| File | Lines | Phase |
| :--- | :--- | :--- |
| `scripts/run_e2e_variance_test.py` | 32 | 11 |
| `scripts/diff_executions.py` | 26 | 11 |
| `scripts/sanitize_seed_vault.py` | 12 | 11 |
| `scripts/audit_database_atoms.py` | 4 | 11 |
| `scripts/audit_dict_eradication.py` | 3 | 11 |
| `scripts/matrix_slice_engine.py` | 3 | 11 |
| `scripts/reconcile_storage.py` | 3 | 11 |
| `scripts/matrix_hardening_generator.py` | 2 | 11 |
| `scripts/migrate_seed_contrastive_pairs.py` | 1 | 11 |
| `backend_v2/tests/unit/hooks/test_scoring.py` | 46 | 11 |
| `backend_v2/tests/unit/hooks/test_matrix_hook.py` | 29 | 11 |
| `backend_v2/tests/unit/test_worker.py` | 16 | 11 |
| `backend_v2/tests/unit/seed/test_overfit_token_sanitization.py` | 12 | 11 |
| `backend_v2/tests/unit/test_worker_synthesis.py` | 9 | 11 |
| `backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py` | 8 | 11 |
| `backend_v2/tests/unit/llm/test_provider.py` | 8 | 11 |
| `backend_v2/tests/unit/test_matrix_data_integrity.py` | 7 | 11 |
| `backend_v2/tests/unit/api/routers/test_server_id_authority.py` | 6 | 11 |
| `backend_v2/tests/unit/seed/test_inverse_atoms_clarity_criteria.py` | 6 | 11 |
| `backend_v2/tests/unit/services/orchestrator/test_enriched_dag_executor.py` | 6 | 11 |
| `backend_v2/tests/unit/llm/adapters/test_adapter_parameter_sanitization.py` | 5 | 11 |
| `backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py` | 5 | 11 |
| `backend_v2/tests/unit/scripts/test_audit_dict_eradication.py` | 5 | 11 |
| `backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py` | 5 | 11 |
| `backend_v2/tests/unit/test_seed_architectural_guardrails.py` | 5 | 11 |
| `backend_v2/tests/unit/hooks/test_input_processing.py` | 4 | 11 |
| `backend_v2/tests/unit/llm/adapters/test_openai_adapter.py` | 4 | 11 |
| `backend_v2/tests/unit/llm/test_transient_error_detection.py` | 4 | 11 |
| `backend_v2/tests/unit/models/test_trace_envelope.py` | 4 | 11 |
| `backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py` | 4 | 11 |
| `backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py` | 4 | 11 |
| `backend_v2/tests/unit/test_model_registry_discovery.py` | 4 | 11 |
| `backend_v2/tests/unit/database/repositories/components/test_prompt_block.py` | 3 | 11 |
| `backend_v2/tests/unit/database/test_tinydb_resilience.py` | 3 | 11 |
| `backend_v2/tests/unit/llm/adapters/test_base_adapter.py` | 3 | 11 |
| `backend_v2/tests/unit/llm/test_fallback_caching.py` | 3 | 1 (file deleted) |
| `backend_v2/tests/unit/llm/test_sdui_schema_discriminator_regression.py` | 3 | 11 |
| `backend_v2/tests/unit/scripts/test_diff_executions.py` | 3 | 11 |
| `backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py` | 3 | 11 |
| `backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py` | 3 | 11 |
| `backend_v2/tests/unit/services/test_competency_workflows_seed.py` | 3 | 11 |
| `backend_v2/tests/unit/test_input_processing.py` | 3 | 11 |
| `backend_v2/tests/unit/test_main.py` | 3 | 11 |
| `backend_v2/tests/unit/database/repositories/test_execution.py` | 2 | 11 |
| `backend_v2/tests/unit/hooks/test_passivity_hook.py` | 2 | 11 |
| `backend_v2/tests/unit/llm/adapters/test_anthropic_adapter.py` | 2 | 11 |
| `backend_v2/tests/unit/llm/test_adaptive_retry.py` | 2 | 11 |
| `backend_v2/tests/unit/llm/test_llm_client_tiers.py` | 2 | 11 |
| `backend_v2/tests/unit/llm/test_provider_toolcalls.py` | 2 | 11 |
| `backend_v2/tests/unit/models/domain/test_output_profile.py` | 2 | 11 |
| `backend_v2/tests/unit/scripts/test_run_e2e_variance_test.py` | 2 | 11 |
| `backend_v2/tests/unit/seed/test_matrix_anchoring_rules.py` | 2 | 11 |
| `backend_v2/tests/unit/seed/test_run_seed.py` | 2 | 11 |
| `backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_source_document_packer.py` | 2 | 11 |
| `backend_v2/tests/unit/services/orchestrator/test_dag_executor.py` | 2 | 11 |
| `backend_v2/tests/unit/services/orchestrator/test_rag_preflight_service.py` | 2 | 11 |
| `backend_v2/tests/unit/services/test_blueprint.py` | 2 | 11 |
| `backend_v2/tests/unit/services/test_matrix_domain_parser.py` | 2 | 11 |
| `backend_v2/tests/unit/test_ast_domain_security_guardrails.py` | 2 | 11 |
| `backend_v2/tests/unit/test_epic93_contract_verification.py` | 2 | 11 |
| `backend_v2/tests/unit/test_provider_rate_limit.py` | 2 | 1 (file deleted) |
| `backend_v2/tests/unit/test_v2_core_models.py` | 2 | 11 |
| `backend_v2/tests/conftest.py` | 1 | 11 |
| `backend_v2/tests/fakes/in_memory_repositories.py` | 1 | 11 |
| `backend_v2/tests/test_worker_models_used.py` | 1 | 11 |
| `backend_v2/tests/unit/api/routers/test_output_profile_metric_mappings_retention.py` | 1 | 11 |
| `backend_v2/tests/unit/database/test_tinydb_driver.py` | 1 | 11 |
| `backend_v2/tests/unit/llm/test_provider_penalties.py` | 1 | 11 |
| `backend_v2/tests/unit/llm/test_provider_retry_after.py` | 1 | 11 |
| `backend_v2/tests/unit/models/dtos/test_output_profile.py` | 1 | 11 |
| `backend_v2/tests/unit/scripts/test_ast_guardrails.py` | 1 | 11 |
| `backend_v2/tests/unit/scripts/test_audit_database_atoms.py` | 1 | 11 |
| `backend_v2/tests/unit/scripts/test_sanitize_seed_vault.py` | 1 | 11 |
| `backend_v2/tests/unit/services/execution/test_ingress_service.py` | 1 | 11 |
| `backend_v2/tests/unit/services/mcp/test_dispatcher.py` | 1 | 11 |
| `backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py` | 1 | 11 |
| `backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py` | 1 | 11 |
| `backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py` | 1 | 11 |
| `backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py` | 1 | 11 |
| `backend_v2/tests/unit/services/orchestrator/test_anchor_validation_atom_result.py` | 1 | 11 |
| `backend_v2/tests/unit/services/orchestrator/test_matrix_reducer.py` | 1 | 11 |
| `backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py` | 1 | 11 |
| `backend_v2/tests/unit/test_backend_l10n_internal_parity.py` | 1 | 11 |
| `backend_v2/tests/unit/test_concurrency_fuzzer.py` | 1 | 11 |
| `backend_v2/tests/unit/test_tier4_metric_mappings_bug.py` | 1 | 11 |
| `backend_v2/tests/unit/test_tier4_profile_dto_bug.py` | 1 | 11 |
| `backend_v2/tests/unit/test_worker_synthesis_accumulation.py` | 1 | 11 |
| `backend_v2/tests/unit/utils/test_math_utils.py` | 1 | 11 |
| `backend_v2/tests/unit/workers/test_variance_synthesis.py` | 1 | 11 |
| **TOTAL** | 390 | |

## Census M: Production `Mapping` Sites and `test_`-Named Production Module Dicts
10 sites. Eradicating Phase 11 for every row.

- `backend_v2/core/test_settings.py:19`
- `backend_v2/core/test_settings.py:51`
- `backend_v2/hooks/input_processing.py:66`
- `backend_v2/hooks/input_processing.py:67`
- `backend_v2/services/ingress/pdf_chat_extractor.py:115`
- `backend_v2/services/orchestrator/strategies/llm.py:160`
- `backend_v2/services/orchestrator/strategies/llm.py:161`
- `backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py:240`
- `backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py:221`
- `backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py:301`

## Census R: Non-Codec `Map<String, dynamic>` (Dart)
193 occurrences in 48 files. Eradicating Phase 12 for every row.

| File | Occurrences | Phase |
| :--- | :--- | :--- |
| `client_app_v2/lib/core/api/studio_client.dart` | 36 | 12 |
| `client_app_v2/lib/shared/widgets/result_dashboard.dart` | 26 | 12 |
| `client_app_v2/lib/features/studio/utils/workflow_cloner.dart` | 11 | 12 |
| `client_app_v2/lib/shared/widgets/specialist_section.dart` | 10 | 12 |
| `client_app_v2/lib/core/api/execution_client.dart` | 7 | 12 |
| `client_app_v2/lib/features/execution/views/dynamic_start_screen.dart` | 7 | 12 |
| `client_app_v2/lib/core/api/reports_client.dart` | 6 | 12 |
| `client_app_v2/lib/shared/widgets/audit_trail_viewer.dart` | 6 | 12 |
| `client_app_v2/lib/shared/widgets/dynamic_form.dart` | 6 | 12 |
| `client_app_v2/lib/features/auth/data/auth_repository.dart` | 5 | 12 |
| `client_app_v2/lib/shared/widgets/comparison_matrix.dart` | 5 | 12 |
| `client_app_v2/lib/core/api/sse_client.dart` | 4 | 12 |
| `client_app_v2/lib/features/execution/models/execution_record.dart` | 4 | 12 |
| `client_app_v2/lib/features/execution/models/frozen_context_snapshot.dart` | 4 | 12 |
| `client_app_v2/lib/router/router.dart` | 4 | 12 |
| `client_app_v2/lib/features/auth/data/repositories/user_repository.dart` | 3 | 12 |
| `client_app_v2/lib/features/execution/views/dashboard_view.dart` | 3 | 12 |
| `client_app_v2/lib/features/execution/views/new_execution_view.dart` | 3 | 12 |
| `client_app_v2/lib/shared/widgets/workflow_selector.dart` | 3 | 12 |
| `client_app_v2/lib/core/network/interceptors/error_interceptor.dart` | 2 | 12 |
| `client_app_v2/lib/features/execution/controllers/execution_controller.dart` | 2 | 12 |
| `client_app_v2/lib/features/studio/models/prompt_block.dart` | 2 | 12 |
| `client_app_v2/lib/features/studio/models/prompt_block_simulation.dart` | 2 | 12 |
| `client_app_v2/lib/features/studio/models/step_simulation.dart` | 2 | 12 |
| `client_app_v2/lib/features/studio/models/workflow.dart` | 2 | 12 |
| `client_app_v2/lib/features/studio/views/blueprint_editor_view.dart` | 2 | 12 |
| `client_app_v2/lib/features/studio/views/mcp_gateway_view.dart` | 2 | 12 |
| `client_app_v2/lib/shared/widgets/generic_grid.dart` | 2 | 12 |
| `client_app_v2/lib/shared/widgets/pre_mortem_card.dart` | 2 | 12 |
| `client_app_v2/lib/shared/widgets/score_card_radar.dart` | 2 | 12 |
| `client_app_v2/lib/core/api/workflow_client.dart` | 1 | 12 |
| `client_app_v2/lib/core/error/app_exception.dart` | 1 | 12 |
| `client_app_v2/lib/features/execution/models/distilled_evaluation.dart` | 1 | 12 |
| `client_app_v2/lib/features/execution/models/execution_create_request_dto.dart` | 1 | 12 |
| `client_app_v2/lib/features/execution/models/execution_metadata.dart` | 1 | 12 |
| `client_app_v2/lib/features/execution/models/report_data_v2_dto.dart` | 1 | 12 |
| `client_app_v2/lib/features/execution/models/workflow_inputs.dart` | 1 | 12 |
| `client_app_v2/lib/features/execution/views/execution_report_view.dart` | 1 | 12 |
| `client_app_v2/lib/features/studio/controllers/blueprint_editor_controller.dart` | 1 | 12 |
| `client_app_v2/lib/features/studio/controllers/prompt_blocks_controller.dart` | 1 | 12 |
| `client_app_v2/lib/features/studio/models/mcp_gateway.dart` | 1 | 12 |
| `client_app_v2/lib/features/studio/models/model_config.dart` | 1 | 12 |
| `client_app_v2/lib/features/studio/models/workflow_simulation.dart` | 1 | 12 |
| `client_app_v2/lib/features/studio/views/matrix_editor_view.dart` | 1 | 12 |
| `client_app_v2/lib/features/studio/views/model_registry_view.dart` | 1 | 12 |
| `client_app_v2/lib/features/studio/views/studio_dashboard_view.dart` | 1 | 12 |
| `client_app_v2/lib/shared/widgets/schema_mapper.dart` | 1 | 12 |
| `client_app_v2/lib/shared/widgets/validation_timeline_widget.dart` | 1 | 12 |
| **TOTAL** | 193 | |

## Census S: Unconditional Skip / Xfail Markers
11 markers. Eradicating Phase 1 for every row.

- `backend_v2/tests/architecture/test_boundaries.py:5` `@pytest.mark.skip`
- `backend_v2/tests/unit/hooks/test_scoring.py:2901` `@pytest.mark.xfail`
- `backend_v2/tests/unit/hooks/test_scoring.py:2966` `@pytest.mark.xfail`
- `backend_v2/tests/unit/hooks/test_scoring.py:3031` `@pytest.mark.xfail`
- `backend_v2/tests/unit/hooks/test_scoring.py:3105` `@pytest.mark.xfail`
- `backend_v2/tests/unit/llm/test_fallback_caching.py:20` `@pytest.mark.skip`
- `backend_v2/tests/unit/test_ast_domain_security_guardrails.py:212` `@pytest.mark.skip`
- `backend_v2/tests/unit/test_epic_61_hardening.py:8` `@pytest.mark.skip`
- `backend_v2/tests/unit/test_matrix_data_integrity.py:92` `@pytest.mark.skip`
- `backend_v2/tests/unit/test_provider_rate_limit.py:20` `@pytest.mark.skip`
- `backend_v2/tests/unit/test_provider_rate_limit.py:76` `@pytest.mark.skip`

# Recorded and Retained (Section 2.6 Baselines, MUST NOT Increase)

## Dart Codec Signatures (Retained Boundary)
67 occurrences in 34 files.

| File | Occurrences | Disposition |
| :--- | :--- | :--- |
| `client_app_v2/lib/features/studio/models/prompt_block.dart` | 10 | Retained |
| `client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart` | 6 | Retained |
| `client_app_v2/lib/features/reports/models/report_artifact.dart` | 5 | Retained |
| `client_app_v2/lib/features/studio/models/step_simulation.dart` | 5 | Retained |
| `client_app_v2/lib/features/studio/models/workflow.dart` | 5 | Retained |
| `client_app_v2/lib/features/execution/models/atom_result_dto.dart` | 3 | Retained |
| `client_app_v2/lib/features/studio/models/mcp_gateway.dart` | 2 | Retained |
| `client_app_v2/lib/features/studio/models/model_config.dart` | 2 | Retained |
| `client_app_v2/lib/features/studio/models/output_profile.dart` | 2 | Retained |
| `client_app_v2/lib/features/studio/models/prompt_block_simulation.dart` | 2 | Retained |
| `client_app_v2/lib/shared/models/sdui_block_dto.dart` | 2 | Retained |
| `client_app_v2/lib/core/models/generic_status_response_dto.dart` | 1 | Retained |
| `client_app_v2/lib/features/auth/domain/models/user.dart` | 1 | Retained |
| `client_app_v2/lib/features/execution/models/distilled_evaluation.dart` | 1 | Retained |
| `client_app_v2/lib/features/execution/models/execution_create_request_dto.dart` | 1 | Retained |
| `client_app_v2/lib/features/execution/models/execution_metadata.dart` | 1 | Retained |
| `client_app_v2/lib/features/execution/models/execution_metrics_dto.dart` | 1 | Retained |
| `client_app_v2/lib/features/execution/models/execution_record.dart` | 1 | Retained |
| `client_app_v2/lib/features/execution/models/execution_step.dart` | 1 | Retained |
| `client_app_v2/lib/features/execution/models/execution_summary_snapshot.dart` | 1 | Retained |
| `client_app_v2/lib/features/execution/models/frozen_context_snapshot.dart` | 1 | Retained |
| `client_app_v2/lib/features/execution/models/human_override_request_dto.dart` | 1 | Retained |
| `client_app_v2/lib/features/execution/models/hydrated_atom_dto.dart` | 1 | Retained |
| `client_app_v2/lib/features/execution/models/report_data_v2_dto.dart` | 1 | Retained |
| `client_app_v2/lib/features/execution/models/synthesis_config_dto.dart` | 1 | Retained |
| `client_app_v2/lib/features/execution/models/tda_state.dart` | 1 | Retained |
| `client_app_v2/lib/features/execution/models/trace_context_carrier.dart` | 1 | Retained |
| `client_app_v2/lib/features/execution/models/workflow_inputs.dart` | 1 | Retained |
| `client_app_v2/lib/features/studio/models/blueprint_config.dart` | 1 | Retained |
| `client_app_v2/lib/features/studio/models/gcp_location.dart` | 1 | Retained |
| `client_app_v2/lib/features/studio/models/llm_platform.dart` | 1 | Retained |
| `client_app_v2/lib/features/studio/models/workflow_simulation.dart` | 1 | Retained |
| `client_app_v2/lib/features/studio/models/workflow_ui_schema.dart` | 1 | Retained |
| `client_app_v2/lib/shared/models/i18n_text.dart` | 1 | Retained |
| **TOTAL** | 67 | |

## Driver-Level Patches (`get_driver` / `get_storage_driver`)
75 occurrences in 11 files.

| File | Occurrences | Disposition |
| :--- | :--- | :--- |
| `backend_v2/tests/unit/test_worker.py` | 24 | Recorded |
| `backend_v2/tests/unit/test_worker_synthesis.py` | 16 | Recorded |
| `backend_v2/tests/unit/services/test_execution.py` | 9 | Recorded |
| `backend_v2/tests/unit/workers/test_synthesis_reducers.py` | 6 | Recorded |
| `backend_v2/tests/unit/workers/test_report_worker.py` | 5 | Recorded |
| `backend_v2/tests/unit/database/repositories/test_execution.py` | 4 | Recorded |
| `backend_v2/tests/unit/workers/test_synthesis_worker.py` | 4 | Recorded |
| `backend_v2/tests/unit/database/test_repository.py` | 3 | Recorded |
| `backend_v2/tests/unit/workers/test_execution_worker.py` | 2 | Recorded |
| `backend_v2/tests/unit/hooks/test_integrity.py` | 1 | Recorded |
| `backend_v2/tests/unit/test_worker_synthesis_accumulation.py` | 1 | Recorded |
| **TOTAL** | 75 | |

## Assertion-Free Test Functions
54 functions in 32 files (no `assert`, `pytest.raises`, `pytest.warns`, `pytest.fail`, or `assert_*` call). Rows marked `Deleted in Phase 1` leave the baseline when their file is deleted.

| File | Functions | Names |
| :--- | :--- | :--- |
| `backend_v2/tests/unit/services/studio/test_auth_validator.py` | 6 | `test_enforce_tenant_isolation_root_allowed`, `test_enforce_tenant_isolation_same_org_allowed`, `test_enforce_tenant_isolation_system_allowed_by_default`, `test_enforce_tenant_isolation_public_allowed`, `test_enforce_modification_rights_root_can_modify_system`, `test_enforce_modification_rights_admin_can_modify_system_with_allow_system` |
| `backend_v2/tests/unit/test_worker.py` | 4 | `test_shutdown`, `test_generate_profile_synthesis_missing_matrix_directive_skips_group`, `test_generate_profile_synthesis_missing_xai_directive_skips_xai`, `test_generate_profile_synthesis_missing_row_explanation_directive_skips_row_explanations` |
| `backend_v2/tests/unit/utils/test_finops_trace_analyzer.py` | 3 | `test_main_cli_monitor`, `test_main_cli_finalize`, `test_main_cli_defaults` |
| `backend_v2/tests/unit/database/test_repository.py` | 2 | `test_workflow_fetching`, `test_all_passthrough_methods` |
| `backend_v2/tests/unit/llm/adapters/test_anthropic_adapter.py` | 2 | `test_lazy_import_proof`, `test_anthropic_teardown_is_noop` |
| `backend_v2/tests/unit/llm/adapters/test_deepseek_adapter.py` | 2 | `test_lazy_import_proof`, `test_deepseek_teardown_is_noop` |
| `backend_v2/tests/unit/llm/adapters/test_mock_adapter.py` | 2 | `test_lazy_import_proof`, `test_mock_adapter_teardown_cache_is_noop` |
| `backend_v2/tests/unit/llm/adapters/test_openai_adapter.py` | 2 | `test_lazy_import_proof`, `test_openai_teardown_is_noop` |
| `backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py` | 2 | `test_lazy_import_proof`, `test_vertex_teardown_is_noop` |
| `backend_v2/tests/unit/scripts/test_matrix_hardening_generator.py` | 2 | `test_print_helpers_execute_without_error`, `test_cli_entrypoints` |
| `backend_v2/tests/unit/scripts/test_matrix_hardening_loop.py` | 2 | `test_print_helpers_execute_without_error`, `test_cli_entrypoints` |
| `backend_v2/tests/unit/scripts/test_run_e2e_variance_test.py` | 2 | `test_force_kill_services_subprocess_error_tolerance`, `test_force_kill_services_port_busy_cleanup_loop` |
| `backend_v2/tests/unit/services/cache/test_typed_cache.py` | 2 | `test_typed_cache_set_cached_no_redis`, `test_typed_cache_delete_no_redis` |
| `backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py` | 2 | `test_llm_strategy_invalid_shuffled_atoms_type`, `test_dlq_handle_debug_log_error` |
| `backend_v2/tests/unit/test_main.py` | 2 | `test_validate_database_preflight_missing_file`, `test_lifespan_workflow_detection` |
| `backend_v2/tests/architecture/test_boundaries.py` (Deleted in Phase 1) | 1 | `test_routers_cannot_import_database_directly` |
| `backend_v2/tests/test_storage_bug.py` | 1 | `test_storage_driver_mock_bug` |
| `backend_v2/tests/unit/llm/adapters/test_adapter_factory.py` | 1 | `test_lazy_import_proof` |
| `backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py` | 1 | `test_ai_studio_teardown_is_noop` |
| `backend_v2/tests/unit/llm/adapters/test_base_adapter.py` | 1 | `test_apply_provider_pacing_disabled_when_delay_zero` |
| `backend_v2/tests/unit/llm/test_provider_telemetry.py` | 1 | `test_gen_ai_none_span_caching_boundary` |
| `backend_v2/tests/unit/seed/test_run_seed.py` | 1 | `test_seed_tinydb_dry_run` |
| `backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py` | 1 | `test_pdf_chat_extractor_truncation_inside_code_fence_not_triggered` |
| `backend_v2/tests/unit/services/orchestrator/test_mcp_schema_bug.py` | 1 | `test_llm_has_search_flag_resolution` |
| `backend_v2/tests/unit/services/orchestrator/test_prompt_compiler_strictness_bug.py` | 1 | `test_prompt_compiler_build_dynamic_schema_accepts_strictness_level` |
| `backend_v2/tests/unit/services/studio/test_simulation_service.py` | 1 | `test_token` |
| `backend_v2/tests/unit/services/studio/test_system_config_service.py` | 1 | `test_delete_system_config_success` |
| `backend_v2/tests/unit/services/test_competency_workflows_seed.py` | 1 | `test_competency_workflows_dag_acyclicity` |
| `backend_v2/tests/unit/test_metrics.py` | 1 | `test_text_metrics_hook_invalid_payload_fails_fast` |
| `backend_v2/tests/unit/test_telemetry.py` | 1 | `test_report_client_error` |
| `backend_v2/tests/unit/test_xai_extensions.py` | 1 | `test_blocks` |
| `backend_v2/tests/unit/workers/test_synthesis_reducers.py` | 1 | `test_handle_synthesis_failure_state_none_profile` |
| **TOTAL** | 54 | |

## Environment-Gated Skips
13 sites in 7 files.

| File | Sites | Disposition |
| :--- | :--- | :--- |
| `backend_v2/tests/integration/test_tavily_live.py` | 3 | Retained |
| `backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py` | 3 | Retained |
| `backend_v2/tests/integration/test_integration_real_llm.py` | 2 | Retained |
| `backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py` | 2 | Retained |
| `backend_v2/tests/integration/test_e2e_orchestration.py` | 1 | Retained |
| `backend_v2/tests/integration/test_sdui_semantic_parity.py` | 1 | Retained |
| `backend_v2/tests/unit/test_document_extraction.py` | 1 | Retained |
| **TOTAL** | 13 | |
