"""PostgreSQL 19 Zero-ORM Persistence Package Facade.

Re-exports connection pool protocols, binary pydantic_core JSONB codecs,
PostgresPoolManager, PostgresGraphAdapter, CteReasoningStrategy,
PostgresEntityAdapter, and PostgresUnitOfWork.
"""

from backend_v2.database.postgres.entity_adapter import (
    PostgresEntityAdapter as PostgresEntityAdapter,
)
from backend_v2.database.postgres.graph_adapter import (
    CteReasoningStrategy as CteReasoningStrategy,
)
from backend_v2.database.postgres.graph_adapter import (
    PostgresGraphAdapter as PostgresGraphAdapter,
)
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
from backend_v2.database.postgres.uow import (
    PostgresUnitOfWork as PostgresUnitOfWork,
)

__all__ = [
    "AsyncPgConnectionProtocol",
    "AsyncPgPoolProtocol",
    "AsyncPgRecordProtocol",
    "AsyncPgTransactionProtocol",
    "CteReasoningStrategy",
    "PostgresEntityAdapter",
    "PostgresGraphAdapter",
    "PostgresPoolManager",
    "PostgresUnitOfWork",
    "decode_jsonb_binary",
    "encode_jsonb_binary",
    "init_connection",
]
