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
<objective>Phase 4: TDA Pipeline Rewiring</objective>
<action>Start session via `/tier5-resume`.</action>
<demolish>REMOVE: `getattr(b, "category_id", None)` in `llm.py` and REPLACE WITH: `b.category_id`.</demolish>
<action>Modify `@[c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py]` to inject the `MatrixEvaluationContext` into the `EngineExecutionRequest` before triggering the `TDAEngine`. Also fix the `getattr(b, "category_id", None)` to use direct attribute access `b.category_id` (violates `the_zero_compromise_pledge` ban on `getattr(obj, key, default)`).</action>
<action>Modify `@[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py]` to pass the `request.matrix_context` to `dag_executor.execute_graph`.</action>
<action>Safely update `execute_graph()` in `@[c:\src\quorum\backend_v2\services\orchestrator\enriched_dag_executor.py]` to accept `matrix_context: MatrixEvaluationContext | None = None` (Python 3.14 modern syntax) and forward it.</action>
<action>Execute `/tier5-session-handover` to flush context window and prepare for Phase 5.</action>
<validation_gate>Ensure backend_audit_loop.py passes flawlessly.</validation_gate>
</system_prompt>
</execution_protocol>
