<execution_protocol>
<required_context_rules>
- @[c:\src\quorum\.agents\rules\00-antigravity-core.md]
- @[c:\src\quorum\.agents\rules\01-python-backend.md]
- @[c:\src\quorum\.agents\rules\03_seed_vault.md]
- @[c:\src\quorum\.agents\rules\04_directory_reference.md]
- @[c:\src\quorum\.agents\rules\05_llm_architecture.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\god_code_prevention\artifacts\ki_god_code_prevention.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\dag_engine_dto_projection_rules\artifacts\ki_dag_engine_dto_projection_rules.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\agent_context_quarantine\artifacts\ki_agent_context_quarantine.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\llm_extraction_architecture\artifacts\ki_llm_extraction_architecture.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\execution_engine_protocol\artifacts\ki_execution_engine_protocol.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\domain_model_prompt_separation\artifacts\ki_domain_model_prompt_separation.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\tripartite_pipeline_architecture\artifacts\ki_tripartite_pipeline_architecture.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\context_enriched_pipeline\artifacts\ki_context_enriched_decompose_verify.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\de_generator_execution_paradigm\artifacts\ki_de_generator_execution_paradigm.md]
</required_context_rules>
<system_prompt>
<objective>Phase 6: Negative Testing & Mocks & Final Audit</objective>
<action>Start session via `/tier5-resume`.</action>
<action>Refactor `ExtractiveSensorService.pre_evaluate`, `_batch_fuzzy_match`, and `batch_pre_evaluate` in `@[c:\src\quorum\backend_v2\services\orchestrator\extractive_sensor_service.py]` to accept `allow_contextual_override: bool = False`. If True, `pre_evaluate` MUST return `PreFlightResult(decided=False)` instead of failing early for missing anchors, delegating the decision to the LLM.</action>
<action>Update `EnrichedDagExecutor.execute_graph` in `@[c:\src\quorum\backend_v2\services\orchestrator\enriched_dag_executor.py]` to pass `matrix_context.allow_contextual_override if matrix_context else False` down to `batch_pre_evaluate`.</action>
<action>Update `BooleanEvaluationResult` inside `ExtractiveSensorService.evaluate_atom_boolean_batch` to include `contextual_override: Annotated[bool | None, Field(default=None, description="True if bypass was used.")] = None`.</action>
<action>Write explicit negative tests in `@[c:\src\quorum\backend_v2\tests\unit\services\orchestrator\test_extractive_sensor_service.py]`: 1) Evaluate graceful handling when `theory_grounding` is missing/null. 2) Evaluate pre-flight bypass when `allow_contextual_override` is strictly set to `False` vs `True`.</action>
<action>Run `uv run python scripts/backend_audit_loop.py backend_v2 --test` to mathematically prove all Python schemas, imports, and tests pass.</action>
<action>If successful, commit seed data: `uv run python backend_v2/seed/run_seed.py local`</action>
<validation_gate>Ensure backend_audit_loop.py passes flawlessly and ExtractiveSensorService tests pass with missing theory_grounding.</validation_gate>
</system_prompt>
</execution_protocol>
