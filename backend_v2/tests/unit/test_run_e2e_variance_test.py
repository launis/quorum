"""Unit tests for run_e2e_variance_test.py run marker injection and user-turn scope guarantees.

Validates that cryptographic Unicode noise markers are reliably injected into human user turns
in chat_log inputs, preventing cache collisions on downstream user-only cognitive evaluations.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from backend_v2.services.chat_normalizer import ChatNormalizerService
from scripts.run_e2e_variance_test import (
    UNICODE_SPACE_REGISTRY,
    _ensure_user_turn_marker,
    inject_unique_run_marker,
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
