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

<action>
### `c:\src\quorum\backend_v2\models\dtos\engine.py`
#### [MODIFY]
- Add `matrix_assertions: list[FlattenedAtom] | None = Field(default=None)` to the `MatrixEvaluationContext` class. This is required because `LinkedAtomGraph/ExtractedAtom` strips the `extraction_rule` and `anchor_target`, so the orchestrator must pass the raw Matrix constraints down via the context.
</action>

<action>
### `c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py`
#### [MODIFY]
- In `TDAEngine.execute()`, when preparing to execute a matrix (`if request.shuffled_atoms:`), mutate the `MatrixEvaluationContext` to attach the assertions before passing it to `dag_executor.execute_graph()`:
  `matrix_context = request.matrix_context.model_copy(update={"matrix_assertions": request.shuffled_atoms}) if request.matrix_context else None`
</action>

<action>
### `c:\src\quorum\backend_v2\services\orchestrator\prompts\matrix_sensor_prompt_builder.py`
#### [NEW]
Create a new pure builder class (`MatrixSensorPromptBuilder`).
- The builder receives `MatrixEvaluationContext` (which will now contain the `matrix_assertions` list of `FlattenedAtom` objects for per-claim extraction_rule, anchor_target, is_inverse). It maps the ExtractedAtom's `tda_id` to the corresponding `FlattenedAtom` for injection.
- The builder MUST expose two separate methods: `build_static_system_messages()` (for 100% cacheable instructions AND the massive `<context>` source text, strictly as a `system` role message) and `build_dynamic_user_messages()` (for the `<tda_validation>` per-claim data, strictly as a `user` role message). This prevents consecutive-user-message API rejections and guarantees Vertex caching prefix parity.
</action>
<constraint invariant="llm_kv_caching_maximization">You MUST use `PromptBlock` assembly for the prompt structure. Raw XML `f-string` concatenation is strictly forbidden. Dynamic variables inside the System Message are strictly forbidden.</constraint>

<action>
### `c:\src\quorum\backend_v2\services\orchestrator\extractive_sensor_service.py`
#### [MODIFY]
- Modify `evaluate_atom_boolean_batch` to delegate generation to this new builder.
- Call `MatrixSensorPromptBuilder.build_static_system_messages(context_text, matrix_context)` to generate the system messages.
- Call `MatrixSensorPromptBuilder.build_dynamic_user_messages(nodes, alias_to_tda_id, matrix_context)` to generate the user messages containing the `<claim>` XML block.
- Pass `messages=static_messages + dynamic_messages` to `executor.execute_structured_task()`.
- Remove the inline prompt string concatenations (lines 308-314).
</action>

<action>
### `c:\src\quorum\backend_v2\services\orchestrator\enriched_dag_executor.py`
#### [MODIFY]
- Update `batch_evaluation_callback` to use `MatrixSensorPromptBuilder.build_static_system_messages(source_text, matrix_context)` to construct the `CompiledPrompt.static_messages`.
- This ensures the heavy `source_text` is placed in the `system` role and exactly matches the execution prefix, achieving 100% cache survival and resolving the duplication anti-pattern (lines 138-142).
</action>

<action>Execute `/tier5-session-handover` to flush context window and prepare for Phase 6.</action>
<validation_gate>Ensure backend_audit_loop.py passes flawlessly.</validation_gate>
</system_prompt>
</execution_protocol>
