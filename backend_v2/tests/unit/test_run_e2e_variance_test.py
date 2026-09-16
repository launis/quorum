"""Unit tests for run_e2e_variance_test.py run marker injection and user-turn scope guarantees.

Validates that cryptographic Unicode noise markers are reliably injected into human user turns
in chat_log inputs, preventing cache collisions on downstream user-only cognitive evaluations.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from backend_v2.models.core_base import I18nText
from backend_v2.models.v2_core import ExpectedInput
from backend_v2.services.chat_normalizer import ChatNormalizerService
from scripts.run_e2e_variance_test import (
    UNICODE_SPACE_REGISTRY,
    _ensure_user_turn_marker,
    _match_input_key,
    inject_unique_run_marker,
    load_inputs_from_path,
)


class TestRunMarkerInjection:
    """Test suite for unique run marker injection and user turn scoping."""

    def test_ensure_user_turn_marker_json_format(self) -> None:
        """Verify _ensure_user_turn_marker mutates user turn and leaves AI turn untouched."""
        marker = "\u00a0"
        raw_chat = json.dumps(
            {
                "conversation": [
                    {"role": "user", "content": "What is the project timeline?"},
                    {"role": "assistant", "content": "The project will take six months."},
                ]
            }
        )

        marked = _ensure_user_turn_marker(raw_chat, marker)
        parsed = json.loads(marked)
        user_turn = parsed["conversation"][0]["content"]
        ai_turn = parsed["conversation"][1]["content"]

        assert marker in user_turn
        assert marker not in ai_turn

    def test_ensure_user_turn_marker_text_with_prefix(self) -> None:
        """Verify colon-delimited User/Assistant text format injects marker into user turn."""
        marker = "\u2002"
        raw_text = "User: Hello, I have an inquiry about expenses.\nAssistant: I can assist with expense reviews."

        marked = _ensure_user_turn_marker(raw_text, marker)
        assert marker in marked

        # Parse via ChatNormalizerService to guarantee user_only carries the marker
        chat_dto = ChatNormalizerService.try_parse_fast_path(marked)
        assert chat_dto is not None
        processed = ChatNormalizerService.build_processed_chat(chat_dto)
        assert marker in processed.user_only

    def test_ensure_user_turn_marker_short_user_turn_with_massive_ai_turn(self) -> None:
        """Negative/Boundary: Short user turn (10 words) with massive AI turn (3000 words).

        Guarantees that user_only carries the marker even when stride=50 would otherwise
        miss the user turn entirely.
        """
        short_user = "Käyttäjä: Miten tämä toimii käytännössä tässä yrityksessä?"
        long_ai_paragraphs = [
            f"ChatGPT: Kappale {i} sisältää runsaasti yksityiskohtaista selitystä aiheesta "
            "ja vertailevia taulukoita kustannuksista sekä henkilöstövaikutuksista."
            for i in range(100)
        ]
        massive_chat = short_user + "\n" + "\n\n".join(long_ai_paragraphs)

        # Standard injection on conversational input
        variant_0 = list(UNICODE_SPACE_REGISTRY.keys())[0]
        payload = inject_unique_run_marker({"chat_log": massive_chat}, 0, stride=50)
        marked = payload.marked_inputs["chat_log"]
        assert variant_0 in marked

        chat_dto = ChatNormalizerService.try_parse_fast_path(marked)
        assert chat_dto is not None
        processed = ChatNormalizerService.build_processed_chat(chat_dto)

        # The evaluated user_only stream MUST carry the marker to bypass caching
        assert variant_0 in processed.user_only, (
            "Cryptographic noise marker was absent from user_only stream! Evaluated prompt would hit cache."
        )

    def test_inject_unique_run_marker_non_conversational_text(self) -> None:
        """Verify non-conversational text gets standard periodic marker injection."""
        marker = list(UNICODE_SPACE_REGISTRY.keys())[0]
        plain_text = " ".join(["word"] * 200)

        payload = inject_unique_run_marker({"product_text": plain_text}, 0, stride=50)
        marked = payload.marked_inputs["product_text"]
        assert marker in marked
        assert marked.count(marker) >= 3

    def test_inject_unique_run_marker_distinct_runs_produce_distinct_markers(self) -> None:
        """Verify Run 0 and Run 1 produce distinct Unicode space markers."""
        plain_text = "Hello world with several spaces to inject noise."
        marker_0 = list(UNICODE_SPACE_REGISTRY.keys())[0]
        marker_1 = list(UNICODE_SPACE_REGISTRY.keys())[1]

        payload_0 = inject_unique_run_marker({"product_text": plain_text}, 0, stride=1)
        payload_1 = inject_unique_run_marker({"product_text": plain_text}, 1, stride=1)
        marked_0 = payload_0.marked_inputs["product_text"]
        marked_1 = payload_1.marked_inputs["product_text"]

        assert marker_0 in marked_0
        assert marker_1 in marked_1
        assert marker_0 not in marked_1
        assert marker_1 not in marked_0

    def test_run_e2e_variance_test_cli_standalone_invocation(self) -> None:
        """Verify scripts/run_e2e_variance_test.py can be invoked directly as a standalone CLI script.

        Regression test: sys.path bootstrap must precede project imports like backend_v2,
        otherwise direct invocation raises ModuleNotFoundError: No module named 'backend_v2'.
        """
        script_path = Path(__file__).resolve().parents[3] / "scripts" / "run_e2e_variance_test.py"
        result = subprocess.run(
            [sys.executable, str(script_path), "--help"],
            capture_output=True,
            text=True,
            cwd=str(script_path.parent.parent),
        )
        assert result.returncode == 0, (
            f"Script execution failed with returncode {result.returncode}.\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )
        assert "End-to-End Variance and Reliability Test Runner" in result.stdout

    def test_run_e2e_variance_test_cli_isolated_cwd(self) -> None:
        """Verify scripts/run_e2e_variance_test.py is invariant to working directory.

        ISTQB Negative Boundary Test: When invoked with cwd=scripts/ (not repo root),
        the deterministic Path(__file__).resolve().parent.parent bootstrap must still
        resolve the project root and allow standalone execution without ModuleNotFoundError.
        """
        script_path = Path(__file__).resolve().parents[3] / "scripts" / "run_e2e_variance_test.py"
        result = subprocess.run(
            [sys.executable, str(script_path), "--help"],
            capture_output=True,
            text=True,
            cwd=str(script_path.parent),
        )
        assert result.returncode == 0, (
            f"Script execution from scripts/ dir failed with returncode {result.returncode}.\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )
        assert "End-to-End Variance and Reliability Test Runner" in result.stdout

    def test_run_e2e_variance_test_cli_unrecognized_argument(self) -> None:
        """Verify scripts/run_e2e_variance_test.py fails fast on unrecognized CLI arguments.

        ISTQB Negative Equivalence Partition: Passing an illegal flag must exit with
        argparse returncode 2 and write 'unrecognized arguments' to stderr without crash.
        """
        script_path = Path(__file__).resolve().parents[3] / "scripts" / "run_e2e_variance_test.py"
        result = subprocess.run(
            [sys.executable, str(script_path), "--illegal-flag-xyz"],
            capture_output=True,
            text=True,
            cwd=str(script_path.parent.parent),
        )
        assert result.returncode == 2, (
            f"Expected argparse returncode 2 for illegal argument, got {result.returncode}.\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )
        assert "unrecognized arguments" in result.stderr


class TestLoadInputsAndKeyMatching:
    """Test suite for 2-tier lexical key matching, input loading, and collision prevention."""

    @pytest.fixture
    def sample_expected_inputs(self) -> list[ExpectedInput]:
        """Provide standard expected inputs fixture."""
        return [
            ExpectedInput(
                input_key="chat_log",
                label=I18nText(
                    translations={
                        "fi": "Keskusteluhistoria (Chat)",
                        "en": "Conversation History (Chat)",
                    }
                ),
                required=True,
                is_chat_history=True,
                input_modes=["file", "paste"],
                description=I18nText(translations={"en": "Chat history", "fi": "Keskusteluhistoria"}),
            ),
            ExpectedInput(
                input_key="product_text",
                label=I18nText(
                    translations={
                        "fi": "Lopputuote",
                        "en": "Final Product",
                    }
                ),
                required=False,
                is_chat_history=False,
                input_modes=["file", "paste"],
                description=I18nText(translations={"en": "Final product", "fi": "Lopputuote"}),
            ),
            ExpectedInput(
                input_key="reflection_text",
                label=I18nText(
                    translations={
                        "fi": "Reflektiodokumentti",
                        "en": "Reflection",
                    }
                ),
                required=False,
                is_chat_history=False,
                input_modes=["file", "paste"],
                description=I18nText(translations={"en": "Reflection document", "fi": "Reflektiodokumentti"}),
            ),
        ]

    def test_match_input_key_tier1_exact(self, sample_expected_inputs: list[ExpectedInput]) -> None:
        """Verify Tier 1 exact normalized key matching."""
        assert _match_input_key("chat_log", sample_expected_inputs) == "chat_log"
        assert _match_input_key("product_text", sample_expected_inputs) == "product_text"
        assert _match_input_key("reflection_text", sample_expected_inputs) == "reflection_text"

    def test_match_input_key_tier2_localized_labels(self, sample_expected_inputs: list[ExpectedInput]) -> None:
        """Verify Tier 2 localized label translations matching without hardcoding Finnish in logic."""
        assert _match_input_key("keskusteluhistoria", sample_expected_inputs) == "chat_log"
        assert _match_input_key("conversation_history", sample_expected_inputs) == "chat_log"
        assert _match_input_key("lopputuote", sample_expected_inputs) == "product_text"
        assert _match_input_key("final_product", sample_expected_inputs) == "product_text"
        assert _match_input_key("reflektio", sample_expected_inputs) == "reflection_text"
        assert _match_input_key("reflection", sample_expected_inputs) == "reflection_text"

    def test_match_input_key_unmatched_returns_none(self, sample_expected_inputs: list[ExpectedInput]) -> None:
        """Verify candidate not matching any slot returns None."""
        assert _match_input_key("document_date", sample_expected_inputs) is None
        assert _match_input_key("unrelated_meta_info", sample_expected_inputs) is None

    def test_match_input_key_empty_candidate(self, sample_expected_inputs: list[ExpectedInput]) -> None:
        """Boundary: Empty or whitespace-only candidate returns None."""
        assert _match_input_key("", sample_expected_inputs) is None
        assert _match_input_key("   ", sample_expected_inputs) is None

    def test_load_inputs_from_path_directory_success(
        self,
        tmp_path: Path,
        sample_expected_inputs: list[ExpectedInput],
    ) -> None:
        """Verify load_inputs_from_path correctly maps directory files to expected slots."""
        (tmp_path / "keskusteluhistoria.txt").write_text("Hello conversation", encoding="utf-8")
        (tmp_path / "lopputuote.md").write_text("# Final product report", encoding="utf-8")
        (tmp_path / "custom_notes.txt").write_text("Extra unconstrained notes", encoding="utf-8")

        inputs = load_inputs_from_path(tmp_path, expected_inputs=sample_expected_inputs)

        assert inputs["chat_log"] == "Hello conversation"
        assert inputs["product_text"] == "# Final product report"
        assert inputs["custom_notes"] == "Extra unconstrained notes"
        assert "document_date" in inputs

    def test_load_inputs_from_path_collision_detection(
        self,
        tmp_path: Path,
        sample_expected_inputs: list[ExpectedInput],
    ) -> None:
        """ISTQB Negative Boundary: Collision between two files mapping to the same slot raises ValueError."""
        (tmp_path / "keskusteluhistoria.txt").write_text("Transcript A", encoding="utf-8")
        (tmp_path / "keskusteluhistoria_user_only.md").write_text("Transcript B", encoding="utf-8")

        with pytest.raises(ValueError, match="Input collision in.*Both.*map to slot 'chat_log'"):
            load_inputs_from_path(tmp_path, expected_inputs=sample_expected_inputs)

    def test_load_inputs_from_path_json_file_with_collision(
        self,
        tmp_path: Path,
        sample_expected_inputs: list[ExpectedInput],
    ) -> None:
        """ISTQB Negative Boundary: Collision within JSON file mapping multiple keys to same slot."""
        json_file = tmp_path / "inputs.json"
        json_file.write_text(
            json.dumps({"keskusteluhistoria": "A", "chat_log": "B"}),
            encoding="utf-8",
        )

        with pytest.raises(ValueError, match="Input collision in JSON file.*map to slot 'chat_log'"):
            load_inputs_from_path(json_file, expected_inputs=sample_expected_inputs)

    def test_load_inputs_from_path_without_expected_inputs(self, tmp_path: Path) -> None:
        """Verify loading without expected_inputs preserves file stems directly."""
        (tmp_path / "my_data.txt").write_text("Sample data", encoding="utf-8")
        inputs = load_inputs_from_path(tmp_path, expected_inputs=None)
        assert inputs["my_data"] == "Sample data"


class TestVarianceRunnerStrategies:
    """Test suite for CLI --strategies, --no-noise, and dynamic strategy routing."""

    def test_run_e2e_variance_test_cli_strategies_parsing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify --strategies strict openai_strict is parsed and forwarded to run_variance_test."""
        from scripts import run_e2e_variance_test

        mock_runner = MagicMock(return_value=["exe_1", "exe_2"])
        monkeypatch.setattr(run_e2e_variance_test, "run_variance_test", mock_runner)

        run_e2e_variance_test.main(["--strategies", "strict", "openai_strict"])

        mock_runner.assert_called_once()
        _, kwargs = mock_runner.call_args
        assert kwargs["strategies"] == ["strict", "openai_strict"]
        assert kwargs["no_noise"] is False

    def test_run_e2e_variance_test_cli_no_noise_parsing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify --no-noise flag sets no_noise=True in run_variance_test."""
        from scripts import run_e2e_variance_test

        mock_runner = MagicMock(return_value=[])
        monkeypatch.setattr(run_e2e_variance_test, "run_variance_test", mock_runner)

        run_e2e_variance_test.main(["--no-noise"])

        mock_runner.assert_called_once()
        _, kwargs = mock_runner.call_args
        assert kwargs["no_noise"] is True

    def test_run_e2e_variance_test_cli_strategies_empty_fails(self) -> None:
        """ISTQB Negative Boundary: Verify passing --strategies without values triggers argparse SystemExit with code 2."""
        from scripts import run_e2e_variance_test

        with pytest.raises(SystemExit) as exc_info:
            run_e2e_variance_test.main(["--strategies"])
        assert exc_info.value.code == 2

    def test_run_e2e_variance_test_empty_strategies_validation(self) -> None:
        """ISTQB Negative Boundary: Passing empty list to run_variance_test raises ValueError."""
        from scripts.run_e2e_variance_test import run_variance_test

        with pytest.raises(ValueError, match="At least one strategy must be provided to --strategies"):
            run_variance_test(strategies=[])

    def test_run_e2e_variance_test_strategy_alias_injection(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify run_variance_test constructs correct STRATEGY_ALIASES for active strategy."""
        from scripts import run_e2e_variance_test

        captured_envs: list[dict[str, str]] = []

        def mock_popen(cmd: list[str], **kwargs: Any) -> Any:
            captured_envs.append(dict(kwargs.get("env", {})))
            return MagicMock()

        monkeypatch.setattr(run_e2e_variance_test, "force_kill_services", lambda: None)
        monkeypatch.setattr(run_e2e_variance_test.subprocess, "Popen", mock_popen)
        monkeypatch.setattr(run_e2e_variance_test, "check_backend", lambda: False)

        with pytest.raises(SystemExit):
            run_e2e_variance_test.run_variance_test(
                inputs_target="dummy.json",
                strategies=["openai_strict"],
            )

        assert len(captured_envs) == 1
        raw_aliases = captured_envs[0].get("STRATEGY_ALIASES")
        assert raw_aliases is not None
        aliases = json.loads(raw_aliases)
        assert aliases["strict"] == "openai_strict"
        assert aliases["reasoning"] == "openai_strict"
        assert aliases["evaluation_strategy"] == "openai_strict"


class TestModelTelemetry:
    """Test suite for model telemetry resolution and hyperparameter printing."""

    def test_resolve_model_telemetry_from_seed(self) -> None:
        """Verify model telemetry extraction correctly identifies Gemini and OpenAI parameters."""
        from scripts.run_e2e_variance_test import resolve_model_telemetry

        telemetry = resolve_model_telemetry(Path("backend_v2/seed/seed_data.json"))
        assert "fast" in telemetry
        assert "fast (google)" in telemetry
        assert "fast (openai)" in telemetry
        assert "deep" in telemetry
        assert "deep (openai)" in telemetry

        fast_gemini = telemetry["fast (google)"]
        assert fast_gemini["provider"] == "google"
        assert "gemini" in fast_gemini["model_name"].lower()
        assert fast_gemini["is_gemini_v3"] is True
        assert "1.0" in fast_gemini["effective_temperature"]
        assert "0 tok" in fast_gemini["thinking_budget"]

        openai_deep = telemetry["deep (openai)"]
        assert openai_deep["provider"] == "openai"
        assert "gpt-5" in openai_deep["model_name"].lower()
        assert openai_deep["is_openai_reasoning"] is True
        assert "1.0" in openai_deep["effective_temperature"]
        assert "'medium'" in openai_deep["reasoning_effort"]
        assert "4096 tok" in openai_deep["thinking_budget"]

    def test_print_model_telemetry_smoke(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify print_model_telemetry formats output without error."""
        from scripts.run_e2e_variance_test import print_model_telemetry

        print_model_telemetry(Path("backend_v2/seed/seed_data.json"), active_strategies=["fast", "deep"])
        captured = capsys.readouterr().out
        assert "Fyysiset Malliparametrit ja Telemetria" in captured
        assert "gemini" in captured.lower()
        assert "gpt-5" in captured.lower()
        assert "1.0" in captured


class TestWorkflowMatrixTelemetry:
    """Test suite for workflow strictness, penalty, and matrix telemetry resolution."""

    def test_resolve_workflow_matrix_telemetry_from_seed(self) -> None:
        """Verify matrix telemetry extraction resolves correct steps, scales, and atom counts."""
        from scripts.run_e2e_variance_test import resolve_workflow_matrix_telemetry

        telemetry = resolve_workflow_matrix_telemetry(
            Path("backend_v2/seed/seed_data.json"),
            workflow_id="wf_03a1d71000000003",
        )
        assert telemetry is not None
        assert telemetry["workflow_id"] == "wf_03a1d71000000003"
        assert telemetry["strictness_level"] == 70
        assert abs(telemetry["strictness_exponent"] - 1.5071) < 0.001
        assert telemetry["enable_contextual_overrides"] is True
        assert telemetry["security_penalty"] == 0.0
        assert telemetry["post_hoc_penalty"] == 0.0
        assert telemetry["passivity_penalty"] == 0.05

        assert telemetry["total_matrices"] == 4
        assert telemetry["total_scales"] == 17
        assert telemetry["total_atoms"] == 85
        assert telemetry["total_high_entropy_atoms"] == 85

        steps = {s["step_rule_id"]: s for s in telemetry["steps"]}
        assert len(steps) == 7

        # Step 2: Archivist (Bloom)
        archivist = steps["sr_03c1d71000000002"]
        assert archivist["cognitive_tier"] == "deep"
        assert archivist["model_strategy"] == "deep"
        assert len(archivist["matrices"]) == 1
        bloom = archivist["matrices"][0]
        assert bloom["block_id"] == "blk_f921c7c0989b47e8"
        assert bloom["computed_min"] == 1
        assert bloom["computed_max"] == 6
        assert len(bloom["scales"]) == 6
        assert bloom["total_atoms"] == 30
        assert bloom["high_entropy_atoms"] == 30

        # Step 3: Analyst (Kahneman)
        analyst = steps["sr_03c1d71000000003"]
        assert analyst["model_strategy"] == "reasoning"
        assert len(analyst["matrices"]) == 1
        kahneman = analyst["matrices"][0]
        assert kahneman["block_id"] == "blk_109dab5b6b3f403a"
        assert len(kahneman["scales"]) == 3
        assert kahneman["total_atoms"] == 15

        # Step 6: Scoring Engine (Logic hook)
        scoring = steps["sr_03c1d71000000006"]
        assert scoring["type"] == "logic"
        assert len(scoring["matrices"]) == 0

    def test_resolve_all_workflows_matrix_telemetry(self) -> None:
        """Verify all workflows in seed data are parsed dynamically with matrix stats."""
        from scripts.run_e2e_variance_test import (
            resolve_all_workflows_matrix_telemetry,
            resolve_workflow_matrix_telemetry,
        )

        all_wfs = resolve_all_workflows_matrix_telemetry(Path("backend_v2/seed/seed_data.json"))
        assert len(all_wfs) == 6
        wf_ids = {w["workflow_id"] for w in all_wfs}
        assert "wf_03a1d71000000003" in wf_ids
        assert "wf_01a1d71000000001" in wf_ids

        # Untargeted resolution on multi-workflow DB returns None (no domain guessing)
        assert resolve_workflow_matrix_telemetry(Path("backend_v2/seed/seed_data.json")) is None
        # Non-existent workflow returns None
        assert resolve_workflow_matrix_telemetry(Path("backend_v2/seed/seed_data.json"), workflow_id="nonexistent") is None

    def test_resolve_workflow_matrix_telemetry_targeted_id(self) -> None:
        """Verify targeted workflow resolution parses specific workflow parameters by ID and slug."""
        from scripts.run_e2e_variance_test import resolve_workflow_matrix_telemetry

        telemetry_by_id = resolve_workflow_matrix_telemetry(
            Path("backend_v2/seed/seed_data.json"),
            workflow_id="wf_05a1d71000000005",
        )
        assert telemetry_by_id is not None
        assert telemetry_by_id["workflow_id"] == "wf_05a1d71000000005"
        assert telemetry_by_id["security_penalty"] == 0.15

        telemetry_by_slug = resolve_workflow_matrix_telemetry(
            Path("backend_v2/seed/seed_data.json"),
            workflow_id="syvallinen_ongelmanratkaisu_kognitio",
        )
        assert telemetry_by_slug is not None
        assert telemetry_by_slug["workflow_id"] == "wf_03a1d71000000003"

    def test_print_workflow_matrix_telemetry_smoke(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify print_workflow_matrix_telemetry outputs formatted telemetry cleanly."""
        from scripts.run_e2e_variance_test import print_workflow_matrix_telemetry

        print_workflow_matrix_telemetry(Path("backend_v2/seed/seed_data.json"))
        captured = capsys.readouterr().out
        assert "Työnkulun ja Arviointimatriisien Parametrit" in captured
        assert "Sovereign Strictness:     50%" in captured
        assert "Bloomin Taksonomia" in captured
        assert "Kahnemanin Kaksoisprosessiteoria" in captured
        assert "Deterministinen UnifiedScoringEngine" in captured

    def test_main_show_matrices_flag(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify main() with --show-matrices prints parameters and exits without executing."""
        from scripts.run_e2e_variance_test import main

        result = main(["--show-matrices", "--db-path", "backend_v2/seed/seed_data.json"])
        assert result == []
        captured = capsys.readouterr().out
        assert "Fyysiset Malliparametrit ja Telemetria" in captured
        assert "Työnkulun ja Arviointimatriisien Parametrit" in captured


