import asyncio
import json
import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, RootModel

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.enums import SystemConcurrency
from backend_v2.models.v2_core import PromptBlock
from backend_v2.models.view.sdui import AnySduiBlock
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.mcp.mcp_tool_loop import execute_tool_loop

logger = logging.getLogger(__name__)


class AtomIdentifier(BaseModel):
    model_config = ConfigDict(frozen=True)
    atom_id: str


class SduiResponseList(RootModel[list[AnySduiBlock]]):
    model_config = ConfigDict(frozen=True)
    pass


class ChunkWorker:
    """Isolates the physical LLM interaction, MCP tool loops, and caching logic for chunks."""

    @staticmethod
    async def process_chunk(
        chunk: Any,
        sem: asyncio.Semaphore,
        compiler: Any,
        criteria_blocks: list[PromptBlock],
        user_payload: str,
        base_system_prompt: str,
        has_search: bool,
        has_shuffled_atoms: bool,
        atom_to_block_ids: dict[str, set[str]],
        effective_mcp_tools: list[str],
        bound_client: LLMClient,
        step_id: str,
        target_locale: str,
        synthesis_instructions: dict[str, Any] | None,
        output_profile: Any | None,
        strictness_level: int = 50,
    ) -> tuple[dict[str, Any], dict[str, Any] | None, list[Any]]:
        """Processes a single execution chunk, mapping dynamic schemas and orchestrating tool loops."""
        async with sem:
            local_payload = user_payload
            chunk_criteria = list(criteria_blocks)

            if chunk is not None:
                atoms_json = json.dumps(chunk.items, ensure_ascii=False, indent=2)
                local_payload += f"\n\n<BLIND_ATOMS_TO_EVALUATE>\n{atoms_json}\n</BLIND_ATOMS_TO_EVALUATE>\n"

                # Apply Chunk context subsetting
                if has_shuffled_atoms:
                    chunk_matrix_ids = set()
                    for item in chunk.items:
                        try:
                            aid_model = AtomIdentifier.model_validate(item)
                            if aid_model.atom_id in atom_to_block_ids:
                                chunk_matrix_ids.update(atom_to_block_ids[aid_model.atom_id])
                        except Exception as e:
                            msg = f"Strict Fail-Fast Enforced: Malformed atom item payload. {str(e)}"
                            logger.error("[ChunkWorker] %s", msg, exc_info=True)
                            raise AppException(
                                message="Atom item validation failed",
                                status_code=500,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                            ) from e

                    chunk_criteria = []
                    for bm in criteria_blocks:
                        if bm.category_id != "matrix" or bm.id in chunk_matrix_ids:
                            chunk_criteria.append(bm)

            # Dynamically build system prompt and schema for this chunk
            local_xml_rubrics = compiler.compile_xml_rubrics(chunk_criteria, target_locale)

            local_system_prompt = base_system_prompt
            if local_xml_rubrics:
                local_system_prompt += f"\n\n{local_xml_rubrics}"

            local_dynamic_schema = compiler.build_dynamic_schema(
                schema_name=f"Step_{step_id}_Response",
                criteria=chunk_criteria,
                has_search_result=has_search,
                has_shuffled_atoms=has_shuffled_atoms,
                target_locale=target_locale,
            )

            strictness_instruction = compiler.calibrate_strictness(strictness_level)

            user_msg = (
                f"System Context & Reference Data:\n\n{local_payload}\n\n"
                f"<execution_parameters>\n<STRICTNESS_CALIBRATION>\n"
                f"{strictness_instruction}\n</STRICTNESS_CALIBRATION>\n</execution_parameters>"
            )

            messages = [
                {"role": "system", "content": local_system_prompt},
                {"role": "user", "content": user_msg},
            ]

            chunk_final: dict[str, Any] = {}
            chunk_usage: dict[str, Any] | None = None
            chunk_traces: list[Any] = []

            if effective_mcp_tools:
                try:
                    executor = LLMTaskExecutor(prompt_compiler=compiler)
                    loop_res = await execute_tool_loop(
                        llm_client=bound_client,
                        executor=executor,
                        messages=messages,
                        response_model=local_dynamic_schema,
                        allowed_tools=effective_mcp_tools,
                        step_name=step_id,
                        mock_identity=step_id,
                        target_language=target_locale,
                        synthesis_instructions=synthesis_instructions,
                        validation_context={"strictness_level": strictness_level},
                    )
                    chunk_final = dict(loop_res.result_data)
                    chunk_usage = dict(loop_res.usage) if loop_res.usage else None
                    if loop_res.audit_traces:
                        chunk_traces.extend(loop_res.audit_traces)
                except Exception as e:
                    logger.error(
                        "Execution of MCP tool loop failed.",
                        extra={
                            "error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.name,
                            "step_id": step_id,
                            "detail": str(e),
                        },
                        exc_info=True,
                    )
                    if isinstance(e, AppException):
                        raise
                    raise AppException(
                        message=f"MCP Tool Loop Execution failed: {str(e)}",
                        status_code=500,
                        details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.value},
                    ) from e
            else:
                try:
                    executor = LLMTaskExecutor(prompt_compiler=compiler)
                    if output_profile is not None:
                        result, usage = await executor.execute_structured_task(
                            client=bound_client,
                            messages=messages,
                            response_model=SduiResponseList,
                            mock_identity=step_id,
                            max_schema_retries=SystemConcurrency.LLM_MAX_RETRIES.value,
                            validation_context={"strictness_level": strictness_level},
                        )
                        chunk_final = {"blocks": result.model_dump(mode="json")}
                    else:
                        result, usage = await executor.execute_structured_task(
                            client=bound_client,
                            messages=messages,
                            response_model=local_dynamic_schema,
                            mock_identity=step_id,
                            max_schema_retries=SystemConcurrency.LLM_MAX_RETRIES.value,
                            validation_context={"strictness_level": strictness_level},
                        )
                        chunk_final = dict(result.model_dump(mode="json"))

                    chunk_usage = usage.model_dump(mode="json") if usage else None
                except Exception as e:
                    logger.error(
                        "Execution of structured LLM task failed.",
                        extra={
                            "error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.name,
                            "step_id": step_id,
                            "detail": str(e),
                        },
                        exc_info=True,
                    )
                    if isinstance(e, AppException):
                        raise
                    raise AppException(
                        message=f"Structured LLM execution failed: {str(e)}",
                        status_code=500,
                        details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.value},
                    ) from e

            return chunk_final, chunk_usage, chunk_traces
