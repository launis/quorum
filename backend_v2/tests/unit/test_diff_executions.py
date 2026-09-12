"""Unit tests for diff_executions.py differential inspection and SSOT registry.

Verifies InputFileInspectionDTO instantiation, dot-notation field access,
noise detection, missing file handling, and cross-script SSOT registry reuse.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from scripts.diff_executions import (
    UNICODE_SPACE_REGISTRY,
    InputFileInspectionDTO,
    TraceTelemetryDTO,
    _inspect_input_file,
    extract_trace_telemetry,
    verify_quote_in_corpus,
)
from scripts.run_e2e_variance_test import (
    UNICODE_SPACE_REGISTRY as IMPORTED_UNICODE_SPACE_REGISTRY,
)


class TestInspectInputFile:
    """Test suite for _inspect_input_file and InputFileInspectionDTO."""

    def test_inspect_input_file_ascii_text(self) -> None:
        """Verify inspecting plain ASCII text returns typed InputFileInspectionDTO."""
        content = "Hello world. This is a clean ASCII document.\n\nSecond paragraph with text."
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_ascii.md"
            file_path.write_text(content, encoding="utf-8")

            info = _inspect_input_file(file_path)

            assert isinstance(info, InputFileInspectionDTO)
            assert info.noise == "Standard ASCII"
            assert info.word_count == 12
            assert info.paragraph_count == 2
            assert info.sentence_count >= 2
            assert len(info.sha256) == 64
            assert info.normalized_text.startswith("Helloworld.")

    def test_inspect_input_file_with_unicode_noise(self) -> None:
        """Verify inspecting file with Unicode non-breaking space detects noise correctly."""
        content = "Hello\u00a0world with a non-breaking space."
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_noise.md"
            file_path.write_text(content, encoding="utf-8")

            info = _inspect_input_file(file_path)

            assert isinstance(info, InputFileInspectionDTO)
            assert "U+00A0" in info.noise
            assert "No-Break Space" in info.noise

    def test_inspect_input_file_multiple_unicode_spaces(self) -> None:
        """Verify multiple distinct Unicode space characters are all reported."""
        content = "Word\u00a0One\u2002Two\u2003Three"
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_multi_noise.md"
            file_path.write_text(content, encoding="utf-8")

            info = _inspect_input_file(file_path)

            assert isinstance(info, InputFileInspectionDTO)
            assert "U+00A0" in info.noise
            assert "U+2002" in info.noise
            assert "U+2003" in info.noise

    def test_inspect_input_file_missing_file(self) -> None:
        """Negative: Inspecting non-existent file returns default DTO with Missing noise."""
        missing_path = Path("non_existent_directory_12345") / "missing.md"
        info = _inspect_input_file(missing_path)

        assert isinstance(info, InputFileInspectionDTO)
        assert info.noise == "Missing"
        assert info.sha256 == "MISSING"
        assert info.char_count == 0
        assert info.word_count == 0

    def test_inspect_input_file_empty_file(self) -> None:
        """Negative: Inspecting 0-byte file returns DTO with Empty noise."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "empty.md"
            file_path.write_text("", encoding="utf-8")

            info = _inspect_input_file(file_path)

            assert isinstance(info, InputFileInspectionDTO)
            assert info.noise == "Empty"
            assert info.char_count == 0
            assert info.word_count == 0


class TestUnicodeSpaceRegistrySSOT:
    """Test suite for UNICODE_SPACE_REGISTRY SSOT governance."""

    def test_unicode_space_registry_identical_reference(self) -> None:
        """Verify run_e2e_variance_test re-exports exact registry instance from diff_executions."""
        assert IMPORTED_UNICODE_SPACE_REGISTRY is UNICODE_SPACE_REGISTRY

    def test_unicode_space_registry_contains_required_markers(self) -> None:
        """Verify registry contains canonical typographical spaces."""
        assert "\u00a0" in UNICODE_SPACE_REGISTRY
        assert "\u2002" in UNICODE_SPACE_REGISTRY
        assert "\u2003" in UNICODE_SPACE_REGISTRY
        assert "\u2009" in UNICODE_SPACE_REGISTRY


class TestVerifyQuoteInCorpus:
    """Test suite for verify_quote_in_corpus verifying exact and whitespace-normalized matching."""

    def test_exact_literal_quote_match(self) -> None:
        """Verify exact identical quote is verified via primary gate."""
        corpus = "This is a clean document text with exact words."
        quote = "clean document text"
        assert verify_quote_in_corpus(quote, corpus) is True

    def test_whitespace_normalized_newline_match(self) -> None:
        """Verify quote with single space matches corpus spanning double newlines."""
        corpus = "Heading text.\n\nSecond paragraph starts here."
        quote = "Heading text. Second paragraph starts here."
        assert verify_quote_in_corpus(quote, corpus) is True

    def test_whitespace_normalized_with_precomputed_norm_corpus(self) -> None:
        """Verify precomputed norm_corpus matches correctly and speeds up execution."""
        corpus = "First sentence.\n\nSecond sentence.\n\nThird sentence."
        norm_corpus = " ".join(corpus.split())
        quote = "Second sentence. Third sentence."
        assert verify_quote_in_corpus(quote, corpus, norm_corpus=norm_corpus) is True

    def test_unicode_space_in_corpus_matches_standard_space_quote(self) -> None:
        """Verify quote with standard ASCII space matches corpus containing Unicode non-breaking space."""
        corpus = "Prefix text\u00a0with non-breaking\u2002spaces."
        quote = "text with non-breaking spaces."
        assert verify_quote_in_corpus(quote, corpus) is True

    def test_hallucinated_quote_returns_false(self) -> None:
        """Negative: Quote containing non-existent text returns False."""
        corpus = "This document only discusses software development practices."
        quote = "This document discusses hardware manufacturing and electronics."
        assert verify_quote_in_corpus(quote, corpus) is False

    def test_empty_inputs_return_false(self) -> None:
        """Negative & Boundary: Empty quote or empty corpus returns False."""
        assert verify_quote_in_corpus("", "Some corpus text.") is False
        assert verify_quote_in_corpus("   ", "Some corpus text.") is False
        assert verify_quote_in_corpus("Some quote.", "") is False


class TestExtractTraceTelemetry:
    """Test suite for extract_trace_telemetry and TraceTelemetryDTO."""

    def test_extract_trace_telemetry_comprehensive(self) -> None:
        """Verify extracting step counts, token metrics, cache hits, MCP calls, and latencies."""
        events = [
            {
                "event_type": "decision",
                "step_name": "rag_grounding",
                "content": {
                    "mcp_audit_traces": [
                        {"tool_id": "search", "claim_text": "claim A"},
                        {"tool_id": "lookup", "claim_text": "claim B"},
                    ],
                },
                "metadata": {
                    "mcp_audit_traces": [
                        {"tool_id": "verify", "claim_text": "claim C"},
                    ],
                },
                "timestamp": "2026-09-11T12:00:00Z",
            },
            {
                "event_type": "output",
                "step_name": "step_fast",
                "content": {
                    "_step_metadata": {
                        "timestamp_isot": "2026-09-11T12:00:30Z",
                        "token_usage": {
                            "prompt_tokens": 1000,
                            "completion_tokens": 200,
                            "cached_tokens": 500,
                            "reasoning_tokens": 800,
                            "cost_usd": 0.005,
                        },
                    },
                },
                "metadata": {
                    "latency_ms": 1500,
                },
            },
            {
                "event_type": "output",
                "step_name": "step_slow",
                "content": {
                    "_step_metadata": {
                        "timestamp_isot": "2026-09-11T12:01:00Z",
                        "token_usage": {
                            "prompt_tokens": 2000,
                            "completion_tokens": 400,
                            "cached_tokens": 0,
                            "reasoning_tokens": 1200,
                            "cost_usd": 0.010,
                        },
                    },
                },
                "metadata": {
                    "latency_ms": 4500,
                },
            },
        ]

        dto = extract_trace_telemetry(events)

        assert isinstance(dto, TraceTelemetryDTO)
        assert dto.step_count == 2
        assert dto.cache_hit_count == 1
        assert dto.reasoning_tokens == 2000
        assert dto.mcp_calls == 3
        assert dto.prompt_tokens == 3000
        assert dto.completion_tokens == 600
        assert dto.cached_tokens == 500
        assert abs(dto.dag_cost - 0.015) < 1e-6
        assert dto.first_timestamp == "2026-09-11T12:00:00Z"
        assert dto.last_timestamp == "2026-09-11T12:01:00Z"
        assert dto.step_latencies == {"step_fast": 1500, "step_slow": 4500}

    def test_extract_trace_telemetry_empty_and_malformed(self) -> None:
        """Negative: Empty list or list with non-dict events returns empty default TraceTelemetryDTO."""
        empty_dto = extract_trace_telemetry([])
        assert isinstance(empty_dto, TraceTelemetryDTO)
        assert empty_dto.step_count == 0
        assert empty_dto.cache_hit_count == 0
        assert empty_dto.reasoning_tokens == 0
        assert empty_dto.mcp_calls == 0
        assert empty_dto.prompt_tokens == 0
        assert empty_dto.completion_tokens == 0
        assert empty_dto.cached_tokens == 0
        assert empty_dto.dag_cost == 0.0
        assert empty_dto.first_timestamp is None
        assert empty_dto.last_timestamp is None
        assert empty_dto.step_latencies == {}

        malformed_events = ["string", 123, None, {}, {"event_type": "unknown"}]
        malformed_dto = extract_trace_telemetry(malformed_events)
        assert malformed_dto.step_count == 0
        assert malformed_dto.mcp_calls == 0

    def test_extract_trace_telemetry_zero_cache_and_zero_reasoning(self) -> None:
        """Boundary: Single output step with zero cached tokens and zero reasoning tokens."""
        events = [
            {
                "event_type": "output",
                "step_name": "step_standard",
                "content": {
                    "_step_metadata": {
                        "token_usage": {
                            "prompt_tokens": 500,
                            "completion_tokens": 100,
                            "cached_tokens": 0,
                            "reasoning_tokens": 0,
                            "cost_usd": 0.001,
                        },
                    },
                },
                "metadata": {
                    "latency_ms": 800,
                },
            }
        ]

        dto = extract_trace_telemetry(events)
        assert dto.step_count == 1
        assert dto.cache_hit_count == 0
        assert dto.reasoning_tokens == 0
        assert dto.prompt_tokens == 500
        assert dto.completion_tokens == 100
        assert dto.cached_tokens == 0
        assert abs(dto.dag_cost - 0.001) < 1e-6
        assert dto.step_latencies == {"step_standard": 800}
