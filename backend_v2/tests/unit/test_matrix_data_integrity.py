import json
import os

import pytest

from backend_v2.settings import get_settings


def load_seed_data():
    settings = get_settings()
    # Or just hardcode path for this specific script
    seed_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "seed", "seed_data.json")
    with open(seed_path, encoding='utf-8') as f:
        return json.load(f)

@pytest.fixture(scope="module")
def db():
    return load_seed_data()

def test_all_bars_matrices_allow_decimals(db):
    """Ensure every PromptBlock or Matrix with 'scales' explicitly permits decimals."""
    for list_name in ["prompt_blocks", "matrices"]:
        for item in db.get(list_name, []):
            if "scales" in item and len(item["scales"]) > 0:
                # The BARS float architecture requires allow_decimals to be True
                assert item.get("allow_decimals") is True, f"Item {item.get('id')} must have allow_decimals=True"

def test_all_bars_matrices_use_discrete_integer_scores(db):
    """Ensure that the defined 'score' values in the BARS matrix are simple integers (1, 2, 3...)"""
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
                assert float(val).is_integer(), f"Score in {item.get('id')} must be a discrete integer like 1, 2, 3. Found: {val}"
                scores.append(int(val))

            # Additional check: values should ideally be 1, 2, 3... pattern starting at 1
            # Even if there are gaps (like 1, 3, 5), they must all be positive small integers
            for score in scores:
                assert 1 <= score <= 10, f"Score {score} in {item.get('id')} is out of expected logical bounds (1-10)"

def test_workflows_have_normalization_hook(db):
    """Ensure that all workflow steps are intercepted by the normalization hook."""
    for workflow in db.get('workflows', []):
        for step in workflow.get('steps', []):
            post_hooks = step.get('post_hooks', [])
            assert isinstance(post_hooks, list), f"Step {step.get('id')} in workflow {workflow.get('id')} must have a post_hooks list"
            assert "normalize_matrix_scores" in post_hooks, f"Step {step.get('id')} in {workflow.get('id')} is missing the 'normalize_matrix_scores' normalization hook."
