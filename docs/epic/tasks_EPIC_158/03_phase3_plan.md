# Phase 3: Lexical Firewall Multi-Segment & Distance Verification (Gates 1–4, WP2)

**Overview:** Upgrade `AnchorValidationService` to validate multi-segment citation tuples, enforcing bidirectional coordinate mapping, forward-scan search monotonic ordering ($s_k < e_k < s_{k+1}$), single-document buffer boundary isolation, and global span limit ($(e_m - s_1) \le 1\,000$ characters). Update prompt extraction mandates in `matrix_evaluation.py` to instruct foundational models on valid 1–3 segment citation extraction while preserving strict specificity.

**Source:** @[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md#L295-L306] Phase 3: Lexical Firewall Multi-Segment & Distance Verification (Gates 1–4, WP2)

**Target Files:**
- `[MODIFY]` @[backend_v2/services/orchestrator/anchor_validation_service.py]
- `[MODIFY]` @[backend_v2/models/prompts/execution/matrix_evaluation.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Phase 1 and Phase 2 foundational DTO contracts (defined `GateMatchResultDTO`, `source_quotes: tuple[str, ...] | None`) are active in @[backend_v2/models/core_base.py] and @[backend_v2/models/dtos/quote_evidence.py].</action>
    <action>Look forward: Verify baseline state in @[backend_v2/services/orchestrator/anchor_validation_service.py] and @[backend_v2/models/prompts/execution/matrix_evaluation.py] before implementing multi-segment verification algorithms.</action>
    <constraint invariant="universal_fail_fast">If alignment is broken or prerequisite models are missing, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md]) and the Tracker document (@[docs/epic/EPIC_158_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/03_phase3_plan.md] @[docs/epic/EPIC_158_tracker.md]`.</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/services/orchestrator/anchor_validation_service.py]</backend>
    <backend>@[backend_v2/models/prompts/execution/matrix_evaluation.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py]</backend>
  </touched_artifacts>

  <dod_checklist>
    <item>`normalize_text_with_mapping` enhanced to preserve bidirectional coordinate mapping across non-contiguous segments in @[backend_v2/services/orchestrator/anchor_validation_service.py].</item>
    <item>`strict_match` updated to accept multi-segment ordered tuples and return strongly typed `GateMatchResultDTO` in @[backend_v2/services/orchestrator/anchor_validation_service.py].</item>
    <item>`_is_lexically_valid` enhanced with forward-scan search `norm_doc.find(norm_q_k, prev_segment_end_idx)`, monotonic ordering ($s_k < e_k < s_{k+1}$), single-document buffer boundary isolation, and global span limit ($(e_m - s_1) \le 1\,000$) in @[backend_v2/services/orchestrator/anchor_validation_service.py].</item>
    <item>`validate_evidence` updated to orchestrate multi-segment validation and provenance stream isolation in @[backend_v2/services/orchestrator/anchor_validation_service.py].</item>
    <item>`evidence_extraction_mandate` updated in @[backend_v2/models/prompts/execution/matrix_evaluation.py] to instruct LLM on 1–3 non-contiguous sentence extraction while retaining Chimera and Ellipsis bans.</item>
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
  </anti_targets>

  <step id="1" name="ENHANCE COORDINATE NORMALIZATION &amp; STRICT MATCHING">
    <action>In @[backend_v2/services/orchestrator/anchor_validation_service.py]: Enhance `normalize_text_with_mapping` with byte-range index bounds tracking across non-contiguous segments. Update `strict_match` to accept multi-segment ordered tuples `tuple[str, ...]` and return strongly typed `GateMatchResultDTO`.</action>
    <constraint invariant="strict_physical_anchoring_mandate">Physical document coordinate mappings must accurately map normalized character offsets back to raw document byte indices.</constraint>
  </step>

  <step id="2" name="IMPLEMENT FORWARD-SCAN SEARCH &amp; BOUNDARY ISOLATION">
    <action>In @[backend_v2/services/orchestrator/anchor_validation_service.py]: Implement forward-scan search `norm_doc.find(norm_q_k, prev_segment_end_idx)` in `_is_lexically_valid`. Enforce monotonic ordering ($s_k < e_k < s_{k+1}$), single-document buffer boundary isolation, individual segment floor of 30 characters when $m > 1$, and global bounding span ceiling ($(e_m - s_1) \le 1\,000$ characters). Raise `SemanticEvidenceError` on boundary breaches.</action>
    <action>In @[backend_v2/services/orchestrator/anchor_validation_service.py]: Update `validate_evidence` to orchestrate multi-segment tuple validation and maintain provenance stream isolation.</action>
    <constraint invariant="the_zero_compromise_pledge">Zero tolerance for inverted segment ordering or cross-document buffer leaks.</constraint>
  </step>

  <step id="3" name="UPDATE PROMPT EXTRACTION MANDATE IN MATRIX EVALUATION">
    <action>In @[backend_v2/models/prompts/execution/matrix_evaluation.py]: Update `evidence_extraction_mandate` to instruct foundational models that citations may consist of 1–3 non-contiguous sentences while maintaining strict specificity and forbidding ellipses within individual segments.</action>
    <constraint invariant="prompt_illustrative_examples_mandate">Preserve illustrative guidance on multi-segment citation formatting without mutating frozen coaching prompts.</constraint>
  </step>

  <step id="4" name="EXPAND ISTQB BOUNDARY &amp; NEGATIVE TEST SUITE">
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py]: Add comprehensive unit and ISTQB boundary test coverage: (1) Inverted segment order ($s_2 < s_1$) raises `SemanticEvidenceError`; (2) Repeated phrase prior to $q_1$ does not trigger false rejection; (3) Cross-document chimera raises `SemanticEvidenceError`; (4) Bounding span exceeding 1 000 characters raises `SemanticEvidenceError`; (5) Multi-segment citation with segment under 30 characters raises `SemanticEvidenceError`.</action>
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
  </test_contracts>

  <validation_gate>
    <action>Execute localized unit tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py`.</action>
    <action>Execute backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation_service.py backend_v2/models/prompts/execution/matrix_evaluation.py --test --ast-strict`.</action>
  </validation_gate>
</execution_protocol>
```
