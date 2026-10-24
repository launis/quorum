<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
</required_context_rules>

# Phase 1: Leaf Constants, Normalizer, Strict Match & Fuzzy Score Extraction (`phase1_normalizer_and_strict_match_extraction.md`)

## 1. Objective
Execute Phase 1 (Leaf Pre-Extraction) of the Two-Epoch Strangler Fig decomposition for `@[backend_v2/services/orchestrator/anchor_validation_service.py#L32-L855]`:
1. Extract the module-level forensic citation constants (`MAX_CITATION_SPAN_CHARS = 1000`, `MIN_MULTI_SEGMENT_FLOOR_CHARS = 30`, `MIN_ENTROPY_GATE_CHARS = 10`) and the three leaf methods `AnchorValidationService.normalize_text_with_mapping` (`@[backend_v2/services/orchestrator/anchor_validation_service.py#L43-L93]`), `AnchorValidationService.strict_match` (`@[backend_v2/services/orchestrator/anchor_validation_service.py#L95-L164]`), and `AnchorValidationService.calculate_fuzzy_score` (`@[backend_v2/services/orchestrator/anchor_validation_service.py#L166-L183]`) into `[NEW] @[backend_v2/services/orchestrator/anchor_validation/lexical_normalizer.py]`.
2. Do NOT create `backend_v2/services/orchestrator/anchor_validation/__init__.py` during Phase 1 (`strangler_fig_mandate`).
3. Retain explicit redundant re-exports and 1-line static method delegations inside `@[backend_v2/services/orchestrator/anchor_validation_service.py#L32-L855]` so all existing callers and unit tests pass 100% unchanged.

### Multi-Phase Decomposition Context (Epoch 1 Surviving Targets)
Across Phases 1–4, the full `backend_v2/services/orchestrator/anchor_validation/` package and 1-hop backend callers comprise:
- `[NEW] @[backend_v2/services/orchestrator/anchor_validation/lexical_normalizer.py]` (Phase 1)
- `[NEW] @[backend_v2/services/orchestrator/anchor_validation/lexical_matcher.py]` (Phase 2)
- `[NEW] @[backend_v2/services/orchestrator/anchor_validation/evidence_validator.py]` (Phase 3)
- `[NEW] @[backend_v2/services/orchestrator/anchor_validation/atom_evaluation_processor.py]` (Phase 3)
- `[NEW] @[backend_v2/services/orchestrator/anchor_validation/__init__.py]` (Phase 4)
- `[MODIFY] @[backend_v2/services/orchestrator/extractive_sensor_service.py#L176-L761]` (Phase 4)
- `[MODIFY] @[backend_v2/services/mcp/mcp_tool_loop.py#L150-L476]` (Phase 4)
- `[MODIFY] @[backend_v2/hooks/integrity.py#L118-L138]` (Phase 4)

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/services/orchestrator/anchor_validation/lexical_normalizer.py]` | Leaf normalization and exact/fuzzy string matching functions (`MAX_CITATION_SPAN_CHARS`, `MIN_MULTI_SEGMENT_FLOOR_CHARS`, `MIN_ENTROPY_GATE_CHARS`, `normalize_text_with_mapping`, `strict_match`, `calculate_fuzzy_score`) |
| `[MODIFY]` | `@[backend_v2/services/orchestrator/anchor_validation_service.py#L32-L855]` | Delegate `normalize_text_with_mapping` (`#L43-L93`), `strict_match` (`#L95-L164`), and `calculate_fuzzy_score` (`#L166-L183`) to `[NEW] @[backend_v2/services/orchestrator/anchor_validation/lexical_normalizer.py]` with explicit redundant re-exports |

## 3. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Create Leaf Lexical Normalizer Module">
    <constraint invariant="topological_leaf_first_extraction_mandate">Extracted leaf module MUST NOT import from backend_v2/services/orchestrator/anchor_validation_service.py and MUST NOT exceed 350 lines.</constraint>
    <constraint invariant="strangler_fig_mandate">Do NOT create backend_v2/services/orchestrator/anchor_validation/__init__.py while backend_v2/services/orchestrator/anchor_validation_service.py exists.</constraint>
    <action>
      1. Create `[NEW] @[backend_v2/services/orchestrator/anchor_validation/lexical_normalizer.py]` (~175 lines, all lines `<= 120` chars) with `__all__ = ["MAX_CITATION_SPAN_CHARS", "MIN_ENTROPY_GATE_CHARS", "MIN_MULTI_SEGMENT_FLOOR_CHARS", "calculate_fuzzy_score", "normalize_text_with_mapping", "strict_match"]`:
         - Define `MAX_CITATION_SPAN_CHARS: int = 1000`, `MIN_MULTI_SEGMENT_FLOOR_CHARS: int = 30`, and `MIN_ENTROPY_GATE_CHARS: int = 10`.
         - `normalize_text_with_mapping(text: str) -> tuple[str, list[int]]`: Relocate verbatim from `@[backend_v2/services/orchestrator/anchor_validation_service.py#L43-L93]`, stripping HTML/XML tags (`</?[a-zA-Z_][a-zA-Z0-9_-]*(?:\s[^>]*)?>`) while mapping `\ufffd` to `'a'` and applying NFKD diacritic folding.
         - `strict_match(norm_quote: str | Sequence[str], norm_source: str, source_mapping: list[int] | None = None, max_span_chars: int = MAX_CITATION_SPAN_CHARS) -> bool`: Relocate verbatim from `@[backend_v2/services/orchestrator/anchor_validation_service.py#L95-L164]`, calling `normalize_text_with_mapping(seg)` on multi-segment parts and enforcing `MIN_MULTI_SEGMENT_FLOOR_CHARS` and `max_span_chars`.
         - `calculate_fuzzy_score(norm_quote: str, norm_source: str) -> float`: Relocate verbatim from `@[backend_v2/services/orchestrator/anchor_validation_service.py#L166-L183]`, returning `float(fuzz.partial_ratio(norm_quote, norm_source))` or `0.0` when either input is empty.
    </action>
  </step>

  <step id="2" name="Wire Proxy Delegations in AnchorValidationService">
    <constraint invariant="explicit_reexport_mandate">Re-export leaf constants and functions in anchor_validation_service.py using explicit redundant aliases (from module import Symbol as Symbol) and __all__.</constraint>
    <action>
      1. Update `@[backend_v2/services/orchestrator/anchor_validation_service.py#L32-L855]` to import from `[NEW] @[backend_v2/services/orchestrator/anchor_validation/lexical_normalizer.py]`:
         - `from backend_v2.services.orchestrator.anchor_validation.lexical_normalizer import MAX_CITATION_SPAN_CHARS as MAX_CITATION_SPAN_CHARS`
         - `from backend_v2.services.orchestrator.anchor_validation.lexical_normalizer import MIN_ENTROPY_GATE_CHARS as MIN_ENTROPY_GATE_CHARS`
         - `from backend_v2.services.orchestrator.anchor_validation.lexical_normalizer import MIN_MULTI_SEGMENT_FLOOR_CHARS as MIN_MULTI_SEGMENT_FLOOR_CHARS`
         - `from backend_v2.services.orchestrator.anchor_validation.lexical_normalizer import calculate_fuzzy_score as calculate_fuzzy_score`
         - `from backend_v2.services.orchestrator.anchor_validation.lexical_normalizer import normalize_text_with_mapping as normalize_text_with_mapping`
         - `from backend_v2.services.orchestrator.anchor_validation.lexical_normalizer import strict_match as strict_match`
      2. Replace the bodies of `AnchorValidationService.normalize_text_with_mapping` (`@[backend_v2/services/orchestrator/anchor_validation_service.py#L43-L93]`), `AnchorValidationService.strict_match` (`@[backend_v2/services/orchestrator/anchor_validation_service.py#L95-L164]`), and `AnchorValidationService.calculate_fuzzy_score` (`@[backend_v2/services/orchestrator/anchor_validation_service.py#L166-L183]`) with 1-line delegations to the imported functions while preserving identical static method signatures and docstrings.
    </action>
  </step>

  <step id="3" name="Run Phase 1 Verification and Quality Gate">
    <constraint invariant="zero_tolerance_audit_loop">Run the full backend_audit_loop.py verification on both the new leaf module and the proxy monolith before committing.</constraint>
    <action>
      1. Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation/lexical_normalizer.py --test --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation_service.py --test --ast-strict`.
      2. Verify all 53 unit tests in `@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py#L14-L21]` and all 6 unit tests in `@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_atom_result.py#L28-L48]` pass 100% with zero regressions.
    </action>
  </step>

  <test_contracts>
    <contract type="regression" name="test_anchor_validation_exact_match">
      Verifies that normalize_text_with_mapping and strict_match preserve exact substring matching parity via AnchorValidationService.validate_evidence.
    </contract>
    <contract type="positive" name="test_anchor_validation_html_tags_ignored">
      Verifies that normalize_text_with_mapping strips inline HTML tags while preserving exact character index mapping to the physical source string.
    </contract>
    <contract type="negative" name="test_anchor_validation_encoding_resilience">
      Verifies that Unicode replacement characters (\ufffd) and Nordic diacritics map deterministically during normalization and fuzzy score calculation.
    </contract>
  </test_contracts>
</execution_protocol>
```
