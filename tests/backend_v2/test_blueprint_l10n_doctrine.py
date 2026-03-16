import pytest
from unittest.mock import AsyncMock, MagicMock
from backend_v2.services.blueprint import BlueprintTransformer

@pytest.fixture
def mock_execution_repo():
    repo = AsyncMock()
    return repo

@pytest.mark.asyncio
async def test_blueprint_translation_doctrine_retains_arb_keys(mock_execution_repo):
    """
    Milestone 3: Translation Doctrine Tests (Zero-String Policy)
    
    Asserts that the backend API payload strictly retains the .arb localization keys 
    (e.g., 'report.matrix_title') instead of dangerously resolving them into English 
    strings on the server. Flutter MUST be the sole owner of the presentation language.
    """
    transformer = BlueprintTransformer(mock_execution_repo)
    
    exec_record = MagicMock()
    exec_record.metadata = {"target_locale": "fi"}
    exec_record.status.value = "completed"
    
    # A blueprint filled with .arb localization keys instead of hardcoded English
    exec_record.render_blueprint = {
        "version": "1.0",
        "components": [
            {
                "type": "header", 
                "title": "loc.report.main_title"
            },
            {
                "type": "1d_gauge", 
                "data_path": "$results.score", 
                "title": "loc.report.gauge_title"
            }
        ]
    }
    exec_record.results = {
        "score": 85.0
    }
    mock_execution_repo.get_execution.return_value = exec_record
    mock_execution_repo.get_all_prompt_blocks.return_value = []
    
    payload = await transformer.build_render_payload("test-id")
    components = payload["blueprint"]["components"]
    
    # The API output MUST NOT modify or "translate" the keys.
    # They should pass through cleanly to the JSON payload so Flutter can map them via `AppLocalizations`.
    assert components[0]["title"] == "loc.report.main_title"
    assert components[1]["title"] == "loc.report.gauge_title"
    
    # Ensure data was still attached alongside the pristine translation key
    assert components[1]["value"] == 85.0
