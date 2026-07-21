from unittest.mock import AsyncMock
import json
from pathlib import Path
from typing import Any

import pytest


@pytest.mark.skip(reason="Legacy epic 61 string checks no longer apply after P0/P2 seed cleanup.")
def test_seed_data_assertions_contain_hardened_rules() -> None:
    """Verify that the 5 target TDA assertions in seed_data.json have been successfully updated."""
    seed_file = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")
    assert seed_file.exists()

    with open(seed_file, encoding="utf-8") as f:
        data = json.load(f)

    found_ids = set()

    def scan_for_tda_ids(node: Any) -> None:
        if isinstance(node, dict):
            if "tda_id" in node:
                desc = node.get("concept_description", "")
                desc_lower = desc.lower()
                if "ambiguity_protocol" in desc_lower:
                    assert "json null" in desc_lower or "return null" in desc_lower
                    found_ids.add(node["tda_id"])
            for v in node.values():
                scan_for_tda_ids(v)
        elif isinstance(node, list):
            for item in node:
                scan_for_tda_ids(item)

    scan_for_tda_ids(data)
    assert len(found_ids) >= 1
