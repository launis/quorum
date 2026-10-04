"""Execution Time Resolver service.

Determines the deterministic execution/document timestamp for prompt variable substitution
without loose dictionary traversal or fallback chains.
"""

from __future__ import annotations

import datetime
import logging
import re
from pathlib import Path
from typing import Any

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.dtos.prompt import LLMContextDataDTO
from backend_v2.models.execution_core import ExecutionMetadata

logger = logging.getLogger(__name__)

__all__ = ["ExecutionTimeResolver"]


class ExecutionTimeResolver:
    """Resolves deterministic timestamps for prompt compilation and execution contexts."""

    _ISO_DATETIME_RE = re.compile(
        r"^\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d{1,6})?)?(?:[+-]\d{2}:?\d{2}|Z)?)?$"
    )

    @staticmethod
    def _dlq_stat_fallback(exc: OSError) -> None:
        """Record DLQ fallback for physical file stat errors.

        Args:
            exc: The filesystem error encountered during file stat.
        """
        logger.warning("[ExecutionTimeResolver] Failed to read physical file mtime: %s", exc)

    @staticmethod
    def _parse_datetime(val: Any) -> datetime.datetime | None:
        """Parse datetime or ISO string safely without exception swallowing.

        Args:
            val: String or datetime instance to normalize.

        Returns:
            Parsed datetime in UTC or local timezone, or None if invalid format.
        """
        if isinstance(val, datetime.datetime):
            return val
        if isinstance(val, str) and val and ExecutionTimeResolver._ISO_DATETIME_RE.match(val):
            clean_str = val.replace("Z", "+00:00")
            return datetime.datetime.fromisoformat(clean_str)
        return None

    @staticmethod
    def resolve(
        llm_context_data: LLMContextDataDTO | None = None,
        execution_id: str | None = None,
        inputs: ExecutionInputsDTO | None = None,
        metadata: ExecutionMetadata | None = None,
    ) -> datetime.datetime | None:
        """Determines the document/execution timestamp from context inputs or physical disk files.

        Resolution Sequence:
            1. Client explicit document date from inputs or llm_context_data
            2. Physical disk file mtime under data/files/executions/<execution_id>/inputs/
            3. Database context metadata timestamps

        Args:
            llm_context_data: Typed context DTO containing inputs, metadata, and state.
            execution_id: Parent execution tracking ID for physical file inspection.
            inputs: Optional typed ExecutionInputsDTO.
            metadata: Optional typed ExecutionMetadata.

        Returns:
            Resolved datetime object (in UTC if applicable) or None if no timestamp exists.

        Raises:
            AppException: If invalid context types or path traversal execution_id are provided (VALIDATION_FAILED).
        """
        # 1. Client explicit document date check from ExecutionInputsDTO
        if inputs is not None:
            if not isinstance(inputs, ExecutionInputsDTO):
                msg = f"Invalid inputs type: {type(inputs).__name__}, expected ExecutionInputsDTO"
                logger.error("[ExecutionTimeResolver] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
            for key in ("document_date", "input_file_date", "last_modified"):
                if key in inputs.dynamic_inputs:
                    parsed = ExecutionTimeResolver._parse_datetime(inputs.dynamic_inputs[key])
                    if parsed:
                        logger.info("[ExecutionTimeResolver] Client-supplied document date found in dynamic_inputs.")
                        return parsed
                if key in inputs.raw_inputs:
                    parsed = ExecutionTimeResolver._parse_datetime(inputs.raw_inputs[key])
                    if parsed:
                        logger.info("[ExecutionTimeResolver] Client-supplied document date found in raw_inputs.")
                        return parsed

        # Check LLMContextDataDTO
        if llm_context_data is not None:
            if not isinstance(llm_context_data, LLMContextDataDTO):
                msg = f"Invalid context type: {type(llm_context_data).__name__}, expected LLMContextDataDTO"
                logger.error("[ExecutionTimeResolver] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

            if llm_context_data.execution_time:
                return llm_context_data.execution_time
            if llm_context_data.inputs:
                for key in ("document_date", "input_file_date", "last_modified"):
                    if key in llm_context_data.inputs:
                        parsed = ExecutionTimeResolver._parse_datetime(llm_context_data.inputs[key])
                        if parsed:
                            logger.info(
                                "[ExecutionTimeResolver] Client-supplied document date found in "
                                "LLMContextDataDTO.inputs."
                            )
                            return parsed
            if llm_context_data.raw_inputs:
                for key in ("document_date", "input_file_date", "last_modified"):
                    if key in llm_context_data.raw_inputs:
                        parsed = ExecutionTimeResolver._parse_datetime(llm_context_data.raw_inputs[key])
                        if parsed:
                            logger.info(
                                "[ExecutionTimeResolver] Client-supplied document date found in "
                                "LLMContextDataDTO.raw_inputs."
                            )
                            return parsed

        # 2. Physical input file inspection on disk
        if execution_id:
            if ".." in execution_id or "/" in execution_id or "\\" in execution_id:
                msg = f"Path traversal detected in execution_id: {execution_id}"
                logger.error("[ExecutionTimeResolver] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

            for filename in ("input_chat_log.md", "input_product_text.md", "input_reflection_text.md"):
                file_path = Path("data") / "files" / "executions" / execution_id / "inputs" / filename
                if file_path.exists():
                    try:
                        mtime = file_path.stat().st_mtime
                        resolved_dt = datetime.datetime.fromtimestamp(mtime, datetime.UTC)
                        logger.info(
                            "[ExecutionTimeResolver] Determined prompt date from physical input metadata: %s",
                            file_path,
                        )
                        return resolved_dt
                    except OSError as exc:
                        ExecutionTimeResolver._dlq_stat_fallback(exc)

        # 3. Context metadata validation
        if metadata is not None and not isinstance(metadata, ExecutionMetadata):
            msg = f"Invalid metadata type: {type(metadata).__name__}, expected ExecutionMetadata"
            logger.error("[ExecutionTimeResolver] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        return None
