"""Unit tests for diff_executions.py differential inspection and SSOT registry.

Verifies InputFileInspectionDTO instantiation, dot-notation field access,
noise detection, missing file handling, and cross-script SSOT registry reuse.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

from scripts.diff_executions import (
    UNICODE_SPACE_REGISTRY,
    DisagreementRootCause,
    EvidenceDistributionDTO,
    InputFileInspectionDTO,
    PhysicalModelBindingDTO,
    TraceTelemetryDTO,
    UserDocumentationVolumeDTO,
    WorkflowProvenanceDTO,
    _inspect_input_file,
    calculate_cohens_kappa,
    calculate_entropy,
    calculate_fleiss_kappa,
    calculate_pairwise_consistency,
    calculate_user_documentation_volume,
    classify_disagreement,
    classify_input_ontology,
    extract_block_normalized_scores,
    extract_block_scoring_diagnostics,
    extract_evidence_distribution,
    extract_trace_telemetry,
    extract_workflow_provenance,
    get_all_evals,
    get_state,
    get_trace,
    has_quote,
    main,
    resolve_physical_model_bindings,
    run_diff,
    uses_contextual_override,
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


class TestWorkflowProvenance:
    """Test suite for extract_workflow_provenance and WorkflowProvenanceDTO."""

    def test_extract_workflow_provenance_competency_workflows(self) -> None:
        """Positive: Test dynamic atom population and metadata resolution from seed data."""
        seed_path = Path(__file__).resolve().parents[2] / "seed" / "seed_data.json"
        with seed_path.open("r", encoding="utf-8") as f:
            seed = json.load(f)

        # wf_01: AI Driving License (65 atoms)
        wf_01 = extract_workflow_provenance(seed, "wf_01a1d71000000001")
        assert wf_01 is not None
        assert isinstance(wf_01, WorkflowProvenanceDTO)
        assert wf_01.workflow_id == "wf_01a1d71000000001"
        assert wf_01.total_workflow_atoms == 65
        assert wf_01.total_active_steps == 6
        assert wf_01.version == 1

        # wf_02: Strategic Leadership (110 atoms)
        wf_02 = extract_workflow_provenance(seed, "wf_02a1d71000000002")
        assert wf_02 is not None
        assert wf_02.total_workflow_atoms == 110

        # wf_03: Deep Problem Solving (85 atoms)
        wf_03 = extract_workflow_provenance(seed, "wf_03a1d71000000003")
        assert wf_03 is not None
        assert wf_03.total_workflow_atoms == 85

    def test_extract_workflow_provenance_empty_and_unknown(self) -> None:
        """Negative: Empty seed returns None, unknown workflow ID falls back to first available workflow."""
        assert extract_workflow_provenance({}, "wf_unknown") is None
        assert extract_workflow_provenance({"workflows": []}, "wf_unknown") is None

        synthetic_seed = {
            "workflows": [
                {
                    "id": "wf_test_first",
                    "name": {"translations": {"fi": "Ensimmäinen", "en": "First"}},
                    "version": 2,
                    "enable_contextual_overrides": False,
                    "default_scoring_strategy": "WATERFALL",
                    "default_strictness_level": 75,
                    "steps": [],
                }
            ],
            "steps": [],
            "prompt_blocks": [],
        }
        res = extract_workflow_provenance(synthetic_seed, "wf_nonexistent")
        assert res is not None
        assert res.workflow_id == "wf_test_first"
        assert res.name_fi == "Ensimmäinen"
        assert res.total_workflow_atoms == 0
        assert res.enable_contextual_overrides is False


class TestPhysicalModelBindings:
    """Test suite for resolve_physical_model_bindings and PhysicalModelBindingDTO."""

    def test_resolve_physical_model_bindings_from_seed(self) -> None:
        """Positive: Verify bindings extracted from seed system_config match registered models."""
        seed_path = Path(__file__).resolve().parents[2] / "seed" / "seed_data.json"
        with seed_path.open("r", encoding="utf-8") as f:
            seed = json.load(f)

        bindings = resolve_physical_model_bindings(seed)
        assert len(bindings) >= 3
        strategies = {b.strategy_name: b for b in bindings}
        assert "fast" in strategies
        assert "reasoning" in strategies
        assert "synthesis" in strategies

        fast_binding = strategies["fast"]
        assert isinstance(fast_binding, PhysicalModelBindingDTO)
        assert "gemini" in fast_binding.physical_model.lower() or "flash" in fast_binding.physical_model.lower()

    def test_resolve_physical_model_bindings_fallback_defaults(self) -> None:
        """Negative: Empty seed data falls back to default Gemini and Claude bindings."""
        fallback_bindings = resolve_physical_model_bindings({})
        assert len(fallback_bindings) == 3
        names = [b.strategy_name for b in fallback_bindings]
        assert names == ["fast", "reasoning", "synthesis"]


class TestInputOntologyAndUserVolume:
    """Test suite for classify_input_ontology and calculate_user_documentation_volume."""

    def test_classify_input_ontology_two_tier(self) -> None:
        """Positive: Verify candidate deliverables vs external frameworks separation."""
        # Candidate deliverables (user documentation)
        assert classify_input_ontology("chat_log_user_only.txt") == "candidate_deliverable"
        assert classify_input_ontology("candidate_product_text.md") == "candidate_deliverable"
        assert classify_input_ontology("reflection_text.md") == "candidate_deliverable"

        # External normative context
        assert classify_input_ontology("assignment_context.md") == "external_context"
        assert classify_input_ontology("compliance_framework.md") == "external_context"
        assert classify_input_ontology("source_evidence.md") == "external_context"
        assert classify_input_ontology("chat_log_ai_only.txt") == "external_context"

        # Raw unseparated log
        assert classify_input_ontology("chat_log.txt") == "raw_log"

    def test_calculate_user_documentation_volume_filtering(self) -> None:
        """Positive: Aggregates volume metrics across candidate deliverables only."""
        files = {
            "chat_log_user_only.txt": InputFileInspectionDTO(
                sha256="abc1",
                noise="Standard ASCII",
                char_count=500,
                word_count=100,
                sentence_count=10,
                paragraph_count=2,
                bullet_count=3,
                normalized_text="user text",
            ),
            "product_text.md": InputFileInspectionDTO(
                sha256="abc2",
                noise="Standard ASCII",
                char_count=1000,
                word_count=200,
                sentence_count=20,
                paragraph_count=4,
                bullet_count=5,
                normalized_text="product text",
            ),
            "assignment_context.md": InputFileInspectionDTO(
                sha256="abc3",
                noise="Standard ASCII",
                char_count=5000,
                word_count=1000,
                sentence_count=100,
                paragraph_count=20,
                bullet_count=15,
                normalized_text="assignment text",
            ),
            "compliance_framework.md": InputFileInspectionDTO(
                sha256="abc4",
                noise="Standard ASCII",
                char_count=10000,
                word_count=2000,
                sentence_count=200,
                paragraph_count=40,
                bullet_count=30,
                normalized_text="compliance text",
            ),
        }

        volume = calculate_user_documentation_volume(files, run_name="run_a")
        assert isinstance(volume, UserDocumentationVolumeDTO)
        assert volume.run_name == "run_a"
        assert volume.user_file_count == 2
        assert volume.total_words == 300  # 100 + 200, ignoring 1000 + 2000
        assert volume.total_sentences == 30  # 10 + 20
        assert volume.total_characters == 1500  # 500 + 1000
        assert volume.total_paragraphs == 6  # 2 + 4
        assert volume.total_bullets == 8  # 3 + 5

    def test_calculate_user_documentation_volume_empty_boundary(self) -> None:
        """Boundary: Empty file mapping returns zero counts."""
        vol = calculate_user_documentation_volume({}, run_name="empty")
        assert vol.user_file_count == 0
        assert vol.total_words == 0
        assert vol.total_characters == 0


class TestEvidenceDistribution:
    """Test suite for extract_evidence_distribution and EvidenceDistributionDTO."""

    def test_extract_evidence_distribution_counts(self) -> None:
        """Positive: Test partition counting across quotes, inverse passes, overrides, and failures."""
        evals: dict[str, dict[str, Any]] = {
            # Empirical citation
            "atom_quote": {
                "status": "PASSED",
                "source_quote": "This is empirical proof in text.",
                "is_inverse_evidence": False,
                "contextual_override": False,
            },
            # Inverse pass
            "atom_inverse": {
                "status": "PASSED",
                "source_quote": None,
                "is_inverse_evidence": True,
                "contextual_override": False,
            },
            # Contextual override allowed
            "atom_override": {
                "status": "PASSED",
                "source_quote": None,
                "is_inverse_evidence": False,
                "contextual_override": True,
            },
            # Contextual override demoted by policy
            "atom_demoted": {
                "status": "PASSED",
                "source_quote": None,
                "is_inverse_evidence": False,
                "contextual_override": True,
            },
            # Outright failure
            "atom_failed": {
                "status": "FAILED",
                "source_quote": None,
                "evaluation_reasoning": "Criteria not satisfied.",
            },
        }

        # Case 1: Overrides enabled -> contextual_overrides = 2, demoted = 0
        dist_enabled = extract_evidence_distribution(evals, enable_contextual_overrides=True, run_name="run_1")
        assert isinstance(dist_enabled, EvidenceDistributionDTO)
        assert dist_enabled.empirical_quotes == 1
        assert dist_enabled.inverse_passes == 1
        assert dist_enabled.contextual_overrides == 2
        assert dist_enabled.demoted_by_policy == 0
        assert dist_enabled.failures == 1
        assert dist_enabled.total_evaluated == 5

        # Case 2: Overrides disabled -> contextual_overrides = 0, demoted = 2
        dist_disabled = extract_evidence_distribution(evals, enable_contextual_overrides=False, run_name="run_2")
        assert dist_disabled.empirical_quotes == 1
        assert dist_disabled.inverse_passes == 1
        assert dist_disabled.contextual_overrides == 0
        assert dist_disabled.demoted_by_policy == 2
        assert dist_disabled.failures == 1
        assert dist_disabled.total_evaluated == 5

    def test_extract_evidence_distribution_empty_boundary(self) -> None:
        """Boundary: Empty evals returns zero counts."""
        dist = extract_evidence_distribution({}, run_name="empty")
        assert dist.total_evaluated == 0
        assert dist.empirical_quotes == 0
        assert dist.inverse_passes == 0
        assert dist.failures == 0


class TestBlockScoringDiagnostics:
    """Test suite for extract_block_scoring_diagnostics."""

    def test_extract_block_scoring_diagnostics_waterfall_and_raw(self) -> None:
        """Positive: Extract raw scores, normalized scores, and waterfall break point."""
        trace_data = [
            {
                "event_type": "output",
                "step_name": "scorecard_step",
                "content": {
                    "blk_waterfall_1": {
                        "normalized_score": 50.0,
                        "raw_score": 2.0,
                        "level_breakdown": {
                            "1": {"hits": 4, "total": 4},
                            "2": {"hits": 1, "total": 3},
                            "3": {"hits": 0, "total": 3},
                        },
                    },
                    "blk_perfect_2": {
                        "normalized_score": 100.0,
                        "raw_score": 5.0,
                        "level_breakdown": {
                            "1": {"hits": 2, "total": 2},
                            "2": {"hits": 3, "total": 3},
                        },
                    },
                },
            }
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            trace_path = Path(tmpdir) / "execution_trace.json"
            with trace_path.open("w", encoding="utf-8") as f:
                json.dump(trace_data, f)

            diag = extract_block_scoring_diagnostics(trace_path)
            assert len(diag) == 2

            blk1 = diag["blk_waterfall_1"]
            assert blk1["normalized_score"] == 50.0
            assert blk1["raw_score"] == 2.0
            assert blk1["waterfall_breakpoint"] == "Taso 2 (1/3 osumaa)"

            blk2 = diag["blk_perfect_2"]
            assert blk2["normalized_score"] == 100.0
            assert blk2["raw_score"] == 5.0
            assert blk2["waterfall_breakpoint"] == "Kaikki tasot läpäisty"

    def test_extract_block_scoring_diagnostics_missing_file_negative(self) -> None:
        """Negative: Non-existent trace file gracefully returns empty dict."""
        assert extract_block_scoring_diagnostics(Path("non_existent_trace.json")) == {}


class TestStatisticalMetrics:
    """Test suite for statistical helpers: entropy, pairwise consistency, Cohen's & Fleiss' Kappa."""

    def test_calculate_entropy_partitions(self) -> None:
        """Positive and Boundary: Test Shannon entropy on empty, homogeneous, and split states."""
        assert calculate_entropy([]) == 0.0
        assert calculate_entropy(["passed", "passed", "passed"]) == 0.0
        # Equal binary split has entropy = 1.0 bit
        assert abs(calculate_entropy(["passed", "failed"]) - 1.0) < 1e-6

    def test_calculate_pairwise_consistency(self) -> None:
        """Positive and Boundary: Test pairwise consistency ratio."""
        assert calculate_pairwise_consistency([]) == 1.0
        assert calculate_pairwise_consistency(["passed"]) == 1.0
        assert calculate_pairwise_consistency(["passed", "passed"]) == 1.0
        assert calculate_pairwise_consistency(["passed", "failed"]) == 0.0
        # 3 raters: 2 agreed, 1 disagreed -> 1 agree pair / 3 total pairs = 0.3333
        assert abs(calculate_pairwise_consistency(["passed", "passed", "failed"]) - (1 / 3)) < 1e-4

    def test_calculate_cohens_kappa_perfect_and_empty(self) -> None:
        """Positive and Boundary: Test Cohen's Kappa perfect agreement and empty boundary."""
        empty = calculate_cohens_kappa([], ["passed", "failed"])
        assert empty.kappa == 0.0
        assert empty.standard_error == 0.0

        ratings = [["passed", "passed"], ["failed", "failed"], ["passed", "passed"]]
        res = calculate_cohens_kappa(ratings, ["passed", "failed"])
        assert res.kappa == 1.0
        assert "Lähes täydellinen" in res.benchmark_category
        assert res.observed_agreement == 1.0

    def test_calculate_fleiss_kappa_partitions(self) -> None:
        """Positive and Boundary: Test Fleiss' Kappa multi-rater consistency."""
        assert calculate_fleiss_kappa([], ["passed", "failed"]) == 0.0
        assert calculate_fleiss_kappa([["passed"]], ["passed", "failed"]) == 1.0
        ratings = [["passed", "passed"], ["failed", "failed"]]
        assert calculate_fleiss_kappa(ratings, ["passed", "failed"]) == 1.0

    def test_calculate_cohens_kappa_error_handling(self) -> None:
        """Negative: Raise ValueError if not exactly two raters or rating pairs malformed."""
        with pytest.raises(ValueError, match="requires exactly two raters"):
            calculate_cohens_kappa([["passed", "passed", "failed"]], ["passed", "failed"])

        with pytest.raises(ValueError, match="must contain exactly 2 ratings"):
            calculate_cohens_kappa([["passed", "passed"], ["failed"]], ["passed", "failed"])

    def test_calculate_cohens_kappa_benchmarks(self) -> None:
        """Positive: Test Substantial, Moderate, and Poor agreement classification tiers."""
        # Substantial: kappa in [0.61, 0.80]
        ratings_sub = [["passed", "passed"]] * 9 + [["passed", "failed"]] * 1 + [["failed", "failed"]] * 8 + [["failed", "passed"]] * 2
        res_sub = calculate_cohens_kappa(ratings_sub, ["passed", "failed"])
        assert 0.61 <= res_sub.kappa <= 0.80
        assert "Huomattava / Vahva" in res_sub.benchmark_category

        # Moderate: kappa in [0.41, 0.60]
        ratings_mod = [["passed", "passed"]] * 8 + [["passed", "failed"]] * 2 + [["failed", "failed"]] * 7 + [["failed", "passed"]] * 3
        res_mod = calculate_cohens_kappa(ratings_mod, ["passed", "failed"])
        assert 0.41 <= res_mod.kappa <= 0.60
        assert "Kohtalainen" in res_mod.benchmark_category

        # Poor: kappa < 0.40
        ratings_poor = [["passed", "failed"]] * 10 + [["failed", "passed"]] * 10
        res_poor = calculate_cohens_kappa(ratings_poor, ["passed", "failed"])
        assert res_poor.kappa <= 0.40
        assert "Heikko sopivuus" in res_poor.benchmark_category

    def test_calculate_fleiss_kappa_perfect(self) -> None:
        """Positive: Homogeneous single category returns 1.0 (p_e >= 1.0 branch)."""
        res = calculate_fleiss_kappa([["passed", "passed"], ["passed", "passed"]], ["passed"])
        assert res == 1.0


class TestEvaluationHelpers:
    """Test suite for atom evaluation parsing, quote inspection, and root cause classification."""

    def test_get_state_resolutions(self) -> None:
        """Positive and Negative: Test state extraction from status, decision, mapped_state, quotes."""
        assert get_state({"status": "PASSED"}) == "passed"
        assert get_state({"decision": "FAILED"}) == "failed"
        assert get_state({"mapped_state": "TRUE"}) == "true"
        assert get_state({"exact_quote": "Valid text quote."}) == "true"
        assert get_state({"exact_quote": "ei löydy"}) == "false"
        assert get_state({"exact_quote": "none"}) == "false"
        assert get_state({}) == "unknown"

    def test_get_trace_fallbacks(self) -> None:
        """Positive: Test reasoning trace extraction across candidate keys."""
        assert get_trace({"evaluation_reasoning": "Reason 1"}) == "Reason 1"
        assert get_trace({"context_scan_trace": "Scan trace"}) == "Scan trace"
        assert get_trace({"semantic_reasoning": "Semantic"}) == "Semantic"
        assert get_trace({}) == ""

    def test_has_quote_formats(self) -> None:
        """Positive and Boundary: Test quote detection for strings, lists, and blacklisted values."""
        assert has_quote({"source_quote": "Real quote"}) is True
        assert has_quote({"exact_quotes": ["Quote 1", "Quote 2"]}) is True
        assert has_quote({"source_quote": "n/a"}) is False
        assert has_quote({"source_quote": "null"}) is False
        assert has_quote({"source_quote": None}) is False
        assert has_quote({}) is False

    def test_uses_contextual_override(self) -> None:
        """Positive: Test override detection from boolean flag or [INFERRED] text."""
        assert uses_contextual_override({"contextual_override": True}) is True
        assert uses_contextual_override({"source_quote": "[INFERRED] based on context"}) is True
        assert uses_contextual_override({"source_quote": "Literal evidence"}) is False

    def test_classify_disagreement_root_causes(self) -> None:
        """Positive: Classify disagreements into 4 distinct root causes."""
        # Technical error
        err1 = {"evaluation_reasoning": "[SYSTEM ERROR: Timeout]"}
        err2 = {"evaluation_reasoning": "Normal pass"}
        assert classify_disagreement(err1, err2) == DisagreementRootCause.TECHNICAL_ERROR

        # Contextual override
        ovr1 = {"contextual_override": True}
        ovr2 = {"source_quote": "evidence"}
        assert classify_disagreement(ovr1, ovr2) == DisagreementRootCause.CONTEXTUAL_OVERRIDE

        # Retrieval gap (one has quote, other doesn't)
        q_yes = {"source_quote": "real text"}
        q_no = {"source_quote": None}
        assert classify_disagreement(q_yes, q_no) == DisagreementRootCause.RETRIEVAL_GAP

        # Reasoning gap (both have quotes or neither has quotes, but differed in state)
        same_q1 = {"source_quote": "text", "evaluation_reasoning": "Reason A"}
        same_q2 = {"source_quote": "text", "evaluation_reasoning": "Reason B"}
        assert classify_disagreement(same_q1, same_q2) == DisagreementRootCause.REASONING_GAP

    def test_extract_block_normalized_scores(self) -> None:
        """Positive and Negative: Test extracting normalized scores from trace file."""
        assert extract_block_normalized_scores(Path("non_existent.json")) == {}

        trace = [{"content": {"blk_1": {"normalized_score": 88.5}}}]
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "trace.json"
            with p.open("w", encoding="utf-8") as f:
                json.dump(trace, f)
            scores = extract_block_normalized_scores(p)
            assert scores == {"blk_1": 88.5}

    def test_get_all_evals(self) -> None:
        """Positive: Extract all evaluated atoms from trace step objects."""
        trace = [
            {
                "content": {
                    "evaluations": [{"atom_id": "atm_1", "status": "PASSED"}],
                    "results": [{"tda_id": "atm_2", "status": "FAILED"}],
                }
            }
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "trace.json"
            with p.open("w", encoding="utf-8") as f:
                json.dump(trace, f)
            all_evals = get_all_evals(p)
            assert "atm_1" in all_evals
            assert "atm_2" in all_evals


class TestRunDiff:
    """Test suite for full differential report generation (run_diff)."""

    def test_run_diff_e2e_executions(self) -> None:
        """Positive: Execute run_diff on physical execution traces and verify self-contained report sections."""
        exe1 = Path("data/files/executions/exe_28f0798ef2d946c7")
        exe2 = Path("data/files/executions/exe_62035476fd1c4934")

        if not exe1.exists() or not exe2.exists():
            return

        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "diff_report.md"
            res_path = run_diff([str(exe1), str(exe2)], output_file=out_file)

            assert Path(res_path).exists()
            content = Path(res_path).read_text(encoding="utf-8")

            # Check that all new Step 6 sections are rendered
            assert "## Ympäristö ja Konteksti" in content
            assert "Työnkulun Provenienssi" in content
            assert "Fyysiset Mallisidokset (Physical Model Bindings)" in content
            assert "## Evidenssiluokkien ja Ohitusten Jakauma (Evidence Class & Override Distribution)" in content
            assert "Input Corpus Profile" in content
            assert "Candidate Deliverable" in content
            assert "Käyttäjädokumentaation volyymi" in content
            assert "## Makrotason Pistemäärä- ja Luottamusdiffit (Macro Score Drift 0–100)" in content
            assert "Waterfall-katkos" in content

    def test_run_diff_error_partitions(self) -> None:
        """Negative: Exit with code 1 if fewer than 2 runs provided."""
        with pytest.raises(SystemExit):
            run_diff(["non_existent_run_1"])

    def test_main_cli_entrypoint(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Positive: Test CLI entrypoint invocation."""
        exe1 = "data/files/executions/exe_28f0798ef2d946c7"
        exe2 = "data/files/executions/exe_62035476fd1c4934"
        if not Path(exe1).exists() or not Path(exe2).exists():
            return
        monkeypatch.setattr(sys, "argv", ["diff_executions.py", exe1, exe2])
        main()

    def test_run_diff_with_frozen_context_snapshot(self) -> None:
        """Positive: Test differential report generation with frozen_context.json present."""
        trace = [
            {
                "content": {
                    "evaluations": [
                        {"atom_id": "atom_01", "status": "PASSED"},
                        {"atom_id": "atom_02", "status": "FAILED"},
                    ]
                }
            }
        ]
        frozen_data = {
            "ui_hints_snapshot": {
                "blk_leadership": {
                    "options": [
                        {"label": {"translations": {"fi": "Johtajuus", "en": "Leadership"}}}
                    ]
                }
            }
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            run1 = tmp_path / "exe_test_1"
            run2 = tmp_path / "exe_test_2"
            run1.mkdir()
            run2.mkdir()

            (run1 / "execution_trace.json").write_text(json.dumps(trace), encoding="utf-8")
            (run2 / "execution_trace.json").write_text(json.dumps(trace), encoding="utf-8")
            (run1 / "frozen_context.json").write_text(json.dumps(frozen_data), encoding="utf-8")

            out_report = tmp_path / "report.md"
            res = run_diff([str(run1), str(run2)], output_file=out_report)
            assert Path(res).exists()
            assert "Aktiiviset Säännöt ja Asetukset (Frozen Context)" in Path(res).read_text(encoding="utf-8")

    def test_run_diff_default_executions(self) -> None:
        """Positive: Test running diff with default latest executions when available."""
        exe1 = Path("data/files/executions/exe_28f0798ef2d946c7")
        exe2 = Path("data/files/executions/exe_62035476fd1c4934")
        if not exe1.exists() or not exe2.exists():
            return
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "default_diff.md"
            res = run_diff(execution_ids=None, output_file=out_file)
            assert Path(res).exists()


