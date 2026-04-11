import pytest
from unittest.mock import AsyncMock

from backend_v2.core.hook_registry import HookDependencies, HookState
from backend_v2.models.enums import MatrixSamplingStrategy
from backend_v2.hooks.atom_flattening import process_matrix_flattening


@pytest.fixture
def mock_dependencies():
    repo_mock = AsyncMock()
    return HookDependencies(repository=repo_mock)


def _build_mock_matrix(block_id: str, num_levels: int, atoms_per_level: int):
    scales = []
    for score in range(1, num_levels + 1):
        atoms = [f"Matrix {block_id} - Score {score} - Atom {i}" for i in range(atoms_per_level)]
        scales.append({
            "score": score,
            "ai_label": f"LABEL_{score}",
            "claims": [
                {
                    "label": {"default_locale": "en", "translations": {"en": "Claim"}},
                    "ai_description": "test",
                    "micro_atoms": atoms
                }
            ]
        })

    return {
        "id": block_id,
        "slug": f"slug_{block_id}",
        "category_id": "matrix",
        "label": {"default_locale": "en", "translations": {"en": "Matrix"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "type": "string",
        "is_evaluative": True,
        "scale_min": 1,
        "scale_max": num_levels,
        "scales": scales
    }


def _build_mock_step(step_id: str, prompt_blocks: list[str]):
    return {
        "id": step_id,
        "slug": f"slug_{step_id}",
        "name": "Test Step",
        "type": "llm",
        "prompt_blocks": prompt_blocks,
        "model_strategy": "fast"
    }


@pytest.mark.asyncio
async def test_atom_flattening_all(mock_dependencies):
    """Test retrieving all atoms when strategy is ALL (0)."""
    # 5 levels, 10 atoms per level = 50 atoms total
    matrix_id = "blk_1234567890abcdef1234567890abcde"
    step_id = "stp_1234567890abcdef1234567890abcde"
    
    mock_matrix = _build_mock_matrix(matrix_id, num_levels=5, atoms_per_level=10)
    mock_step = _build_mock_step(step_id, prompt_blocks=[matrix_id])
    
    mock_dependencies.repository.get_step_by_id.return_value = mock_step
    mock_dependencies.repository.get_all_prompt_blocks.return_value = [mock_matrix]
    
    state = HookState(
        execution_id="exe_1234567890abcdef1234567890abcde",
        workflow_id="wf_123",
        step_id=step_id,
        task_blueprint=step_id,
        inputs={},
        metadata={"matrix_sampling_strategy": MatrixSamplingStrategy.ALL.value}
    )
    
    result = await process_matrix_flattening(state, mock_dependencies)
    
    assert result.success is True
    
    shuffled_atoms = result.state_delta.get("shuffled_atoms")
    assert shuffled_atoms is not None
    assert len(shuffled_atoms) == 50  # All 50 atoms collected
    
    # Check structure
    sample = shuffled_atoms[0]
    assert "atom_id" in sample


@pytest.mark.asyncio
async def test_atom_flattening_stratified(mock_dependencies):
    """Test retrieving stratified sampled atoms."""
    # 5 levels, 10 atoms per level
    matrix_id = "blk_1234567890abcdef1234567890abcde"
    step_id = "stp_1234567890abcdef1234567890abcde"
    
    mock_matrix = _build_mock_matrix(matrix_id, num_levels=5, atoms_per_level=10)
    mock_step = _build_mock_step(step_id, prompt_blocks=[matrix_id])
    
    mock_dependencies.repository.get_step_by_id.return_value = mock_step
    mock_dependencies.repository.get_all_prompt_blocks.return_value = [mock_matrix]
    
    # Attempting to fetch exactly 3 atoms per scale (5 scales * 3 = 15 total)
    state = HookState(
        execution_id="exe_1234567890abcdef1234567890abcde",
        workflow_id="wf_123",
        step_id=step_id,
        task_blueprint=step_id,
        inputs={},
        metadata={"matrix_sampling_strategy": MatrixSamplingStrategy.STRATIFIED_3.value}
    )
    
    result = await process_matrix_flattening(state, mock_dependencies)
    
    assert result.success is True
    shuffled_atoms = result.state_delta.get("shuffled_atoms")
    assert len(shuffled_atoms) == 15


@pytest.mark.asyncio
async def test_atom_flattening_deterministic_shuffle(mock_dependencies):
    """Test that two executions with the same execution_id yield the exact same order."""
    matrix_id = "blk_1234567890abcdef1234567890abcde"
    step_id = "stp_1234567890abcdef1234567890abcde"
    
    mock_matrix = _build_mock_matrix(matrix_id, num_levels=5, atoms_per_level=10)
    mock_step = _build_mock_step(step_id, prompt_blocks=[matrix_id])
    
    mock_dependencies.repository.get_step_by_id.return_value = mock_step
    mock_dependencies.repository.get_all_prompt_blocks.return_value = [mock_matrix]
    
    state1 = HookState(
        execution_id="exe_IDENTICAL00000000000000000000",
        workflow_id="wf_123",
        step_id=step_id,
        task_blueprint=step_id,
        inputs={},
        metadata={"matrix_sampling_strategy": MatrixSamplingStrategy.STRATIFIED_5.value}
    )
    
    state2 = HookState(
        execution_id="exe_IDENTICAL00000000000000000000",
        workflow_id="wf_123",
        step_id=step_id,
        task_blueprint=step_id,
        inputs={},
        metadata={"matrix_sampling_strategy": MatrixSamplingStrategy.STRATIFIED_5.value}
    )
    
    res1 = await process_matrix_flattening(state1, mock_dependencies)
    res2 = await process_matrix_flattening(state2, mock_dependencies)
    
    list1 = [x["atom_id"] for x in res1.state_delta["shuffled_atoms"]]
    list2 = [x["atom_id"] for x in res2.state_delta["shuffled_atoms"]]
    
    assert len(list1) == 25  # 5 STRATIFIED * 5 levels
    assert list1 == list2  # Exact deterministic order match

