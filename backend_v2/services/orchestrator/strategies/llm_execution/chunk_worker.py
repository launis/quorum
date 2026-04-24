import asyncio
import json
import logging
from typing import Any

from pydantic import RootModel

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.view.sdui import AnySduiBlock
from backend_v2.services.mcp.mcp_tool_loop import execute_tool_loop

logger = logging.getLogger(__name__)


class ChunkWorker:
    """Isolates the physical LLM interaction, MCP tool loops, and caching logic for chunks."""

    @staticmethod
    async def process_chunk(
        chunk: Any,
        sem: asyncio.Semaphore,
        compiler: Any,
        criteria_blocks: list[dict[str, Any]],
        user_payload: str,
        base_system_prompt: str,
        has_search: bool,
        has_shuffled_atoms: bool,
        atom_to_block_ids: dict[str, set[str]],
        effective_mcp_tools: list[str],
        bound_client: LLMClient,
        step_id: str,
        target_locale: str,
        state_data: dict[str, Any],
        output_profile: Any | None,
    ) -> tuple[dict[str, Any], dict[str, Any], list[Any]]:
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
                        aid = item.get("atom_id") if isinstance(item, dict) else getattr(item, "atom_id", None)
                        if aid and aid in atom_to_block_ids:
                            chunk_matrix_ids.update(atom_to_block_ids[aid])

                    chunk_criteria = [
                        b
                        for b in criteria_blocks
                        if b.get("category_id") != "matrix" or b.get("id") in chunk_matrix_ids
                    ]

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

            messages = [
                {"role": "system", "content": f"System Context & Reference Data:\n\n{local_payload}"},
                {"role": "user", "content": local_system_prompt},
            ]

            chunk_final: dict[str, Any] = {}
            chunk_usage: dict[str, Any] = {}
            chunk_traces: list[Any] = []

            if effective_mcp_tools:
                try:
                    loop_res = await execute_tool_loop(
                        llm_client=bound_client,
                        messages=messages,
                        response_model=local_dynamic_schema,
                        allowed_tools=effective_mcp_tools,
                        step_name=step_id,
                        mock_identity=step_id,
                        target_language=target_locale,
                        synthesis_instructions=state_data.get("synthesis_instructions"),
                    )
                    chunk_final = dict(loop_res.result_data)
                    chunk_usage = dict(loop_res.usage) if loop_res.usage else {}
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
                    if output_profile is not None:

                        class SduiResponseList(RootModel[list[AnySduiBlock]]):
                            pass

                        result, usage = await bound_client.run_structured_task(
                            messages=messages,
                            response_model=SduiResponseList,
                            mock_identity=step_id,
                            max_retries=3,
                        )
                        chunk_final = {"blocks": result.model_dump(mode="json")}
                    else:
                        result, usage = await bound_client.run_structured_task(
                            messages=messages,
                            response_model=local_dynamic_schema,
                            mock_identity=step_id,
                        )
                        chunk_final = dict(result.model_dump(mode="json"))

                    chunk_usage = dict(usage) if usage else {}
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
