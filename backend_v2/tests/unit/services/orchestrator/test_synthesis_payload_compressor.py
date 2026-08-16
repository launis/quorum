"""Unit tests for SynthesisPayloadCompressor (SSOT).

Re-exports unit tests for synthesis payload compression so that backend_audit_loop
can deterministically discover and execute tests for synthesis_payload_compressor.py.
"""

from backend_v2.tests.unit.test_synthesis_payload_compression import (
    test_compress_synthesis_payload_basemodel_input,
    test_compress_synthesis_payload_negative_empty_input,
    test_compress_synthesis_payload_negative_invalid_types,
    test_compress_synthesis_payload_negative_missing_mandatory_field,
    test_compress_synthesis_payload_negative_non_dict_evaluation,
    test_compress_synthesis_payload_negative_validation_error,
    test_compress_synthesis_payload_strips_atom_quotes,
)

__all__ = [
    "test_compress_synthesis_payload_basemodel_input",
    "test_compress_synthesis_payload_negative_empty_input",
    "test_compress_synthesis_payload_negative_invalid_types",
    "test_compress_synthesis_payload_negative_missing_mandatory_field",
    "test_compress_synthesis_payload_negative_non_dict_evaluation",
    "test_compress_synthesis_payload_negative_validation_error",
    "test_compress_synthesis_payload_strips_atom_quotes",
]
