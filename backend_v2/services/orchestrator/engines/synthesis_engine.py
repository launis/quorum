"""Synthesis Execution Engine.

Implements the ExecutionEngine protocol for LLM-driven synthesis processing.
"""

import logging

from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.domain.blackboard import GlobalAtomBlackboard
from backend_v2.models.dtos.engine import EngineExecutionRequest, EngineExecutionResult
from backend_v2.models.state import TraceEvent
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.utils.alias_engine import AliasEngine

logger = logging.getLogger(__name__)


class SynthesisEngine:
    """Execution engine for LLM-driven synthesis.

    Generates unstructured text and schema-bound UI layouts (SDUI) using pre-compiled
    schema instructions and a static-first message injection strategy for optimal caching.
    """

    def __init__(self, llm_executor: LLMTaskExecutor) -> None:
        """Initializes the synthesis engine.

        Args:
            llm_executor: Service for executing structured LLM tasks.
        """
        self._executor = llm_executor

    async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:
        """Executes the synthesis generation pipeline.

        Args:
            request: The EngineExecutionRequest containing compiled schemas and context.

        Returns:
            EngineExecutionResult containing the generated output dict.

        Raises:
            AppException: If blackboard is missing, validation fails, or LLM errors occur.
        """
        # Epic 101: Rule 1 - Extract Blackboard (Dependency Fail-Fast)
        raw_blackboard = request.context.context_variables.get("__GLOBAL_ATOM_BLACKBOARD__")
        if raw_blackboard is None:
            logger.error(
                "preflight_blackboard_missing",
                extra={"execution_id": request.context.execution_id, "step_id": request.step.id},
            )
            raise AppException(
                status_code=500,
                message="__GLOBAL_ATOM_BLACKBOARD__ missing from context_variables",
                details={"error_code": "SYNTHESIS_ENGINE_ERROR"},
            )

        try:
            blackboard = GlobalAtomBlackboard.model_validate(raw_blackboard)
            all_atom_ids = blackboard.get_all_atom_ids()
            doc_aliases = list(blackboard.atoms_by_input.keys())

            # Epic 101: Rule 2 - Dual-Input Context
            # Use hydrated messages if provided by LLMNodeStrategy, otherwise crash fail-fast
            if request.hydrated_messages is None:
                raise ValueError("hydrated_messages must be provided for SynthesisEngine")

            local_messages = [dict(msg) for msg in request.hydrated_messages]

            matrix_reducer_output = request.context.context_variables.get("__MATRIX_REDUCER_OUTPUT__")
            raw_xai_extensions_str = ""
            if matrix_reducer_output and "raw_extensions" in matrix_reducer_output:
                import json

                extensions_json = json.dumps(matrix_reducer_output["raw_extensions"], indent=2)
                raw_xai_extensions_str = f"\n<raw_xai_extensions>\n{extensions_json}\n</raw_xai_extensions>"

            local_messages.append(
                {
                    "role": "user",
                    "content": (
                        "Synthesize the following atoms according to the instructions:\n"
                        "<user_payload>\n"
                        f"{blackboard.to_markdown_synthesis_injection()}\n"
                        "</user_payload>"
                        f"{raw_xai_extensions_str}"
                    ),
                }
            )

            logger.info("SynthesisEngine: Final hydrated message count: %d", len(local_messages))

            if request.compiled_schema is None:
                raise ValueError("compiled_schema must be provided for SynthesisEngine")

            if request.progress_callback:
                await request.progress_callback(10, 100)

            # Epic 101: Rule 4 - Execution Delegation
            async with request.semaphore:
                validated_model, usage = await self._executor.execute_structured_task(
                    client=request.bound_client,
                    messages=local_messages,
                    response_model=request.compiled_schema,
                    validation_context={"strictness_level": request.context.strictness_level},
                )

            if request.progress_callback:
                await request.progress_callback(90, 100)

            output_dict = validated_model.model_dump()

            # Epic 101: Rule 5 - Alias Hydration and Filtering
            alias_engine = AliasEngine()
            for atom_id in all_atom_ids:
                alias_engine.alias_map[atom_id] = atom_id
            for doc_id in doc_aliases:
                alias_engine.alias_map[doc_id] = doc_id

            # Hydrate and strictly DROP hallucinated opaque UUIDs
            alias_engine.hydrate_and_filter_aliases(output_dict, {"atom_id", "source_id"})

            trace_events: list[TraceEvent] = []
            if usage.total_tokens > 0 or usage.cost_usd > 0.0:
                output_dict.setdefault("_step_metadata", {})
                output_dict["_step_metadata"]["token_usage"] = usage.model_dump()
                output_dict["_step_metadata"]["model_strategy"] = "reasoning"

            trace_events.append(
                TraceEvent(
                    step_name=request.step.id,
                    event_type="output",
                    content=output_dict,
                )
            )

            return EngineExecutionResult(
                results=[],
                hydrated_references={},
                synthesis_output=output_dict,
                trace_events=trace_events,
            )

        except ValidationError as e:
            logger.error("SynthesisEngine validation failed", exc_info=True)
            raise AppException(
                status_code=500,
                message=f"Synthesis engine validation failed: {e}",
                details={"error_code": "SYNTHESIS_ENGINE_ERROR"},
            ) from e
        except Exception as e:
            logger.error("SynthesisEngine unexpected error", exc_info=True)
            if isinstance(e, AppException):
                raise
            raise AppException(
                status_code=500,
                message=f"Synthesis engine encountered an error: {e}",
                details={"error_code": "SYNTHESIS_ENGINE_ERROR"},
            ) from e
