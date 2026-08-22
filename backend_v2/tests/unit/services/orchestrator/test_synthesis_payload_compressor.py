"""Unit tests for SynthesisPayloadCompressor (SSOT).

Re-exports unit tests for synthesis payload compression so that backend_audit_loop
can deterministically discover and execute tests for synthesis_payload_compressor.py.
"""

from backend_v2.tests.unit.test_synthesis_payload_compression import (
    test_compress_payload_evaluations_empty_after_compression_fails_fast,
    test_compress_payload_heterogeneous_dag_types,
    test_compress_payload_prioritized_stratification_retains_critical_deficits_over_passes,
    test_compress_payload_stratification_is_100_percent_deterministic_with_tiebreakers,
    test_compress_payload_strips_hydrated_references_and_heavy_keys,
    test_compress_payload_unbounded_when_zero_evaluations_limit,
    test_compress_payload_with_results_only_no_evaluations,
    test_compress_synthesis_payload_basemodel_input,
    test_compress_synthesis_payload_negative_empty_input,
    test_compress_synthesis_payload_negative_invalid_types,
    test_compress_synthesis_payload_negative_missing_mandatory_field,
    test_compress_synthesis_payload_negative_non_dict_evaluation,
    test_compress_synthesis_payload_negative_validation_error,
    test_compress_synthesis_payload_scalar_input,
    test_compress_synthesis_payload_string_input,
    test_compress_synthesis_payload_strips_atom_quotes,
)

__all__ = [
    "test_compress_payload_evaluations_empty_after_compression_fails_fast",
    "test_compress_payload_heterogeneous_dag_types",
    "test_compress_payload_prioritized_stratification_retains_critical_deficits_over_passes",
    "test_compress_payload_stratification_is_100_percent_deterministic_with_tiebreakers",
    "test_compress_payload_strips_hydrated_references_and_heavy_keys",
    "test_compress_payload_unbounded_when_zero_evaluations_limit",
    "test_compress_payload_with_results_only_no_evaluations",
    "test_compress_synthesis_payload_basemodel_input",
    "test_compress_synthesis_payload_negative_empty_input",
    "test_compress_synthesis_payload_negative_invalid_types",
    "test_compress_synthesis_payload_negative_missing_mandatory_field",
    "test_compress_synthesis_payload_negative_non_dict_evaluation",
    "test_compress_synthesis_payload_negative_validation_error",
    "test_compress_synthesis_payload_scalar_input",
    "test_compress_synthesis_payload_string_input",
    "test_compress_synthesis_payload_strips_atom_quotes",
]
