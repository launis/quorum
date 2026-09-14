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
- [x] Step 2: Enhance `verify_quote_in_corpus` with Dual-Substitution Normalization
  - [x] In `scripts/diff_executions.py#L20-L32`, add `import re` in alphabetical order between `os` and `subprocess`
  - [x] In `scripts/diff_executions.py#L886-L925`, define module-level compiled regexes: `_HTML_TAG_PATTERN` and `_MARKDOWN_DECORATOR_PATTERN`
  - [x] In `scripts/diff_executions.py#L888-L924`, upgrade `verify_quote_in_corpus` to 4 tiers: literal exact, whitespace-normalized, HTML-tag-normalized, and Markdown-decorator-relaxed
  - [x] In `scripts/diff_executions.py#L1915-L1985`, pre-compute `html_norm_corpus` and `md_norm_corpus` in outer loop for O(1) matching
- [x] Step 3: Expand `test_diff_executions.py` Unit Test Suite
  - [x] Positive: `<br>`, `<br/>`, `<br />` table cell variants (`ja<br>**omaan**` vs `ja\n**omaan**`)
  - [x] Positive: Markdown bold/italic decorators adjacent to punctuation (`*huomio*.`, `**huomio**,`, `(*huomio*)`)
  - [x] Positive: Generic types in text (`List<String>`, `Dict<str, Any>`) shielded
  - [x] Positive: Mathematical inequalities (`x < y and y > z`, `x <y and y> z`) shielded
  - [x] Positive: Snake_case identifiers (`user_id_column`, `_user_id_column_`) shielded
  - [x] Negative & boundary: character typos ("Näitä" vs "Nämä"), unanchored text, HTML-only/whitespace-only/empty inputs
  - [x] Run `uv run pytest backend_v2/tests/unit/test_diff_executions.py -k TestVerifyQuoteInCorpus`
- [x] Step 4: Update Layer 1 Speaker Attribution Protocol in Matrix Evaluation
  - [x] In `backend_v2/models/prompts/execution/matrix_evaluation.py#L99-L112`, expand `<speaker_attribution_protocol>` with Cognitive Agency vs. Echo Parroting and Submitted Deliverables & Artifacts
  - [x] Preserve `+ CONTEXTUAL_OVERRIDE_DIRECTIVE + "\n"` concatenation
- [x] Step 5: Update Prompt Unit Tests & Assertion Gates
  - [x] In `backend_v2/tests/unit/models/prompts/test_matrix_evaluation.py`, add `"speaker_attribution_protocol"` to `tags` list in `test_matrix_sensor_system_prompt_structure()`
  - [x] Add assertions in `test_matrix_sensor_system_prompt_directives()` for Cognitive Agency, Echo Parroting, and Submitted Deliverables
  - [x] Verify `test_matrix_sensor_system_prompt_negative_partitions()` passes with 100% tag matching and zero banned ambiguous phrases
- [x] Step 6: Synchronize Knowledge Item (`ki_structured_forensic_quotes.md`)
  - [x] Expand `speaker_stream_provenance_gating` rule block with Point 4 (Echo Parroting & Cognitive Agency Boundary) and Point 5 (Dual-Track Attribution Standard)
- [x] Step 7: Global Audit & E2E Re-Evaluation Gate
  - [x] Run `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/models/prompts/test_matrix_evaluation.py --test`
  - [x] Run `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_diff_executions.py --test`
  - [x] Run `uv run python scripts/diff_executions.py data/files/executions/exe_26f38060c9bd4ef3 data/files/executions/exe_1aaabc9556704edc -o scratch/diff_report_post_fix.md`
  - [x] Verify MyPy Strict, Ruff format, and Pytest coverage are 100% green

# Session Handover Context
## Achieved
- Step 1: Resolved pre-existing MyPy strict typing issue in `backend_v2/tests/unit/test_diff_executions.py#L887` (`model_validate`).
- Steps 2-3: Implemented 4-tier lexical verification with dual-substitution normalization in `scripts/diff_executions.py` and added 10 ISTQB test partitions.
- Steps 4-5: Added Cognitive Agency vs Echo Parroting boundary and Dual-Track Attribution directives to Layer 1 prompt in `backend_v2/models/prompts/execution/matrix_evaluation.py` with 100% prompt unit test coverage.
- Step 6: Synchronized `ki_structured_forensic_quotes.md` with echo parroting boundary and dual-track attribution standards.
- Step 7: Completed global audit loops (100% pass, 0 lint/mypy/AST errors) and verified E2E differential report on Sitra run (`exe_26f38060c9bd4ef3` vs `exe_1aaabc9556704edc`), increasing verified quote rate from 62.5% to 87.5% and isolating genuine character typo.

## Learned
- Boundary defense is vital when stripping HTML tags; explicit known-tag regex prevents accidental destruction of generic type signatures and mathematical inequalities.
- Markdown decorator stripping must substitute empty string rather than space to preserve punctuation adhesion.
- Conversational cognitive competence requires distinguishing independent human thought from passive AI prompt echoing, whereas standalone deliverables represent candidate-endorsed text evaluated directly.

## Remaining
- None (All 7 implementation plan steps completed). Ready for Tier 8 Plan Audit.
