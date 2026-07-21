from unittest.mock import AsyncMock
from unittest.mock import MagicMock, patch

from backend_v2.database.wrapper import TinyDBTable


def test_tinydb_table_operations_are_locked() -> None:
    """Verify that every database operation on TinyDBTable acquires the db_lock."""
    table = TinyDBTable(db_path="dummy_path.json", table_name="dummy_table")

    # We patch the db_lock function in the wrapper module
    with patch("backend_v2.database.wrapper.db_lock") as mock_db_lock:
        mock_context = MagicMock()
        mock_db_lock.return_value = mock_context

        # Patch TinyDB constructor so we don't try to open a real file
        with patch("backend_v2.database.wrapper.TinyDB") as mock_tinydb:
            mock_db_instance = MagicMock()
            mock_tinydb.return_value.__enter__.return_value = mock_db_instance

            # 1. Test insert
            table.insert({"data": "test"})
            mock_db_lock.assert_called_with("dummy_path.json")
            mock_context.__enter__.assert_called()
            mock_db_lock.reset_mock()
            mock_context.__enter__.reset_mock()

            # 2. Test all
            table.all()
            mock_db_lock.assert_called_with("dummy_path.json")
            mock_context.__enter__.assert_called()
            mock_db_lock.reset_mock()
            mock_context.__enter__.reset_mock()

            # 3. Test get
            table.get(query=None)
            mock_db_lock.assert_called_with("dummy_path.json")
            mock_context.__enter__.assert_called()
            mock_db_lock.reset_mock()
            mock_context.__enter__.reset_mock()

            # 4. Test update
            table.update(fields={"a": 1})
            mock_db_lock.assert_called_with("dummy_path.json")
            mock_context.__enter__.assert_called()
            mock_db_lock.reset_mock()
            mock_context.__enter__.reset_mock()

            # 5. Test upsert
            table.upsert(document={"id": "1"}, query=None)
            mock_db_lock.assert_called_with("dummy_path.json")
            mock_context.__enter__.assert_called()
            mock_db_lock.reset_mock()
            mock_context.__enter__.reset_mock()

            # 6. Test remove
            table.remove(query=None)
            mock_db_lock.assert_called_with("dummy_path.json")
            mock_context.__enter__.assert_called()
            mock_db_lock.reset_mock()
            mock_context.__enter__.reset_mock()

            # 7. Test truncate
            table.truncate()
            mock_db_lock.assert_called_with("dummy_path.json")
            mock_context.__enter__.assert_called()
            mock_db_lock.reset_mock()
            mock_context.__enter__.reset_mock()

            # 8. Test count
            table.count()
            mock_db_lock.assert_called_with("dummy_path.json")
            mock_context.__enter__.assert_called()
            mock_db_lock.reset_mock()
            mock_context.__enter__.reset_mock()

            # 9. Test contains
            table.contains(query=None)
            mock_db_lock.assert_called_with("dummy_path.json")
            mock_context.__enter__.assert_called()
