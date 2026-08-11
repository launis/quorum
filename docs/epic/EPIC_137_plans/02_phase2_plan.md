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
<objective>Phase 2: Dead Code Eradication (Code + Tests Atomically)</objective>
<action>Start session via `/tier5-resume`.</action>
<constraint invariant="atomic_data_test_migration">Dead code methods and their corresponding tests MUST be deleted in the SAME phase to prevent a broken test suite between phases. Splitting them across phases violates the Atomic Data & Test Migration mandate.</constraint>
<demolish>REMOVE: `compile_xml_rubrics` entirely from `@[c:\src\quorum\backend_v2\services\orchestrator\localization_compiler.py#L80-L208]`.</demolish>
<demolish>REMOVE: `compile_xml_rubrics` entirely from `@[c:\src\quorum\backend_v2\services\orchestrator\prompt_compiler.py#L67-L80]`.</demolish>
<demolish>REMOVE: `compile_chunk_prompt` entirely from `@[c:\src\quorum\backend_v2\services\orchestrator\prompt_compiler_adapter.py#L31-L127]`.</demolish>
<action>Delete `compile_xml_rubrics()` from `@[c:\src\quorum\backend_v2\services\orchestrator\localization_compiler.py]` and `@[c:\src\quorum\backend_v2\services\orchestrator\prompt_compiler.py]`. **USER PERMISSION GRANTED to modify prompt_compiler.py** (dead code verified: zero production callers outside its own definition and the dead `compile_chunk_prompt` method).</action>
<action>Delete `compile_chunk_prompt()` from `@[c:\src\quorum\backend_v2\services\orchestrator\prompt_compiler_adapter.py]`.</action>
<action>Delete corresponding dead tests from `@[c:\src\quorum\backend_v2\tests\unit\services\orchestrator\test_prompt_compiler_adapter.py]` and `@[c:\src\quorum\backend_v2\tests\unit\services\orchestrator\test_localization_compiler.py]` and `@[c:\src\quorum\backend_v2\tests\unit\services\orchestrator\strategies\test_prompt_compiler_schema_strictness.py]` and `@[c:\src\quorum\backend_v2\tests\integration\test_prompt_compiler.py]`.</action>
<action>Run `uv run python scripts/backend_audit_loop.py backend_v2 --test` to confirm no import errors from removed methods.</action>
<action>Execute `/tier5-session-handover` to flush context window and prepare for Phase 3.</action>
<validation_gate>Ensure backend_audit_loop.py passes flawlessly.</validation_gate>
</system_prompt>
</execution_protocol>
