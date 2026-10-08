"""Synthesis Execution Engine.

Implements the ExecutionEngine protocol for LLM-driven synthesis processing.
"""

from __future__ import annotations

import contextlib
import json
import logging
from enum import Enum
from typing import override

import opentelemetry.trace as trace
from pydantic import BaseModel, ValidationError

from backend_v2.core.telemetry import get_tracer
from backend_v2.core.template_processor import TemplateProcessor
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.atom_evaluation import LightweightMatrixDTO, RawXAIExtensionDTO
from backend_v2.models.dtos.base import DataStarvationEvent
from backend_v2.models.dtos.engine import EngineExecutionRequest, EngineExecutionResult
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.prompts.synthesis import SPARSE_DATA_SYNTHESIS_MANDATE
from backend_v2.models.state import TraceEvent
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.engines.base import ExecutionEngine
from backend_v2.settings import get_settings
from backend_v2.utils.alias_engine import AliasEngine

logger = logging.getLogger(__name__)

__all__ = ["SynthesisEngine"]


class SynthesisEngine(ExecutionEngine):
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

    @override
    async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:
        """Executes the synthesis generation pipeline.

        Args:
            request: The EngineExecutionRequest containing compiled schemas and context.

        Returns:
            EngineExecutionResult containing the generated output dict.

        Raises:
            AppException: If blackboard is missing or execution errors occur (ErrorCodes.SYNTHESIS_ENGINE_ERROR),
                or if payload validation fails (ErrorCodes.VALIDATION_FAILED).
        """
        tracer = get_tracer(__name__)
        distill_stack = contextlib.ExitStack()
        distill_span = distill_stack.enter_context(tracer.start_as_current_span("synthesis.distill"))
        distill_span.set_attribute("execution.id", request.context.execution_id)
        distill_span.set_attribute("step.id", request.step.id)

        try:
            blackboard = request.context.context_variables.global_atom_blackboard
            if blackboard is None:
                distill_span.set_status(
                    trace.StatusCode.ERROR, "__GLOBAL_ATOM_BLACKBOARD__ missing from context_variables"
                )
                logger.error(
                    "preflight_blackboard_missing",
                    extra={"execution_id": request.context.execution_id, "step_id": request.step.id},
                )
                raise AppException(
                    message="__GLOBAL_ATOM_BLACKBOARD__ missing from context_variables",
                    status_code=500,
                    details={"error_code": ErrorCodes.SYNTHESIS_ENGINE_ERROR.value},
                )

            all_atom_ids = blackboard.get_all_atom_ids()
            doc_aliases = list(blackboard.atoms_by_input.keys())
            total_atoms = len(all_atom_ids)
            settings = get_settings()

            matrix_reducer_output = request.context.context_variables.matrix_reducer_output

            has_matrix_evidence = False
            if matrix_reducer_output is not None:
                if isinstance(matrix_reducer_output, LightweightMatrixDTO):
                    if (
                        matrix_reducer_output.reduced_atoms
                        or matrix_reducer_output.evaluated_matrices
                        or matrix_reducer_output.raw_extensions
                    ):
                        has_matrix_evidence = True
                elif isinstance(matrix_reducer_output, LightweightMatrixOutput):
                    if (
                        matrix_reducer_output.evaluated_atoms
                        or matrix_reducer_output.level_breakdown
                        or matrix_reducer_output.extensions
                    ):
                        has_matrix_evidence = True

            is_starved = False
            starvation_reason = ""

            if total_atoms <= settings.synthesis_starvation_threshold:
                is_starved = True
                starvation_reason = (
                    f"Data starvation: zero atoms extracted "
                    f"({total_atoms} <= {settings.synthesis_starvation_threshold})"
                )
            elif total_atoms < settings.synthesis_sparse_threshold and not has_matrix_evidence:
                is_starved = True
                starvation_reason = (
                    f"Data starvation: sparse atoms ({total_atoms}) yielded zero evaluative matrix evidence"
                )

            if is_starved:
                logger.warning(
                    "SynthesisEngine: Circuit breaker triggered (%s). Bypassing LLM execution.",
                    starvation_reason,
                )
                starvation_dto = DataStarvationEvent(
                    total_atoms=total_atoms,
                    reason=starvation_reason,
                )
                starvation_event = TraceEvent(
                    step_name=request.step.id,
                    event_type="output",
                    content=starvation_dto,
                )
                return EngineExecutionResult(
                    results=[],
                    hydrated_references={},
                    synthesis_output=starvation_dto,
                    trace_events=[starvation_event],
                )

            # Validate dual-input context (hydrated messages required)
            if request.hydrated_messages is None:
                logger.error(
                    "synthesis_engine_missing_hydrated_messages",
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "step_id": request.step.id},
                )
                raise AppException(
                    message="hydrated_messages must be provided for SynthesisEngine",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "step_id": request.step.id},
                )

            local_messages = list(request.hydrated_messages)

            raw_xai_extensions_str = ""
            if matrix_reducer_output is not None:
                try:
                    if isinstance(matrix_reducer_output, LightweightMatrixDTO):
                        if matrix_reducer_output.raw_extensions:
                            raw_list = [
                                ext.model_dump(mode="json", exclude_none=True)
                                if isinstance(ext, (RawXAIExtensionDTO, BaseModel))
                                else ext
                                for ext in matrix_reducer_output.raw_extensions
                            ]
                            extensions_json = json.dumps(raw_list, indent=2)
                            raw_xai_extensions_str = f"\n<raw_xai_extensions>\n{extensions_json}\n</raw_xai_extensions>"
                    elif isinstance(matrix_reducer_output, LightweightMatrixOutput):
                        if matrix_reducer_output.extensions:
                            ext_dict = {
                                (k.value if isinstance(k, Enum) else str(k)): v
                                for k, v in matrix_reducer_output.extensions.items()
                            }
                            extensions_json = json.dumps(ext_dict, indent=2)
                            raw_xai_extensions_str = f"\n<raw_xai_extensions>\n{extensions_json}\n</raw_xai_extensions>"
                except (TypeError, KeyError) as err:
                    msg = f"Corrupted raw_extensions in __MATRIX_REDUCER_OUTPUT__: {err}"
                    logger.error("[SynthesisEngine] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from err

            raw_blackboard_markdown = blackboard.to_markdown_synthesis_injection()
            user_payload_xml = TemplateProcessor.render_prompt(
                t"Synthesize the following atoms according to the instructions:\n"
                t"<user_payload>\n"
                t"{raw_blackboard_markdown}\n"
                t"</user_payload>"
            )

            user_content_parts = [user_payload_xml]

            if raw_xai_extensions_str:
                user_content_parts.append(raw_xai_extensions_str)

            if total_atoms < settings.synthesis_sparse_threshold:
                user_content_parts.append(SPARSE_DATA_SYNTHESIS_MANDATE)

            final_user_content = "\n\n".join(user_content_parts)
            local_messages.append(LLMMessageDTO(role="user", content=final_user_content))

            logger.info("SynthesisEngine: Final hydrated message count: %d", len(local_messages))

            if request.compiled_schema is None:
                logger.error(
                    "synthesis_engine_missing_compiled_schema",
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "step_id": request.step.id},
                )
                raise AppException(
                    message="compiled_schema must be provided for SynthesisEngine",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "step_id": request.step.id},
                )

            if request.progress_callback:
                await request.progress_callback(10, 100)

            # Delegate to LLM executor
            validated_model, usage = await self._executor.execute_structured_task(
                client=request.bound_client,
                messages=local_messages,
                response_model=request.compiled_schema,
                validation_context={"strictness_level": request.context.strictness_level},
            )

            if request.progress_callback:
                await request.progress_callback(90, 100)

            output_dict = validated_model.model_dump()

            # Alias hydration and hallucinated UUID filtering
            alias_engine = AliasEngine()
            for atom_id in all_atom_ids:
                alias_engine.alias_map[atom_id] = atom_id
            for doc_id in doc_aliases:
                alias_engine.alias_map[doc_id] = doc_id

            # Hydrate and strictly DROP hallucinated opaque UUIDs
            alias_engine.hydrate_and_filter_aliases(output_dict, {"atom_id", "source_id"})

            # Re-validate model after alias hydration
            validated_output = request.compiled_schema.model_validate(output_dict)

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
                synthesis_output=validated_output,
                trace_events=trace_events,
                usage=usage,
            )

        except ValidationError as e:
            distill_span.record_exception(e)
            distill_span.set_status(trace.StatusCode.ERROR, str(e))
            logger.error("SynthesisEngine validation failed", exc_info=True)
            raise AppException(
                message=f"Synthesis engine validation failed: {e}",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e
        except Exception as e:
            distill_span.record_exception(e)
            distill_span.set_status(trace.StatusCode.ERROR, str(e))
            logger.error("SynthesisEngine unexpected error", exc_info=True)
            if isinstance(e, AppException):
                raise
            raise AppException(
                message=f"Synthesis engine encountered an error: {e}",
                status_code=500,
                details={"error_code": ErrorCodes.SYNTHESIS_ENGINE_ERROR.value},
            ) from e
        finally:
            distill_stack.close()
