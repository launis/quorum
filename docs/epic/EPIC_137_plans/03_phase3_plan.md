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
<objective>Phase 3: DTO Strictness & Engine Metadata Wiring</objective>
<action>Start session via `/tier5-resume`.</action>
<constraint invariant="schema_convergence_mandate">Do NOT create TheoryGroundingDTO — reuse the existing `TheoryGrounding` model from `@[c:\src\quorum\backend_v2\models\v2_core.py#L187-L198]`. Do NOT create MatrixClaimRuleDTO — per-claim metadata already flows through the existing `FlattenedAtom` model from `@[c:\src\quorum\backend_v2\models\dtos\engine.py#L21-L38]`. One Concept = One Schema.</constraint>
<action>Define a strict `MatrixEvaluationContext` Pydantic V2 DTO in `@[c:\src\quorum\backend_v2\models\dtos\engine.py]` with `ConfigDict(strict=True, extra='forbid', frozen=True)` to hold `theory_grounding: TheoryGrounding | None` (reusing existing model from `v2_core.py`), `matrix_objective: str | None`, and `allow_contextual_override: bool`. CRITICAL: This class MUST be defined structurally BEFORE `EngineExecutionRequest`.</action>
<action>Add `matrix_context: MatrixEvaluationContext | None = None` to `EngineExecutionRequest` in `@[c:\src\quorum\backend_v2\models\dtos\engine.py]`.</action>
<constraint invariant="domain_model_purity_mandate">Do NOT modify `ExtractedAtom` in `@[c:\src\quorum\backend_v2\models\dtos\dag_models.py]`. It must remain a pure data carrier. Rules MUST be passed strictly via Context Injection.</constraint>
<action>Execute `/tier5-session-handover` to flush context window and prepare for Phase 4.</action>
<validation_gate>Ensure backend_audit_loop.py passes flawlessly.</validation_gate>
</system_prompt>
</execution_protocol>
