import typing
from typing import Any

ChunkRecordModel = object()

if typing.TYPE_CHECKING:
    ChunkRecordModelType = Any
else:
    ChunkRecordModelType = ChunkRecordModel

records = (
    list[ChunkRecordModelType],
    'field'
)

