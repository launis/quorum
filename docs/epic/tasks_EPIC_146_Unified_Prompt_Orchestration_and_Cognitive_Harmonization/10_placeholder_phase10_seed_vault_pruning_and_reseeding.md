# Phase 10: Seed Vault Pruning & Database Reseeding

**Overview:** Execute Python audit script proving candidate blocks are 100% covered by GLOBAL_MANDATES_XML, prune verified redundant global mandate blocks from criteria_block_ids in seed_data.json, fix corrupted HTML entity (&lt;mechanical_anchors&gt; -> <mechanical_anchors>), and reseed database.
**Target Files:**
- `[MODIFY]` @[backend_v2/seed/seed_data.json]

Source: @[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md#L379-L385] Phase 10: Seed Vault Pruning & Database Reseeding

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 9. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/seed/seed_data.json].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] Programmatic redundancy verification passes in `scratch/` proving candidate blocks are covered by `GLOBAL_MANDATES_XML`.
    - [ ] Redundant global mandate blocks pruned from `criteria_block_ids` in @[backend_v2/seed/seed_data.json].
    - [ ] Corrupted HTML entity `&lt;mechanical_anchors&gt;` fixed to `<mechanical_anchors>` in `seed_data.json`.
    - [ ] Database re-seeded via `uv run python backend_v2/seed/run_seed.py local`.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
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
  </touched_artifacts>

  <anti_targets>
    - Do NOT prune required step-specific task directives or primary matrix blocks.
    - Do NOT modify `db_v2.json` directly.
  </anti_targets>

  <step id="1" name="Vault Pruning &amp; Reseeding">
    <action>Remove verified redundant global mandate blocks (specifically and exhaustively: `block_headermandates`, `block_mandate2`, `block_mandate3`, `block_mandate5`, `block_headerrules`, `block_rule1`, `block_rule2`, `block_rule3`, `block_rule4`, `block_rule5`, `block_rule6`, `block_oprule1`, `block_oprule2`, `block_oprule3`, `block_instructionnohallucination`, `block_instructionlanguage_dynamic`, `block_headerinstructions`) from individual step `criteria_block_ids` in @[backend_v2/seed/seed_data.json].</action>
    <action>Fix corrupted HTML entity in `seed_data.json` (`&lt;mechanical_anchors&gt;` -> `<mechanical_anchors>`).</action>
    <action>Reseed local database: `uv run python backend_v2/seed/run_seed.py local`.</action>
  </step>

  <validation_gate>
    <action>Execute Backend Audit Loop: `uv run python scripts/backend_audit_loop.py backend_v2 --test`</action>
    <action>Execute Database Reseeding: `uv run python backend_v2/seed/run_seed.py local`</action>
  </validation_gate>
</execution_protocol>
```
