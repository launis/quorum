import json
import os
from typing import Any

import pytest


def load_seed_data() -> dict[str, Any]:
    # Removed unused settings
    # Or just hardcode path for this specific script
    seed_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "seed", "seed_data.json")
    with open(seed_path, encoding="utf-8") as f:
        return dict(json.load(f))


@pytest.fixture(scope="module")
def db() -> dict[str, Any]:
    return load_seed_data()


def test_all_bars_matrices_allow_decimals(db: dict[str, Any]) -> None:
    """Ensure every PromptBlock or Matrix with 'scales' explicitly permits decimals."""
    for list_name in ["prompt_blocks", "matrices"]:
        for item in db.get(list_name, []):
            if "scales" in item and len(item["scales"]) > 0:
                # The BARS float architecture requires allow_decimals to be True
                assert item.get("allow_decimals") is True, f"Item {item.get('id')} must have allow_decimals=True"


def test_all_bars_matrices_use_discrete_integer_scores(db: dict[str, Any]) -> None:
    """Ensure that the defined 'score' values in the BARS matrix are simple integers (1, 2, 3...)."""
    for list_name in ["prompt_blocks", "matrices"]:
        for item in db.get(list_name, []):
            scales = item.get("scales", [])
            if not scales:
                continue

            scores = []
            for s in scales:
                val = s.get("score")
                assert val is not None, f"Scale inside {item.get('id')} is missing 'score'"

                # Verify numeric type
                assert isinstance(val, (int, float)), f"Score in {item.get('id')} must be a number, got {type(val)}"

                # Check that it's actually an integer value logically (e.g. 1 or 1.0)
                assert float(val).is_integer(), (
                    f"Score in {item.get('id')} must be a discrete integer like 1, 2, 3. Found: {val}"
                )
                scores.append(int(val))

            # Additional check: values should ideally be 1, 2, 3... pattern starting at 1
            # Even if there are gaps (like 1, 3, 5), they must all be positive small integers
            for score in scores:
                assert 1 <= score <= 10, f"Score {score} in {item.get('id')} is out of expected logical bounds (1-10)"


def test_blueprints_have_normalization_hook(db: dict[str, Any]) -> None:
    """Ensure that all evaluating step blueprints are intercepted by the normalization hook."""
    for step in db.get("steps", []):
        step_id = step.get("id", "")
        if "factcheck" in step_id or "scoreengine" in step_id or "input_processing" in step_id:
            continue  # Structural synthesis nodes do not produce matrices natively

        post_hooks = step.get("post_hooks", [])
        assert isinstance(post_hooks, list), f"Blueprint {step.get('id')} must have a post_hooks list"

        # Only verify if it's actually an evaluation node (has prompt blocks mapping to a matrix)
        # We can loosely check if the step is LLM type and not structural.
        if step.get("type", "llm") == "llm":
            # If it's a generic analyst, it might not need normalization if it's not a BARS matrix.
            # But the previous logic checked all steps EXCEPT factcheck/scoreengine.
            assert "normalize_matrix_scores" in post_hooks, (
                f"Blueprint {step.get('id')} is missing the 'normalize_matrix_scores' normalization hook."
            )
