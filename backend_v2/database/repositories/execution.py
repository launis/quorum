"""Database repository implementation module."""

import json
import logging
import uuid
from typing import Any

from pydantic import TypeAdapter, ValidationError

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.base import BaseRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.state import ErrorTraceEvent, TombstoneEvent, TraceEvent
from backend_v2.models.v2_core import ExecutionRecord, FrozenContext, MCPAuditTrace
from backend_v2.services.storage import get_storage_driver

logger = logging.getLogger(__name__)


class ExecutionRepositoryImpl(BaseRepository):
    """Repository implementation for Execution traces and statuses."""

    async def _offload_payloads(self, doc_id: str, data: dict[str, Any]) -> None:
        """Repository method implementation.

        Args:
            doc_id: The execution document ID.
            data: Raw execution data dictionary.

        Raises:
            AppException: If a critical operation fails.
        """
        driver = get_storage_driver()

        # 1. Decouple MCP Audit Trails into native DB subcollection
        if "frozen_context" in data:
            fc_raw = data["frozen_context"]
            if fc_raw:
                try:
                    fc = FrozenContext.model_validate(fc_raw, strict=False)
                    if fc.mcp_tool_audit:
                        coll_path = f"executions/{doc_id}/audit_trails"
                        for audit_trace in fc.mcp_tool_audit:
                            item_id = audit_trace.id or str(uuid.uuid4())
                            trace_dict = audit_trace.model_dump(mode="json")
                            trace_dict["id"] = item_id
                            try:
                                await self.driver.upsert(coll_path, trace_dict, item_id)
                            except Exception as e:
                                msg = f"Failed to persist audit trace {item_id}: {e}"
                                logger.error("[ExecutionRepository] %s", msg)
                                raise AppException(
                                    message=msg,
                                    status_code=500,
                                    details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                                ) from e

                        # Remove audit trails from frozen context in-place for offloaded payload
                        fc_without_audit = fc.model_copy(update={"mcp_tool_audit": []})
                        data["frozen_context"] = fc_without_audit.model_dump(mode="json")
                except ValidationError as ve:
                    msg = f"Invalid FrozenContext payload during offload for {doc_id}: {ve}"
                    logger.error("[ExecutionRepository] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                    raise AppException(
                        message=msg,
                        status_code=422,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from ve

        # 2. Extract massive payloads to Storage Blobs
        for field in ["execution_trace", "frozen_context", "context_variables"]:
            if field in data and data[field]:
                try:
                    payload = json.dumps(data[field], default=str)
                    if len(payload) > 100_000:
                        blob_path = f"executions/{doc_id}/{field}.json"
                        await driver.save(blob_path, payload.encode("utf-8"))
                        data[f"{field}_storage_path"] = blob_path
                        del data[field]
                except Exception as e:
                    msg = f"Failed to offload {field} for {doc_id}: {e}"
                    logger.error("[ExecutionRepository] %s", msg, exc_info=True)
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                    ) from e

    async def _hydrate_payloads(self, data: dict[str, Any] | None) -> None:
        """Hydrate storage blob payloads and subcollection audit trails.

        Args:
            data: Execution record dictionary to hydrate in-place.

        Raises:
            AppException: If blob trace data is missing or corrupted.
        """
        if not data:
            return

        driver = get_storage_driver()

        for field in ["execution_trace", "frozen_context", "context_variables"]:
            path_key = f"{field}_storage_path"
            if path_key in data and data[path_key]:
                try:
                    blob_data = await driver.read(data[path_key])
                    if not blob_data or not blob_data.strip():
                        if field == "execution_trace" and (data["status"] if "status" in data else None) in [
                            "PENDING",
                            "RUNNING",
                            "pending",
                            "running",
                        ]:
                            data[field] = []
                            continue
                        raise ValueError(f"Hydration payload is empty for {field} at {data[path_key]}")

                    if field == "execution_trace":
                        data[field] = TypeAdapter(list[ErrorTraceEvent | TombstoneEvent | TraceEvent]).validate_json(
                            blob_data
                        )
                    elif field == "frozen_context":
                        data[field] = FrozenContext.model_validate_json(blob_data)
                    elif field == "context_variables":
                        data[field] = TypeAdapter(dict[str, Any]).validate_json(blob_data)
                    else:
                        data[field] = TypeAdapter(Any).validate_json(blob_data)
                except Exception as e:
                    logger.warning(
                        "[ExecutionRepository] Failed to hydrate %s from %s. Error: %s",
                        field,
                        data[path_key],
                        e,
                        exc_info=True,
                    )
                    raise AppException(
                        message=f"Missing blob trace data for {field}.",
                        status_code=500,
                        details={"error_code": ErrorCodes.DATA_CORRUPTION.value, "path": data[path_key]},
                    ) from e

        doc_id = data["id"] if "id" in data else None
        if doc_id:
            try:
                coll_path = f"executions/{doc_id}/audit_trails"
                trails = await self.driver.query(coll_path)
                if trails:
                    trails.sort(key=lambda x: x["timestamp"] if "timestamp" in x else "")
                    audit_models = TypeAdapter(list[MCPAuditTrace]).validate_python(trails, strict=False)
                    fc_data = data["frozen_context"] if "frozen_context" in data else None
                    if fc_data:
                        fc = (
                            fc_data
                            if isinstance(fc_data, FrozenContext)
                            else FrozenContext.model_validate(fc_data, strict=False)
                        )
                        fc_updated = fc.model_copy(update={"mcp_tool_audit": audit_models})
                        data["frozen_context"] = fc_updated
                    else:
                        data["frozen_context"] = FrozenContext(mcp_tool_audit=audit_models)
            except Exception as e:
                msg = f"Failed to hydrate audit_trails for {doc_id}: {e}"
                logger.error("[ExecutionRepository] %s", msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.DATA_CORRUPTION.value},
                ) from e

    async def get_execution(self, execution_id: str, hydrate: bool = True) -> ExecutionRecord | None:
        """Retrieves an execution record by its ID.

        Args:
            execution_id: The unique identifier of the execution record.
            hydrate: Whether to hydrate offloaded blob payloads.

        Returns:
            The validated ExecutionRecord instance if found, otherwise None.

        Raises:
            AppException: If data corruption prevents parsing the record.
        """
        data = await self.driver.get("executions", execution_id)
        if data:
            try:
                if hydrate:
                    await self._hydrate_payloads(data)
                return ExecutionRecord.model_validate(data, strict=False)
            except AppException:
                raise
            except Exception as e:
                logger.error(
                    "[ExecutionRepository] %s: Data corruption - Failed to parse execution %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    execution_id,
                    e,
                    exc_info=True,
                )
                raise AppException(
                    message=f"Failed to parse execution {execution_id} from database",
                    status_code=500,
                    details={"error_code": ErrorCodes.DATA_CORRUPTION.value},
                ) from e
        return None

    async def get_execution_status(self, execution_id: str) -> str | None:
        """Retrieves the status of an execution.

        Args:
            execution_id: The ID of the execution.

        Returns:
            The execution status string if found, otherwise None.
        """
        data = await self.driver.get("executions", execution_id)
        return data["status"] if (data and "status" in data) else None

    async def create_execution(self, execution_data: dict[str, Any]) -> str:
        """Creates a new execution record.

        Args:
            execution_data: Dictionary containing execution fields.

        Returns:
            The created execution ID.
        """
        doc_id = execution_data["id"] if "id" in execution_data else str(uuid.uuid4())
        execution_data["id"] = doc_id
        await self._offload_payloads(doc_id, execution_data)
        return await self.driver.upsert("executions", execution_data, doc_id)

    async def update_execution(self, execution_id: str, updates: dict[str, Any]) -> bool:
        """Updates an existing execution record.

        Args:
            execution_id: The ID of the execution to update.
            updates: Dictionary of fields to update.

        Returns:
            True if the update succeeded, False otherwise.
        """
        await self._offload_payloads(execution_id, updates)
        return await self.driver.update("executions", execution_id, updates)

    async def append_trace_event(self, execution_id: str, event_data: dict[str, Any]) -> bool:
        """Appends a trace event to the execution trace log.

        Args:
            execution_id: The ID of the execution.
            event_data: The TraceEvent dictionary to append.

        Returns:
            True if updated successfully, False if execution not found.

        Raises:
            AppException: If hydration or persistence fails.
        """
        data = await self.driver.get("executions", execution_id)
        if not data:
            return False

        try:
            await self._hydrate_payloads(data)
        except Exception as e:
            logger.error("[ExecutionRepository] Failed to hydrate during append: %s", e, exc_info=True)
            raise

        trace = data["execution_trace"] if "execution_trace" in data else []
        trace.append(event_data)

        return await self.update_execution(execution_id, {"execution_trace": trace})

    async def delete_execution(self, execution_id: str) -> bool:
        """Deletes an execution record by ID.

        Args:
            execution_id: The ID of the execution to delete.

        Returns:
            True if deleted, False otherwise.
        """
        return await self.driver.delete("executions", execution_id)

    async def get_all_executions(
        self, organization_id: str | None = None, user_id: str | None = None
    ) -> list[ExecutionRecord]:
        """Retrieves all executions matching optional organization or user filters.

        Args:
            organization_id: Optional organization filter.
            user_id: Optional user filter.

        Returns:
            List of validated ExecutionRecord instances.
        """
        filters = []
        if organization_id:
            filters.append(Filter("organization_id", "==", organization_id))
        if user_id:
            filters.append(Filter("user_id", "==", user_id))

        results = await self.driver.query("executions", filters)

        parsed_results = []
        for r in results:
            try:
                parsed_results.append(ExecutionRecord.model_validate(r, strict=False))
            except Exception as e:
                item_id = r["id"] if "id" in r else "unknown"
                logger.error(
                    "[ExecutionRepository] %s: Skipping corrupted execution %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    item_id,
                    e,
                    exc_info=True,
                )
                raise AppException(
                    message=f"Corrupted execution {item_id} in database",
                    status_code=500,
                    details={"error_code": ErrorCodes.DATA_CORRUPTION.value},
                ) from e
        return parsed_results

    async def get_recent_completed_executions(self, limit: int = 5) -> list[ExecutionRecord]:
        """Retrieves recent completed executions ordered by completed_at descending.

        Args:
            limit: Maximum number of records to return.

        Returns:
            List of validated ExecutionRecord instances.
        """
        filters = [Filter("status", "==", "completed")]
        results = await self.driver.query(
            "executions", filters=filters, limit=limit, order_by="completed_at", descending=True
        )

        parsed_results = []
        for r in results:
            try:
                parsed_results.append(ExecutionRecord.model_validate(r, strict=False))
            except Exception as e:
                item_id = r["id"] if "id" in r else "unknown"
                logger.error(
                    "[ExecutionRepository] %s: Skipping corrupted execution %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    item_id,
                    e,
                    exc_info=True,
                )
                raise AppException(
                    message=f"Corrupted execution {item_id} in database",
                    status_code=500,
                    details={"error_code": ErrorCodes.DATA_CORRUPTION.value},
                ) from e
        return parsed_results

    async def count_executions_by_matrix(self, matrix_id: str) -> int:
        """Counts executions associated with a specific matrix ID.

        Args:
            matrix_id: The matrix ID to count executions for.

        Returns:
            The total count of matching executions.
        """
        return await self.driver.count("executions", [Filter("settings.matrix_id", "==", matrix_id)])
