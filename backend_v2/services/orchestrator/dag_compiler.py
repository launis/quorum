import logging

from backend_v2.exceptions import AppException, ErrorCodes, WorkflowCompilationError
from backend_v2.models.v2_core import StepRule, Workflow

logger = logging.getLogger(__name__)


class DAGCompilerService:
    """Pre-Flight Validation Engine for Workflow Graphs (The Shift-Left Strategy).

    Verifies Directed Acyclic Graph topology and forward-variable-reference safety
    statically during save time to prevent late-stage execution Deadlocks causing API cost waste.
    """

    @staticmethod
    def validate_workflow(workflow: Workflow) -> None:
        """Runs the complete Pre-Flight validation suite on a Workflow definition.

        Args:
            workflow: The Pydantic Workflow model to validate.

        Raises:
            WorkflowCompilationError: On cyclic dependency, dangling reference, or topological failure.
            AppException: For general architectural rule violations (e.g., no required inputs).
        """
        # 0. Fast Business Logic Validation (Migrated from Pydantic for speed)
        if workflow.expected_inputs:
            if not any(inp.required for inp in workflow.expected_inputs):
                msg = (
                    f"Workflow '{workflow.id}' is invalid: if 'expected_inputs' are defined, "
                    "at least one input must be 'required=True'."
                )
                logger.error("[DAGCompiler] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED}, status_code=400)

        # 1. Cycle Detection & Assurance
        DAGCompilerService._ensure_acyclic(workflow.steps)

        # 2. Topological Analysis & Reference Resolution
        available_keys = {f"$inputs.{inp.input_key}" for inp in workflow.expected_inputs}

        # We also have access to $global configurations if needed, but per Epic, Focus on $inputs and $steps.
        ordered_steps = DAGCompilerService._get_topological_order(workflow.steps)

        for step in ordered_steps:
            for ref_str in step.extract_variable_references():
                # Parse the root_key from the reference e.g., $inputs.doc_id -> $inputs.doc_id
                # Wait, if reference is $steps.step1_id.result, we just need to ensure step1_id ran before.
                root_namespace = DAGCompilerService._extract_root_namespace(ref_str)

                # Check $inputs
                if root_namespace.startswith("$inputs"):
                    # For $inputs, we check if the exact key "$inputs.doc_id" is declared,
                    # or if it's the generic "$inputs" namespace which is always allowed.
                    if root_namespace == "$inputs":
                        continue

                    if root_namespace not in available_keys:
                        raise WorkflowCompilationError(
                            step_id=step.id,
                            message=f"Step '{step.id}' references unknown input '{root_namespace}'. "
                            f"Available inputs dynamically defined: {available_keys}",
                        )
                # Check $steps
                elif root_namespace.startswith("$steps"):
                    if root_namespace == "$steps":
                        continue

                    if root_namespace not in available_keys:
                        raise WorkflowCompilationError(
                            step_id=step.id,
                            message=f"Step '{step.id}' references unexecuted or missing step '{root_namespace}'. "
                            f"Ensure forward topological dependencies are enforced in depends_on.",
                        )

            # After step simulates successfully, it becomes available to downstream nodes
            available_keys.add(f"$steps.{step.id}")

    @staticmethod
    def _extract_root_namespace(ref_str: str) -> str:
        """Parses variable paths to their verifiable origin node.

        E.g. '$inputs.user_id' -> '$inputs.user_id'
        E.g. '$steps.my_step.output.result' -> '$steps.my_step'
        """
        parts = ref_str.split(".")
        if len(parts) >= 2 and parts[0] == "$steps":
            return f"$steps.{parts[1]}"
        if len(parts) >= 2 and parts[0] == "$inputs":
            # For inputs, we must usually require the specific key, e.g. $inputs.doc_id
            return f"$inputs.{parts[1]}"
        # If it's just raw "$inputs"
        return parts[0]

    @staticmethod
    def _ensure_acyclic(steps: list[StepRule]) -> None:
        """Analyzes the graph for Infinite Loops / Cycles using DFS."""
        adj_list = {step.id: step.depends_on for step in steps}
        visited = set()
        rec_stack = set()

        def is_cyclic(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in adj_list.get(node, []):
                if neighbor not in visited:
                    if is_cyclic(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for step in steps:
            if step.id not in visited:
                if is_cyclic(step.id):
                    # We found a loop!
                    raise WorkflowCompilationError(
                        step_id=step.id,
                        message=f"Cyclic dependency (Infinite Loop) detected involving step: '{step.id}'",
                    )

    @staticmethod
    def _get_topological_order(steps: list[StepRule]) -> list[StepRule]:
        """Returns the DAG Steps sorted topologically.

        Since _ensure_acyclic guarantees no cycles, this Kahn's iteration will always cleanly drain.
        """
        step_map = {step.id: step for step in steps}
        in_degree = {step.id: 0 for step in steps}
        adj_list: dict[str, list[str]] = {step.id: [] for step in steps}

        # Build graphs
        for step in steps:
            for dep_id in step.depends_on:
                if dep_id in adj_list:
                    adj_list[dep_id].append(step.id)
                    in_degree[step.id] += 1
                else:
                    # Depends on a step that doesn't exist? That's a syntax error.
                    raise WorkflowCompilationError(
                        step_id=step.id,
                        message=(
                            f"Step '{step.id}' declares dependency on '{dep_id}' which does not exist in the workflow."
                        ),
                    )

        # Start queue with nodes having no dependencies
        queue = [step_id for step_id, degree in in_degree.items() if degree == 0]
        ordered_ids = []

        while queue:
            current = queue.pop(0)
            ordered_ids.append(current)

            for neighbor in adj_list[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Return them ordered
        return [step_map[step_id] for step_id in ordered_ids]
