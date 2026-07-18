"""Pre-Hydrated Synthesis Strategy.

Executes the final Synthesis step by relying on pre-extracted Atoms rather than
large document bodies, minimizing Context Window and avoiding Attention Dilution.
"""

import asyncio
import logging

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.blackboard import GlobalAtomBlackboard
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.models.state import StateProjector, TraceEvent
from backend_v2.models.v2_core import FrozenContext, PromptBlock, StepRule
from backend_v2.models.v2_core import Step as V2Step
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.strategies.base import NodeStrategy, StrategyContext
from backend_v2.utils.alias_engine import AliasEngine

logger = logging.getLogger(__name__)


class PreHydratedSynthesisStrategy(NodeStrategy):
    """Executes the pre-hydrated synthesis workflow for Epic 101."""

    async def execute(
        self,
        step: StepRule,
        projector: StateProjector,
        context: StrategyContext,
        frozen_ctx: FrozenContext | None,
        trace: list[TraceEvent] | None,
        semaphore: asyncio.Semaphore,
        running_event: asyncio.Event | None = None,
    ) -> list[TraceEvent]:
        # Epic 101: Rule 1 - Extract Blackboard (Dependency Fail-Fast)
        raw_blackboard = context.context_variables.get("__GLOBAL_ATOM_BLACKBOARD__")
        if raw_blackboard is None:
            logger.error(
                "preflight_blackboard_missing",
                extra={"execution_id": context.execution_id, "step_id": step.id},
            )
            raise AppException(
                status_code=500,
                message="__GLOBAL_ATOM_BLACKBOARD__ missing from context_variables",
                details={"error_code": "DEPENDENCY_ERROR"},
            )

        blackboard = GlobalAtomBlackboard.model_validate(raw_blackboard)
        all_atom_ids = blackboard.get_all_atom_ids()

        blueprint_id = step.task_blueprint
        if not blueprint_id:
            raise AppException(
                message=f"Step {step.id} has no task_blueprint configured.",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        step_def_raw = await self.workflow_repo.get_step_by_id(blueprint_id)
        step_obj = V2Step.model_validate(step_def_raw)

        # Build Criteria Blocks
        all_blocks_raw = await self.prompt_block_repo.get_all_prompt_blocks()
        block_map = {b["id"]: PromptBlock.model_validate(b) for b in all_blocks_raw if "id" in b}

        criteria_blocks: list[PromptBlock] = []
        for m_id in step_obj.criteria_block_ids:
            if m_id in block_map:
                criteria_blocks.append(block_map[m_id])
            else:
                raise AppException(
                    message=f"Criteria PromptBlock '{m_id}' not found.",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

        target_locale = str(context.metadata.get("target_locale", "en"))

        # Epic 101: Rule 3 - Schema Acquisition
        # We assume doc_ids from projector are the original input keys
        doc_aliases = list(blackboard.atoms_by_input.keys())

        DynamicSchema = self.compiler.build_dynamic_schema(
            schema_name=f"Step_{step.id}_Response",
            criteria=criteria_blocks,
            has_shuffled_atoms=False,  # Synthesis evaluates atoms at the global matrix/criteria level, not shuffled array
            target_locale=target_locale,
            strictness_level=context.strictness_level,
            source_document_ids=doc_aliases,
            allowed_atom_ids=all_atom_ids,
        )

        # Epic 101: Rule 2 - Dual-Input Context
        static_instructions = self.compiler.compile_static_instructions(criteria_blocks, target_locale)
        static_msg = {"role": "system", "content": static_instructions}

        user_content = (
            "Synthesize the following atoms according to the instructions:\n"
            "<user_payload>\n"
            f"{blackboard.to_markdown_synthesis_injection()}\n"
            "</user_payload>"
        )
        dynamic_msg = {"role": "user", "content": user_content}

        compiled_prompt = CompiledPrompt(
            static_messages=[static_msg],
            dynamic_messages=[dynamic_msg],
        )

        # Epic 101: Rule 4 - Execution Delegation
        client = await LLMClient.from_strategy("reasoning", self.system_repo, pipeline_name="synthesis")
        llm_executor = LLMTaskExecutor(self.compiler)

        validated_model, usage = await llm_executor.execute_structured_task(
            client=client,
            messages=compiled_prompt,
            response_model=DynamicSchema,
            validation_context={"strictness_level": context.strictness_level},
        )

        output_dict = validated_model.model_dump()

        # Epic 101: Rule 5 - Alias Hydration and Filtering
        # Populate alias map with atoms mapping to themselves for identity verification
        alias_engine = AliasEngine()
        for atom_id in all_atom_ids:
            alias_engine.alias_map[atom_id] = atom_id
        for doc_id in doc_aliases:
            alias_engine.alias_map[doc_id] = doc_id

        # Hydrate and strictly DROP hallucinated opaque UUIDs
        alias_engine.hydrate_and_filter_aliases(output_dict, {"atom_id", "source_id"})

        # Final serialization for TraceEvent
        if usage.total_tokens > 0 or usage.cost_usd > 0.0:
            output_dict.setdefault("_step_metadata", {})
            output_dict["_step_metadata"]["token_usage"] = usage.model_dump()
            output_dict["_step_metadata"]["model_strategy"] = "reasoning"

        return [
            TraceEvent(
                step_name=step.id,
                event_type="output",
                content=output_dict,
            )
        ]
