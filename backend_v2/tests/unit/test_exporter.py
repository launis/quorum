from unittest.mock import AsyncMock
from unittest.mock import MagicMock, mock_open, patch

from backend_v2.database.exporter import export_db_to_files


def test_export_db_to_files_success() -> None:
    """Test successful export of database to files."""
    mock_settings = MagicMock()
    mock_settings.prod_db_path = "dummy_db.json"
    mock_settings.seed_data_path = "dummy_seed.json"

    mock_db = MagicMock()
    mock_table = MagicMock()
    mock_table.all.return_value = [{"id": "1", "data": "test"}]
    mock_db.table.return_value = mock_table
    mock_db.tables.return_value = ["concepts", "references", "claims", "system_config"]

    with patch("backend_v2.database.exporter.get_settings", return_value=mock_settings):
        with patch("backend_v2.database.exporter.TinyDB", return_value=mock_db):
            with patch("backend_v2.database.exporter.os.path.exists", return_value=False):
                m_open = mock_open()
                with patch("backend_v2.database.exporter.open", m_open):
                    result = export_db_to_files("test_db_path")

    assert result["status"] == "success"
    assert result["message"] == "Configuration exported to files."
    m_open.assert_called_once_with("dummy_seed.json", "w", encoding="utf-8")
