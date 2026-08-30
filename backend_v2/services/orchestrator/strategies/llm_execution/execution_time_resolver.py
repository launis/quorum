"""Execution Time Resolver service.

Determines the deterministic execution/document timestamp for prompt variable substitution
without loose dictionary traversal or fallback chains.
"""

import datetime
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["ExecutionTimeResolver"]


class ExecutionTimeResolver:
    """Resolves deterministic timestamps for prompt compilation and execution contexts."""

    @staticmethod
    def resolve(
        llm_context_data: dict[str, Any] | None = None,
        execution_id: str | None = None,
    ) -> datetime.datetime | None:
        """Determines the document/execution timestamp from context inputs or physical disk files.

        Resolution Sequence:
            1. Client explicit document date from raw_inputs.dynamic_inputs
            2. Physical disk file mtime under data/files/executions/<execution_id>/inputs/
            3. Database context metadata timestamps (metadata.created_at, raw_inputs.timestamp, created_at)

        Args:
            llm_context_data: Context dictionary containing inputs, metadata, and state.
            execution_id: Parent execution tracking ID for physical file inspection.

        Returns:
            Resolved datetime object (in UTC if applicable) or None if no timestamp exists.
        """
        # 1. Client dynamic inputs check
        if isinstance(llm_context_data, dict) and "raw_inputs" in llm_context_data:  # noqa: QGR012 [REASON: Polymorphic DAG payload validation]
            raw_inputs = llm_context_data["raw_inputs"]
            if isinstance(raw_inputs, dict) and "dynamic_inputs" in raw_inputs:  # noqa: QGR012 [REASON: Polymorphic DAG payload validation]
                dynamic_inputs = raw_inputs["dynamic_inputs"]
                if isinstance(dynamic_inputs, dict):  # noqa: QGR012 [REASON: Polymorphic DAG payload validation]
                    doc_date = None
                    for key in ("document_date", "input_file_date", "last_modified"):
                        if key in dynamic_inputs and dynamic_inputs[key]:
                            doc_date = dynamic_inputs[key]
                            break
                    if doc_date:
                        logger.info("[ExecutionTimeResolver] Client-supplied document date found.")
                        if isinstance(doc_date, datetime.datetime):
                            return doc_date
                        if isinstance(doc_date, str):
                            try:
                                clean_str = doc_date.replace("Z", "+00:00")
                                return datetime.datetime.fromisoformat(clean_str)
                            except ValueError:
                                logger.warning(
                                    "[ExecutionTimeResolver] Failed to parse client document_date '%s'.",
                                    doc_date,
                                )

        # 2. Physical input file inspection on disk
        if execution_id:
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
                        logger.warning(
                            "[ExecutionTimeResolver] Failed to read physical file mtime for %s: %s",
                            file_path,
                            str(exc),
                        )

        # 3. Context metadata timestamps
        if isinstance(llm_context_data, dict):  # noqa: QGR012 [REASON: Polymorphic DAG payload validation]
            if "metadata" in llm_context_data:
                metadata = llm_context_data["metadata"]
                if isinstance(metadata, dict):  # noqa: QGR012 [REASON: Polymorphic DAG payload validation]
                    meta_dt = None
                    for key in ("created_at", "timestamp"):
                        if key in metadata and metadata[key]:
                            meta_dt = metadata[key]
                            break
                    if meta_dt:
                        logger.info("[ExecutionTimeResolver] Using metadata timestamp.")
                        if isinstance(meta_dt, datetime.datetime):
                            return meta_dt
                        if isinstance(meta_dt, str):
                            try:
                                clean_str = meta_dt.replace("Z", "+00:00")
                                return datetime.datetime.fromisoformat(clean_str)
                            except ValueError:
                                pass

            if "raw_inputs" in llm_context_data:
                raw_inputs = llm_context_data["raw_inputs"]
                if isinstance(raw_inputs, dict):  # noqa: QGR012 [REASON: Polymorphic DAG payload validation]
                    raw_dt = raw_inputs["timestamp"] if "timestamp" in raw_inputs else None
                    if not raw_dt and "metadata" in raw_inputs and isinstance(raw_inputs["metadata"], dict):  # noqa: QGR012 [REASON: Polymorphic DAG payload validation]
                        raw_dt = raw_inputs["metadata"]["timestamp"] if "timestamp" in raw_inputs["metadata"] else None
                    if raw_dt:
                        logger.info("[ExecutionTimeResolver] Using raw_inputs timestamp.")
                        if isinstance(raw_dt, datetime.datetime):
                            return raw_dt
                        if isinstance(raw_dt, str):
                            try:
                                clean_str = raw_dt.replace("Z", "+00:00")
                                return datetime.datetime.fromisoformat(clean_str)
                            except ValueError:
                                pass

            top_dt = None
            for key in ("created_at", "timestamp"):
                if key in llm_context_data and llm_context_data[key]:
                    top_dt = llm_context_data[key]
                    break
            if top_dt:
                logger.info("[ExecutionTimeResolver] Using top-level context timestamp.")
                if isinstance(top_dt, datetime.datetime):
                    return top_dt
                if isinstance(top_dt, str):
                    try:
                        clean_str = top_dt.replace("Z", "+00:00")
                        return datetime.datetime.fromisoformat(clean_str)
                    except ValueError:
                        pass

        return None
