import json
from pathlib import Path
from typing import Any

from backend_v2.core.system_directives import GLOBAL_HARDENING_FRAMEWORK
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler


def test_global_hardening_framework_contains_epic_61_rule() -> None:
    """Verify that GLOBAL_HARDENING_FRAMEWORK has the Zero-Trust Negative Condition Matching rule."""
    assert "ZERO-TRUST NEGATIVE CONDITION MATCHING" in GLOBAL_HARDENING_FRAMEWORK
    assert "If the text does not contain the exact physical anchors defined in the rule" in GLOBAL_HARDENING_FRAMEWORK


def test_compile_blind_system_instruction_contains_epic_61_rule() -> None:
    """Verify that compile_blind_system_instruction appends the Zero-Trust rule in rules list."""
    compiler = PromptCompiler()
    instruction = compiler.compile_blind_system_instruction("fi")
    assert "When evaluating negative conditions or presence of flaws" in instruction
    assert "you must look ONLY for physical semantic matches" in instruction
    assert "Speculation, extrapolation, or rationalizing away missing evidence is strictly banned." in instruction


def test_seed_data_assertions_contain_hardened_rules() -> None:
    """Verify that the 5 target TDA assertions in seed_data.json have been successfully updated."""
    seed_file = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")
    assert seed_file.exists()

    with open(seed_file, encoding="utf-8") as f:
        data = json.load(f)

    target_ids = {
        "tda_c74c4367acc028cf",
        "tda_d204baf0bdf74ff7",
        "tda_3d3f1162d2ff1558",
        "tda_d0b6789c895808eb",
        "tda_8d049ce6e39a465c",
    }

    found_ids = set()

    def scan_for_tda_ids(node: Any) -> None:
        if isinstance(node, dict):
            if "tda_id" in node and node["tda_id"] in target_ids:
                found_ids.add(node["tda_id"])
                desc = node.get("ai_rule_description", "")
                desc_lower = desc.lower()
                assert "ambiguity_protocol" in desc_lower
                assert "json null" in desc_lower
            else:
                for v in node.values():
                    scan_for_tda_ids(v)
        elif isinstance(node, list):
            for item in node:
                scan_for_tda_ids(item)

    scan_for_tda_ids(data)
    assert found_ids == target_ids
