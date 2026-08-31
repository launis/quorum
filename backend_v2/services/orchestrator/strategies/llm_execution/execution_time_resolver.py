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
        if llm_context_data:
            try:
                raw_inputs = llm_context_data.get("raw_inputs")
                dynamic_inputs = raw_inputs.get("dynamic_inputs") if raw_inputs else None
                if dynamic_inputs:
                    doc_date = None
                    for key in ("document_date", "input_file_date", "last_modified"):
                        val = dynamic_inputs.get(key)
                        if val:
                            doc_date = val
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
            except AttributeError, TypeError:
                pass

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
        if llm_context_data:
            try:
                metadata = llm_context_data.get("metadata")
                if metadata:
                    meta_dt = None
                    for key in ("created_at", "timestamp"):
                        val = metadata.get(key)
                        if val:
                            meta_dt = val
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
            except AttributeError, TypeError:
                pass

            try:
                raw_inputs = llm_context_data.get("raw_inputs")
                if raw_inputs:
                    raw_dt = raw_inputs.get("timestamp")
                    if not raw_dt:
                        raw_meta = raw_inputs.get("metadata")
                        if raw_meta:
                            raw_dt = raw_meta.get("timestamp")
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
            except AttributeError, TypeError:
                pass

            try:
                top_dt = None
                for key in ("created_at", "timestamp"):
                    val = llm_context_data.get(key)
                    if val:
                        top_dt = val
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
            except AttributeError, TypeError:
                pass

        return None
