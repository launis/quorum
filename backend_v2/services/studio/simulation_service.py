"""Studio Simulation Service."""

from __future__ import annotations

import logging
import string
from typing import Any

from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.auth import TokenData
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PersonaPromptBlock,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.dtos.dag_models import ExtractedAtom, LinkedAtomGraph
from backend_v2.models.dtos.engine import FlattenedAtom, MatrixEvaluationContext
from backend_v2.models.dtos.prompt_context import PromptContextDTO
from backend_v2.models.dtos.studio import (
    PromptBlockSimulationRequest,
    PromptBlockSimulationResponse,
    StepSimulationResponse,
    StepSimulationTraceDTO,
    WorkflowSimulationResponse,
)
from backend_v2.models.enums import EntityPrefix
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.v2_core import (
    Step,
    Workflow,
)
from backend_v2.services.orchestrator.prompts.matrix_sensor_prompt_builder import MatrixSensorPromptBuilder
from backend_v2.services.studio.prompt_block_service import StudioPromptBlockService
from backend_v2.utils.alias_engine import AliasEngine

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
        self, initiator: TokenData, request: PromptBlockSimulationRequest
    ) -> PromptBlockSimulationResponse:
        """Simulate prompt block.

        Args:
            initiator: The authenticated user initiating the simulation.
            request: The prompt block simulation request DTO.

        Returns:
            A PromptBlockSimulationResponse model containing the simulated render context and any evaluation errors.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing or target score not found.
            AppException (ErrorCodes.VALIDATION_FAILED): If the prompt block or scales
                contain no valid claims or assertions.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
        """
        errors: list[str] = []

        if isinstance(request.block, MatrixPromptBlock):
            scales = list(request.block.scales)
            if request.target_scale_score is not None:
                scales = [s for s in scales if s.score == request.target_scale_score]
                if not scales:
                    msg = (
                        f"Scale with score {request.target_scale_score} not found in prompt block '{request.block.id}'."
                    )
                    logger.error("[StudioSimulation] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
                    raise AppException(
                        message=msg,
                        status_code=404,
                        details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
                    )

            has_assertions = any(claim.tda_assertions for scale in scales for claim in scale.claims)
            if not has_assertions:
                msg = f"Prompt block '{request.block.id}' scales contain zero claims or assertions to simulate."
                logger.error("[StudioSimulation] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg,
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

            flattened_atoms: list[FlattenedAtom] = []
            graph_nodes: list[LinkedAtomGraph] = []
            tda_id_to_alias: dict[str, str] = {}
            alias_engine = AliasEngine()
            seq_idx = 0

            for scale in scales:
                for claim in scale.claims:
                    claim_text = "[UNTITLED CLAIM]"
                    resolved_text = claim.label.resolve(request.target_locale)
                    if resolved_text:
                        claim_text = resolved_text

                    for tda in claim.tda_assertions:
                        synthetic_id = generate_opaque_id(EntityPrefix.TDA)
                        alias = alias_engine.register(synthetic_id, prefix="a")
                        tda_id_to_alias[synthetic_id] = alias

                        if tda.concept_description:
                            rule_text = tda.concept_description
                        elif tda.extraction_rule:
                            rule_text = tda.extraction_rule
                        else:
                            rule_text = "Extract evidence"

                        anchor_target = ""
                        if tda.anchor_target:
                            anchor_target = tda.anchor_target

                        flattened_atoms.append(
                            FlattenedAtom(
                                atom_id=synthetic_id,
                                question=claim_text,
                                extraction_rule=rule_text,
                                anchor_target=anchor_target,
                                is_inverse=tda.inverse_evidence,
                                depends_on=(),
                                contrastive_example=tda.contrastive_example,
                                acceptance_criteria=tuple(tda.acceptance_criteria),
                                anti_patterns=tuple(tda.anti_patterns),
                                syntactic_anchors=tuple(tda.syntactic_anchors),
                            )
                        )

                        graph_nodes.append(
                            LinkedAtomGraph(
                                atom=ExtractedAtom(
                                    reasoning="[SIMULATION]",
                                    resolved_claim=claim_text,
                                    is_logical_deduction=True,
                                    source_quote=None,
                                    tda_id=synthetic_id,
                                    source_sequence_index=seq_idx,
                                ),
                                depends_on=[],
                            )
                        )
                        seq_idx += 1

            matrix_context = MatrixEvaluationContext(
                matrix_assertions=flattened_atoms,
                matrix_objective=request.block.ai_description,
            )
            compiled_prompt = MatrixSensorPromptBuilder.build_compiled_prompt(
                context_text=request.context_text,
                nodes=graph_nodes,
                tda_id_to_alias=tda_id_to_alias,
                target_locale=request.target_locale,
                matrix_context=matrix_context,
            )

            prompt_context = PromptContextDTO(
                static_messages=compiled_prompt.static_messages,
                dynamic_messages=compiled_prompt.dynamic_messages,
                metadata={"simulated_block": request.block.id},
            )
            rendered_prompt = "\n\n".join(
                f"[{m.role.upper()}]\n{m.content}"
                for m in compiled_prompt.static_messages + compiled_prompt.dynamic_messages
            )

            return PromptBlockSimulationResponse(
                valid=True,
                errors=[],
                rendered_prompt=rendered_prompt,
                trace={},
                prompt_context=prompt_context,
            )

        rendered = ""

        # Extract base instruction text polymorphically
        match request.block:
            case SystemRulePromptBlock(instruction_text=text) if text:
                rendered = text
            case PersonaPromptBlock(role_enforcement=text) if text:
                rendered = text
            case ProtocolPromptBlock(protocol_instructions=text) if text:
                rendered = text

        # 1. Base rendering using template syntax if needed
        if rendered and request.mock_inputs:
            # Basic python formatting simulation if {} brackets exist
            if "{" in rendered and "}" in rendered:
                # Very simple loose formatting for dry-run safely
                t = string.Formatter()
                keys = [k[1] for k in t.parse(rendered) if k[1] is not None]
                clean_mocks = {k: request.mock_inputs[k] if k in request.mock_inputs else f"[{k} MOCKED]" for k in keys}
                rendered = rendered.format(**clean_mocks)

        prompt_context = PromptContextDTO(
            static_messages=[LLMMessageDTO(role="system", content=rendered.strip())],
            dynamic_messages=[],
            metadata={"simulated_block": request.block.id},
        )

        return PromptBlockSimulationResponse(
            valid=len(errors) == 0,
            errors=errors,
            rendered_prompt=rendered.strip(),
            trace={},
            prompt_context=prompt_context,
        )

    async def simulate_step(
        self,
        initiator: TokenData,
        data: Step,
        mock_inputs: dict[str, Any],
        target_locale: str = "en",
        context_text: str = "[SIMULATED CONTEXT DOCUMENT]",
    ) -> StepSimulationResponse:
        """Simulate step.

        Args:
            initiator: The authenticated user initiating the simulation.
            data: The step domain object to evaluate.
            mock_inputs: Mocked inputs to satisfy dependency variables.
            target_locale: Target locale for prompt compilation.
            context_text: Context document text for sensor simulation.

        Returns:
            A StepSimulationResponse model containing the full context payload and step-specific simulation errors.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
            AppException (ErrorCodes.AGENT_EXECUTION_CRITICAL): On core errors during simulation.
        """
        errors: list[str] = []
        rendered_parts: list[str] = []

        # Resolve prompt blocks in DAG execution order
        prompt_blocks_refs: list[str] = []
        if data.role_block_id:
            prompt_blocks_refs.append(data.role_block_id)
        if data.extraction_protocol_block_id:
            prompt_blocks_refs.append(data.extraction_protocol_block_id)
        if data.execution_persona_block_id:
            prompt_blocks_refs.append(data.execution_persona_block_id)
        if data.criteria_block_ids:
            prompt_blocks_refs.extend(data.criteria_block_ids)

        prompt_context_msgs: list[LLMMessageDTO] = []
        dynamic_messages_aggregated: list[LLMMessageDTO] = []
        for block_ref in prompt_blocks_refs:
            try:
                block = await self.prompt_block_service.get_prompt_block(initiator, block_ref)
                sim = await self.simulate_prompt_block(
                    initiator,
                    PromptBlockSimulationRequest(
                        block=block,
                        mock_inputs=mock_inputs,
                        target_locale=target_locale,
                        context_text=context_text,
                    ),
                )
                if not sim.valid:
                    errors.extend(sim.errors)

                rendered_parts.append(f"--- Prompt Block: {block.id} ---")
                rendered_parts.append(sim.rendered_prompt)
                if sim.prompt_context:
                    prompt_context_msgs.extend(sim.prompt_context.static_messages)
                    dynamic_messages_aggregated.extend(sim.prompt_context.dynamic_messages)
            except ResourceNotFoundError:
                errors.append(f"Missing referenced Prompt Block: {block_ref}")
                rendered_parts.append(f"--- Prompt Block: {block_ref} [NOT FOUND] ---")

        if data.hook:
            rendered_parts.append(f"\n[Execution Hook: {data.hook}]")

        step_context = PromptContextDTO(
            static_messages=prompt_context_msgs,
            dynamic_messages=dynamic_messages_aggregated,
            metadata={"simulated_step": data.id},
        )

        estimated_tokens = sum(
            len(m.content) // 4 for m in step_context.static_messages + step_context.dynamic_messages
        )

        return StepSimulationResponse(
            valid=len(errors) == 0,
            errors=errors,
            rendered_prompt="\n\n".join(rendered_parts),
            trace=StepSimulationTraceDTO(execution_time_ms=0.0, estimated_tokens=estimated_tokens),
            prompt_context=step_context,
        )
