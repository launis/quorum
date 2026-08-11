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
<action>Update ALL existing `AsyncMock` implementations for `ExtractiveSensorService` across the test suite to support the new signature.</action>
<action>Write explicit negative tests in `@[c:\src\quorum\backend_v2\tests\unit\services\orchestrator\test_extractive_sensor_service.py]`: 1) Evaluate handling when `theory_grounding` is missing/null. 2) Evaluate strict bypass when `allow_contextual_override` is strictly set to `False`.</action>
<action>Run `uv run python scripts/backend_audit_loop.py backend_v2 --test` to mathematically prove all Python schemas, imports, and tests pass.</action>
<action>If successful, commit seed data: `uv run python backend_v2/seed/run_seed.py local`</action>
<validation_gate>Ensure backend_audit_loop.py passes flawlessly and ExtractiveSensorService tests pass with missing theory_grounding.</validation_gate>
</system_prompt>
</execution_protocol>
