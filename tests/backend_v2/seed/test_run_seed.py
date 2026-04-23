import sys
from unittest.mock import MagicMock
sys.modules['backend_v2.services.orchestrator.atomizer'] = MagicMock()
sys.modules['backend_v2.llm.client'] = MagicMock()

import pytest
from unittest.mock import patch, mock_open, AsyncMock
from backend_v2.seed.run_seed import _atomize_with_cache, seed_database, main

@pytest.mark.asyncio
async def test_atomize_with_cache_hit():
    mock_validated = MagicMock()
    mock_validated.id = "test_id"
    mock_validated.content = "test_content"
    mock_validated.label.translations.get.return_value = "en_label"
    
    with patch("builtins.open", mock_open(read_data='{"fake_hash": [{"score": 1, "ai_label": "FAIL"}]}')) as m_open, \
         patch("json.load", return_value={"fake_hash": [{"score": 1, "ai_label": "FAIL"}]}), \
         patch("hashlib.md5") as mock_md5, \
         patch("backend_v2.models.v2_core.MatrixScale") as mock_scale:
        
        mock_md5.return_value.hexdigest.return_value = "fake_hash"
        
        res = await _atomize_with_cache(mock_validated, None, 1, 10, True)
        
        assert res == mock_validated
        mock_scale.model_validate.assert_called_once()

@pytest.mark.asyncio
async def test_atomize_with_cache_miss():
    mock_validated = MagicMock()
    mock_validated.id = "test_id"
    mock_md5_ret = "fake_hash_miss"
    
    with patch("builtins.open", mock_open(read_data='{}')), \
         patch("hashlib.md5") as mock_md5, \
         patch("backend_v2.services.orchestrator.atomizer.PromptAtomizer.atomize_prompt_block", new_callable=AsyncMock) as mock_atomize, \
         patch("json.dump"):
        
        mock_md5.return_value.hexdigest.return_value = mock_md5_ret
        mock_atomize.return_value = mock_validated
        
        res = await _atomize_with_cache(mock_validated, None, 1, 10, True)
        
        assert res == mock_validated
        mock_atomize.assert_called_once()

@pytest.mark.asyncio
async def test_seed_database_local():
    with patch("backend_v2.seed.run_seed._seed_tinydb", new_callable=AsyncMock) as mock_tinydb, \
         patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data='{}')), \
         patch("json.load", return_value={}):
         
         await seed_database("local")
         mock_tinydb.assert_called_once()

@pytest.mark.asyncio
async def test_seed_database_mock():
    with patch("backend_v2.seed.run_seed._seed_tinydb", new_callable=AsyncMock) as mock_tinydb, \
         patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data='{}')), \
         patch("json.load", return_value={}):
         
         await seed_database("mock")
         mock_tinydb.assert_called_once()

def test_main():
    with patch("sys.argv", ["run_seed.py", "local"]), \
         patch("backend_v2.seed.run_seed.seed_database", MagicMock(return_value=None)), \
         patch("asyncio.run") as mock_run:
         
         main()
         mock_run.assert_called_once()
