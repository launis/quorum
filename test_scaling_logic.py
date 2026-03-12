import asyncio
from backend_v2.hooks.scoring import normalize_matrix_scores_hook
from backend_v2.models.state import WorkflowState
from backend_v2.models.v2_core import PromptBlock
from pydantic import BaseModel

class MockRepo:
    async def get_prompt_block_by_id(self, slug: str) -> dict:
        if slug == "test_matrix":
            return {
                "id": "test_matrix",
                "label": {"default_locale": "fi", "translations": {}},
                "description": {"default_locale": "fi", "translations": {}},
                "category_id": "sys",
                "type": "float",
                "strictness_level": 50,
                "allow_decimals": True,
                "require_justification": False,
                "scale_min": 4.0,
                "scale_max": 10.0,
                "scales": [
                    {"score": 1, "name": {"default_locale": "fi", "translations": {}}, "claims": [{"default_locale": "fi", "translations": {}}]},
                    {"score": 5, "name": {"default_locale": "fi", "translations": {}}, "claims": [{"default_locale": "fi", "translations": {}}]}
                ]
            }
        return {}

    async def get_step_by_id(self, step_id: str) -> dict:
        if step_id == "test_step":
            return {
                "id": "test_step",
                "slug": "test_step",
                "name": {"default_locale": "fi", "translations": {}},
                "prompt_blocks": ["test_matrix"]
            }
        return {}

class MockEvent:
    def __init__(self):
        self.event_type = "output"
        self.step_name = "test_step"
        self.content = {"test_matrix": 2.5}

async def test_normalization():
    state = WorkflowState(
        execution_id="123e4567-e89b-12d3-a456-426614174000",
        workflow_id="test_wf",
        current_step="test_step",
        execution_trace=[{
            "event_id": "123e4567-e89b-12d3-a456-426614174000",
            "execution_id": "123e4567-e89b-12d3-a456-426614174000",
            "event_type": "output",
            "step_name": "test_step",
            "content": {"test_matrix": 2.5}
        }],
        context_variables={
            "test_step": {"test_matrix": 2.5},
            "test_step_slug": {"test_matrix": 2.5}
        },
        step_outputs={"test_step": {"test_matrix": 2.5}}
    )
    repo = MockRepo()
    
    result = await normalize_matrix_scores_hook(state=state, repository=repo)
    
    # 2.5 raw on a 1-5 scale is 37.5% of the way up.
    # Target scale is 4 to 10. Range is 6.
    # (2.5 - 1) / (5 - 1) = 1.5 / 4 = 0.375
    # 4 + (0.375 * 6) = 4 + 2.25 = 6.25
    
    print("Hook Result Variables:", result.context_variables)
    
    cv = result.context_variables.get("test_step", {})
    assert cv.get("test_matrix_raw") == 2.5, "Raw score was not saved."
    assert cv.get("test_matrix") == 6.25, f"Scaled score was incorrect: {cv.get('test_matrix')}"
    print("SUCCESS: Normalization logic passed.")

if __name__ == "__main__":
    asyncio.run(test_normalization())
