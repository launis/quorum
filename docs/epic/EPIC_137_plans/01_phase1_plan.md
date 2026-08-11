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
<action>Run a Python audit script to identify all matrix opaque IDs and their line numbers: `uv run python -c "import json; data=json.load(open('backend_v2/seed/seed_data.json')); blocks=[b for b in data.get('prompt_blocks',[]) if b.get('category_id')=='matrix']; [print(b['id'], b.get('slug','')) for b in blocks]"`. Use these IDs for bounded MCP edits on `@[c:\src\quorum\backend_v2\seed\seed_data.json]`.</action>
<action>Using bounded `multi_replace_file_content`, update the `tone_instruction` for the output profile `prf_5d6e7f8091a2b3c4` to the Senior Executive Coach persona in `@[c:\src\quorum\backend_v2\seed\seed_data.json]`.</action>
<action>Using `search_web` to verify canonical citations for ALL 13 matrices, then apply individual bounded `multi_replace_file_content` edits to standardize `theory_grounding.citation_reference` fields into strict English APA format (Author (Year). Title. Publisher.) in `@[c:\src\quorum\backend_v2\seed\seed_data.json]`.</action>
<action>Using bounded `multi_replace_file_content`, clean up `ai_description` by stripping obsolete `RULES:` blocks for ALL matrices that contain them in `@[c:\src\quorum\backend_v2\seed\seed_data.json]`.</action>
<action>Verify JSON syntax after each batch of mutations: `uv run python -c "import json; json.load(open('backend_v2/seed/seed_data.json')); print('JSON OK')"`. If JSON is broken, immediately restore backup and STOP.</action>
<action>Execute `/tier5-session-handover` to flush context window and prepare for Phase 2.</action>
<constraint invariant="context_amnesia_prevention">Do NOT proceed to Dead Code Purge in the same session, as modifying 6 files violates the max-5 file limit.</constraint>
<validation_gate>Ensure run_seed.py validates all seed changes without errors.</validation_gate>
</system_prompt>
</execution_protocol>
