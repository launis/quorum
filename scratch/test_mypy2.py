import typing
from typing import Any
from pydantic import Field

def test():
    ChunkRecordModel = object()
    records_tuple: Any = (list[Any], Field())
    if not typing.TYPE_CHECKING:
        records_tuple = (list[ChunkRecordModel], records_tuple[1])

