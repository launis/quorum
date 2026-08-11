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
<objective>Phase 1: Database Snapshot & Seed Hygiene</objective>
<action>Execute PowerShell commands to safely backup data: `New-Item -ItemType Directory -Force -Path backend_v2/seed/backups; Copy-Item backend_v2/seed/seed_data.json -Destination backend_v2/seed/backups/seed_data_pre_epic137.json`</action>
<constraint invariant="live_database_mutation">All structural data modifications MUST occur purely in the master source file before sync.</constraint>
<constraint invariant="inline_terminal_scripting">Per `03_seed_vault.md`, disposable Python mutation scripts are STRICTLY PROHIBITED. ALL seed mutations MUST use the native MCP `multi_replace_file_content` tool with bounded line ranges. Python scripts are ONLY allowed for READ/VERIFY operations (identifying line numbers, validating JSON syntax).</constraint>
<action>Using bounded `multi_replace_file_content`, update the `tone_instruction` for the output profile `prf_5d6e7f8091a2b3c4` in `@[c:\src\quorum\backend_v2\seed\seed_data.json]`. 
Set EN to: "Act as a Senior Executive Coach. Provide deep, provocative, and strategic analysis rather than merely listing data."
Set FI to: "Toimi ylemmän johdon valmentajana (Senior Executive Coach). Tarjoa syvällistä, provosoivaa ja strategista analyysiä pelkän datan luettelemisen sijaan."
</action>
<action>Apply bounded `multi_replace_file_content` edits to standardize `theory_grounding.citation_reference` fields into strict English APA format in `@[c:\src\quorum\backend_v2\seed\seed_data.json]`. Use these exact pre-verified citations (do NOT use search_web):
- blk_440a5fef9331451b: "Toulmin, S. E. (2003). The uses of argument. Cambridge University Press."
- blk_f921c7c0989b47e8: "Anderson, L. W., & Krathwohl, D. R. (Eds.). (2001). A taxonomy for learning, teaching, and assessing: A revision of Bloom's taxonomy of educational objectives. Longman."
- blk_109dab5b6b3f403a: "Kahneman, D. (2011). Thinking, fast and slow. Farrar, Straus and Giroux."
- blk_53f32679aa514fcb: "Stumborg, M. F., et al. (2022). Goodhart's law."
- blk_fb15f8dcf23f4865: "ARMA International. (2017). Generally Accepted Recordkeeping Principles."
- blk_c5804a9143c34cb1: "Pearl, J., & Mackenzie, D. (2018). The book of why: The new science of cause and effect. Basic Books."
- blk_b476f89fb732448c: "Popper, K. (1963). Conjectures and refutations: The growth of scientific knowledge. Routledge."
- blk_ff72c2d79edb4ebf: "Deming, W. E. (1986). Out of the crisis. MIT Center for Advanced Engineering Study."
- blk_6b8c766185294f7e: "DARPA. (2017). Explainable artificial intelligence (XAI). Defense Advanced Research Projects Agency."
- blk_80732a33fe1947ee: "OWASP Foundation. (2025). OWASP Top 10 for Large Language Model Applications."
- blk_c3bc5f3eb8e74110: "Pearl, J., & Mackenzie, D. (2018). The book of why: The new science of cause and effect. Basic Books."
- blk_f6e286f050c94d60: "Lipton, Z. C. (2018). The mythos of model interpretability. Communications of the ACM, 61(10), 36-43."
- blk_22e3598e06414409: "Kahneman, D. (2011). Thinking, fast and slow. Farrar, Straus and Giroux; Floridi, L. (2014). The 4th revolution: How the infosphere is reshaping human reality. Oxford University Press."
</action>
<action>Using bounded `multi_replace_file_content`, clean up `ai_description` by stripping obsolete `RULES:` blocks for ONLY the 9 matrices that contain them in `@[c:\src\quorum\backend_v2\seed\seed_data.json]` (blk_440a5fef9331451b, blk_f921c7c0989b47e8, blk_109dab5b6b3f403a, blk_53f32679aa514fcb, blk_fb15f8dcf23f4865, blk_c5804a9143c34cb1, blk_b476f89fb732448c, blk_ff72c2d79edb4ebf, blk_6b8c766185294f7e). Do not modify the rest of the description.</action>
<action>Verify JSON syntax after each batch of mutations: `uv run python -c "import json; json.load(open('backend_v2/seed/seed_data.json')); print('JSON OK')"`. If JSON is broken, immediately restore backup and STOP.</action>
<action>Execute `/tier5-session-handover` to flush context window and prepare for Phase 2.</action>
<constraint invariant="context_amnesia_prevention">Do NOT proceed to Dead Code Purge in the same session, as modifying 6 files violates the max-5 file limit.</constraint>
<validation_gate>Ensure run_seed.py validates all seed changes without errors.</validation_gate>

<anti_targets>
  - Do NOT modify the raw extraction prompt in ExtractiveSensorService with hardcoded XML strings.
  - Do NOT use generic kwargs to pass matrix metadata into dag_executor.
  - Do NOT map the new forensic metadata fields to the Flutter UI DTOs.
  - Do NOT inject dynamic claim variables into the System Prompt Builder (destroys Prefix Caching).
</anti_targets>

<dod_checklist>
  - [ ] Matrix output profile tone updated.
  - [ ] Theory grounding citations in seed_data updated to exact APA format via manual search verification and hardcoded dictionary.
  - [ ] Obsolete ai_descriptions cleared of RULES blocks via safe string splitting.
  - [ ] Dead prompt compiler methods deleted.
  - [ ] MatrixEvaluationContext DTO created strictly, reusing existing TheoryGrounding from v2_core.py and existing FlattenedAtom from engine.py. No new duplicate schemas created.
  - [ ] LLMNodeStrategy updated with safe DI to inject MatrixEvaluationContext.
  - [ ] MatrixSensorPromptBuilder created for STATIC system prompts only.
  - [ ] ExtractiveSensorService updated to inject DYNAMIC rules into User Prompts.
  - [ ] All async mocks updated and negative tests passed.
  - [ ] Backend audit loop and seed generation script passed.
</dod_checklist>
</system_prompt>
</execution_protocol>
