"""Unit test bridge for CausalCohesionEvaluator service.

Provides 1:1 test discovery parity with backend_audit_loop automated test resolution.
"""

from __future__ import annotations

from backend_v2.tests.unit.services.orchestrator.test_causal_cohesion_scoring import (
    evaluator,
    test_causal_cohesion_algorithm_1_cascading_node_failure,
    test_causal_cohesion_algorithm_1_warrant_vs_node_failure,
    test_causal_cohesion_ast_monotonic_chain_verified,
    test_causal_cohesion_cognitive_atom_validation,
    test_causal_cohesion_cumulative_guttman_invariant,
    test_causal_cohesion_cyclic_defect_grounding,
    test_causal_cohesion_dynamic_matrix_id_binding,
    test_causal_cohesion_idempotency_set_guard,
    test_causal_cohesion_level_2_discontinuous_cohesion,
    test_causal_cohesion_level_3_moderate_cohesion,
    test_causal_cohesion_level_4_failure_blocks_level_5,
    test_causal_cohesion_level_4_strong_cohesion,
    test_causal_cohesion_level_5_full_mastery,
    test_causal_cohesion_mandatory_matrix_block_id,
    test_causal_cohesion_monotonic_inheritance_invariant,
    test_causal_cohesion_subgraph_cumulative_guttman_invariant,
    test_causal_cohesion_zero_node_grounding,
)

__all__ = [
    "evaluator",
    "test_causal_cohesion_algorithm_1_cascading_node_failure",
    "test_causal_cohesion_algorithm_1_warrant_vs_node_failure",
    "test_causal_cohesion_ast_monotonic_chain_verified",
    "test_causal_cohesion_cognitive_atom_validation",
    "test_causal_cohesion_cumulative_guttman_invariant",
    "test_causal_cohesion_cyclic_defect_grounding",
    "test_causal_cohesion_dynamic_matrix_id_binding",
    "test_causal_cohesion_idempotency_set_guard",
    "test_causal_cohesion_level_2_discontinuous_cohesion",
    "test_causal_cohesion_level_3_moderate_cohesion",
    "test_causal_cohesion_level_4_failure_blocks_level_5",
    "test_causal_cohesion_level_4_strong_cohesion",
    "test_causal_cohesion_level_5_full_mastery",
    "test_causal_cohesion_mandatory_matrix_block_id",
    "test_causal_cohesion_monotonic_inheritance_invariant",
    "test_causal_cohesion_subgraph_cumulative_guttman_invariant",
    "test_causal_cohesion_zero_node_grounding",
]
