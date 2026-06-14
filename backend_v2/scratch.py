"""Development scratchpad for direct execution querying."""

import json
import logging

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.v2_core import ExecutionRecord

logger = logging.getLogger(__name__)


def main() -> None:
    """Main execution block for querying execution trace.

    Raises:
        AppException: If the file reading or JSON parsing fails.
    """
    try:
        with open("data/db_v2.json", encoding="utf-8") as f:
            db_data = json.load(f)

        if not isinstance(db_data, dict):
            raise ValueError("Root element is not a dictionary.")

        executions = db_data.get("executions", {})
        if not isinstance(executions, dict):
            executions = {}

        exe_id = "exe_7330f7fdf4eb402f9e6fa919f168299c"
        if exe_id in executions:
            exe_dict = executions[exe_id]
            # Enforce Fail-Fast Hydration Mandate (Rule 3)
            exe = ExecutionRecord.model_validate(exe_dict, strict=False)
            print("Execution found!")

            for trace in exe.execution_trace:
                if trace.event_type == "output":
                    # Accessing Pydantic properties
                    content = trace.content
                    if isinstance(content, dict):
                        print(
                            f"Step: {trace.step_name} - Score: {content.get('score')} - Reasoning: {str(content.get('reasoning'))[:200]}"
                        )

            print("Syntheses:")
            if exe.profile_syntheses:
                for k, v in exe.profile_syntheses.items():
                    print(f"Synthesis {k}: {str(v)[:500]}")
        else:
            print("Execution not found in local db.")
    except Exception as e:
        logger.error(
            "Scratchpad failed: %s",
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.UNKNOWN_ERROR.value},
        )
        raise AppException(
            message=f"Scratchpad failed: {e}",
            status_code=500,
            details={"error_code": ErrorCodes.UNKNOWN_ERROR.value},
        ) from e


if __name__ == "__main__":
    main()
