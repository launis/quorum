"""Pre-flight DAG compilation and topological validation service for workflows.

Statically verifies Directed Acyclic Graph (DAG) topology, cycle freedom, and
forward variable reference resolution across workflow steps before execution.
"""

import logging

from fastapi import status

from backend_v2.exceptions import AppException, ErrorCodes, WorkflowCompilationError
from backend_v2.models.domain.step import StepRule
from backend_v2.models.domain.workflow import Workflow

logger = logging.getLogger(__name__)

__all__ = ["DAGCompilerService"]

_ALLOWED_GLOBAL_STEP_REFS: frozenset[str] = frozenset({"$steps", "$steps.matrix_reducer"})


class DAGCompilerService:
    """Pre-Flight Validation Engine for Workflow Graphs (The Shift-Left Strategy).

    Verifies Directed Acyclic Graph topology and forward-variable-reference safety
    statically during save time to prevent late-stage execution deadlocks causing API cost waste.
    """

    @staticmethod
    def validate_workflow(workflow: Workflow) -> None:
        """Runs the complete Pre-Flight validation suite on a Workflow definition.

        Args:
            workflow: The Pydantic Workflow model to validate.

        Raises:
            AppException: If expected_inputs are defined without at least one required input (VALIDATION_FAILED).
            WorkflowCompilationError: On cyclic dependency, dangling reference, or topological failure
                (WORKFLOW_COMPILATION_ERROR).
        """
        if workflow.expected_inputs and not any(inp.required for inp in workflow.expected_inputs):
            msg = (
                f"Workflow '{workflow.id}' is invalid: if 'expected_inputs' are defined, "
                "at least one input must be 'required=True'."
            )
            logger.error(
                "[DAGCompiler] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        DAGCompilerService._ensure_acyclic(workflow.steps)

        available_keys = {f"$inputs.{inp.input_key}" for inp in workflow.expected_inputs}
        ordered_steps = DAGCompilerService._get_topological_order(workflow.steps)

        for step in ordered_steps:
            for ref_str in step.extract_variable_references():
                DAGCompilerService._validate_step_reference(
                    step=step,
                    ref_str=ref_str,
                    available_keys=available_keys,
                )
            available_keys.add(f"$steps.{step.id}")

    @staticmethod
    def _validate_step_reference(step: StepRule, ref_str: str, available_keys: set[str]) -> None:
        """Validates a single variable reference from a step against currently available keys.

        Args:
            step: The workflow step containing the variable reference.
            ref_str: The raw variable reference string from step input mappings.
            available_keys: Set of currently resolved input and upstream step keys.

        Raises:
            WorkflowCompilationError: If an input or upstream step reference cannot be resolved
                (WORKFLOW_COMPILATION_ERROR).
        """
        root_namespace = DAGCompilerService._extract_root_namespace(ref_str)
        namespace_prefix = root_namespace.split(".", maxsplit=1)[0]

        if namespace_prefix == "$inputs":
            if root_namespace not in available_keys:
                msg = (
                    f"Step '{step.id}' references unknown or generic input '{root_namespace}'. "
                    f"Available inputs dynamically defined: {sorted(available_keys)}"
                )
                logger.error(
                    "[DAGCompiler] %s: %s",
                    ErrorCodes.WORKFLOW_COMPILATION_ERROR.name,
                    msg,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.WORKFLOW_COMPILATION_ERROR.value},
                )
                raise WorkflowCompilationError(step_id=step.id, message=msg)
        elif namespace_prefix == "$steps":
            if root_namespace in _ALLOWED_GLOBAL_STEP_REFS:
                return

            if root_namespace not in available_keys:
                msg = (
                    f"Step '{step.id}' references unexecuted or missing step '{root_namespace}'. "
                    "Ensure forward topological dependencies are enforced in depends_on."
                )
                logger.error(
                    "[DAGCompiler] %s: %s",
                    ErrorCodes.WORKFLOW_COMPILATION_ERROR.name,
                    msg,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.WORKFLOW_COMPILATION_ERROR.value},
                )
                raise WorkflowCompilationError(step_id=step.id, message=msg)

    @staticmethod
    def _extract_root_namespace(ref_str: str) -> str:
        """Parses variable paths to their verifiable origin node.

        Args:
            ref_str: The full reference string from step input mappings.

        Returns:
            The root node dependency path.
        """
        parts = ref_str.split(".")
        if len(parts) >= 2 and parts[0] == "$steps":
            return f"$steps.{parts[1]}"
        if len(parts) >= 2 and parts[0] == "$inputs":
            return f"$inputs.{parts[1]}"
        return parts[0]

    @staticmethod
    def _ensure_acyclic(steps: list[StepRule]) -> None:
        """Analyzes the graph for infinite loops and cycles using depth-first search.

        Args:
            steps: The list of workflow steps to analyze.

        Raises:
            WorkflowCompilationError: If a cyclic dependency is detected (WORKFLOW_COMPILATION_ERROR).
        """
        adj_list = {step.id: step.depends_on for step in steps}
        visited: set[str] = set()
        rec_stack: set[str] = set()

        def is_cyclic(node: str) -> bool:
            """Recursively traverses the adjacency list to detect back-edges.

            Args:
                node: The step ID currently being visited.

            Returns:
                True if a cycle is reachable from the given node, otherwise False.
            """
            visited.add(node)
            rec_stack.add(node)

            if node in adj_list:
                for neighbor in adj_list[node]:
                    if neighbor not in visited:
                        if is_cyclic(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        return True

            rec_stack.remove(node)
            return False

        for step in steps:
            if step.id not in visited and is_cyclic(step.id):
                msg = f"Cyclic dependency (Infinite Loop) detected involving step: '{step.id}'"
                logger.error(
                    "[DAGCompiler] %s: %s",
                    ErrorCodes.WORKFLOW_COMPILATION_ERROR.name,
                    msg,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.WORKFLOW_COMPILATION_ERROR.value},
                )
                raise WorkflowCompilationError(step_id=step.id, message=msg)

    @staticmethod
    def compute_topological_waves(steps: list[StepRule]) -> list[list[StepRule]]:
        """Computes Kahn's topological waves for workflow steps.

        Args:
            steps: The list of workflow steps to partition into concurrent waves.

        Returns:
            The ordered list of waves, where each wave is a list of steps that
            can be safely executed concurrently.

        Raises:
            WorkflowCompilationError: If a declared dependency does not exist in the workflow
                (WORKFLOW_COMPILATION_ERROR).
        """
        step_map = {step.id: step for step in steps}
        in_degree = {step.id: 0 for step in steps}
        adj_list: dict[str, list[str]] = {step.id: [] for step in steps}

        for step in steps:
            for dep_id in step.depends_on:
                if dep_id in adj_list:
                    adj_list[dep_id].append(step.id)
                    in_degree[step.id] += 1
                else:
                    msg = f"Step '{step.id}' declares dependency on '{dep_id}' which does not exist in the workflow."
                    logger.error(
                        "[DAGCompiler] %s: %s",
                        ErrorCodes.WORKFLOW_COMPILATION_ERROR.name,
                        msg,
                        exc_info=True,
                        extra={"error_code": ErrorCodes.WORKFLOW_COMPILATION_ERROR.value},
                    )
                    raise WorkflowCompilationError(step_id=step.id, message=msg)

        current_wave_ids = [step_id for step_id, degree in in_degree.items() if degree == 0]
        waves: list[list[StepRule]] = []

        while current_wave_ids:
            waves.append([step_map[s_id] for s_id in current_wave_ids])
            next_wave_ids: list[str] = []
            for s_id in current_wave_ids:
                for neighbor in adj_list[s_id]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        next_wave_ids.append(neighbor)
            current_wave_ids = next_wave_ids

        return waves

    @staticmethod
    def _get_topological_order(steps: list[StepRule]) -> list[StepRule]:
        """Returns the DAG steps sorted topologically.

        Since _ensure_acyclic guarantees no cycles, this Kahn's iteration always cleanly drains.

        Args:
            steps: The list of workflow steps to sort.

        Returns:
            The topologically sorted list of steps.

        Raises:
            WorkflowCompilationError: If a declared dependency does not exist in the workflow
                (WORKFLOW_COMPILATION_ERROR).
        """
        waves = DAGCompilerService.compute_topological_waves(steps)
        return [step for wave in waves for step in wave]
