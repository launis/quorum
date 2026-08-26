# Phase 1: Theory Grounding & Epistemic Anchor Sanitization

**Overview:** Prune redundant `EPISTEMIC ANCHOR:` tails across all 13 matrix blocks in `seed_data.json` while strictly preserving qualitative prompt philosophy, eradicate ephemeral block helpers and fake IDs in `MatrixSensorPromptBuilder`, format pure `<theory_context>` and `<matrix_objective>` XML blocks via direct `TemplateProcessor.safe_interpolate()` CDATA Breakout Shielding (omitting raw URLs from prompt payloads), and execute touched scope technical debt cleanups across adapters and widgets.
**Target Files:**
- `[MODIFY]` @[backend_v2/seed/seed_data.json#L336-L6900]
- `[MODIFY]` @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L30-L52]
- `[MODIFY]` @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L54-L112]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py]
- `[MODIFY]` @[.agents/rules/01-python-backend.md]
- `[MODIFY]` @[scripts/_ast_guardrails.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by previous epics. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/seed/seed_data.json#L336-L6900] and @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L30-L52] and @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L54-L112].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_148_Domain_Model_SSOT_and_Localization_Modernization.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [x] Pre-implementation technical debt cleanups executed: `FlattenedAtom` instantiations in @[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py] updated with `depends_on=()` to satisfy strict MyPy typing.
    - [x] Seed vault backup created in `backend_v2/seed/backups/seed_data_pre_epic148_cleanup.json` prior to any modifications.
    - [x] All 13 matrix blocks in @[backend_v2/seed/seed_data.json#L336-L6900] sanitized by removing duplicate `EPISTEMIC ANCHOR:` tails; qualitative prompt definitions preserved verbatim per `prompt_preservation_mandate`.
    - [x] `_create_ephemeral_block` helper and fake IDs (`blk_1111...`, `blk_2222...`, `blk_3333...`) eradicated in @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L30-L52].
    - [x] `MatrixSensorPromptBuilder.build_caching_prefix` refactored in @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L54-L112] to format pure `<theory_context>` and `<matrix_objective>` XML blocks via direct `TemplateProcessor.safe_interpolate()` with CDATA Breakout Shielding, omitting raw URLs from LLM prompt payloads.
    - [x] Rule `QGR001` in @[scripts/_ast_guardrails.py] extended to detect and ban `setattr(...)` and `object.__setattr__(...)` in-place model mutations across domain code (excluding test suites and necessary Pydantic root/after validators).
    - [x] `frozen_state_mutability` rule block in @[.agents/rules/01-python-backend.md] updated to explicitly ban `setattr(...)`, `object.__setattr__(...)`, and `__setattr__()` mutations on Pydantic models and frozen entities.
    - [x] Unit test assertions in @[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py] and @[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py] updated and passing with clean CDATA formatting and XML injection protection (TC-TG-01 through TC-TG-06).
    - [x] Backend quality gate passes: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py --test`.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_polymorphic_rule_routing.md]</knowledge_item>
    <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_testing.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
    <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_error_handling_and_fail_fast_rfc7807.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
  </required_context_rules>

  <touched_artifacts>
    <backend>@[backend_v2/seed/seed_data.json]</backend>
    <backend>@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py]</backend>
    <backend>@[scripts/_ast_guardrails.py]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT modify `I18nText` schema in `backend_v2/models/v2_core.py` in Phase 1 (strictly reserved for atomic Phase 2).
    - Do NOT modify `OutputProfile` schema or delete `OutputLayoutBlock` in Phase 1 (strictly reserved for atomic Phase 3).
    - Do NOT modify Flutter `.dart` models or views in Phase 1 (reserved for Phase 2 and Phase 3).
    - Do NOT alter the qualitative prompt texts in `seed_data.json` (`OBJECTIVE:`, `ROLE:`, `TASK:`, `MANDATE:`, `<role_enforcement>`, and `<banned_concepts>`) per `prompt_preservation_mandate`.
    - Treat read-only context references as immutable:
      - @[backend_v2/models/v2_core.py#L194-L207] (`TheoryGrounding` schema SSOT)
      - @[backend_v2/settings.py] (Backend global configuration SSOT)
  </anti_targets>

  <test_contracts>
    <test name="test_build_caching_prefix_with_context" category="positive">
      <input>TheoryGrounding(source_url="https://arma.org", citation_reference="ARMA Principles")</input>
      <expected>Static prompt contains `&lt;theory_context&gt;\n&lt;![CDATA[ARMA Principles]]&gt;\n&lt;/theory_context&gt;` and zero occurrence of "https://arma.org"</expected>
    </test>
    <test name="test_build_caching_prefix_theory_grounding_none_citation" category="boundary">
      <input>TheoryGrounding(source_url="https://arma.org", citation_reference=None)</input>
      <expected>theory_context block is not appended, avoiding empty XML tags</expected>
    </test>
    <test name="test_build_caching_prefix_theory_grounding_empty_citation" category="boundary">
      <input>TheoryGrounding(source_url="https://arma.org", citation_reference="")</input>
      <expected>theory_context block is not appended, avoiding empty XML tags</expected>
    </test>
    <test name="test_build_caching_prefix_theory_grounding_whitespace_only" category="boundary">
      <input>TheoryGrounding(source_url="https://arma.org", citation_reference="   \n\t")</input>
      <expected>theory_context block is not appended, avoiding whitespace-only tags</expected>
    </test>
    <test name="test_build_caching_prefix_theory_grounding_omits_raw_urls" category="boundary">
      <input>TheoryGrounding(source_url="https://secret-domain.org/doc", citation_reference="Valid Citation")</input>
      <expected>Static prompt does NOT contain "https://secret-domain.org" (zero token bloat / URL leakage)</expected>
    </test>
    <test name="test_build_caching_prefix_theory_grounding_xml_injection_shield" category="error_path">
      <input>TheoryGrounding(citation_reference="Author (2020) &lt;tag&gt; &amp; ]]&gt; &lt;/theory_context&gt;&lt;injected&gt;")</input>
      <expected>Static prompt wraps citation in CDATA and safely breaks `]]&gt;` without closing tag early</expected>
    </test>
  </test_contracts>

  <step id="1" name="Pre-Implementation Technical Debt Sweeps &amp; AST Guardrail Extension">
    <action>In @[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]: Clean technical debt on lines 129, 262, and 343 by supplying `depends_on=()` to `FlattenedAtom` constructors to satisfy strict MyPy typing.</action>
    <action>In @[scripts/_ast_guardrails.py]: Extend rule `QGR001` in `QuorumGuardrailVisitor.visit_Call` to detect and fail fast on `ast.Name(id="getattr" | "hasattr" | "setattr")` and `ast.Attribute(value=ast.Name(id="object"), attr="__setattr__")` in non-test files, preventing frozen mutation anti-patterns across domain code.</action>
    <action>In @[.agents/rules/01-python-backend.md]: Update `frozen_state_mutability` rule block to explicitly ban in-place model mutations using `setattr(...)`, `object.__setattr__(...)`, or `__setattr__()` on Pydantic models or frozen domain entities, mandating pre-instantiation `@field_validator` data sanitization and `.model_copy(update=...)` for state transitions.</action>
    <constraint invariant="touched_scope_tech_debt_mandate">All pre-existing technical debt in touched backend files and AST guardrail definitions must be locked in Phase 1 before domain model mutations.</constraint>
  </step>

  <step id="2" name="Backup Seed Vault (vault_mutation_protocol)">
    <action>Ensure directory `backend_v2/seed/backups/` exists and execute backup command via PowerShell:
      `New-Item -ItemType Directory -Force -Path backend_v2/seed/backups; Copy-Item backend_v2/seed/seed_data.json -Destination backend_v2/seed/backups/seed_data_pre_epic148_cleanup.json`
    </action>
    <constraint invariant="vault_mutation_protocol">Must create timestamped backup of seed_data.json prior to any surgical edits.</constraint>
  </step>

  <step id="3" name="Deterministic Seed Vault Sanitization across all 13 Matrix Blocks">
    <action>Surgically sanitize the `ai_description` field across specifically and exhaustively all 13 matrices in @[backend_v2/seed/seed_data.json#L336-L6900]:
      1. `blk_440a5fef9331451b` (matrix_toulmin): Remove `EPISTEMIC ANCHOR:\nToulmin, S. E. (2003)...`
      2. `blk_f921c7c0989b47e8` (matrix_bloom): Remove `EPISTEMIC ANCHOR:\nAnderson, L. W., &amp; Krathwohl...`
      3. `blk_109dab5b6b3f403a` (matrix_kahneman): Remove `EPISTEMIC ANCHOR:\nKahneman, D. (2011)...`
      4. `blk_53f32679aa514fcb` (matrix_goodhart): Remove `EPISTEMIC ANCHOR:\nStumborg, M. F., et al...`
      5. `blk_fb15f8dcf23f4865` (matrix_archivist): Remove `EPISTEMIC ANCHOR:\nARMA International...`
      6. `blk_c5804a9143c34cb1` (matrix_causal_analyst): Remove `EPISTEMIC ANCHOR:\nPearl, J. 'The Book of Why...`
      7. `blk_b476f89fb732448c` (matrix_falsifier): Remove `EPISTEMIC ANCHOR:\nKarl Popper's Theory of Falsification...`
      8. `blk_ff72c2d79edb4ebf` (matrix_judge): Remove `EPISTEMIC ANCHOR:\nW. Edwards Deming...`
      9. `blk_6b8c766185294f7e` (matrix_xai_reporter): Remove `EPISTEMIC ANCHOR:\nDARPA XAI Program (2017)...`
      10. `blk_80732a33fe1947ee` (matrix_taskguard): Remove `EPISTEMIC ANCHOR:\nAnchored in the OWASP Top 10...`
      11. `blk_c3bc5f3eb8e74110` (matrix_causal_abductive): Remove `EPISTEMIC ANCHOR:\nAnchored in Judea Pearl's 'The Book of Why'...`
      12. `blk_f6e286f050c94d60` (matrix_taskxai_clarity): Remove `EPISTEMIC ANCHOR:\nAnchored in Zachary C. Lipton's 'The Mythos of Model Interpretability'...`
      13. `blk_22e3598e06414409` (matrix_epistemic_humility): Remove `EPISTEMIC ANCHOR:\nGrounded in Kahneman's Dual Process Theory...`
      Preserve all `OBJECTIVE:`, `ROLE:`, `TASK:`, `MANDATE:`, `&lt;role_enforcement&gt;`, and `&lt;banned_concepts&gt;` sections intact per `prompt_preservation_mandate`.
    </action>
    <demolish>REMOVE: `EPISTEMIC ANCHOR:` tails across all 13 matrix blocks in @[backend_v2/seed/seed_data.json#L336-L6900].</demolish>
  </step>

  <step id="4" name="Format Pure &lt;theory_context&gt; in MatrixSensorPromptBuilder via Direct TemplateProcessor Assembly">
    <action>In @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L30-L52] and @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L54-L112]:
      1. Completely delete `_create_ephemeral_block` helper and purge artificial `blk_1111...`, `blk_2222...`, `blk_3333...` IDs.
      2. Refactor `MatrixSensorPromptBuilder.build_caching_prefix` to assemble static system instructions directly from `GLOBAL_MANDATES_XML`, `MATRIX_SENSOR_SYSTEM_PROMPT`, and conditionally interpolated `&lt;matrix_objective&gt;` / `&lt;theory_context&gt;` XML sections using `TemplateProcessor.safe_interpolate()` with Breakout Shielding, completely omitting raw URLs.
    </action>
    <demolish>REMOVE: `_create_ephemeral_block` helper at @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L30-L52]. REPLACE WITH: direct `TemplateProcessor.safe_interpolate()` assembly in `build_caching_prefix`.</demolish>
    <demolish>REMOVE: `PromptCompilerAdapter` instantiation and `compiler.compile_static_instructions(blocks, target_locale="en")` at @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L54-L112].</demolish>
  </step>

  <step id="5" name="Unit Tests for Theory Grounding Prompt Builder">
    <action>In @[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py] and @[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py]:
      Update test assertions to verify clean `&lt;theory_context&gt;` and `&lt;matrix_objective&gt;` CDATA-shielded pure citation XML structure without raw URLs, without legacy `&lt;STATIC_INSTRUCTION&gt;` wrapping, and assert protection against XML injection characters (`&lt;`, `&gt;`, `&amp;`, `]]&gt;`) via test case `test_build_caching_prefix_theory_grounding_xml_injection_shield` (TC-TG-06).
    </action>
  </step>

  <validation_gate>
    <assertion>Run backend unit test suite: `uv run pytest backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py`</assertion>
    <assertion>Run backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py --test`</assertion>
  </validation_gate>
</execution_protocol>
```
