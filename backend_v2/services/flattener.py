"""Service for flattening complex execution DAG results into a flat file format (e.g. CSV-compatible dict).

Adheres to V2 Architecture:
- Flattens nested 'results' dictionaries.
- Uses `[step_id]_[key]` naming convention to guarantee uniquely identifiable global columns.
- Prevents deep nesting hiding crucial data for data analysts.
"""

import json
from typing import Any

from backend_v2.models.state import StateProjector, StepOutputDTO
from backend_v2.models.v2_core import ExecutionRecord


class FlatFileService:
    """Service to flatten nested ExecutionRecord results."""

    @staticmethod
    def flatten_results(execution: ExecutionRecord) -> dict[str, Any]:
        """Flattens the DAG results dictionary into a single-level dictionary.

        Rule: [step_id]_[key] = value.
        If a result does not stem from a step specifically but exists at the root,
        it defaults to just [key] = value.

        Args:
            execution: The ExecutionRecord to flatten.

        Returns:
            dict[str, Any]: A flat dictionary suitable for CSV serialization.
        """
        flat_record: dict[str, Any] = {
            "execution_id": execution.id,
            "workflow_id": execution.workflow_id,
            "status": execution.status.value,
        }

        projector = StateProjector()
        results: list[StepOutputDTO] = projector.fold_trace(execution.execution_trace)

        if not results:
            return flat_record

        # Epic 43 Phase 2: Iterating over strict StepOutputDTO list
        for dto in results:
            val = dto.payload
            if isinstance(val, (dict, list)):
                flat_record[f"{dto.step_id}_{dto.block_id}"] = json.dumps(val, ensure_ascii=False)
            else:
                flat_record[f"{dto.step_id}_{dto.block_id}"] = val

        return flat_record
