"""PostgreSQL 19 Zero-ORM Persistence Package Facade.

Re-exports connection pool management, binary JSONB codecs, and structural driver protocols.
"""

from __future__ import annotations

from backend_v2.database.postgres.pool import (
    AsyncPgConnectionProtocol as AsyncPgConnectionProtocol,
)
from backend_v2.database.postgres.pool import (
    AsyncPgPoolProtocol as AsyncPgPoolProtocol,
)
from backend_v2.database.postgres.pool import (
    AsyncPgRecordProtocol as AsyncPgRecordProtocol,
)
from backend_v2.database.postgres.pool import (
    AsyncPgTransactionProtocol as AsyncPgTransactionProtocol,
)
from backend_v2.database.postgres.pool import (
    PostgresPoolManager as PostgresPoolManager,
)
from backend_v2.database.postgres.pool import (
    decode_jsonb_binary as decode_jsonb_binary,
)
from backend_v2.database.postgres.pool import (
    encode_jsonb_binary as encode_jsonb_binary,
)
from backend_v2.database.postgres.pool import (
    init_connection as init_connection,
)

__all__ = [
    "AsyncPgConnectionProtocol",
    "AsyncPgPoolProtocol",
    "AsyncPgRecordProtocol",
    "AsyncPgTransactionProtocol",
    "PostgresPoolManager",
    "decode_jsonb_binary",
    "encode_jsonb_binary",
    "init_connection",
]
