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
<objective>Phase 5: Sensor Prompt Re-Architecture</objective>
<action>Start session via `/tier5-resume`.</action>
<action>Create a new pure builder class in `@[c:\src\quorum\backend_v2\services\orchestrator\prompts\matrix_sensor_prompt_builder.py]`. This directory already contains `atom_extraction.py` and `graph_linking.py`, confirming it is the correct location for prompt builder logic.</action>
<constraint invariant="llm_kv_caching_maximization">You MUST use `PromptBlock` assembly for the prompt structure. Raw XML `f-string` concatenation is strictly forbidden. The builder MUST expose two separate methods: `build_static_system_prompt()` (for 100% cacheable instructions) and `build_dynamic_user_payload()` (for the `<tda_validation>` per-claim data). Dynamic variables inside the System Message are strictly forbidden.</constraint>
<action>The builder receives `MatrixEvaluationContext` (for theory_grounding, objective, override flag) and the `FlattenedAtom` list (for per-claim extraction_rule, anchor_target, is_inverse). It maps the FlattenedAtom's `atom_id` to the corresponding `LinkedAtomGraph` node for injection.</action>
<action>Modify `evaluate_atom_boolean_batch` in `@[c:\src\quorum\backend_v2\services\orchestrator\extractive_sensor_service.py]` to delegate generation to this new builder, constructing separated System and User messages.</action>
<action>Modify `batch_evaluation_callback` in `@[c:\src\quorum\backend_v2\services\orchestrator\enriched_dag_executor.py]` to also use this new builder for cache pre-warming, ensuring prompt prefix parity and resolving the duplicate prompt anti-pattern (currently duplicated at `extractive_sensor_service.py:308-312` and `enriched_dag_executor.py:138-142`).</action>
<action>Execute `/tier5-session-handover` to flush context window and prepare for Phase 6.</action>
<validation_gate>Ensure backend_audit_loop.py passes flawlessly.</validation_gate>
</system_prompt>
</execution_protocol>
