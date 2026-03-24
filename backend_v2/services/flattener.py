"""Service for flattening complex execution DAG results into a flat file format (e.g. CSV-compatible dict).

Adheres to V2 Architecture:
- Flattens nested 'results' dictionaries.
- Uses `[step_id]_[slug]` naming convention to guarantee uniquely identifiable global columns.
- Prevents deep nesting hiding crucial data for data analysts.
"""

from typing import Any

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

        from backend_v2.models.state import StateProjector
        projector = StateProjector()
        results = projector.fold_trace(execution.execution_trace)

        if not results:
            return flat_record
            
        # Currently in V2, DAG Executor dumps step outputs under the 'results' dictionary
        # with keys usually corresponding to step_ids (e.g., 'results': {'step_judge': {...}}).
        for step_id, step_output in results.items():
            if isinstance(step_output, dict):
                # We prefix all keys inside this step output with the step_id
                for key, value in step_output.items():
                    # Check for further nesting (e.g., lists or deep objects).
                    # In a fully analytical view, we might flatten further or stringify.
                    # Stringifying objects for CSV safety:
                    if isinstance(value, (dict, list)):
                        flat_record[f"{step_id}_{key}"] = str(value)
                    else:
                        flat_record[f"{step_id}_{key}"] = value
            else:
                # If a result is a primitive at the root level of results
                flat_record[str(step_id)] = step_output

        return flat_record
