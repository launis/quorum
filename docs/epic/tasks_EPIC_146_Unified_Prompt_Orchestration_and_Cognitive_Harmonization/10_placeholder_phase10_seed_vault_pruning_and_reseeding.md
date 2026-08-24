# Phase 10: Seed Vault Pruning & Database Reseeding

**Overview:** Execute Python audit script proving candidate blocks are 100% covered by `GLOBAL_MANDATES_XML`, prune verified redundant global mandate blocks from `criteria_block_ids` in `seed_data.json` across 12 steps (105 references total), fix corrupted HTML entity (`&lt;mechanical_anchors&gt;` -> `<mechanical_anchors>`), establish seed guardrail tests in `test_ast_prompt_xml_sovereignty.py`, and reseed the database.

**Target Files:**
- `[MODIFY]` @[backend_v2/seed/seed_data.json#L6705-L8649]
- `[MODIFY]` @[backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py#L240-L245]

**Context Files:**
- `[CONTEXT]` @[backend_v2/models/prompts/global_mandates.py#L7-L161]
- `[CONTEXT]` @[backend_v2/seed/seed_registry.py#L43-L54]
- `[CONTEXT]` @[backend_v2/seed/run_seed.py#L101-L222]
- `[CONTEXT]` @[backend_v2/tests/unit/test_ast_matrix_claim_guardrails.py#L132-L260]

Source: @[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md#L386-L392] Phase 10: Seed Vault Pruning & Database Reseeding

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify baseline state from Phase 9 in @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart] and @[client_app_v2/lib/features/studio/views/step_builder_view.dart]. Confirm that UI forms are fully modernized for Zero-XML entry and Layer 1 global mandates are automatically applied by the compiler foundation.</action>
    <action>Look forward: Verify requirements for Phase 10 in @[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md] and ensure that pruning redundant global mandate blocks from individual step `criteria_block_ids` in @[backend_v2/seed/seed_data.json] preserves all step-specific task directives, matrix blocks, heuristics, principles, and protocols.</action>
    <constraint invariant="zero_legacy_state_support">Zero tolerance for legacy fallback bridges or un-audited database states. All database state is ephemeral and backed by seed_data.json.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [x] Programmatic redundancy verification script executed in `scratch/verify_redundancy.py` proving all 17 candidate blocks are 100% subsumed and covered by Layer 1 `GLOBAL_MANDATES_XML`.
    - [x] Exact timestamped backup of @[backend_v2/seed/seed_data.json] created in `backend_v2/seed/backups/seed_data_<timestamp>.json` prior to any structural file mutations.
    - [x] 17 verified redundant global mandate block IDs (105 total references across 12 steps) pruned from `criteria_block_ids` in @[backend_v2/seed/seed_data.json] while strictly preserving step-specific criteria, matrix blocks, task definitions, and runtime variable blocks.
    - [x] Corrupted HTML entity `&lt;mechanical_anchors&gt;` on line 6705 of `seed_data.json` fixed to `<mechanical_anchors>`.
    - [x] 4 new AST/Seed guardrail test cases (2 positive seed checks + 2 negative mock AST/data tests) established in `test_ast_prompt_xml_sovereignty.py` verifying zero redundant mandate criteria in steps and zero corrupted XML entities in seed prompt blocks.
    - [x] JSON schema and blueprint integrity verified: all AST and seed guardrail tests in `test_ast_matrix_claim_guardrails.py` and `test_ast_prompt_xml_sovereignty.py` pass.
    - [x] Database re-seeded cleanly via `uv run python backend_v2/seed/run_seed.py local`.
    - [x] Full backend audit loop passes with 0 errors: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_testing.md]</knowledge_item>
    <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_matrix_boolean_evaluation_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_synthesis_payload_compression.md]</knowledge_item>
    <knowledge_item>@[ki_context_enriched_pipeline.md]</knowledge_item>
    <knowledge_item>@[ki_strict_sdui_serialization.md]</knowledge_item>
    <knowledge_item>@[ki_polymorphic_rule_routing.md]</knowledge_item>
    <knowledge_item>@[ki_sdui_adapter_pattern.md]</knowledge_item>
    <knowledge_item>@[ki_neuro_symbolic_agentic_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
  </required_context_rules>

  <touched_artifacts>
    <backend>@[backend_v2/seed/seed_data.json]</backend>
    <backend>@[backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT prune required step-specific task directives (specifically: `block_taskfactauditor`, `block_taskanalyst`, `block_taskfalsifier`, `block_taskjudge`, `block_tasklogician`, `block_taskoverseer`, `block_taskprofiler`, `analytical_synthesis`, `block_taskarchivist`, `block_taskcausal`, `block_taskcoach`, `block_taskperformativity`) or primary matrix blocks (`matrix_kahneman`, `matrix_bloom`, `matrix_causal_analyst`, `matrix_goodhart`, `matrix_archivist`, `matrix_falsifier`, `matrix_taskguard`, `matrix_judge`, `matrix_toulmin`, `matrix_taskxai_clarity`, `matrix_causal_abductive`, `matrix_xai_reporter`).
    - Do NOT delete candidate `prompt_blocks` definitions from the `prompt_blocks` array in `seed_data.json`; only prune their redundant assignment from `criteria_block_ids` within individual steps.
    - Do NOT modify `db_v2.json` directly.
    - Do NOT use ad-hoc terminal patching scripts (`python -c` or `sed`) to mutate `seed_data.json`; execute modifications via surgical native editing tools (`multi_replace_file_content`).
  </anti_targets>

  <step id="1" name="Seed Vault Backup &amp; Programmatic Redundancy Audit">
    <action>Execute timestamped backup of @[backend_v2/seed/seed_data.json] to `backend_v2/seed/backups/` using PowerShell:
      ```powershell
      New-Item -ItemType Directory -Force -Path backend_v2/seed/backups ; Copy-Item backend_v2/seed/seed_data.json -Destination "backend_v2/seed/backups/seed_data_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
      ```
    </action>
    <action>Execute Python redundancy verification script in `scratch/verify_redundancy.py` against `GLOBAL_MANDATES_XML` in @[backend_v2/models/prompts/global_mandates.py] proving that all 17 candidate blocks are 100% subsumed:
      - `block_headermandates` (`blk_bd7c5a9f27504a2c`) -> Subsumed by `<global_system_mandates>` header.
      - `block_mandate2` (`blk_9d68ceff695b4196`) -> Subsumed by `ANTI_SCORE_MANDATE` (`<anti_score_mandate>`).
      - `block_mandate3` (`blk_23ca73cf267d4078`) -> Subsumed by `ANTI_ID_MANDATE` (`<anti_id_mandate>`).
      - `block_mandate5` (`blk_2cbe96bffde04571`) -> Subsumed by `SEMANTIC_BLEED_MANDATE` (`<semantic_bleed_mandate>`), `NULL_HYPOTHESIS_MANDATE` (`<null_hypothesis_mandate>`), and `VERBATIM_EXTRACTION_MANDATE` (`<verbatim_extraction_mandate>`).
      - `block_headerrules` (`blk_f2cb51b5d074419a`) -> Subsumed by Layer 1 Mandates.
      - `block_rule1` (`blk_665b2e223f214564`) -> Subsumed by Layer 1 Zero-Trust Perimeter & Verbatim Extraction.
      - `block_rule2` (`blk_78d110eb0bad4541`) -> Subsumed by Layer 1 Jurisdictional Boundaries & Semantic Bleed.
      - `block_rule3` (`blk_cc852aa44a1a464e`) -> Subsumed by Layer 1 Substance Over Form & Epistemic Glossary.
      - `block_rule4` (`blk_04544fa8b5ca408f`) -> Subsumed by Layer 1 Process Integrity & Null Hypothesis.
      - `block_rule5` (`blk_c1cc56f65f6a47e1`) -> Subsumed by Layer 1 Epistemic Humility & Glossary.
      - `block_rule6` (`blk_e71bcbeb90244b37`) -> Subsumed by Layer 1 Falsification & Verbatim Extraction.
      - `block_oprule1` (`blk_080a729c8b974492`) -> Subsumed by Layer 1 Factuality & Grounding (`<verbatim_extraction_mandate>`).
      - `block_oprule2` (`blk_5b5f6faf0144401f`) -> Subsumed by `CONTEXT_SEGREGATION_MANDATE` (`<context_segregation_mandate>`).
      - `block_oprule3` (`blk_6a02268ad79542de`) -> Subsumed by Layer 1 Evidence-Claim Distinction & Verbatim Quotes.
      - `block_instructionnohallucination` (`blk_71b84ce7c6554639`) -> Subsumed by `VERBATIM_EXTRACTION_MANDATE` and `NULL_HYPOTHESIS_MANDATE`.
      - `block_instructionlanguage_dynamic` (`blk_a5ce16009a514628`) -> Subsumed by `LANGUAGE_MANDATE` (`<language_mandate>`).
      - `block_headerinstructions` (`blk_091db241c5154336`) -> Subsumed by `CONTEXT_SEGREGATION_MANDATE` and Layer 1 Execution Instructions.
    </action>
    <constraint invariant="ai_context_amnesia_guard">All inspection of seed_data.json must be executed through bounded reads or deterministic Python scripts.</constraint>
  </step>

  <step id="2" name="Vault Pruning &amp; HTML Entity Repair">
    <action>Surgically prune the 17 verified redundant global mandate block IDs from `criteria_block_ids` in @[backend_v2/seed/seed_data.json] across the following 12 steps:
      1. `sp_b5c751d1cbe24735` (`sp_1624bd0454c9425e`) [Lines 7990-8006]: Prune 8 IDs (`blk_bd7c5a9f27504a2c`, `blk_f2cb51b5d074419a`, `blk_665b2e223f214564`, `blk_78d110eb0bad4541`, `blk_6a02268ad79542de`, `blk_71b84ce7c6554639`, `blk_a5ce16009a514628`, `blk_091db241c5154336`). Retain remaining 7 step-specific criteria and matrix blocks (`blk_9e44687dff884ff6`, `blk_f27f6d04c1f74257`, `blk_44b0c6cc5ec24151`, `blk_1ca6f187c5b04d2b`, `blk_3cc672a8038144e0`, `blk_280fd9eb2f2543f6`, `blk_109dab5b6b3f403a`).
      2. `sp_f22db9f1dde048b7` (`sp_2a81cb9e3e4b4694`) [Lines 8049-8060]: Prune 7 IDs (`blk_bd7c5a9f27504a2c`, `blk_2cbe96bffde04571`, `blk_f2cb51b5d074419a`, `blk_c1cc56f65f6a47e1`, `blk_71b84ce7c6554639`, `blk_a5ce16009a514628`, `blk_091db241c5154336`). Retain remaining 3 step-specific criteria and matrix blocks (`blk_9e44687dff884ff6`, `blk_3744757fbff44175`, `blk_f921c7c0989b47e8`).
      3. `sp_bd0b3054fe664960` (`step_causal_analyst`) [Lines 8102-8116]: Prune 7 IDs (`blk_bd7c5a9f27504a2c`, `blk_2cbe96bffde04571`, `blk_f2cb51b5d074419a`, `blk_c1cc56f65f6a47e1`, `blk_71b84ce7c6554639`, `blk_a5ce16009a514628`, `blk_091db241c5154336`). Retain remaining 6 step-specific criteria and matrix blocks (`blk_3568312503964aec`, `blk_cb6217bccc974cca`, `blk_9e44687dff884ff6`, `blk_3cc672a8038144e0`, `blk_43e297666d3b4359`, `blk_c5804a9143c34cb1`).
      4. `sp_25664f44773a4354` (`sp_744ca2e40b51424b`) [Lines 8158-8185]: Prune 16 IDs (`blk_bd7c5a9f27504a2c`, `blk_9d68ceff695b4196`, `blk_23ca73cf267d4078`, `blk_2cbe96bffde04571`, `blk_f2cb51b5d074419a`, `blk_665b2e223f214564`, `blk_78d110eb0bad4541`, `blk_cc852aa44a1a464e`, `blk_04544fa8b5ca408f`, `blk_c1cc56f65f6a47e1`, `blk_e71bcbeb90244b37`, `blk_080a729c8b974492`, `blk_5b5f6faf0144401f`, `blk_6a02268ad79542de`, `blk_a5ce16009a514628`, `blk_091db241c5154336`). Retain remaining 10 step-specific criteria and matrix blocks (`blk_9e44687dff884ff6`, `blk_2c13f67014094f3b`, `blk_fb0b98da76e046dd`, `blk_cb6217bccc974cca`, `blk_3568312503964aec`, `blk_8b6e5fba923642f2`, `blk_5d26dff39e574d5f`, `blk_2305f4ac865a4815`, `blk_0217b0b725b54b10`, `blk_53f32679aa514fcb`).
      5. `sp_7f9649114d2344dc` (`step_performativity_detector`) [Lines 8227-8239]: Prune 7 IDs (`blk_bd7c5a9f27504a2c`, `blk_2cbe96bffde04571`, `blk_f2cb51b5d074419a`, `blk_c1cc56f65f6a47e1`, `blk_71b84ce7c6554639`, `blk_a5ce16009a514628`, `blk_091db241c5154336`). Retain remaining 4 step-specific criteria and matrix blocks (`blk_9e44687dff884ff6`, `blk_3cc672a8038144e0`, `blk_b4912f9ff3a24b31`, `blk_fb15f8dcf23f4865`).
      6. `sp_6f40b964895c426b` (`sp_d948cb51bed3454c`) [Lines 8284-8298]: Prune 8 IDs (`blk_04544fa8b5ca408f`, `blk_bd7c5a9f27504a2c`, `blk_2cbe96bffde04571`, `blk_f2cb51b5d074419a`, `blk_c1cc56f65f6a47e1`, `blk_71b84ce7c6554639`, `blk_a5ce16009a514628`, `blk_091db241c5154336`). Retain remaining 5 step-specific criteria and matrix blocks (`blk_ab65a936bca34bf1`, `blk_9e44687dff884ff6`, `blk_3cc672a8038144e0`, `blk_90d0dd098757433e`, `blk_b476f89fb732448c`).
      7. `sp_ddb7cf7c8a0245d4` (`sp_b080d22fcc2f4ff0`) [Lines 8342-8356]: Prune 8 IDs (`blk_bd7c5a9f27504a2c`, `blk_2cbe96bffde04571`, `blk_f2cb51b5d074419a`, `blk_665b2e223f214564`, `blk_78d110eb0bad4541`, `blk_5b5f6faf0144401f`, `blk_a5ce16009a514628`, `blk_091db241c5154336`). Retain remaining 5 step-specific criteria and matrix blocks (`blk_9e44687dff884ff6`, `blk_f27f6d04c1f74257`, `blk_6e08842eae9146a2`, `blk_608ba7099d07428f`, `blk_80732a33fe1947ee`).
      8. `sp_48974af1fc584407` (`sp_282a7b15f76d4c9e`) [Lines 8400-8415]: Prune 7 IDs (`blk_6a02268ad79542de`, `blk_bd7c5a9f27504a2c`, `blk_9d68ceff695b4196`, `blk_23ca73cf267d4078`, `blk_2cbe96bffde04571`, `blk_a5ce16009a514628`, `blk_091db241c5154336`). Retain remaining 7 step-specific criteria and matrix blocks (`blk_a93c517915f94e09`, `blk_9e44687dff884ff6`, `blk_2c13f67014094f3b`, `blk_fb0b98da76e046dd`, `blk_f971def5b3864ba4`, `blk_2305f4ac865a4815`, `blk_ff72c2d79edb4ebf`).
      9. `sp_8daee218c6b14f02` (`sp_b7aea7179c1b4193`) [Lines 8457-8471]: Prune 7 IDs (`blk_bd7c5a9f27504a2c`, `blk_2cbe96bffde04571`, `blk_f2cb51b5d074419a`, `blk_cc852aa44a1a464e`, `blk_71b84ce7c6554639`, `blk_a5ce16009a514628`, `blk_091db241c5154336`). Retain remaining 6 step-specific criteria and matrix blocks (`blk_9e44687dff884ff6`, `blk_3cc672a8038144e0`, `blk_280fd9eb2f2543f6`, `blk_652fce41dcb54793`, `blk_2305f4ac865a4815`, `blk_440a5fef9331451b`).
      10. `sp_dfc365994fa944b2` (`sp_76b0dbf44e36495e`) [Lines 8513-8541]: Prune 17 IDs (`blk_bd7c5a9f27504a2c`, `blk_9d68ceff695b4196`, `blk_23ca73cf267d4078`, `blk_2cbe96bffde04571`, `blk_f2cb51b5d074419a`, `blk_665b2e223f214564`, `blk_78d110eb0bad4541`, `blk_cc852aa44a1a464e`, `blk_04544fa8b5ca408f`, `blk_c1cc56f65f6a47e1`, `blk_e71bcbeb90244b37`, `blk_080a729c8b974492`, `blk_5b5f6faf0144401f`, `blk_6a02268ad79542de`, `blk_71b84ce7c6554639`, `blk_a5ce16009a514628`, `blk_091db241c5154336`). Retain remaining 10 step-specific criteria and matrix blocks (`blk_9e44687dff884ff6`, `blk_2c13f67014094f3b`, `blk_fb0b98da76e046dd`, `blk_cb6217bccc974cca`, `blk_3568312503964aec`, `blk_8b6e5fba923642f2`, `blk_7260c1b6ac5648ca`, `blk_3cc672a8038144e0`, `blk_58f750206a4c4af0`, `blk_f6e286f050c94d60`).
      11. `sp_6a45d484ad5b497c` (`sp_d86aaa8a2756481b`) [Lines 8585-8600]: Prune 8 IDs (`blk_bd7c5a9f27504a2c`, `blk_9d68ceff695b4196`, `blk_2cbe96bffde04571`, `blk_f2cb51b5d074419a`, `blk_c1cc56f65f6a47e1`, `blk_71b84ce7c6554639`, `blk_a5ce16009a514628`, `blk_091db241c5154336`). Retain remaining 6 step-specific criteria and matrix blocks (`blk_9e44687dff884ff6`, `blk_3568312503964aec`, `blk_3cc672a8038144e0`, `blk_cb6217bccc974cca`, `blk_9c0c7c46568648c4`, `blk_c3bc5f3eb8e74110`).
      12. `sp_192910b5f5a34c79` (`step_xai_reporter`) [Lines 8639-8649]: Prune 5 IDs (`blk_bd7c5a9f27504a2c`, `blk_9d68ceff695b4196`, `blk_23ca73cf267d4078`, `blk_a5ce16009a514628`, `blk_091db241c5154336`). Retain remaining 4 step-specific criteria and matrix blocks (`blk_9e44687dff884ff6`, `blk_2c13f67014094f3b`, `blk_fb0b98da76e046dd`, `blk_6b8c766185294f7e`).
    </action>
    <action>Repair corrupted HTML entity on line 6705 of `seed_data.json` (inside `ai_description` of `blk_b4912f9ff3a24b31`):
      Replace `&lt;mechanical_anchors&gt;` with `<mechanical_anchors>`.
    </action>
    <action>Execute JSON integrity check verifying valid syntax, zero trailing commas, and correct indentation.</action>
    <constraint invariant="the_zero_compromise_pledge">Pydantic validation must strictly reject malformed JSON. Ensure seed_data.json parses without error.</constraint>
  </step>

  <step id="3" name="AST Seed Guardrail Test Suite Expansion">
    <action>Add 4 new AST/Seed guardrail test cases to @[backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py]:
      1. `test_seed_steps_criteria_blocks_have_no_redundant_mandates()`: Loads `seed_data.json` and verifies 0 candidate redundant mandate block IDs exist in any step's `criteria_block_ids`.
      2. `test_seed_prompt_blocks_zero_escaped_xml_tags()`: Loads `seed_data.json` and verifies 0 prompt blocks contain `&lt;mechanical_anchors&gt;` or `&lt;` escaped XML tags.
      3. `test_seed_guardrail_catches_redundant_criteria_in_step_negative()`: Anti-happy path test proving validator flags mock step containing candidate block ID.
      4. `test_seed_guardrail_catches_escaped_html_entity_in_prompt_block_negative()`: Anti-happy path test proving validator flags mock block containing `&lt;mechanical_anchors&gt;`.
    </action>
    <action>Execute AST Guardrails test suite:
      `uv run pytest backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py`
      `uv run pytest backend_v2/tests/unit/test_ast_matrix_claim_guardrails.py`
    </action>
  </step>

  <step id="4" name="Seed Integrity Validation &amp; Database Reseeding">
    <action>Reseed the local database with explicit environment parameter:
      `uv run python backend_v2/seed/run_seed.py local`
    </action>
    <action>Execute full Backend Audit Loop:
      `uv run python scripts/backend_audit_loop.py backend_v2 --test`
    </action>
    <constraint invariant="local_data_ephemeral_nature">Always execute clean-slate database re-seeding via `run_seed.py local` after mutating seed_data.json.</constraint>
  </step>

  <validation_gate>
    <action>Execute AST Guardrails Suite:
      `uv run pytest backend_v2/tests/unit/test_ast_matrix_claim_guardrails.py`
      `uv run pytest backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py`
    </action>
    <action>Execute Database Reseeding Gate:
      `uv run python backend_v2/seed/run_seed.py local`
    </action>
    <action>Execute Global Backend Audit Loop:
      `uv run python scripts/backend_audit_loop.py backend_v2 --test`
    </action>
  </validation_gate>
</execution_protocol>
```
