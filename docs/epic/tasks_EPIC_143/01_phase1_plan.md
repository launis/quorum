# Phase 1: Foundation & SSOT Utilities

**Overview:** Centralize synthesis quote and deficit limit settings in `Settings` and implement the generic, pure `ranked_round_robin_select[T]` algorithm with dedicated unit test coverage. This phase provides the foundation for downstream curation in Phase 3 and Phase 4.
**Target Files:**
- `[MODIFY]` @[backend_v2/settings.py]
- `[NEW]` @[backend_v2/utils/ranked_round_robin.py]
- `[NEW]` @[backend_v2/tests/unit/utils/test_ranked_round_robin.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by previous epics (EPIC 141, EPIC 142). Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/settings.py] and the newly targeted files.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_143_Synthesis_Matrix_Explanation_Fix.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [x] Settings SSOT verified or updated in @[backend_v2/settings.py] with max_synthesis_quote_length (300), max_synthesis_quotes_per_matrix (5), and max_synthesis_unmet_criteria_per_matrix (5).
    - [x] Pure, deterministic ranked_round_robin_select[T] utility implemented in `[NEW]` @[backend_v2/utils/ranked_round_robin.py] with O(N log N + K) complexity via native O(1) tail .pop() and inverted sorting.
    - [x] Comprehensive unit tests created in `[NEW]` @[backend_v2/tests/unit/utils/test_ranked_round_robin.py] covering empty inputs, single group, multi-group interleaving, budget capping, unequal groups, and O(1) performance scaling (&lt;25ms for 10^4 items).
  </dod_checklist>

  <required_context_rules>
    - @[.agents/rules/00-antigravity-core.md]
    - @[.agents/rules/01-python-backend.md]
    - @[.agents/rules/05_llm_architecture.md]
    - @[ki_god_code_prevention.md]
    - @[ki_synthesis_payload_compression.md]
    - @[ki_matrix_boolean_evaluation_strictness.md]
    - @[ki_dual_axis_localization_architecture.md]
    - @[ki_tripartite_pipeline_architecture.md]
    - @[ki_sdui_matrix_synthesis.md]
    - @[ki_sdui_adapter_pattern.md]
    - @[ki_flat_polymorphic_pipeline.md]
    - @[ki_global_config_sovereignty.md]
    - @[ki_python_314_concurrency_strictness.md]
    - @[ki_ai_testing_standards.md]
    - @[ki_ast_guardrail_testing.md]
    - @[ki_dag_engine_dto_projection_rules.md]
    - @[ki_epic_lifecycle_workflow.md]
    - @[ki_context_enriched_decompose_verify.md]
    - @[ki_strict_sdui_serialization.md]
    - @[ki_llm_extraction_architecture.md]
    - @[ki_topological_engine.md]
    - @[ki_execution_engine_protocol.md]
    - @[ki_matrix_sensor_prompt_builder.md]
  </required_context_rules>

  <anti_targets>
    - Do NOT hardcode magic numbers (specifically: raw numerical slices) inside service files.
    - Do NOT implement naive pop(0) in ranked_round_robin_select that causes O(N^2) list shifting degradation.
    - Do NOT modify any synthesis distiller, explanation service, or SDUI adapter files in Phase 1.
  </anti_targets>

  <step id="1" name="Centralized Settings SSOT Verification">
    <action>[ALREADY_IMPLEMENTED] - Skip execution. Verified at: @[backend_v2/settings.py#L136-L138]. Verify that Settings class contains:
max_synthesis_quote_length: Annotated[int, Field(description="Maximum character length for evidence quotes in synthesis payloads")] = 300
max_synthesis_quotes_per_matrix: Annotated[int, Field(description="Maximum number of evidence quotes per matrix in synthesis explanation context")] = 5
max_synthesis_unmet_criteria_per_matrix: Annotated[int, Field(description="Maximum number of unmet criteria descriptions per matrix in synthesis explanation context")] = 5
    </action>
    <constraint invariant="global_config_sovereignty">All quote truncation, quote counts, and criteria limits must reference centralized settings in Settings.</constraint>
  </step>

  <step id="2" name="Ranked Round-Robin SSOT Utility Implementation">
    <action>Create `[NEW]` @[backend_v2/utils/ranked_round_robin.py] implementing pure, deterministic generic function ranked_round_robin_select[T] using PEP 695 generics with O(N log N + K) complexity via native O(1) tail .pop() extraction and inverted sorting.</action>
    <contract_freeze>
      <signature>def ranked_round_robin_select[T](items: Sequence[T], group_key: Callable[[T], Hashable], rank_key: Callable[[T], Any], max_items: int, *, reverse_rank: bool = True) -> list[T]:</signature>
    </contract_freeze>
    <action>Implement exact logic:
1. Return empty list if max_items &lt;= 0 or not items.
2. Group items by group_key preserving first appearance order: groups.setdefault(g_key, []).append(item).
3. Sort each group internally with reverse=not reverse_rank so highest-priority item is at the tail of the list (-1 index).
4. Interleave groups in round-robin order, popping from tail in O(1) time: selected.append(group_items.pop()).
5. When group empty, delete key via del groups[eg].
6. Stop when len(selected) &gt;= max_items or all groups exhausted.
    </action>
    <constraint invariant="ssot_reuse_mandate">Pure, side-effect free, deterministic generic utility acting as Single Source of Truth for group interleaving.</constraint>
  </step>

  <step id="3" name="Ranked Round-Robin Unit Tests">
    <action>Create `[NEW]` @[backend_v2/tests/unit/utils/test_ranked_round_robin.py] covering comprehensive test contracts.</action>
    <test_contracts>
      <test name="test_ranked_round_robin_empty_items_returns_empty" category="boundary">
        <input>items=[], group_key=lambda x: x, rank_key=lambda x: len(x), max_items=5</input>
        <expected>returns []</expected>
      </test>
      <test name="test_ranked_round_robin_max_items_non_positive_returns_empty" category="boundary">
        <input>items=["a", "b"], group_key=lambda x: x, rank_key=lambda x: len(x), max_items=0</input>
        <expected>returns []</expected>
      </test>
      <test name="test_ranked_round_robin_negative_max_items_returns_empty" category="boundary">
        <input>items=["a", "b"], group_key=lambda x: x, rank_key=lambda x: len(x), max_items=-5</input>
        <expected>returns []</expected>
      </test>
      <test name="test_ranked_round_robin_single_group_maintains_rank_order" category="positive">
        <input>items=["short", "very_long_string", "medium"], group_key=lambda x: "g1", rank_key=lambda x: len(x), max_items=3, reverse_rank=True</input>
        <expected>returns ["very_long_string", "medium", "short"]</expected>
      </test>
      <test name="test_ranked_round_robin_multi_group_interleaving" category="positive">
        <input>items=[("A", "a_short"), ("A", "a_longest_str"), ("B", "b_short"), ("B", "b_longest_str")], group_key=lambda x: x[0], rank_key=lambda x: len(x[1]), max_items=4, reverse_rank=True</input>
        <expected>interleaves groups: [("A", "a_longest_str"), ("B", "b_longest_str"), ("A", "a_short"), ("B", "b_short")]</expected>
      </test>
      <test name="test_ranked_round_robin_budget_truncation" category="boundary">
        <input>items=[("A", "a1"), ("A", "a2"), ("B", "b1"), ("B", "b2")], group_key=lambda x: x[0], rank_key=lambda x: x[1], max_items=3</input>
        <expected>len(result) == 3</expected>
      </test>
      <test name="test_ranked_round_robin_budget_exceeds_total_items_returns_all" category="boundary">
        <input>items=[("A", "a1"), ("B", "b1")], group_key=lambda x: x[0], rank_key=lambda x: x[1], max_items=100</input>
        <expected>returns all 2 items in round-robin order</expected>
      </test>
      <test name="test_ranked_round_robin_unequal_groups" category="positive">
        <input>group A with 1 item, group B with 4 items, max_items=4</input>
        <expected>picks 1 from A, 1 from B, then remaining from B without error</expected>
      </test>
      <test name="test_ranked_round_robin_reverse_rank_false_sorts_ascending" category="positive">
        <input>items=[("A", 10), ("A", 2), ("B", 20), ("B", 1)], group_key=lambda x: x[0], rank_key=lambda x: x[1], max_items=4, reverse_rank=False</input>
        <expected>interleaves smallest values first: [("A", 2), ("B", 1), ("A", 10), ("B", 20)]</expected>
      </test>
      <test name="test_ranked_round_robin_sequence_tuple_input" category="boundary">
        <input>items=(("A", "x"), ("B", "y")), group_key=lambda x: x[0], rank_key=lambda x: x[1], max_items=2</input>
        <expected>accepts immutable Sequence tuple without error</expected>
      </test>
      <test name="test_ranked_round_robin_unhashable_group_key_raises_type_error" category="negative">
        <input>items=[[1, 2], [3, 4]], group_key=lambda x: x, rank_key=lambda x: len(x), max_items=2</input>
        <expected>raises TypeError</expected>
      </test>
      <test name="test_ranked_round_robin_incompatible_rank_keys_raises_type_error" category="negative">
        <input>items=[("A", 1), ("A", "str_val")], group_key=lambda x: x[0], rank_key=lambda x: x[1], max_items=2</input>
        <expected>raises TypeError</expected>
      </test>
      <test name="test_ranked_round_robin_performance_scaling_o1_tail_pop" category="boundary">
        <input>10,000 items in 50 groups, max_items=5000</input>
        <expected>executes in &lt; 25ms proving O(1) tail .pop() efficiency</expected>
      </test>
    </test_contracts>
  </step>

  <validation_gate>
    Run automated unit tests:
    `uv run pytest backend_v2/tests/unit/utils/test_ranked_round_robin.py`
    `uv run python scripts/backend_audit_loop.py backend_v2/utils/ --test`
  </validation_gate>
</execution_protocol>
```
