from typing import Any

from backend_v2.database.driver import Filter, StorageDriver


def test_filter_creation() -> None:
    f = Filter(field="test", operator="==", value=1)
    assert f.field == "test"
    assert f.operator == "=="
    assert f.value == 1


def test_storage_driver_abstract() -> None:
    class DummyDriver(StorageDriver):
        async def init(self) -> None:
            pass

        async def close(self) -> None:
            pass

        async def get(self, coll: Any, doc_id: Any) -> Any:
            return None

        async def query(
            self, coll: Any, filters: Any = None, limit: Any = None, order_by: Any = None, descending: bool = False
        ) -> Any:
            return []

        async def upsert(self, coll: Any, data: Any, doc_id: Any = None) -> str:
            return "1"

        async def update(self, coll: Any, doc_id: Any, data: Any) -> bool:
            return True

        async def delete(self, coll: Any, doc_id: Any) -> bool:
            return True

        async def clear(self, coll: Any) -> None:
            pass

        async def count(self, coll: Any, filters: Any = None) -> int:
            return 0

    d = DummyDriver()
    assert d is not None
