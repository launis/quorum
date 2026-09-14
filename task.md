# Task Checklist: Lexical Grounding Normalization & Dual-Track Speaker Attribution (Echo Parroting Guardrail)

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
  <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
</required_context_rules>

- [x] Step 1: Technical Debt Cleanup & Baseline Test Suite Verification
  - [x] In `backend_v2/tests/unit/test_diff_executions.py#L885-L898`, change `MacroBlockScoreDTO(..., unexpected_field="disallowed")` to `MacroBlockScoreDTO.model_validate({...})` to preserve runtime `ValidationError` verification under `extra='forbid'` while satisfying MyPy strict typing (`[call-arg]`)
  - [x] Run baseline unit tests to guarantee clean starting state (`test_diff_executions.py -k TestVerifyQuoteInCorpus` and `test_matrix_evaluation.py`)
- [ ] Step 2: Enhance `verify_quote_in_corpus` with Dual-Substitution Normalization
  - [ ] In `scripts/diff_executions.py#L20-L32`, add `import re` in alphabetical order between `os` and `subprocess`
  - [ ] In `scripts/diff_executions.py#L886-L925`, define module-level compiled regexes: `_HTML_TAG_PATTERN` and `_MARKDOWN_DECORATOR_PATTERN`
  - [ ] In `scripts/diff_executions.py#L888-L924`, upgrade `verify_quote_in_corpus` to 4 tiers: literal exact, whitespace-normalized, HTML-tag-normalized, and Markdown-decorator-relaxed
  - [ ] In `scripts/diff_executions.py#L1915-L1985`, pre-compute `html_norm_corpus` and `md_norm_corpus` in outer loop for O(1) matching
- [ ] Step 3: Expand `test_diff_executions.py` Unit Test Suite
  - [ ] Positive: `<br>`, `<br/>`, `<br />` table cell variants (`ja<br>**omaan**` vs `ja\n**omaan**`)
  - [ ] Positive: Markdown bold/italic decorators adjacent to punctuation (`*huomio*.`, `**huomio**,`, `(*huomio*)`)
  - [ ] Positive: Generic types in text (`List<String>`, `Dict<str, Any>`) shielded
  - [ ] Positive: Mathematical inequalities (`x < y and y > z`, `x <y and y> z`) shielded
  - [ ] Positive: Snake_case identifiers (`user_id_column`, `_user_id_column_`) shielded
  - [ ] Negative & boundary: character typos ("Näitä" vs "Nämä"), unanchored text, HTML-only/whitespace-only/empty inputs
  - [ ] Run `uv run pytest backend_v2/tests/unit/test_diff_executions.py -k TestVerifyQuoteInCorpus`
- [ ] Step 4: Update Layer 1 Speaker Attribution Protocol in Matrix Evaluation
  - [ ] In `backend_v2/models/prompts/execution/matrix_evaluation.py#L99-L112`, expand `<speaker_attribution_protocol>` with Cognitive Agency vs. Echo Parroting and Submitted Deliverables & Artifacts
  - [ ] Preserve `+ CONTEXTUAL_OVERRIDE_DIRECTIVE + "\n"` concatenation
- [ ] Step 5: Update Prompt Unit Tests & Assertion Gates
  - [ ] In `backend_v2/tests/unit/models/prompts/test_matrix_evaluation.py`, add `"speaker_attribution_protocol"` to `tags` list in `test_matrix_sensor_system_prompt_structure()`
  - [ ] Add assertions in `test_matrix_sensor_system_prompt_directives()` for Cognitive Agency, Echo Parroting, and Submitted Deliverables
  - [ ] Verify `test_matrix_sensor_system_prompt_negative_partitions()` passes with 100% tag matching and zero banned ambiguous phrases
- [ ] Step 6: Synchronize Knowledge Item (`ki_structured_forensic_quotes.md`)
  - [ ] Expand `speaker_stream_provenance_gating` rule block with Point 4 (Echo Parroting & Cognitive Agency Boundary) and Point 5 (Dual-Track Attribution Standard)
- [ ] Step 7: Global Audit & E2E Re-Evaluation Gate
  - [ ] Run `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/models/prompts/test_matrix_evaluation.py --test`
  - [ ] Run `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_diff_executions.py --test`
  - [ ] Run `uv run python scripts/diff_executions.py data/files/executions/exe_26f38060c9bd4ef3 data/files/executions/exe_1aaabc9556704edc -o scratch/diff_report_post_fix.md`
  - [ ] Verify MyPy Strict, Ruff format, and Pytest coverage are 100% green

# Session Handover Context
## Achieved
- Initialized execution context for Implementation Plan: Lexical Grounding Normalization & Dual-Track Speaker Attribution.
## Learned
- Pre-existing MyPy strict failure in `backend_v2/tests/unit/test_diff_executions.py#L887` must be addressed in Step 1.
## Remaining
- Steps 1-7.
