import pytest
from unittest.mock import AsyncMock, MagicMock
from backend_v2.services.blueprint import BlueprintTransformer
from backend_v2.exceptions import AppException

@pytest.fixture
def mock_execution_repo():
    repo = AsyncMock()
    return repo

@pytest.mark.asyncio
async def test_blueprint_schema_validation(mock_execution_repo):
    """Test that validating the backend Pydantic Blueprint schemas throws the correct AppException fail-fast."""
    transformer = BlueprintTransformer(mock_execution_repo)
    
    # Missing required components in an invalid representation
    bad_execution = MagicMock()
    bad_execution.render_blueprint = {
        "version": "1.0",
        "components": "this_should_be_a_list" # Invalid structure forces Pydantic ValidationError
    }
    mock_execution_repo.get_execution.return_value = bad_execution
    
    with pytest.raises(AppException) as exc:
        await transformer.build_render_payload("test-id")
    
    assert exc.value.status_code == 400
    assert exc.value.details["error_code"].name == "VALIDATION_FAILED"

@pytest.mark.asyncio
async def test_blueprint_transformer_graceful_missing_data(mock_execution_repo):
    """Test that resolving a missing data path degrades gracefully without breaking the layout."""
    transformer = BlueprintTransformer(mock_execution_repo)
    
    good_execution = MagicMock()
    good_execution.metadata = {"target_locale": "en"}
    good_execution.status.value = "completed"
    good_execution.render_blueprint = {
        "version": "1.0",
        "components": [
            {
                "type": "1d_gauge",
                "data_path": "$results.score",
                "title": "Gauge"
            }
        ]
    }
    good_execution.results = {} # Data path $results.score is missing
    mock_execution_repo.get_execution.return_value = good_execution
    mock_execution_repo.get_all_prompt_blocks.return_value = []
    
    payload = await transformer.build_render_payload("test-id")
    components = payload["blueprint"]["components"]
    
    assert len(components) == 1
    # Expected fallback is None/0.0 if missing
    assert components[0]["value"] is None

@pytest.mark.asyncio
async def test_blueprint_transformer_bibliography_extraction(mock_execution_repo):
    """Test that compound logic extracts citations into a global bibliography."""
    transformer = BlueprintTransformer(mock_execution_repo)
    
    exec_record = MagicMock()
    exec_record.metadata = {}
    exec_record.status.value = "completed"
    exec_record.render_blueprint = {
        "version": "1.0",
        "components": [
            {"type": "bibliography_footer"}
        ]
    }
    exec_record.results = {
        "some_key": {"citation_reference": "EU AI Act, Article 14."},
        "other_key": {"citation_reference": "Some other book."}
    }
    mock_execution_repo.get_execution.return_value = exec_record
    mock_execution_repo.get_all_prompt_blocks.return_value = []
    
    payload = await transformer.build_render_payload("test-id")
    
    assert "bibliography" in payload
    assert "EU AI Act, Article 14." in payload["bibliography"]
    assert "Some other book." in payload["bibliography"]
    assert len(payload["bibliography"]) == 2

@pytest.mark.asyncio
async def test_blueprint_transformer_strict_float_casting(mock_execution_repo):
    """Test that numbers returned as strings by the LLM are aggressively cast to float."""
    transformer = BlueprintTransformer(mock_execution_repo)
    
    exec_record = MagicMock()
    exec_record.metadata = {}
    exec_record.status.value = "completed"
    exec_record.render_blueprint = {
        "version": "1.0",
        "components": [
            {"type": "1d_gauge", "data_path": "$results.score_raw", "title": "Raw"},
            {"type": "1d_gauge", "data_path": "$results.score_string", "title": "String"},
            {"type": "1d_gauge", "data_path": "$results.score_bad", "title": "Corrupt"}
        ]
    }
    exec_record.results = {
        "score_raw": 95.5,
        "score_string": "88.2",
        "score_bad": "N/A"
    }
    mock_execution_repo.get_execution.return_value = exec_record
    mock_execution_repo.get_all_prompt_blocks.return_value = []
    
    payload = await transformer.build_render_payload("test-id")
    components = payload["blueprint"]["components"]
    
    assert len(components) == 3
    
    # 1. Pure float remains float
    assert components[0]["value"] == 95.5
    assert isinstance(components[0]["value"], float)
    
    # 2. String representation of float is aggressively cast to float
    assert components[1]["value"] == 88.2
    assert isinstance(components[1]["value"], float)
    
    # 3. Corrupt missing string falls gracefully back to None
    assert components[2]["value"] is None
