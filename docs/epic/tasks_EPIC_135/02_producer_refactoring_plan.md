# Phase 2: Producer Refactoring & Type Strictness

**Overview:** Rewrite `process_atom_evaluation` to accept `AtomResultDTO` instead of `Any`, eradicating ALL duck-typing (`getattr`, `hasattr`, `isinstance`) patterns and adapting the internal logic to `AtomResultDTO`'s field schema (`source_quote` string instead of `exact_quotes` list, `evaluation_reasoning` instead of `semantic_reasoning`, no `internal_logic_en`).
**Target Files:**
- `@[c:\src\quorum\backend_v2\services\orchestrator\anchor_validation_service.py]`

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 1A/1B. Verify `AtomResultDTO` fields and confirm `ExecutionStatus` migration is complete.</action>
    <action>Look forward: Verify the method `process_atom_evaluation` at `@[c:\src\quorum\backend_v2\services\orchestrator\anchor_validation_service.py#L320-L458]` is the ONLY target. Confirm zero production callers (preparatory work for Phase 3).</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <dod_checklist>
    - [ ] `anchor_validation_service.py` method `process_atom_evaluation` signature is: `atom: AtomResultDTO`, `alias_map: dict[str, str]`, `source_documents: list[SourceDocumentContext] | None = None`, `mcp_source_texts: dict[str, str] | None = None`, `locale: str | None = None`, `strictness_level: int = 50`, return type `-> AtomResultDTO`.
    - [ ] ALL `getattr()`, `hasattr()`, and `isinstance(data, dict)` duck-typing patterns in `process_atom_evaluation` are eradicated.
    - [ ] `semantic_reasoning` references replaced with `evaluation_reasoning`.
    - [ ] `internal_logic_en` hydration logic completely removed.
    - [ ] `exact_quotes: list[LLMExtractedQuote]` handling replaced with `source_quote: str | None` handling.
    - [ ] `used_evidence_ids` update logic removed (not on `AtomResultDTO`).
    - [ ] Method uses `AtomResultDTO.model_validate(atom.model_dump() | {...})` to create the returned instance. The `model_copy(update={...})` pattern is STRICTLY FORBIDDEN per `frozen_state_mutability` because it silently bypasses the `@model_validator(mode="before")` on `AtomResultDTO`.
    - [ ] Docstring updated to reference `AtomResultDTO` (not `AtomEvaluationItemDTO`).
    - [ ] `from typing import Any` import removed from the file if no other usage remains.
    - [ ] MyPy strict passes with zero errors.
    - [ ] Old test `test_atom_evaluation_item_dto_enforce_null_hypothesis` at `@[c:\src\quorum\backend_v2\tests\unit\models\dtos\test_lightweight_matrix.py#L100-L132]` will break because it passes `AtomEvaluationItemDTO` to the retyped signature. You MUST surgically delete this specific test function in THIS Phase (Phase 2) to maintain global CI/CD test suite parity, complying with `fragmented_quality_gates_prevention`. New tests in the test_contracts below supersede it.
  </dod_checklist>

  <required_context_rules>
    - `@[c:\src\quorum\.agents\rules\00-antigravity-core.md]`
    - `@[c:\src\quorum\.agents\rules\01-python-backend.md]`
    - `@[c:\src\quorum\.agents\rules\04_directory_reference.md]`
    - `@[c:\src\quorum\docs\epic\EPIC_135_Schema_Convergence_Architecture.md]`
    - `@[c:\Users\risto\.gemini\antigravity-ide\knowledge\dag_engine_dto_projection_rules\artifacts\ki_dag_engine_dto_projection_rules.md]` <!-- forensic_naming_law: source_quote naming -->
    - `@[c:\Users\risto\.gemini\antigravity-ide\knowledge\context_enriched_pipeline\artifacts\ki_context_enriched_decompose_verify.md]` <!-- structured_tda_state_mandate: no raw dicts -->
    - `@[c:\Users\risto\.gemini\antigravity-ide\knowledge\god_code_prevention\artifacts\ki_god_code_prevention.md]` <!-- anti_god_file_dumping: 400-line limit -->
  </required_context_rules>

  <anti_targets>
    - DO NOT replace `ScorecardAtomDTO` with `AtomResultDTO` in `matrix_domain_parser.py`.
    - DO NOT modify `backend_v2/hooks/scoring.py` yet.
    - DO NOT touch `test_lazy_llm_simulation.py` — deferred to Phase 3 (Consumer Convergence) because it relies on `calculate_rule_satisfied()` which is being centralized into `ScoringHook`.
    - DO NOT touch `matrix_domain_parser.py` or `matrix_reducer.py` — already migrated in Phase 1A.
  </anti_targets>

  <step id="1" name="REWRITE PROCESS_ATOM_EVALUATION METHOD">
    <action>In `@[c:\src\quorum\backend_v2\services\orchestrator\anchor_validation_service.py#L320-L458]`, perform a COMPLETE REWRITE of `process_atom_evaluation` with the following exact field mapping changes:</action>
    <action>UPDATE SIGNATURE: Change `atom: Any` to `atom: AtomResultDTO`. Change `source_documents: list[Any] | None` to `source_documents: list[SourceDocumentContext] | None`. Change return type `-> Any` to `-> AtomResultDTO`. RETAIN `alias_map: dict[str, str]`, `mcp_source_texts: dict[str, str] | None = None`, `locale: str | None = None`, `strictness_level: int = 50`.</action>
    <action>ADD IMPORTS: `from backend_v2.models.v2_core import AtomResultDTO` and `from backend_v2.models.dtos.quote_evidence import SourceDocumentContext`.</action>
    <demolish>REMOVE: ALL `getattr(atom, "field", default)` patterns. REPLACE WITH: direct attribute access on `AtomResultDTO` (specifically `atom.evaluation_reasoning`, `atom.contextual_override`, `atom.source_quote`).</demolish>
    <demolish>REMOVE: `internal_logic_en` hydration block (lines 351-362). `AtomResultDTO` does not have this field.</demolish>
    <demolish>REMOVE: `exact_quotes` list iteration logic (lines 404-449). REPLACE WITH: single `source_quote: str | None` validation. The new logic MUST:
      (1) If `atom.contextual_override is True`, return immediately with `source_quote` forced to `None` and hydrated reasoning.
      (2) If `atom.source_quote is not None`, match the single quote string against source documents using `_is_match()`. The matching logic MUST iterate over `source_documents` (typed as `list[SourceDocumentContext]`) and access `.text_content` and `.opaque_id` directly — NO `isinstance(doc, dict)` checks.
      (3) If no match found in static source_documents, attempt matching against `mcp_source_texts` (dict[str, str]). Iterate over `mcp_source_texts.items()` and call `_is_match(mcp_text, atom.source_quote)`. If matched, the quote is validated (no source_id enrichment needed since `source_quote` is a plain string, not an `LLMExtractedQuote` object).
      (4) If `atom.source_quote is None`, skip matching entirely.
    </demolish>
    <demolish>REMOVE: `used_evidence_ids` from return update dict. This field does not exist on `AtomResultDTO`.</demolish>
    <demolish>REMOVE: `internal_logic_en` from return update dict. This field does not exist on `AtomResultDTO`.</demolish>
    <demolish>REMOVE: ALL `model_copy(update={...})` patterns. REPLACE WITH: `AtomResultDTO.model_validate(atom.model_dump() | {"source_quote": validated_quote, "evaluation_reasoning": hydrated_reasoning})`. This is MANDATORY per `frozen_state_mutability` rule because `AtomResultDTO` has `ConfigDict(frozen=True)` and a critical `@model_validator(mode="before")` that enforces the null hypothesis (contextual_override vs source_quote mutual exclusion, FAILED atoms cannot have quotes, PASSED atoms must have evidence). Using `model_copy` would silently bypass these validators.</demolish>
    <action>UPDATE DOCSTRING: Replace all `AtomEvaluationItemDTO` references with `AtomResultDTO`. Update Args descriptions to match new types.</action>
    <action>HYDRATE REASONING: Use `engine.hydrate_reasoning_text(atom.evaluation_reasoning)` directly (no `getattr` guard — `evaluation_reasoning` is `str | None` on `AtomResultDTO`, check for `None` directly with `if atom.evaluation_reasoning:`).</action>
    <action>REMOVE `from typing import Any` import if no other usage remains in the file. `source_documents` parameter MUST use `list[SourceDocumentContext] | None`, not `list[Any]`.</action>
    <action>RETAIN `_is_match` inner function and its closure over `locale` and `strictness_level`. The matching logic (normalize → exact substring → fuzzy threshold) is unchanged; only the outer loop is simplified from list iteration to single-string matching.</action>
    <action>TEST SUITE PARITY: Surgically delete the broken legacy test `test_atom_evaluation_item_dto_enforce_null_hypothesis` from `@[c:\src\quorum\backend_v2\tests\unit\models\dtos\test_lightweight_matrix.py]` to prevent Fake Green CI/CD failures.</action>
  </step>

  <test_contracts>
    <test_location>Write ALL new tests in `@[c:\src\quorum\backend_v2\tests\unit\services\orchestrator\test_anchor_validation_atom_result.py]` (NEW FILE).</test_location>
    <test name="test_process_atom_evaluation_with_atom_result_dto" category="positive">
      <input>AtomResultDTO with source_quote matching a SourceDocumentContext text_content</input>
      <expected>Returns validated AtomResultDTO with hydrated evaluation_reasoning (aliases resolved) and source_quote preserved</expected>
    </test>
    <test name="test_process_atom_evaluation_contextual_override_clears_quote" category="negative">
      <input>AtomResultDTO with contextual_override=True and source_quote="some text"</input>
      <expected>Returns AtomResultDTO with source_quote forced to None (enforced by model_validator)</expected>
    </test>
    <test name="test_process_atom_evaluation_no_match_preserves_quote" category="negative">
      <input>AtomResultDTO with source_quote that does NOT match any SourceDocumentContext</input>
      <expected>Returns AtomResultDTO with original source_quote preserved (unresolved)</expected>
    </test>
    <test name="test_process_atom_evaluation_mcp_source_match" category="positive">
      <input>AtomResultDTO with source_quote matching an MCP source text (mcp_source_texts dict value)</input>
      <expected>Returns validated AtomResultDTO with source_quote preserved (validated against MCP source)</expected>
    </test>
    <test name="test_process_atom_evaluation_none_source_quote_skips_matching" category="boundary">
      <input>AtomResultDTO with source_quote=None, contextual_override=True (valid PASSED state)</input>
      <expected>Returns AtomResultDTO with source_quote=None and hydrated reasoning, no matching attempted</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation_service.py --test`</action>
  </validation_gate>
</execution_protocol>
```
