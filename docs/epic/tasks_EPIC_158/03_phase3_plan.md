# Phase 3: Lexical Firewall Multi-Segment & Distance Verification (Gates 1–4, WP2)

**Overview:** Upgrade `AnchorValidationService` to validate multi-segment citation tuples, enforcing bidirectional coordinate mapping, forward-scan search monotonic ordering ($s_k < e_k < s_{k+1}$), single-document buffer boundary isolation, and global span limit ($(e_m - s_1) \le 1\,000$ characters). Update prompt extraction mandates in `matrix_evaluation.py` to instruct foundational models on valid 1–3 segment citation extraction while preserving strict specificity.

**Source:** @[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md#L295-L306] Phase 3: Lexical Firewall Multi-Segment & Distance Verification (Gates 1–4, WP2)

**Target Files:**
- `[MODIFY]` @[backend_v2/services/orchestrator/anchor_validation_service.py#L20-L518]
- `[MODIFY]` @[backend_v2/models/prompts/execution/matrix_evaluation.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py]

### 5-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`AnchorValidationService.strict_match` (`@[backend_v2/services/orchestrator/anchor_validation_service.py#L79-L112]`)** | Banned mutable `list[str]` parameter signature, greedy un-ordered find without forward offset, and unconstrained bounding spans. | Modernized signature `strict_match(pdf_text: str, exact_quotes: Sequence[str] \| tuple[str, ...] \| list[str]) -> GateMatchResultDTO`, forward-scan search `find(norm_q_k, prev_end + 1)`, monotonic ordering $s_k < e_k < s_{k+1}$, segment floor $\ge 30$ chars when $m > 1$, span ceiling $(e_m - s_1) \le 1\,000$ chars, returning immutable `GateMatchResultDTO`. | Pruned separate single vs multi-segment matching functions; unified under one monotonic loop where single quote is $m=1$. | `pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py` asserting `GateMatchResultDTO(is_valid=False)` on inverted order or span $>1\,000$. |
| **`AnchorValidationService._is_lexically_valid` (`@[backend_v2/services/orchestrator/anchor_validation_service.py#L133-L305]`)** | Banned greedy first-match locking on $q_1$ causing false rejection when $q_1$ repeats prior to true evidence window. | Candidate $s_1$ anchor iteration: iterate candidate occurrences of $q_1$ in `norm_doc` and chain subsequent segments $k > 1$ within $[prev\_end + 1, s_1 + 1\,000]$, returning strongly typed `GateMatchResultDTO` across Gates 1–4. | Pruned recursive backtracking search tree; bounded linear forward-scan within $[s_1, s_1 + 1\,000]$ window. | `pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py` asserting repeated phrase prior to $q_1$ passes without false rejection. |
| **`AnchorValidationService.validate_evidence` (`@[backend_v2/services/orchestrator/anchor_validation_service.py#L307-L445]`)** | Banned returning mutable `list[str]`, independent per-segment validation that ignores monotonic order, magic numbers, and cross-document buffer leaks. | Modernized signature `validate_evidence(..., exact_quotes: Sequence[str] \| tuple[str, ...] \| list[str] \| None, ...) -> tuple[str, ...] \| None`, single-document buffer boundary isolation (`<ai_context_directive>`, `<user_payload>`, `<ai_draft_context>`), constants `MAX_CITATION_SPAN_CHARS = 1000`, `MIN_MULTI_SEGMENT_FLOOR_CHARS = 30`, `MIN_ENTROPY_GATE_CHARS = 10`, and symmetric physical slicing via `pdf_map`. | Pruned duplicate per-segment loop; orchestrate multi-segment tuple verification in one atomic pass. | `pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py` asserting `SemanticEvidenceError` on cross-document chimera, inverted order, or span $>1\,000$. |
| **`AnchorValidationService.process_atom_evaluation` (`@[backend_v2/services/orchestrator/anchor_validation_service.py#L447-L518]`)** | Banned per-segment independent document matching allowing segment 1 to match Document A and segment 2 to match Document B. | Cohesive tuple matching: all segments in `atom.source_quotes` must resolve within the same single `SourceDocumentContext` or MCP text monotonically within 1 000 chars, eliminating cross-document chimeras. | Pruned cross-document union accumulation; evaluate candidate documents independently as isolated units. | `pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py` asserting cross-document quote splits fail matching. |
| **`MATRIX_SENSOR_SYSTEM_PROMPT` (`@[backend_v2/models/prompts/execution/matrix_evaluation.py]`)** | Banned open-ended ambiguities, intra-segment ellipses, and cross-document chimera extraction in prompt directives. | Updated `evidence_extraction_mandate` instructing 1 to 3 non-contiguous sentence segments in `source_quotes`, retaining unbroken character substring mandate per segment, Chimera ban, Null Hypothesis (`source_quotes = null` on absence), and zero prohibited open-ended qualifiers. | Pruned redundant prompt guidelines; consolidated into clear, static XML mandates. | `pytest backend_v2/tests/unit/models/prompts/test_matrix_evaluation.py` passing 100% with zero banned ambiguities. |
| **Unit & ISTQB Boundary Tests (`@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py]`)** | Banned happy-path only testing and unverified boundary edge cases. | Comprehensive ISTQB coverage: (1) inverted order raises `SemanticEvidenceError`; (2) repeated phrase prior to $q_1$ passes; (3) cross-document chimera raises `SemanticEvidenceError`; (4) span $>1\,000$ chars raises `SemanticEvidenceError`; (5) segment $<30$ chars when $m > 1$ raises `SemanticEvidenceError`; (6) symmetric extraction of 2- and 3-segment tuples; (7) single-segment ($m=1$) under 30 chars passes. | Pruned redundant assertion duplication; structured test fixtures with parameterized inputs. | `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation_service.py --test --ast-strict`. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK &amp; PRE-IMPLEMENTATION TECHNICAL DEBT CLEANUPS">
    <action>Look backward: Verify Phase 1 and Phase 2 foundational DTO contracts (defined `GateMatchResultDTO`, `source_quotes: tuple[str, ...] | None`) are active in @[backend_v2/models/core_base.py] and @[backend_v2/models/dtos/quote_evidence.py].</action>
    <action>Look forward: Verify baseline state in @[backend_v2/services/orchestrator/anchor_validation_service.py#L20-L518] and @[backend_v2/models/prompts/execution/matrix_evaluation.py] before implementing multi-segment verification algorithms.</action>
    <action>Pre-Implementation Debt Cleanup in @[backend_v2/services/orchestrator/anchor_validation_service.py#L20-L518]: Modernize parameter types on `strict_match` (`exact_quotes: Sequence[str] | tuple[str, ...] | list[str]`), `validate_evidence` (`exact_quotes: Sequence[str] | tuple[str, ...] | list[str] | None`), and modernize return type of `validate_evidence` to immutable `tuple[str, ...] | None`.</action>
    <action>Pre-Implementation Debt Cleanup in @[backend_v2/services/orchestrator/anchor_validation_service.py#L20-L518]: Extract unannotated magic number limits into explicit class/module constants: `MAX_CITATION_SPAN_CHARS: int = 1000`, `MIN_MULTI_SEGMENT_FLOOR_CHARS: int = 30`, `MIN_ENTROPY_GATE_CHARS: int = 10`.</action>
    <constraint invariant="universal_fail_fast">If alignment is broken or prerequisite models are missing, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md]) and the Tracker document (@[docs/epic/EPIC_158_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/03_phase3_plan.md] @[docs/epic/EPIC_158_tracker.md]`.</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/services/orchestrator/anchor_validation_service.py#L20-L518]</backend>
    <backend>@[backend_v2/models/prompts/execution/matrix_evaluation.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py]</backend>
  </touched_artifacts>

  <dod_checklist>
    <item>`normalize_text_with_mapping` enhanced to preserve bidirectional coordinate mapping across non-contiguous segments in @[backend_v2/services/orchestrator/anchor_validation_service.py#L27-L77].</item>
    <item>`strict_match` updated to accept multi-segment ordered tuples, enforce forward-scan search monotonic ordering ($s_k < e_k < s_{k+1}$), enforce individual segment floor of 30 characters when $m > 1$, enforce bounding span limit ($(e_m - s_1) \le 1\,000$ characters), and return strongly typed `GateMatchResultDTO` in @[backend_v2/services/orchestrator/anchor_validation_service.py#L79-L112].</item>
    <item>`_is_lexically_valid` enhanced with candidate $s_1$ anchor iteration, forward-scan search `norm_doc.find(norm_q_k, prev_segment_end_idx + 1)`, monotonic ordering ($s_k < e_k < s_{k+1}$), single-document buffer boundary isolation, and global span limit ($(e_m - s_1) \le 1\,000$) in @[backend_v2/services/orchestrator/anchor_validation_service.py#L133-L305].</item>
    <item>`validate_evidence` updated to orchestrate multi-segment validation, enforce single-document buffer isolation, extract symmetric physical slices via `pdf_map`, and return `tuple[str, ...] | None` in @[backend_v2/services/orchestrator/anchor_validation_service.py#L307-L445].</item>
    <item>`process_atom_evaluation` updated to match multi-segment citations cohesively against individual candidate documents, preventing cross-document chimera matches in @[backend_v2/services/orchestrator/anchor_validation_service.py#L447-L518].</item>
    <item>`evidence_extraction_mandate` updated in @[backend_v2/models/prompts/execution/matrix_evaluation.py] to instruct LLM on 1–3 non-contiguous sentence extraction while retaining Chimera and Ellipsis bans and zero ambiguous phrases.</item>
    <item>ISTQB negative and boundary test suite passing in @[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py].</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
    <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_opaque_id_hydration.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
    <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
    <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_chat_ingress_and_provenance_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_generation_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Do NOT modify Gate 5 Snowball morphological strictness or workflow strictness fields in Phase 3.</anti_target>
    <anti_target>Do NOT alter sliding window causal linker algorithms prior to Phase 5.</anti_target>
    <anti_target>Do NOT allow intra-segment ellipsis stitching or relax the single continuous substring rule within an individual segment.</anti_target>
    <anti_target>Do NOT return anonymous tuples from `AnchorValidationService` matching methods.</anti_target>
    <anti_target>Do NOT introduce ambiguous open-ended qualifiers or ungrounded illustrative markers into prompt assets or system instructions.</anti_target>
  </anti_targets>

  <step id="1" name="ENHANCE COORDINATE NORMALIZATION &amp; STRICT MATCHING">
    <action>In @[backend_v2/services/orchestrator/anchor_validation_service.py#L27-L77]: Enhance `normalize_text_with_mapping` with byte-range index bounds tracking across non-contiguous segments.</action>
    <action>In @[backend_v2/services/orchestrator/anchor_validation_service.py#L79-L112]: Update `strict_match` to accept multi-segment ordered tuples `tuple[str, ...] | list[str] | Sequence[str]`, enforce forward-scan search monotonic ordering ($s_k < e_k < s_{k+1}$), enforce individual segment floor of 30 characters when $m > 1$, enforce bounding span limit ($(e_m - s_1) \le 1\,000$ characters), and return strongly typed `GateMatchResultDTO`.</action>
    <constraint invariant="strict_physical_anchoring_mandate">Physical document coordinate mappings must accurately map normalized character offsets back to raw document byte indices.</constraint>
  </step>

  <step id="2" name="IMPLEMENT FORWARD-SCAN SEARCH, MONOTONIC ORDERING &amp; SPAN BOUNDING">
    <action>In @[backend_v2/services/orchestrator/anchor_validation_service.py#L133-L305]: Implement candidate $s_1$ anchor iteration and forward-scan search `norm_doc.find(norm_q_k, prev_segment_end_idx + 1)` in `_is_lexically_valid`. Enforce monotonic ordering ($s_k < e_k < s_{k+1}$), single-document buffer boundary isolation, individual segment floor of 30 characters when $m > 1$, and global bounding span ceiling ($(e_m - s_1) \le 1\,000$ characters). Raise `SemanticEvidenceError` on boundary breaches or inverted ordering.</action>
    <action>In @[backend_v2/services/orchestrator/anchor_validation_service.py#L307-L445]: Update `validate_evidence` to orchestrate multi-segment tuple validation with candidate $s_1$ iteration, enforce single-document buffer isolation (preventing citations from crossing `<ai_context_directive>`, `<user_payload>`, or `<ai_draft_context>` boundaries), extract symmetric physical slices via `pdf_map`, and return `tuple[str, ...] | None`.</action>
    <constraint invariant="the_zero_compromise_pledge">Zero tolerance for inverted segment ordering or cross-document buffer leaks.</constraint>
  </step>

  <step id="3" name="ENFORCE SINGLE-DOCUMENT BUFFER ISOLATION IN ATOM PROCESSING">
    <action>In @[backend_v2/services/orchestrator/anchor_validation_service.py#L447-L518]: In `process_atom_evaluation`, validate multi-segment citations as a cohesive tuple against each candidate source document in `source_documents` and `mcp_source_texts`. Enforce that all segments must resolve monotonically within the same single source document buffer, eliminating cross-document chimera matching.</action>
    <constraint invariant="universal_fail_fast">Multi-segment quotes spanning across discrete document boundaries must fail matching.</constraint>
  </step>

  <step id="4" name="UPDATE PROMPT EXTRACTION MANDATE IN MATRIX EVALUATION">
    <action>In @[backend_v2/models/prompts/execution/matrix_evaluation.py]: Update `evidence_extraction_mandate` to instruct foundational models that citations may consist of 1 to 3 non-contiguous sentence segments in `source_quotes`, while preserving strict specificity, forbidding ellipses within individual segments, banning cross-document chimeras, and adhering strictly to the Null Hypothesis (`source_quotes = null` on absence or ungrounded claims). Ensure zero prohibited open-ended markers or ungrounded illustrative qualifiers are introduced.</action>
    <constraint invariant="prompt_illustrative_examples_mandate">Preserve illustrative guidance on multi-segment citation formatting without mutating frozen coaching prompts.</constraint>
  </step>

  <step id="5" name="EXPAND ISTQB BOUNDARY &amp; NEGATIVE TEST SUITE">
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py]: Add comprehensive unit and ISTQB boundary test coverage:
      (1) Inverted segment order ($s_2 < s_1$) raises `SemanticEvidenceError`;
      (2) Repeated phrase prior to $q_1$ does not trigger false rejection via candidate $s_1$ anchor iteration and forward-scan search;
      (3) Cross-document chimera across `<ai_context_directive>` boundaries raises `SemanticEvidenceError`;
      (4) Bounding span exceeding 1 000 characters raises `SemanticEvidenceError`;
      (5) Multi-segment citation with any segment under 30 characters when $m > 1$ raises `SemanticEvidenceError`;
      (6) Valid 2-segment and 3-segment ordered citations match and slice physical source text symmetrically;
      (7) Single-segment citation ($m=1$) under 30 characters (but $\ge 10$ chars) passes without being rejected by multi-segment floor;
      (8) Cross-document chimera across separate `SourceDocumentContext` instances in `process_atom_evaluation` fails matching.
    </action>
    <constraint invariant="universal_quality_gate">All test cases must pass 100% with strict AST compliance.</constraint>
  </step>

  <test_contracts>
    <test name="test_anchor_validation_multi_segment_ordered_monotonic_success" category="positive">
      <input>tuple of 2 ordered segments separated by intervening text within 1 000 characters</input>
      <expected>GateMatchResultDTO(is_valid=True, start_idx=s1, end_idx=e2)</expected>
    </test>
    <test name="test_anchor_validation_inverted_segment_order_raises_semantic_error" category="error_path">
      <input>tuple of 2 segments where segment 2 precedes segment 1 in source text</input>
      <expected>raises SemanticEvidenceError</expected>
    </test>
    <test name="test_anchor_validation_span_exceeding_1000_chars_raises_semantic_error" category="boundary">
      <input>tuple of 2 segments where (e2 - s1) = 1 001 characters</input>
      <expected>raises SemanticEvidenceError</expected>
    </test>
    <test name="test_anchor_validation_cross_document_chimera_raises_semantic_error" category="error_path">
      <input>segment 1 from document A and segment 2 from document B</input>
      <expected>raises SemanticEvidenceError</expected>
    </test>
    <test name="test_anchor_validation_multi_segment_floor_under_30_chars_raises_semantic_error" category="boundary">
      <input>tuple of 2 segments where one segment is 25 characters (< 30)</input>
      <expected>raises SemanticEvidenceError</expected>
    </test>
    <test name="test_anchor_validation_candidate_s1_iteration_repeated_phrase_success" category="positive">
      <input>segment 1 repeats in document preamble, and subsequent segments match after second occurrence</input>
      <expected>matches successfully via candidate s1 iteration</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute localized unit tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py`.</action>
    <action>Execute backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation_service.py backend_v2/models/prompts/execution/matrix_evaluation.py --test --ast-strict`.</action>
  </validation_gate>
</execution_protocol>
```

