import json
import pytest
from pathlib import Path

SEED_FILE = Path("backend_v2/seed/seed_data.json")

@pytest.fixture
def seed_data():
    with open(SEED_FILE, encoding="utf-8") as f:
        return json.load(f)

def test_all_workflows_have_normalize_hook(seed_data):
    """Enforces that all workflows have the 'normalize_matrix_scores' block in post_hooks."""
    for wf in seed_data.get("workflows", []):
        assert "normalize_matrix_scores" in wf.get("post_hooks", []), f"Workflow {wf['id']} is missing normalize_matrix_scores hook"

def test_xai_reporter_scales_are_strictly_1_2_3(seed_data):
    """Enforces that the XAI Reporter matrix scales are strictly 1, 2, and 3."""
    xai_matrix = next((m for m in seed_data.get("prompt_blocks", []) if m["id"] == "matrix_xai_reporter"), None)
    assert xai_matrix is not None, "matrix_xai_reporter block not found"
    
    scales = xai_matrix.get("scales", [])
    assert len(scales) == 3, "XAI Reporter should have exactly 3 scales"
    
    scores = sorted([s["score"] for s in scales])
    assert scores == [1, 2, 3], f"XAI Reporter scores must be [1, 2, 3], got {scores}"

def test_all_matrices_have_valid_scales(seed_data):
    """Enforces that all matrix prompt blocks have valid score scaling."""
    for block in seed_data.get("prompt_blocks", []):
        if block["id"].startswith("matrix_") and block["id"] != "matrix_xai_reporter":
            scales = block.get("scales", [])
            if scales:
                for scale in scales:
                    score = scale.get("score")
                    assert isinstance(score, (int, float)), f"Scale score must be a number in {block['id']}"
                    assert score > 0, f"Scale score must be strictly positive in {block['id']}"
