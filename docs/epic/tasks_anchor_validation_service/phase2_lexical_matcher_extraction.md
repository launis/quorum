<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
</required_context_rules>

# Phase 2: Multi-Tier Lexical Matcher Extraction (`phase2_lexical_matcher_extraction.md`)

## 1. Objective
Execute Phase 2 of the Two-Epoch Strangler Fig decomposition for `@[backend_v2/services/orchestrator/anchor_validation_service.py#L32-L855]`:
1. Extract the multi-tier lexical matcher `AnchorValidationService._is_lexically_valid` (`@[backend_v2/services/orchestrator/anchor_validation_service.py#L185-L425]`) into `[NEW] @[backend_v2/services/orchestrator/anchor_validation/lexical_matcher.py]` as `is_lexically_valid`.
2. Ensure `[NEW] @[backend_v2/services/orchestrator/anchor_validation/lexical_matcher.py]` imports leaf utilities exclusively from `[NEW] @[backend_v2/services/orchestrator/anchor_validation/lexical_normalizer.py]`, `backend_v2.models.dtos.quote_evidence`, `backend_v2.settings`, and `backend_v2.utils.linguistics`, with zero imports from `anchor_validation_service.py`.
3. Retain a 1-line delegation inside `AnchorValidationService._is_lexically_valid` (`@[backend_v2/services/orchestrator/anchor_validation_service.py#L185-L425]`) so all existing callers and unit tests pass 100% unchanged.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/services/orchestrator/anchor_validation/lexical_matcher.py]` | Multi-tier lexical verifier (`is_lexically_valid`) executing Gate 0 (multi-segment sequence), Gate 1 (exact `str.find`), Gate 2 (RapidFuzz `partial_ratio_alignment`), and Gate 3 (Snowball stem window contiguity), returning `GateMatchResultDTO` |
| `[MODIFY]` | `@[backend_v2/services/orchestrator/anchor_validation_service.py#L32-L855]` | Delegate `AnchorValidationService._is_lexically_valid` (`#L185-L425`) to `[NEW] @[backend_v2/services/orchestrator/anchor_validation/lexical_matcher.py]` with explicit redundant re-export |

## 3. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Create Multi-Tier Lexical Matcher Sub-Module">
    <constraint invariant="topological_leaf_first_extraction_mandate">lexical_matcher.py MUST import leaf functions from lexical_normalizer.py and MUST NOT import from anchor_validation_service.py.</constraint>
    <constraint invariant="strict_physical_anchoring_mandate">Preserve Gate 0, Gate 1 (exact str.find), Entropy Gate (MIN_ENTROPY_GATE_CHARS = 10), Gate 2 (RapidFuzz partial_ratio_alignment), and Gate 3 (Snowball stem contiguity) 100% verbatim.</constraint>
    <action>
      1. Create `[NEW] @[backend_v2/services/orchestrator/anchor_validation/lexical_matcher.py]` (~270 lines, all lines `<= 120` chars) with `__all__ = ["is_lexically_valid"]`:
         - Import `MAX_CITATION_SPAN_CHARS`, `MIN_ENTROPY_GATE_CHARS`, `MIN_MULTI_SEGMENT_FLOOR_CHARS`, `calculate_fuzzy_score`, `normalize_text_with_mapping`, and `strict_match` from `backend_v2.services.orchestrator.anchor_validation.lexical_normalizer`.
         - Import `GateMatchResultDTO` from `backend_v2.models.dtos.quote_evidence`, `get_lexical_fuzz_threshold` from `backend_v2.settings`, and `check_entropy_gate`, `check_window_contiguity`, `extract_stems`, `find_candidate_windows` from `backend_v2.utils.linguistics`.
         - Implement `is_lexically_valid(quote: str | Sequence[str], source_text: str, norm_source: str | None = None, locale: str = "en", strictness_level: int = 50, source_mapping: list[int] | None = None, max_span_chars: int = MAX_CITATION_SPAN_CHARS) -> GateMatchResultDTO` relocated verbatim from `@[backend_v2/services/orchestrator/anchor_validation_service.py#L185-L425]`, replacing internal `AnchorValidationService.*` calls with direct calls to `normalize_text_with_mapping`, `strict_match`, `calculate_fuzzy_score`, and recursive `is_lexically_valid` for multi-segment parts.
    </action>
  </step>

  <step id="2" name="Wire Proxy Delegation in AnchorValidationService">
    <constraint invariant="explicit_reexport_mandate">Import is_lexically_valid as is_lexically_valid in anchor_validation_service.py and delegate AnchorValidationService._is_lexically_valid to it.</constraint>
    <action>
      1. Update `@[backend_v2/services/orchestrator/anchor_validation_service.py#L32-L855]` to import `from backend_v2.services.orchestrator.anchor_validation.lexical_matcher import is_lexically_valid as is_lexically_valid`.
      2. Replace the method body of `AnchorValidationService._is_lexically_valid` (`@[backend_v2/services/orchestrator/anchor_validation_service.py#L185-L425]`) with a 1-line return delegating all arguments to `is_lexically_valid(...)` while keeping `validate_evidence` and `process_atom_evaluation` calling `is_lexically_valid`.
    </action>
  </step>

  <step id="3" name="Run Phase 2 Verification and Quality Gate">
    <constraint invariant="zero_tolerance_audit_loop">Run backend_audit_loop.py with --test --ast-strict on the new sub-module and the proxy monolith.</constraint>
    <action>
      1. Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation/lexical_matcher.py --test --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation_service.py --test --ast-strict`.
      2. Execute `uv run pytest backend_v2/tests/unit/services/orchestrator/test_multi_segment_quote_foundation.py` to verify multi-segment exact and fuzzy index resolution parity.
    </action>
  </step>

  <test_contracts>
    <contract type="regression" name="test_anchor_validation_symmetric_index_resolution_exact">
      Verifies that Gate 1 exact matching in is_lexically_valid returns exact physical start_idx and end_idx bounds in GateMatchResultDTO.
    </contract>
    <contract type="positive" name="test_anchor_validation_symmetric_index_resolution_fuzzy">
      Verifies that Gate 2 RapidFuzz partial_ratio_alignment and Gate 3 stem window contiguity resolve physical character indices across inflected morphology.
    </contract>
    <contract type="negative" name="test_multi_segment_causal_e2e_negative_chimera_and_ordering_rejection">
      Verifies that multi-segment quotes violating physical ordering, minimum floor length, or maximum span cap are rejected deterministically by Gate 0.
    </contract>
  </test_contracts>
</execution_protocol>
```
