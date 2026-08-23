# Architecture Implementation Plan: Theory Grounding Dual Injection Elimination (`theory_grounding` vs. `ai_description`)

## Executive Summary & Objective

In accordance with **Chapter 2 of `@[docs/arkkitehtuurin_parannuskohteet.md]`**, this implementation plan eliminates prompt duplication, URL token bloat, and Single Source of Truth (SSOT) violations caused by storing theoretical and epistemic anchors concurrently in both `PromptBlock.ai_description` (as freeform `EPISTEMIC ANCHOR:` text blocks) and `PromptBlock.theory_grounding` (as structured `TheoryGrounding` DTOs).

Currently, all 13 matrices in `@[backend_v2/seed/seed_data.json]` contain redundant theoretical descriptions in `ai_description` while also defining structured `theory_grounding`. Furthermore, `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L36-L88]` injects `theory_grounding` as a raw JSON dump (`model_dump_json()`) into `<STATIC_INSTRUCTION>`, causing token waste, attention dilution, and semantic degradation.

This plan executes the **5-Phase Atomic Migration Protocol** (Chapter 6 of `@[docs/arkkitehtuurin_parannuskohteet.md]`):
1. Reformat `theory_grounding` prompt injection in `MatrixSensorPromptBuilder` into a pure, semantic `<theory_context>\n{citation_reference}\n</theory_context>` XML block, omitting raw URLs from the LLM prompt while preserving `source_url` in the database and DTOs for Flutter UI and PDF reports.
2. Atomically sanitize `ai_description` across all 13 matrices in `seed_data.json` by removing `EPISTEMIC ANCHOR:` sections while preserving core `OBJECTIVE:`, `ROLE:`, `TASK:`, `MANDATE:`, `<role_enforcement>`, and `<banned_concepts>` instructions.
3. Validate and re-seed the local database via `uv run python backend_v2/seed/run_seed.py local`.
4. Update unit tests and prompt factory assertions to verify the semantic citation XML output.
5. Create AST architectural guardrails ([NEW] `@[backend_v2/tests/unit/test_ast_theory_grounding_guardrails.py]`) to permanently prevent regression.

---

## User Review Required

> [!IMPORTANT]
> **Zero-Downtime Atomic Seeding**: In accordance with `03_seed_vault.md`, a timestamped backup copy (`backend_v2/seed/backups/seed_data_<timestamp>.json`) will be created before modifying `seed_data.json`.
> The prompt texts in `seed_data.json` are sanitized exclusively by stripping the duplicated `EPISTEMIC ANCHOR:` tail; the human-authored qualitative `OBJECTIVE:`, `ROLE:`, and `MANDATE:` prompt definitions are preserved verbatim.

```xml
<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_testing.md]</knowledge_item>
</required_context_rules>
```

---

## Scope & File Modification Boundary

### TARGET Files (Editable)
- `[MODIFY]` `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L36-L88]`
- `[MODIFY]` `@[backend_v2/seed/seed_data.json]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py#L12-L36]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py#L32-L48]`
- `[NEW]` `@[backend_v2/tests/unit/test_ast_theory_grounding_guardrails.py]`

### CONTEXT Files (Read-Only)
- `@[docs/arkkitehtuurin_parannuskohteet.md]` (Architecture Improvement Manifesto - Chapter 2)
- `@[backend_v2/models/v2_core.py#L194-L207]` (`TheoryGrounding` schema SSOT)
- `@[backend_v2/models/v2_core.py#L380-L544]` (`PromptBlock` schema SSOT)
- `@[backend_v2/models/dtos/engine.py#L41-L61]` (`MatrixEvaluationContext` DTO)
- `@[backend_v2/services/orchestrator/prompt_compiler_adapter.py#L10-L139]` (`PromptCompilerAdapter`)
- `@[backend_v2/services/orchestrator/localization_compiler.py#L79-L115]` (`LocalizationCompiler.compile_static_instructions`)

---

## Technical Debt Itemization & Pre-Implementation Remediation

Pre-flight inspection of touched targets and 1-hop dependencies reveals:
1. **Raw JSON in System Prompt**: `MatrixSensorPromptBuilder.build_caching_prefix` calls `matrix_context.theory_grounding.model_dump_json()`, injecting unformatted JSON strings into static LLM system directives.
2. **Duplicate Test Files**: `@[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py]` and `@[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]` exist in parallel. Both must be updated and aligned to the directory structure standard.
3. **Missing AST Guardrail**: No static AST verification currently protects against reintroducing `EPISTEMIC ANCHOR:` in `seed_data.json` or calling `model_dump_json()` inside `MatrixSensorPromptBuilder`.

---

```xml
<execution_protocol>
  <phase id="1" name="TECHNICAL_DEBT_REMEDIATION_AND_TEST_PREPARATION">
    <step id="1.1" name="ISOLATE_PROMPT_BUILDER_THEORY_GROUNDING_LOGIC">
      <target>@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L36-L88]</target>
      <action>
        Refactor the theory_grounding injection in `MatrixSensorPromptBuilder.build_caching_prefix`:
        Replace `ai_desc=matrix_context.theory_grounding.model_dump_json()` with pure citation XML formatting (excluding URL token bloat):
        ```python
        if matrix_context.theory_grounding and matrix_context.theory_grounding.citation_reference:
            citation = matrix_context.theory_grounding.citation_reference.strip()
            if citation:
                theory_desc = f"<theory_context>\n{citation}\n</theory_context>"
                blocks.append(
                    MatrixSensorPromptBuilder._create_ephemeral_block(
                        block_id="blk_3333333333333333",
                        category_id=PromptBlockCategory.SYSTEM_RULE,
                        ai_desc=theory_desc,
                    )
                )
        ```
      </action>
      <constraint invariant="xml_structural_sovereignty_mandate">
        Wrap the theoretical citation in explicit named XML tags (&lt;theory_context&gt;) instead of dumping raw JSON or injecting unclickable URL strings into the LLM prompt.
      </constraint>
      <constraint invariant="prompt_preservation_mandate">
        Preserve the citation_reference text cleanly without amputation.
      </constraint>
    </step>

    <step id="1.2" name="UPDATE_SENSOR_PROMPT_BUILDER_UNIT_TESTS">
      <target>@[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py#L12-L36]</target>
      <action>
        Update test assertions in `test_build_caching_prefix_with_context` to verify the pure `&lt;theory_context&gt;\nTest Citation\n&lt;/theory_context&gt;` XML structure.
        Add negative and boundary test cases:
        1. `test_build_caching_prefix_theory_grounding_none_citation`: Verifies behavior when `citation_reference` is None.
        2. `test_build_caching_prefix_theory_grounding_empty_citation`: Verifies behavior when `citation_reference` is empty string.
        3. `test_build_caching_prefix_theory_grounding_whitespace_only`: Verifies behavior when `citation_reference` contains only whitespace.
      </action>
      <constraint invariant="anti_happy_path_mandate">
        Every feature change must include at least 2 negative test cases covering boundary values or missing fields.
      </constraint>
    </step>

    <step id="1.3" name="UPDATE_ROOT_UNIT_TEST_MATRIX_SENSOR_PROMPT_BUILDER">
      <target>@[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py#L32-L48]</target>
      <action>
        Update `test_build_caching_prefix_success` to assert pure `&lt;theory_context` formatting when `theory_grounding` is supplied.
      </action>
    </step>
  </phase>

  <phase id="2" name="ATOMIC_SEED_DATA_MIGRATION">
    <step id="2.1" name="CREATE_TIMESTAMPED_SEED_BACKUP">
      <target>@[backend_v2/seed/seed_data.json]</target>
      <action>
        Ensure directory `backend_v2/seed/backups/` exists and execute backup command:
        `New-Item -ItemType Directory -Force -Path backend_v2/seed/backups; Copy-Item backend_v2/seed/seed_data.json -Destination backend_v2/seed/backups/seed_data_pre_theory_grounding_cleanup.json`
      </action>
      <constraint invariant="vault_mutation_protocol">
        A backup MUST be physically recorded in `backend_v2/seed/backups/` before mutating `seed_data.json`.
      </constraint>
    </step>

    <step id="2.2" name="EXECUTE_DETERMINISTIC_SEED_MIGRATION">
      <target>@[backend_v2/seed/seed_data.json]</target>
      <action>
        Surgically sanitize the `ai_description` field across specifically and exhaustively all 13 matrices:
        1. `blk_440a5fef9331451b` (matrix_toulmin): Remove `EPISTEMIC ANCHOR:\nToulmin, S. E. (2003)...`
        2. `blk_f921c7c0989b47e8` (matrix_bloom): Remove `EPISTEMIC ANCHOR:\nAnderson, L. W., & Krathwohl...`
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

        Preserve all `OBJECTIVE:`, `ROLE:`, `TASK:`, `MANDATE:`, `&lt;role_enforcement&gt;`, and `&lt;banned_concepts&gt;` sections intact.
      </action>
      <constraint invariant="prompt_preservation_mandate">
        The core prompt text is the user's intellectual property. Only remove the duplicate epistemic citation tail that is already structured in `theory_grounding`.
      </constraint>
    </step>

    <step id="2.3" name="VERIFY_SEED_JSON_INTEGRITY_AND_RESEED">
      <target>@[backend_v2/seed/seed_data.json]</target>
      <action>
        Verify JSON syntax and re-seed the local test database:
        Run: `uv run python backend_v2/seed/run_seed.py local`
      </action>
      <constraint invariant="local_data_ephemeral_nature">
        Always execute database re-seeding via `run_seed.py local` after modifying `seed_data.json`.
      </constraint>
    </step>
  </phase>

  <phase id="3" name="AST_GUARDRAILS_AND_VERIFICATION">
    <step id="3.1" name="CREATE_AST_THEORY_GROUNDING_GUARDRAIL">
      <target>[NEW] @[backend_v2/tests/unit/test_ast_theory_grounding_guardrails.py]</target>
      <action>
        Create comprehensive AST and Seed schema guardrail tests:
        1. `test_seed_matrices_have_no_epistemic_anchor_in_ai_description`: Parses `backend_v2/seed/seed_data.json` and asserts that 0 matrix blocks contain `"EPISTEMIC ANCHOR:"` in `ai_description`.
        2. `test_seed_matrices_have_valid_theory_grounding`: Asserts that all 13 matrix blocks have non-null `theory_grounding` with non-empty `source_url` and `citation_reference`.
        3. `test_matrix_sensor_prompt_builder_ast_uses_pure_theory_citation`: Inspects the AST of `MatrixSensorPromptBuilder.build_caching_prefix` to verify that `&lt;theory_context&gt;` is constructed with pure `citation_reference` and `model_dump_json` is not called on `theory_grounding`.
      </action>
      <constraint invariant="ast_guardrail_mandate">
        New architectural constraints must be statically locked with AST and structural tests to prevent regression.
      </constraint>
    </step>

    <step id="3.2" name="EXECUTE_GLOBAL_QUALITY_GATE">
      <target>@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L18-L204]</target>
      <action>
        Run the comprehensive backend audit loop:
        `uv run python scripts/backend_audit_loop.py backend_v2 --test`
      </action>
      <constraint invariant="quality_gate_execution">
        The task is not complete until `backend_audit_loop.py` passes with Ruff formatting, MyPy strict typing, and full Pytest execution.
      </constraint>
    </step>
  </phase>
</execution_protocol>
```

---

## Verification Plan

### Automated Tests
1. **Isolated Unit Tests**:
   ```powershell
   uv run pytest backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py backend_v2/tests/unit/test_ast_theory_grounding_guardrails.py
   ```
2. **Local Database Re-Seeding**:
   ```powershell
   uv run python backend_v2/seed/run_seed.py local
   ```
3. **Global Backend Audit Gate**:
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2 --test
   ```

### ISTQB Equivalence Partitions & Boundary Scenarios
| Scenario ID | Test Name | Input State | Expected Outcome |
| :--- | :--- | :--- | :--- |
| **TC-TG-01** (Happy Path: Pure Citation) | `test_build_caching_prefix_with_context` | `TheoryGrounding(source_url="https://arma.org", citation_reference="ARMA Principles")` | Static prompt contains `<theory_context>\nARMA Principles\n</theory_context>` (no raw URL in prompt) |
| **TC-TG-02** (Boundary: Null Citation) | `test_build_caching_prefix_theory_grounding_none_citation` | `TheoryGrounding(source_url="https://arma.org", citation_reference=None)` | Ephemeral block is not appended, avoiding empty XML tags |
| **TC-TG-03** (Boundary: Empty Citation) | `test_build_caching_prefix_theory_grounding_empty_citation` | `TheoryGrounding(source_url="https://arma.org", citation_reference="")` | Ephemeral block is not appended, avoiding empty XML tags |
| **TC-TG-04** (AST Guardrail) | `test_seed_matrices_have_no_epistemic_anchor_in_ai_description` | `seed_data.json` | 0 occurrences of `EPISTEMIC ANCHOR:` across all 13 matrices |
| **TC-TG-05** (AST Guardrail) | `test_seed_matrices_have_valid_theory_grounding` | `seed_data.json` | Exactly 13 matrices have populated `theory_grounding` with valid URLs and citations |
