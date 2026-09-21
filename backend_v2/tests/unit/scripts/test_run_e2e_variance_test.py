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
from unittest.mock import MagicMock, patch

import pytest
import requests

from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.step import ExpectedInput
from backend_v2.services.chat_normalizer import ChatNormalizerService
from scripts.run_e2e_variance_test import (
    UNICODE_SPACE_REGISTRY,
    _ensure_user_turn_marker,
    _match_input_key,
    check_backend,
    force_kill_services,
    inject_unique_run_marker,
    load_inputs_from_path,
    main,
    make_noise_injector,
    poll_database_for_execution,
    run_variance_test,
    trigger_execution,
    validate_execution_kelvollisuus,
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

    @staticmethod
    def _resolve_script_path() -> Path:
        current = Path(__file__).resolve()
        for parent in current.parents:
            cand = parent / "scripts" / "run_e2e_variance_test.py"
            if cand.exists():
                return cand
        raise FileNotFoundError("scripts/run_e2e_variance_test.py not found")

    def test_run_e2e_variance_test_cli_standalone_invocation(self) -> None:
        """Verify scripts/run_e2e_variance_test.py can be invoked directly as a standalone CLI script.

        Regression test: sys.path bootstrap must precede project imports like backend_v2,
        otherwise direct invocation raises ModuleNotFoundError: No module named 'backend_v2'.
        """
        script_path = self._resolve_script_path()
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
        script_path = self._resolve_script_path()
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
        script_path = self._resolve_script_path()
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

    def test_match_input_key_dict_payload_validated_as_expected_input(
        self,
        sample_expected_inputs: list[ExpectedInput],
    ) -> None:
        """Verify that dictionary payloads passed to _match_input_key are parsed via ExpectedInput.model_validate."""
        dict_expected_inputs = [item.model_dump(mode="json") for item in sample_expected_inputs]
        assert _match_input_key("chat_log", dict_expected_inputs) == "chat_log"
        assert _match_input_key("keskusteluhistoria", dict_expected_inputs) == "chat_log"
        assert _match_input_key("final_product", dict_expected_inputs) == "product_text"

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
        """ISTQB Negative Boundary: Verify passing --strategies without values triggers SystemExit."""
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
        monkeypatch.setattr("scripts.run_e2e_variance_test.subprocess.Popen", mock_popen)
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
        assert "fast (ai_studio)" in telemetry
        assert "fast (openai)" in telemetry
        assert "deep" in telemetry
        assert "deep (openai)" in telemetry

        fast_gemini = telemetry["fast (ai_studio)"]
        assert fast_gemini["provider"] == "ai_studio"
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
        assert analyst["model_strategy"] == "deep"
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
        assert (
            resolve_workflow_matrix_telemetry(Path("backend_v2/seed/seed_data.json"), workflow_id="nonexistent") is None
        )

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


class TestModelRegistryComparison:
    """Test suite for sovereign model stack comparison and dynamic CLI resolution."""

    def test_resolve_comparison_registries_auto_pairing(self) -> None:
        """Verify resolve_comparison_registries automatically resolves workflow stack and alternative stack."""
        from scripts.run_e2e_variance_test import resolve_comparison_registries

        reg_a, reg_b = resolve_comparison_registries(Path("backend_v2/seed/seed_data.json"))
        assert reg_a["id"] == "sys_e26807f3bfa3454d"
        assert reg_b["id"] != reg_a["id"]
        assert reg_b["id"] in ("sys_b1c2d3e4f5a60718", "sys_6f8b1c4a2e0d49f1")

    def test_resolve_comparison_registries_explicit_args(self) -> None:
        """Verify resolve_comparison_registries supports explicit provider and name matches."""
        from scripts.run_e2e_variance_test import resolve_comparison_registries

        reg_a, reg_b = resolve_comparison_registries(
            Path("backend_v2/seed/seed_data.json"),
            compare_args=["openai", "google"],
        )
        assert reg_a["default_provider"] == "openai"
        assert reg_b["default_provider"] in ("ai_studio", "vertex_ai")

    def test_resolve_comparison_registries_invalid_count_raises(self) -> None:
        """Verify resolve_comparison_registries fails fast when compare_args has invalid count."""
        import pytest

        from scripts.run_e2e_variance_test import resolve_comparison_registries

        with pytest.raises(ValueError, match="expects either 0 arguments"):
            resolve_comparison_registries(
                Path("backend_v2/seed/seed_data.json"),
                compare_args=["only_one"],
            )

    def test_resolve_comparison_registries_same_registry_raises(self) -> None:
        """Verify resolve_comparison_registries fails fast when both targets resolve to identical stack."""
        import pytest

        from scripts.run_e2e_variance_test import resolve_comparison_registries

        with pytest.raises(ValueError, match="Cannot compare model registry"):
            resolve_comparison_registries(
                Path("backend_v2/seed/seed_data.json"),
                compare_args=["google", "sys_e26807f3bfa3454d"],
            )

    def test_resolve_model_telemetry_targeted_registry(self) -> None:
        """Verify resolve_model_telemetry targets specific stack when registry_id is provided."""
        from scripts.run_e2e_variance_test import resolve_model_telemetry

        telemetry_openai = resolve_model_telemetry(
            Path("backend_v2/seed/seed_data.json"),
            registry_id="openai",
        )
        assert "fast" in telemetry_openai
        assert telemetry_openai["fast"]["provider"] == "openai"
        assert "gpt-5" in telemetry_openai["fast"]["model_name"].lower()

        telemetry_google = resolve_model_telemetry(
            Path("backend_v2/seed/seed_data.json"),
            registry_id="google",
        )
        assert "fast" in telemetry_google
        assert telemetry_google["fast"]["provider"] in ("ai_studio", "vertex_ai")
        assert "gemini" in telemetry_google["fast"]["model_name"].lower()

    def test_main_show_matrices_compare_registries(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify main() with --show-matrices and --compare-registries prints comparison preview."""
        from scripts.run_e2e_variance_test import main

        result = main(
            [
                "--show-matrices",
                "--compare-registries",
                "google",
                "openai",
                "--db-path",
                "backend_v2/seed/seed_data.json",
            ]
        )
        assert result == []
        captured = capsys.readouterr().out
        assert "SOVEREIGN MODEL STACK COMPARISON PREVIEW" in captured
        assert "Google AI Studio Stack" in captured
        assert "OpenAI O-Series Stack" in captured

    def test_main_model_registry_cli_parsing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify CLI correctly parses --model-registry and --compare-registries and forwards to runner."""
        from scripts import run_e2e_variance_test

        recorded_kwargs: dict[str, Any] = {}

        def mock_runner(**kwargs: Any) -> list[str]:
            recorded_kwargs.update(kwargs)
            return ["exe_mock1", "exe_mock2"]

        monkeypatch.setattr(run_e2e_variance_test, "run_variance_test", mock_runner)

        run_e2e_variance_test.main(
            [
                "--model-registry",
                "sys_6f8b1c4a2e0d49f1",
                "--compare-registries",
                "google",
                "openai",
            ]
        )

        assert recorded_kwargs["model_registry"] == "sys_6f8b1c4a2e0d49f1"
        assert recorded_kwargs["compare_registries"] == ["google", "openai"]


class TestNoNoiseIngressInvariance:
    """Test suite for --no-noise input hoisting, caching, and pre-flight ingress hash assertions."""

    def test_run_variance_test_no_noise_caches_inputs_and_asserts_hash(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Verify load_inputs_from_path is called only once in --no-noise mode across runs."""
        from scripts import run_e2e_variance_test

        load_calls = 0

        def mock_load_inputs(*args: Any, **kwargs: Any) -> dict[str, Any]:
            nonlocal load_calls
            load_calls += 1
            return {"chat_log": "Hello test prompt", "product_text": "Sample text"}

        mock_res = MagicMock()
        mock_res.json.return_value = [
            {
                "id": "wf_test",
                "default_profile_id": "prf_test",
                "default_strictness_level": 50,
                "expected_inputs": [],
            }
        ]

        monkeypatch.setattr(run_e2e_variance_test, "force_kill_services", lambda: None)
        monkeypatch.setattr("scripts.run_e2e_variance_test.subprocess.Popen", lambda *a, **kw: MagicMock())
        monkeypatch.setattr(run_e2e_variance_test, "check_backend", lambda: True)
        monkeypatch.setattr("scripts.run_e2e_variance_test.requests.get", lambda *a, **kw: mock_res)
        monkeypatch.setattr(run_e2e_variance_test, "load_inputs_from_path", mock_load_inputs)
        monkeypatch.setattr(run_e2e_variance_test, "trigger_execution", lambda *a, **kw: "exe_test_id")
        monkeypatch.setattr(
            run_e2e_variance_test,
            "poll_database_for_execution",
            lambda *a, **kw: {"status": "PASSED"},
        )
        monkeypatch.setattr(
            "scripts.run_e2e_variance_test.subprocess.run",
            lambda *a, **kw: MagicMock(stdout="", stderr=""),
        )

        runs = run_e2e_variance_test.run_variance_test(
            inputs_target=str(tmp_path),
            num_runs=2,
            no_noise=True,
            workflow="wf_test",
            profile="prf_test",
        )

        assert len(runs) == 2
        # Crucial invariant: load_inputs_from_path must be called strictly once due to hoisting/caching
        assert load_calls == 1

    def test_run_variance_test_no_noise_hash_mismatch_raises_runtime_error(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Verify pre-flight ingress hash mismatch triggers Fail-Fast RuntimeError."""
        from scripts import run_e2e_variance_test

        mock_res = MagicMock()
        mock_res.json.return_value = [
            {
                "id": "wf_test",
                "default_profile_id": "prf_test",
                "default_strictness_level": 50,
                "expected_inputs": [],
            }
        ]

        # Simulate corrupted inputs on second iteration
        run_count = 0

        def mock_dump(obj: Any, f: Any, **kwargs: Any) -> None:
            nonlocal run_count
            run_count += 1
            if run_count == 2:
                f.write('{"diverged": true}')
            else:
                f.write('{"standard": true}')

        monkeypatch.setattr(run_e2e_variance_test, "force_kill_services", lambda: None)
        monkeypatch.setattr("scripts.run_e2e_variance_test.subprocess.Popen", lambda *a, **kw: MagicMock())
        monkeypatch.setattr(run_e2e_variance_test, "check_backend", lambda: True)
        monkeypatch.setattr("scripts.run_e2e_variance_test.requests.get", lambda *a, **kw: mock_res)
        monkeypatch.setattr(
            run_e2e_variance_test,
            "load_inputs_from_path",
            lambda *a, **kw: {"text": "hello"},
        )
        monkeypatch.setattr("scripts.run_e2e_variance_test.json.dump", mock_dump)
        monkeypatch.setattr(run_e2e_variance_test, "trigger_execution", lambda *a, **kw: "exe_test_id")
        monkeypatch.setattr(
            run_e2e_variance_test,
            "poll_database_for_execution",
            lambda *a, **kw: {"status": "PASSED"},
        )

        with pytest.raises(
            RuntimeError,
            match=r"Pre-flight Ingress Hash Mismatch: e2e_inputs_run1\.json and e2e_inputs_run2\.json",
        ):
            run_e2e_variance_test.run_variance_test(
                inputs_target=str(tmp_path),
                num_runs=2,
                no_noise=True,
                workflow="wf_test",
                profile="prf_test",
            )


class TestCheckBackend:
    """Test suite for backend service readiness probing."""

    def test_check_backend_immediate_success(self) -> None:
        """Verify check_backend returns True when endpoint immediately responds HTTP 200."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        with patch("requests.get", return_value=mock_resp):
            assert check_backend(base_url="http://127.0.0.1:8000/docs", max_retries=2) is True

    def test_check_backend_retry_then_success(self) -> None:
        """Verify check_backend retries on non-200 and succeeds when 200 is received."""
        mock_fail = MagicMock()
        mock_fail.status_code = 500
        mock_ok = MagicMock()
        mock_ok.status_code = 200
        with patch("requests.get", side_effect=[mock_fail, mock_ok]), patch("time.sleep"):
            assert check_backend(base_url="http://127.0.0.1:8000/docs", max_retries=3) is True

    def test_check_backend_network_exception_then_timeout(self) -> None:
        """Verify check_backend handles RequestException and returns False after max retries."""
        with patch("requests.get", side_effect=requests.RequestException("Connection refused")), patch("time.sleep"):
            assert check_backend(base_url="http://127.0.0.1:8000/docs", max_retries=2) is False

    def test_check_backend_non_200_reaches_max_retries(self) -> None:
        """Verify check_backend returns False when max_retries exhausted without HTTP 200."""
        mock_fail = MagicMock()
        mock_fail.status_code = 503
        with patch("requests.get", return_value=mock_fail), patch("time.sleep"):
            assert check_backend(base_url="http://127.0.0.1:8000/docs", max_retries=2) is False


class TestForceKillServices:
    """Test suite for process termination and port draining."""

    def test_force_kill_services_clean_flow(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Verify force_kill_services executes bat script, powershell, and taskkill commands."""
        monkeypatch.chdir(tmp_path)
        kill_bat = tmp_path / "kill_services.bat"
        kill_bat.write_text("@echo off\n", encoding="utf-8")

        mock_sub = MagicMock()
        mock_sub.returncode = 0
        mock_sub.stdout = ""
        mock_sub.stderr = ""

        with patch("subprocess.run", return_value=mock_sub) as mock_run, patch("time.sleep"):
            force_kill_services()
            assert mock_run.call_count >= 5

    def test_force_kill_services_subprocess_error_tolerance(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Verify force_kill_services gracefully catches SubprocessError without crashing."""
        monkeypatch.chdir(tmp_path)
        kill_bat = tmp_path / "kill_services.bat"
        kill_bat.write_text("@echo off\n", encoding="utf-8")

        def mock_subprocess_run(cmd: Any, *args: Any, **kwargs: Any) -> MagicMock:
            if isinstance(cmd, list) and "kill_services.bat" in str(cmd[0]):
                raise subprocess.SubprocessError("Failed bat")
            res = MagicMock()
            res.stdout = ""
            res.stderr = ""
            return res

        with patch("subprocess.run", side_effect=mock_subprocess_run), patch("time.sleep"):
            force_kill_services()

    def test_force_kill_services_port_busy_cleanup_loop(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Verify force_kill_services port verification loop kills lingering PID and drains port."""
        monkeypatch.chdir(tmp_path)
        calls = 0

        def mock_subprocess_run(cmd: Any, *args: Any, **kwargs: Any) -> MagicMock:
            nonlocal calls
            res = MagicMock()
            res.stderr = ""
            if isinstance(cmd, str) and "netstat" in cmd:
                calls += 1
                if calls == 1:
                    res.stdout = "  TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING       12345"
                else:
                    res.stdout = ""
            elif isinstance(cmd, list) and len(cmd) > 0 and "powershell" in str(cmd[0]) and "Count" in str(cmd[-1]):
                res.stdout = "0"
            else:
                res.stdout = ""
            return res

        with patch("subprocess.run", side_effect=mock_subprocess_run), patch("time.sleep"):
            force_kill_services()


class TestTriggerExecution:
    """Test suite for trigger_execution API client logic."""

    def test_trigger_execution_no_workflows_raises(self) -> None:
        """Verify trigger_execution raises RuntimeError if workflows endpoint returns empty list."""
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = []
        with patch("requests.get", return_value=mock_resp):
            with pytest.raises(RuntimeError, match="No workflows found in database"):
                trigger_execution(raw_inputs={"a": "b"})

    def test_trigger_execution_workflow_not_found_raises(self) -> None:
        """Verify trigger_execution raises RuntimeError if specified workflow ID is absent."""
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = [{"id": "wf_other", "is_system_core": False}]
        with patch("requests.get", return_value=mock_resp):
            with pytest.raises(RuntimeError, match="Workflow 'wf_target' not found"):
                trigger_execution(raw_inputs={"a": "b"}, workflow_id="wf_target")

    def test_trigger_execution_multiple_workflows_unspecified_raises(self) -> None:
        """Verify trigger_execution raises RuntimeError if multiple non-core workflows exist without --workflow."""
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = [
            {"id": "wf_1", "is_system_core": False},
            {"id": "wf_2", "is_system_core": False},
        ]
        with patch("requests.get", return_value=mock_resp):
            with pytest.raises(RuntimeError, match="Multiple workflows found in database"):
                trigger_execution(raw_inputs={"a": "b"})

    def test_trigger_execution_no_default_profile_raises(self) -> None:
        """Verify trigger_execution raises RuntimeError if resolved workflow lacks default_profile_id."""
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = [{"id": "wf_1", "default_profile_id": None}]
        with patch("requests.get", return_value=mock_resp):
            with pytest.raises(RuntimeError, match="has no default_profile_id and no --profile was specified"):
                trigger_execution(raw_inputs={"a": "b"}, workflow_id="wf_1")

    def test_trigger_execution_success_with_overrides(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify trigger_execution sends correct POST body and saves execution trace to disk."""
        monkeypatch.chdir(tmp_path)
        mock_wf_resp = MagicMock()
        mock_wf_resp.ok = True
        mock_wf_resp.json.return_value = [{"id": "wf_1", "default_profile_id": "prf_1"}]

        mock_post_resp = MagicMock()
        mock_post_resp.ok = True
        mock_post_resp.json.return_value = {
            "id": "exe_test_123",
            "execution_trace": [{"step": 1}],
        }

        with patch("requests.get", return_value=mock_wf_resp), patch("requests.post", return_value=mock_post_resp):
            exec_id = trigger_execution(
                raw_inputs={"text": "hello"},
                workflow_id="wf_1",
                profile_id="prf_1",
                provider_override="openai",
                model_registry_override="reg_custom",
            )
            assert exec_id == "exe_test_123"
            assert (tmp_path / "backend_v2" / "tests" / "test_data" / "e2e_new_trace.json").exists()

    def test_trigger_execution_missing_trace_exits(self) -> None:
        """Verify trigger_execution exits with code 1 if execution_trace is absent from response."""
        mock_wf_resp = MagicMock()
        mock_wf_resp.ok = True
        mock_wf_resp.json.return_value = [{"id": "wf_1", "default_profile_id": "prf_1"}]

        mock_post_resp = MagicMock()
        mock_post_resp.ok = True
        mock_post_resp.json.return_value = {"id": "exe_test_123", "execution_trace": None}

        with patch("requests.get", return_value=mock_wf_resp), patch("requests.post", return_value=mock_post_resp):
            with pytest.raises(SystemExit):
                trigger_execution(raw_inputs={"text": "hello"}, workflow_id="wf_1")


class TestValidateExecutionKelvollisuus:
    """Test suite for execution kelvollisuus and data starvation validation."""

    def test_status_not_passed(self) -> None:
        """Verify non-passed execution status returns False."""
        valid, reason = validate_execution_kelvollisuus({"status": "FAILED"})
        assert valid is False
        assert "non-passed status: 'FAILED'" in reason

    def test_profile_data_starvation(self) -> None:
        """Verify data starvation event in profile_syntheses returns False."""
        record = {
            "status": "PASSED",
            "profile_syntheses": {
                "prf_1": {
                    "data_starvation": {"reason": "Insufficient observations in matrix"}
                }
            },
        }
        valid, reason = validate_execution_kelvollisuus(record)
        assert valid is False
        assert "Insufficient observations in matrix" in reason

    def test_trace_starvation_event(self, tmp_path: Path) -> None:
        """Verify starvation event in execution_trace.json returns False."""
        trace_file = tmp_path / "execution_trace.json"
        trace_file.write_text(
            json.dumps([
                {"step_id": "stp_1", "content": {"event_type": "starvation", "reason": "No evidence extracted"}}
            ]),
            encoding="utf-8",
        )
        record = {"status": "PASSED"}
        valid, reason = validate_execution_kelvollisuus(record, trace_path=trace_file)
        assert valid is False
        assert "Trace event starvation in step 'stp_1'" in reason

    def test_trace_file_json_error_warning(self, tmp_path: Path) -> None:
        """Verify corrupt trace file does not crash validation and logs a warning."""
        trace_file = tmp_path / "execution_trace.json"
        trace_file.write_text("NOT_JSON", encoding="utf-8")
        record = {"status": "PASSED"}
        valid, reason = validate_execution_kelvollisuus(record, trace_path=trace_file)
        assert valid is True

    def test_valid_execution(self, tmp_path: Path) -> None:
        """Verify valid execution with clean trace returns True."""
        trace_file = tmp_path / "execution_trace.json"
        trace_file.write_text(json.dumps([{"step_id": "stp_1", "content": "valid"}]), encoding="utf-8")
        record = {
            "status": "PASSED",
            "profile_syntheses": {
                "prf_1": {"data_starvation": None}
            },
        }
        valid, reason = validate_execution_kelvollisuus(record, trace_path=trace_file)
        assert valid is True
        assert "Execution is valid" in reason


class TestPollDatabaseForExecution:
    """Test suite for poll_database_for_execution."""

    def test_poll_terminal_status_passed(self, tmp_path: Path) -> None:
        """Verify poll_database_for_execution returns record when status is PASSED."""
        db_file = tmp_path / "db.json"
        db_file.write_text(
            json.dumps({
                "executions": {
                    "exe_1": {"id": "exe_1", "status": "PASSED"}
                }
            }),
            encoding="utf-8",
        )
        with patch("time.sleep"):
            res = poll_database_for_execution(db_file, "exe_1", timeout_seconds=10)
            assert res is not None
            assert res["status"] == "PASSED"

    def test_poll_terminal_status_failed(self, tmp_path: Path) -> None:
        """Verify poll_database_for_execution returns record when status is FAILED."""
        db_file = tmp_path / "db.json"
        db_file.write_text(
            json.dumps({
                "executions": {
                    "exe_2": {"id": "exe_2", "status": "FAILED"}
                }
            }),
            encoding="utf-8",
        )
        with patch("time.sleep"):
            res = poll_database_for_execution(db_file, "exe_2", timeout_seconds=10)
            assert res is not None
            assert res["status"] == "FAILED"

    def test_poll_timeout_returns_none(self, tmp_path: Path) -> None:
        """Verify poll_database_for_execution returns None on timeout."""
        db_file = tmp_path / "db.json"
        db_file.write_text(
            json.dumps({
                "executions": {
                    "exe_3": {"id": "exe_3", "status": "RUNNING"}
                }
            }),
            encoding="utf-8",
        )
        with patch("time.sleep"), patch("time.time", side_effect=[0.0, 5.0, 20.0]):
            res = poll_database_for_execution(db_file, "exe_3", timeout_seconds=10)
            assert res is None

    def test_poll_json_decode_error_resilient(self, tmp_path: Path) -> None:
        """Verify poll_database_for_execution tolerates JSONDecodeError gracefully during polling."""
        db_file = tmp_path / "db.json"
        db_file.write_text("INVALID_JSON", encoding="utf-8")
        with patch("time.sleep"), patch("time.time", side_effect=[0.0, 5.0, 20.0]):
            res = poll_database_for_execution(db_file, "exe_4", timeout_seconds=10)
            assert res is None


class TestPdfLoadingAndSpecialCases:
    """Test suite for PDF loading and parsing in load_inputs_from_path."""

    def test_load_inputs_pdf_conversation(self, tmp_path: Path) -> None:
        """Verify PDF conversation extraction using PdfChatExtractorService."""
        pdf_file = tmp_path / "chat_log.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 mock")

        mock_doc = MagicMock()
        mock_doc.metadata = {"modDate": "D:20260921120000"}

        mock_fitz = MagicMock()
        mock_fitz.open.return_value = mock_doc

        mock_pymupdf = MagicMock()

        mock_chat_dto = MagicMock()
        mock_chat_dto.model_dump_json.return_value = '{"conversation": []}'

        with (
            patch.dict("sys.modules", {"fitz": mock_fitz, "pymupdf4llm": mock_pymupdf}),
            patch(
                "backend_v2.services.ingress.pdf_chat_extractor.PdfChatExtractorService.is_conversation_pdf",
                return_value=True,
            ),
            patch(
                "backend_v2.services.ingress.pdf_chat_extractor.PdfChatExtractorService.extract_conversation",
                return_value=mock_chat_dto,
            ),
            patch(
                "backend_v2.services.document_extraction.DocumentExtractionService.parse_pdf_date",
                return_value="2026-09-21",
            ),
        ):
            res = load_inputs_from_path(str(tmp_path))
            assert "chat_log" in res
            assert res["document_date"] == "2026-09-21"

    def test_load_inputs_pdf_non_conversation(self, tmp_path: Path) -> None:
        """Verify non-conversation PDF extraction falls back to markdown conversion."""
        pdf_file = tmp_path / "document.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 mock")

        mock_doc = MagicMock()
        mock_doc.metadata = {}

        mock_fitz = MagicMock()
        mock_fitz.open.return_value = mock_doc

        mock_pymupdf = MagicMock()
        mock_pymupdf.to_markdown.return_value = "# Markdown Content"

        with (
            patch.dict("sys.modules", {"fitz": mock_fitz, "pymupdf4llm": mock_pymupdf}),
            patch(
                "backend_v2.services.ingress.pdf_chat_extractor.PdfChatExtractorService.is_conversation_pdf",
                return_value=False,
            ),
        ):
            res = load_inputs_from_path(str(tmp_path))
            assert "document" in res
            assert res["document"] == "# Markdown Content"


class TestRunVarianceTestOrchestration:
    """Test suite for run_variance_test orchestration branches."""

    def test_run_variance_test_single_run_success(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify run_variance_test executes single-run workflow cleanly with dev flags."""
        monkeypatch.chdir(tmp_path)
        db_file = tmp_path / "db.json"
        db_file.write_text(json.dumps({"executions": {}}), encoding="utf-8")

        mock_exec = {
            "id": "exe_1",
            "status": "PASSED",
            "execution_trace": [{"step": 1}],
        }

        with (
            patch("scripts.run_e2e_variance_test.force_kill_services"),
            patch("scripts.run_e2e_variance_test.check_backend", return_value=True),
            patch("scripts.run_e2e_variance_test.trigger_execution", return_value="exe_1"),
            patch("scripts.run_e2e_variance_test.poll_database_for_execution", return_value=mock_exec),
            patch("scripts.run_e2e_variance_test.validate_execution_kelvollisuus", return_value=(True, "OK")),
            patch("scripts.run_e2e_variance_test.load_inputs_from_path", return_value={"chat_log": "Hello world"}),
            patch("scripts.run_e2e_variance_test.print_model_telemetry"),
            patch("scripts.run_e2e_variance_test.print_workflow_matrix_telemetry"),
            patch("subprocess.Popen"),
            patch("subprocess.run") as mock_sub,
            patch("requests.get") as mock_get,
        ):
            mock_wf = MagicMock()
            mock_wf.ok = True
            mock_wf.json.return_value = [{"id": "wf_1", "default_profile_id": "prf_1", "is_system_core": True}]
            mock_get.return_value = mock_wf

            mock_res = MagicMock()
            mock_res.stdout = "Diff completed successfully"
            mock_res.stderr = ""
            mock_sub.return_value = mock_res

            res = run_variance_test(
                inputs_target=str(tmp_path),
                num_runs=1,
                db_path=db_file,
                dev=True,
                no_cache=True,
                cooldown_seconds=1,
            )
            assert res == ["exe_1"]

    def test_run_variance_test_backend_start_failure(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify run_variance_test exits with code 1 if check_backend returns False."""
        monkeypatch.chdir(tmp_path)
        db_file = tmp_path / "db.json"
        db_file.write_text(json.dumps({"executions": {}}), encoding="utf-8")

        with (
            patch("scripts.run_e2e_variance_test.force_kill_services"),
            patch("scripts.run_e2e_variance_test.check_backend", return_value=False),
            patch("scripts.run_e2e_variance_test.print_model_telemetry"),
            patch("scripts.run_e2e_variance_test.print_workflow_matrix_telemetry"),
            patch("subprocess.Popen"),
        ):
            with pytest.raises(SystemExit):
                run_variance_test(num_runs=1, db_path=db_file)

    def test_run_variance_test_no_workflows_found_exits(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify run_variance_test exits with code 1 if no workflows are returned."""
        monkeypatch.chdir(tmp_path)
        db_file = tmp_path / "db.json"
        db_file.write_text(json.dumps({"executions": {}}), encoding="utf-8")

        with (
            patch("scripts.run_e2e_variance_test.force_kill_services"),
            patch("scripts.run_e2e_variance_test.check_backend", return_value=True),
            patch("scripts.run_e2e_variance_test.print_model_telemetry"),
            patch("scripts.run_e2e_variance_test.print_workflow_matrix_telemetry"),
            patch("subprocess.Popen"),
            patch("requests.get") as mock_get,
        ):
            mock_wf = MagicMock()
            mock_wf.ok = True
            mock_wf.json.return_value = []
            mock_get.return_value = mock_wf

            with pytest.raises(SystemExit):
                run_variance_test(num_runs=1, db_path=db_file)

    def test_run_variance_test_data_starvation_exits(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify run_variance_test exits with code 1 if validate_execution_kelvollisuus fails."""
        monkeypatch.chdir(tmp_path)
        db_file = tmp_path / "db.json"
        db_file.write_text(json.dumps({"executions": {}}), encoding="utf-8")

        mock_exec = {"id": "exe_1", "status": "PASSED"}

        with (
            patch("scripts.run_e2e_variance_test.force_kill_services"),
            patch("scripts.run_e2e_variance_test.check_backend", return_value=True),
            patch("scripts.run_e2e_variance_test.trigger_execution", return_value="exe_1"),
            patch("scripts.run_e2e_variance_test.poll_database_for_execution", return_value=mock_exec),
            patch(
                "scripts.run_e2e_variance_test.validate_execution_kelvollisuus",
                return_value=(False, "Starvation detected"),
            ),
            patch("scripts.run_e2e_variance_test.load_inputs_from_path", return_value={"chat_log": "Hello world"}),
            patch("scripts.run_e2e_variance_test.print_model_telemetry"),
            patch("scripts.run_e2e_variance_test.print_workflow_matrix_telemetry"),
            patch("subprocess.Popen"),
            patch("requests.get") as mock_get,
        ):
            mock_wf = MagicMock()
            mock_wf.ok = True
            mock_wf.json.return_value = [{"id": "wf_1", "default_profile_id": "prf_1", "is_system_core": True}]
            mock_get.return_value = mock_wf

            with pytest.raises(SystemExit):
                run_variance_test(num_runs=1, db_path=db_file)


class TestMainCliDispatch:
    """Test suite for main CLI entrypoint."""

    def test_main_runs_variance_test(self) -> None:
        """Verify main parses CLI arguments and delegates to run_variance_test."""
        with patch("scripts.run_e2e_variance_test.run_variance_test", return_value=["exe_1", "exe_2"]) as mock_run:
            res = main(["--num-runs", "2", "--dev"])
            assert res == ["exe_1", "exe_2"]
            assert mock_run.call_args[1]["num_runs"] == 2
            assert mock_run.call_args[1]["dev"] is True

    def test_main_inputs_flag_precedence(self) -> None:
        """Verify --inputs flag takes precedence over positional input argument in main."""
        with patch("scripts.run_e2e_variance_test.run_variance_test", return_value=[]) as mock_run:
            main(["pos_path", "--inputs", "opt_path"])
            assert mock_run.call_args[1]["inputs_target"] == "opt_path"


class TestNoiseInjectorAndFallback:
    """Test suite for make_noise_injector, short text fallback, and user turn edge cases."""

    def test_make_noise_injector_empty_or_no_spaces(self) -> None:
        """Verify make_noise_injector returns original string when empty or space-free."""
        injector = make_noise_injector(0)
        assert injector("") == ""
        assert injector("SingleWord") == "SingleWord"

    def test_make_noise_injector_with_spaces(self) -> None:
        """Verify make_noise_injector replaces spaces with Unicode space."""
        injector = make_noise_injector(0)
        res = injector("Hello world testing")
        assert any(c in res for c in UNICODE_SPACE_REGISTRY)

    def test_short_text_fallback_injection(self) -> None:
        """Verify inject_unique_run_marker handles strings shorter than stride via fallback."""
        payload = inject_unique_run_marker({"short_field": "a b"}, run_index=0)
        assert len(payload.marker_metadata.injected_keys) == 1
        assert any(c in payload.marked_inputs["short_field"] for c in UNICODE_SPACE_REGISTRY)

    def test_ensure_user_turn_marker_raw_list_format(self) -> None:
        """Verify _ensure_user_turn_marker modifies user turn when chat is a raw JSON list."""
        raw_list_json = json.dumps([
            {"role": "user", "content": "Hello there friend"},
            {"role": "assistant", "content": "Greetings"},
        ])
        marker = "\u00a0"
        marked = _ensure_user_turn_marker(raw_list_json, marker)
        parsed = json.loads(marked)
        assert marker in parsed[0]["content"]
        assert marker not in parsed[1]["content"]

    def test_ensure_user_turn_marker_invalid_json_tolerated(self) -> None:
        """Verify _ensure_user_turn_marker tolerates malformed JSON without raising exception."""
        marker = "\u00a0"
        marked = _ensure_user_turn_marker("{invalid json", marker)
        assert isinstance(marked, str)


class TestKeyMatchingAndInputLoadingEdgeCases:
    """Test suite for edge cases in _match_input_key and load_inputs_from_path."""

    def test_match_input_key_ambiguous_tier1_raises(self) -> None:
        """Verify _match_input_key raises ValueError when candidate matches multiple slots in Tier 1."""
        desc = I18nText(translations={"en": "Description"})
        expected = [
            ExpectedInput(input_key="SlotA", label=I18nText(translations={"en": "Slot A"}), description=desc, input_modes=["file"], required=True),
            ExpectedInput(input_key="slota", label=I18nText(translations={"en": "Slot A Lower"}), description=desc, input_modes=["file"], required=True),
        ]
        with pytest.raises(ValueError, match="Ambiguous Tier 1 match"):
            _match_input_key("slota", expected)

    def test_match_input_key_parenthesis_matching(self) -> None:
        """Verify _match_input_key matches tokens inside parentheses in label."""
        expected = [
            ExpectedInput(
                input_key="chat_slot",
                label=I18nText(translations={"en": "Chat (Conversation)", "fi": "Keskustelu (Chat)"}),
                description=I18nText(translations={"en": "Chat description"}),
                input_modes=["file"],
                required=True,
            )
        ]
        assert _match_input_key("conversation", expected) == "chat_slot"

    def test_match_input_key_ambiguous_tier2_raises(self) -> None:
        """Verify _match_input_key raises ValueError when candidate matches multiple slots in Tier 2."""
        desc = I18nText(translations={"en": "Description"})
        expected = [
            ExpectedInput(input_key="slot_1", label=I18nText(translations={"en": "Report", "fi": "Raportti"}), description=desc, input_modes=["file"], required=True),
            ExpectedInput(input_key="slot_2", label=I18nText(translations={"en": "Report Summary", "fi": "Raportti"}), description=desc, input_modes=["file"], required=True),
        ]
        with pytest.raises(ValueError, match="Ambiguous Tier 2 match"):
            _match_input_key("raportti", expected)

    def test_load_inputs_non_existent_path_raises(self) -> None:
        """Verify load_inputs_from_path raises FileNotFoundError when path is missing."""
        with pytest.raises(FileNotFoundError, match="Inputs path does not exist"):
            load_inputs_from_path("non_existent_directory_xyz")

    def test_load_inputs_from_directory_with_subdirs_and_json(self, tmp_path: Path) -> None:
        """Verify load_inputs_from_path skips subdirs and loads inputs.json and other json files."""
        sub_dir = tmp_path / "ignored_subdir"
        sub_dir.mkdir()

        inputs_json = tmp_path / "inputs.json"
        inputs_json.write_text(json.dumps({"sub_chat": "Chat content"}), encoding="utf-8")

        other_json = tmp_path / "payload.json"
        other_json.write_text(json.dumps({"key": "val"}), encoding="utf-8")

        txt_file = tmp_path / "notes.txt"
        txt_file.write_text("Text note", encoding="utf-8")

        res = load_inputs_from_path(str(tmp_path))
        assert "sub_chat" in res
        assert "payload" in res
        assert "notes" in res
        assert res["notes"] == "Text note"

    def test_load_inputs_single_json_non_dict_raises(self, tmp_path: Path) -> None:
        """Verify load_inputs_from_path raises ValueError if single JSON file is not a dict."""
        json_file = tmp_path / "list_inputs.json"
        json_file.write_text(json.dumps(["item1", "item2"]), encoding="utf-8")
        with pytest.raises(ValueError, match="JSON inputs file must contain a dictionary"):
            load_inputs_from_path(str(json_file))


class TestRunVarianceTestEdgeCases:
    """Test suite for additional branches in run_variance_test."""

    def test_run_variance_test_empty_providers_raises(self, tmp_path: Path) -> None:
        """Verify run_variance_test raises ValueError if providers list is empty."""
        db_file = tmp_path / "db.json"
        db_file.write_text(json.dumps({}), encoding="utf-8")
        with pytest.raises(ValueError, match="At least one provider must be provided"):
            run_variance_test(providers=[], db_path=db_file)

    def test_run_variance_test_empty_strategies_raises(self, tmp_path: Path) -> None:
        """Verify run_variance_test raises ValueError if strategies list is empty."""
        db_file = tmp_path / "db.json"
        db_file.write_text(json.dumps({}), encoding="utf-8")
        with pytest.raises(ValueError, match="At least one strategy must be provided"):
            run_variance_test(strategies=[], db_path=db_file)

    def test_run_variance_test_compare_registries_flow(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify run_variance_test executes side-by-side comparison across two stacks."""
        monkeypatch.chdir(tmp_path)
        db_file = tmp_path / "db.json"
        db_file.write_text(json.dumps({"executions": {}}), encoding="utf-8")

        mock_pair = (
            {"id": "reg_a", "name": "Stack A", "default_provider": "google"},
            {"id": "reg_b", "name": "Stack B", "default_provider": "openai"},
        )
        mock_exec = {"id": "exe_1", "status": "PASSED"}

        with (
            patch("scripts.run_e2e_variance_test.resolve_comparison_registries", return_value=mock_pair),
            patch("scripts.run_e2e_variance_test.force_kill_services"),
            patch("scripts.run_e2e_variance_test.check_backend", return_value=True),
            patch("scripts.run_e2e_variance_test.trigger_execution", side_effect=["exe_a", "exe_b"]),
            patch("scripts.run_e2e_variance_test.poll_database_for_execution", return_value=mock_exec),
            patch("scripts.run_e2e_variance_test.validate_execution_kelvollisuus", return_value=(True, "OK")),
            patch("scripts.run_e2e_variance_test.load_inputs_from_path", return_value={"chat_log": "hello world"}),
            patch("scripts.run_e2e_variance_test.print_model_telemetry"),
            patch("scripts.run_e2e_variance_test.print_workflow_matrix_telemetry"),
            patch("subprocess.Popen"),
            patch("subprocess.run") as mock_sub,
            patch("requests.get") as mock_get,
        ):
            mock_wf = MagicMock()
            mock_wf.ok = True
            mock_wf.json.return_value = [{"id": "wf_1", "default_profile_id": "prf_1", "is_system_core": True}]
            mock_get.return_value = mock_wf

            mock_res = MagicMock()
            mock_res.stdout = "Diff completed"
            mock_res.stderr = "Notice: stderr emitted"
            mock_sub.return_value = mock_res

            res = run_variance_test(
                inputs_target=str(tmp_path),
                compare_registries=["reg_a", "reg_b"],
                db_path=db_file,
                dev=True,
            )
            assert res == ["exe_a", "exe_b"]

    def test_run_variance_test_no_whitespace_raises(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify run_variance_test raises RuntimeError if inputs have no whitespace to inject noise."""
        monkeypatch.chdir(tmp_path)
        db_file = tmp_path / "db.json"
        db_file.write_text(json.dumps({"executions": {}}), encoding="utf-8")

        with (
            patch("scripts.run_e2e_variance_test.force_kill_services"),
            patch("scripts.run_e2e_variance_test.check_backend", return_value=True),
            patch("scripts.run_e2e_variance_test.load_inputs_from_path", return_value={"word": "NoSpacesHere"}),
            patch("scripts.run_e2e_variance_test.print_model_telemetry"),
            patch("scripts.run_e2e_variance_test.print_workflow_matrix_telemetry"),
            patch("subprocess.Popen"),
            patch("requests.get") as mock_get,
        ):
            mock_wf = MagicMock()
            mock_wf.ok = True
            mock_wf.json.return_value = [{"id": "wf_1", "default_profile_id": "prf_1", "is_system_core": True}]
            mock_get.return_value = mock_wf

            with pytest.raises(RuntimeError, match="No whitespace found in any string input fields"):
                run_variance_test(inputs_target=str(tmp_path), num_runs=1, db_path=db_file)

    def test_run_variance_test_no_execution_ids_warning(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify run_variance_test returns empty list when trigger_execution yields empty string."""
        monkeypatch.chdir(tmp_path)
        db_file = tmp_path / "db.json"
        db_file.write_text(json.dumps({"executions": {}}), encoding="utf-8")

        with (
            patch("scripts.run_e2e_variance_test.force_kill_services"),
            patch("scripts.run_e2e_variance_test.check_backend", return_value=True),
            patch("scripts.run_e2e_variance_test.trigger_execution", return_value=""),
            patch("scripts.run_e2e_variance_test.poll_database_for_execution", return_value={"status": "PASSED"}),
            patch("scripts.run_e2e_variance_test.validate_execution_kelvollisuus", return_value=(True, "OK")),
            patch("scripts.run_e2e_variance_test.load_inputs_from_path", return_value={"chat_log": "hello world"}),
            patch("scripts.run_e2e_variance_test.print_model_telemetry"),
            patch("scripts.run_e2e_variance_test.print_workflow_matrix_telemetry"),
            patch("subprocess.Popen"),
            patch("requests.get") as mock_get,
        ):
            mock_wf = MagicMock()
            mock_wf.ok = True
            mock_wf.json.return_value = [{"id": "wf_1", "default_profile_id": "prf_1", "is_system_core": True}]
            mock_get.return_value = mock_wf

            res = run_variance_test(inputs_target=str(tmp_path), num_runs=1, db_path=db_file)
            assert res == []
