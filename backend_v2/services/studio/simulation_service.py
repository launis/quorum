"""Studio Simulation Service."""

from __future__ import annotations

import logging
import string
from typing import Any

from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.auth import TokenData
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PersonaPromptBlock,
    PromptBlock,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.dtos.prompt_context import PromptContextDTO
from backend_v2.models.dtos.studio import (
    PromptBlockSimulationResponse,
    StepSimulationResponse,
    WorkflowSimulationResponse,
)
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.v2_core import (
    Step,
    Workflow,
)
from backend_v2.services.studio.prompt_block_service import StudioPromptBlockService

logger = logging.getLogger(__name__)

__all__ = ["StudioSimulationService"]


class StudioSimulationService:
    """Domain Service for simulating Admin Studio configurations."""

    def __init__(
        self,
        prompt_block_service: StudioPromptBlockService,
    ):
        """Initialize the simulation service.

        Args:
            prompt_block_service: Studio prompt block service.
        """
        self.prompt_block_service = prompt_block_service

    async def simulate_workflow(self, initiator: TokenData, data: Workflow) -> WorkflowSimulationResponse:
        """Simulate workflow.

        Args:
            initiator: The authenticated user initiating the simulation.
            data: The workflow domain object to simulate.

        Returns:
            A WorkflowSimulationResponse model containing validation status, errors, and topological execution order.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
            AppException (ErrorCodes.AGENT_EXECUTION_CRITICAL): On core errors during simulation.
        """
        errors = []
        step_status = {}

        # 1. Map expected inputs
        available_inputs = [inp.input_key for inp in data.expected_inputs]

        # 2. Track provided outputs step by step
        _provided_outputs = set(available_inputs)

        # 3. Build Dependency Graph
        dag_order = []
        visited = set()
        in_progress = set()

        all_steps = {s.id: s for s in data.steps}

        def resolve_deps(step_id: str) -> None:
            """Resolve deps.

            Args:
                step_id: Parameter step_id.

            Raises:
                PermissionDeniedError: If tenant access is violated.
                ResourceNotFoundError: If the resource is missing.
                AppException: On other core errors.
            """
            if step_id in in_progress:
                errors.append(f"Cycle detected involving step {step_id}")
                return
            if step_id in visited:
                return

            in_progress.add(step_id)
            step = all_steps.get(step_id)
            if not step:
                # Missing reference in depends_on
                return

            for dep in step.depends_on:
                resolve_deps(dep)

            in_progress.remove(step_id)
            visited.add(step_id)
            dag_order.append(step_id)

        try:
            for s_id in all_steps:
                resolve_deps(s_id)
        except (AppException, ValueError, KeyError, RecursionError, RuntimeError) as e:
            logger.error(
                "[StudioSimulationService] %s: Simulation graph resolution failed (Initiator: %s, Workflow: %s): %s",
                ErrorCodes.AGENT_EXECUTION_CRITICAL.name,
                initiator.id,
                data.id,
                e,
            )
            errors.append("Fatal error resolving DAG structure.")

        # 4. Step-by-Step topological check
        for step_id in dag_order:
            step = all_steps[step_id]
            is_valid = True
            step_errors = []

            # Check mappings
            for _tgt, src in step.input_mappings.items():
                if isinstance(src, str) and src.startswith("$"):
                    if src.startswith("$inputs."):
                        var = src.split(".")[1]
                        if var not in available_inputs:
                            step_errors.append(f"Missing input reference: {var}")
                            is_valid = False
                    elif src.startswith("$steps."):
                        parts = src.split(".")
                        if len(parts) >= 3:
                            dep_step = parts[1]
                            if dep_step not in step.depends_on:
                                step_errors.append(f"Undeclared dependency on step: {dep_step}")
                                is_valid = False

            if is_valid:
                step_status[step_id] = "OK"
            else:
                step_status[step_id] = "ERROR"
                errors.extend([f"Step {step_id}: {e}" for e in step_errors])

        return WorkflowSimulationResponse(
            valid=len(errors) == 0,
            errors=errors,
            step_status=step_status,
            execution_order=dag_order,
            trace={},
        )

    async def simulate_prompt_block(
        self, initiator: TokenData, data: PromptBlock, mock_inputs: dict[str, Any]
    ) -> PromptBlockSimulationResponse:
        """Simulate prompt block.

        Args:
            initiator: The authenticated user initiating the simulation.
            data: The prompt block domain object.
            mock_inputs: A dictionary of mocked string inputs for dry-run rendering.

        Returns:
            A PromptBlockSimulationResponse model containing the simulated render context and any evaluation errors.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
            AppException (ErrorCodes.AGENT_EXECUTION_CRITICAL): On core errors during simulation.
        """
        errors: list[str] = []
        rendered = ""

        # Extract base instruction text polymorphically
        match data:
            case MatrixPromptBlock():
                rendered = data.ai_description or ""
            case SystemRulePromptBlock():
                rendered = data.instruction_text or data.ai_description or ""
            case PersonaPromptBlock():
                rendered = data.role_enforcement or data.ai_description or ""
            case ProtocolPromptBlock():
                rendered = data.protocol_instructions or data.ai_description or ""

        # 1. Base rendering using template syntax if needed
        if rendered and mock_inputs:
            # Basic python formatting simulation if {} brackets exist
            if "{" in rendered and "}" in rendered:
                # Very simple loose formatting for dry-run safely
                t = string.Formatter()
                keys = [k[1] for k in t.parse(rendered) if k[1] is not None]
                clean_mocks = {k: mock_inputs[k] if k in mock_inputs else f"[{k} MOCKED]" for k in keys}
                rendered = rendered.format(**clean_mocks)

        # 2. Append Matrix Logic
        if isinstance(data, MatrixPromptBlock) and data.scales:
            rendered += "\n\n--- EVALUATION SCALES ---\n"
            for scale in data.scales:
                rendered += f"\nScore {scale.score}:\n"
                for claim in scale.claims:
                    en_text = claim.label.resolve("en")
                    if en_text:
                        rendered += f"- {en_text.strip()}\n"
                    for tda in claim.tda_assertions:
                        if tda.concept_description:
                            rendered += f"  Rule: {tda.concept_description.strip()}\n"

        prompt_context = PromptContextDTO(
            static_messages=[LLMMessageDTO(role="system", content=rendered.strip())],
            dynamic_messages=[],
            metadata={"simulated_block": data.id},
        )

        return PromptBlockSimulationResponse(
            valid=len(errors) == 0,
            errors=errors,
            rendered_prompt=rendered.strip(),
            trace={},
            prompt_context=prompt_context,
        )

    async def simulate_step(
        self, initiator: TokenData, data: Step, mock_inputs: dict[str, Any]
    ) -> StepSimulationResponse:
        """Simulate step.

        Args:
            initiator: The authenticated user initiating the simulation.
            data: The step domain object to evaluate.
            mock_inputs: Mocked inputs to satisfy dependency variables.

        Returns:
            A StepSimulationResponse model containing the full context payload and step-specific simulation errors.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
            AppException (ErrorCodes.AGENT_EXECUTION_CRITICAL): On core errors during simulation.
        """
        errors = []
        rendered_parts = []

        # Resolve prompt blocks
        prompt_blocks_refs = []
        if data.role_block_id:
            prompt_blocks_refs.append(data.role_block_id)
        if data.extraction_protocol_block_id:
            prompt_blocks_refs.append(data.extraction_protocol_block_id)
        if data.criteria_block_ids:
            prompt_blocks_refs.extend(data.criteria_block_ids)

        prompt_context_msgs = []
        for block_ref in prompt_blocks_refs:
            try:
                block = await self.prompt_block_service.get_prompt_block(initiator, block_ref)
                sim = await self.simulate_prompt_block(initiator, block, mock_inputs)
                if not sim.valid:
                    errors.extend(sim.errors)

                rendered_parts.append(f"--- Prompt Block: {block.id} ---")
                rendered_parts.append(sim.rendered_prompt)
                if sim.prompt_context:
                    prompt_context_msgs.extend(sim.prompt_context.static_messages)
            except ResourceNotFoundError:
                errors.append(f"Missing referenced Prompt Block: {block_ref}")
                rendered_parts.append(f"--- Prompt Block: {block_ref} [NOT FOUND] ---")

        if data.hook:
            rendered_parts.append(f"\n[Execution Hook: {data.hook}]")

        step_context = PromptContextDTO(
            static_messages=prompt_context_msgs, dynamic_messages=[], metadata={"simulated_step": data.id}
        )

        return StepSimulationResponse(
            valid=len(errors) == 0,
            errors=errors,
            rendered_prompt="\n\n".join(rendered_parts),
            trace={},
            prompt_context=step_context,
        )
