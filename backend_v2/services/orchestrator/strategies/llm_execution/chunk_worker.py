import asyncio
import copy
import json
import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes, LLMSchemaValidationError, SemanticEvidenceError
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.enums import SystemConcurrency
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.models.v2_core import PromptBlock
from backend_v2.models.view.sdui import AnySduiBlock
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.mcp.mcp_tool_loop import execute_tool_loop
from backend_v2.services.orchestrator.anchor_validation_service import AnchorValidationService

logger = logging.getLogger(__name__)


class AtomIdentifier(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")
    atom_id: str


class ExtractionPayload(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    exact_quote: str | None = ""
    contextual_override: bool = False
    semantic_reasoning: str | None = ""


def evaluate_extraction(extraction: BaseModel, source_text: str, is_negative_rule: bool) -> str:
    """Evaluates the deterministic extraction with dual-track validation.
    Returns PASS, FAIL, or DLQ.
    """
    exact_quote = getattr(extraction, "exact_quote", None)
    contextual_override = getattr(extraction, "contextual_override", False)
    semantic_reasoning = getattr(extraction, "semantic_reasoning", None)

    # Track A: Physical Match
    if exact_quote and exact_quote != "[CONTEXTUAL_OVERRIDE_APPLIED]":
        try:
            AnchorValidationService.validate_evidence(
                pdf_text=source_text,
                exact_quote=exact_quote,
                reasoning_trace=semantic_reasoning,
                contextual_override=contextual_override,
            )
            status = "PASS"
        except SemanticEvidenceError:
            status = "FAIL"
    # Track B: Semantic Override
    else:
        if contextual_override:
            status = "DLQ"
        else:
            status = "FAIL"

    # Negative condition handling
    if is_negative_rule:
        if status == "PASS":
            status = "FAIL"
        elif status == "FAIL":
            status = "PASS"

    return status


class SduiResponseList(BaseModel):
    """Strict schema to validate lists of SDUI blocks from LLM responses."""

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)
    blocks: list[AnySduiBlock]


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
        running_event: asyncio.Event | None = None,
        step_metadata: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], TokenUsage | None, list[Any]]:
        """Processes a single execution chunk, mapping dynamic schemas and orchestrating tool loops."""
        async with sem:
            if running_event is not None and not running_event.is_set():
                running_event.set()
            chunk_criteria = list(criteria_blocks)

            # V3 Cache Fix: Separate atoms from base payload
            chunk_atoms_xml: str | None = None
            if chunk is not None:
                atoms_json = json.dumps(chunk.items, ensure_ascii=False, indent=2)
                chunk_atoms_xml = f"<BLIND_ATOMS_TO_EVALUATE>\n{atoms_json}\n</BLIND_ATOMS_TO_EVALUATE>"

                # Apply Chunk context subsetting
                if has_shuffled_atoms:
                    chunk_matrix_ids = set()
                    for item in chunk.items:
                        try:
                            aid_model = AtomIdentifier.model_validate(item)
                            if aid_model.atom_id in atom_to_block_ids:
                                chunk_matrix_ids.update(atom_to_block_ids[aid_model.atom_id])
                        except ValidationError as e:
                            logger.error(
                                "[ChunkWorker] Strict Fail-Fast Enforced: Malformed atom item payload.",
                                extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
                            )
                            raise AppException(
                                message="Atom item validation failed",
                                status_code=500,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                            ) from e

                    chunk_criteria = []
                    for bm in criteria_blocks:
                        if bm.category_id != "matrix" or bm.id in chunk_matrix_ids:
                            chunk_criteria.append(bm)

            # V3: Build dynamic schema for this chunk's criteria subset
            local_dynamic_schema = compiler.build_dynamic_schema(
                schema_name=f"Step_{step_id}_Response",
                criteria=chunk_criteria,
                has_search_result=has_search,
                has_shuffled_atoms=has_shuffled_atoms,
                target_locale=target_locale,
            )

            persona = chunk_criteria[0].execution_persona if chunk_criteria else None

            # V3 Cache Fix: Use CompiledPrompt with separated static/dynamic tiers
            compiled_prompt = compiler.compile_chunk_prompt(
                base_system_prompt=base_system_prompt,
                chunk_criteria=chunk_criteria,
                base_payload=user_payload,
                chunk_atoms_xml=chunk_atoms_xml,
                strictness_level=strictness_level,
                target_locale=target_locale,
            )

            chunk_final: dict[str, Any] = {}
            chunk_usage: TokenUsage | None = None
            chunk_traces: list[Any] = []

            try:
                if effective_mcp_tools:
                    executor = LLMTaskExecutor(prompt_compiler=compiler)
                    loop_res = await execute_tool_loop(
                        llm_client=bound_client,
                        executor=executor,
                        messages=compiled_prompt.to_flat_messages(),
                        response_model=local_dynamic_schema,
                        allowed_tools=effective_mcp_tools,
                        step_name=step_id,
                        mock_identity=step_id,
                        target_language=target_locale,
                        synthesis_instructions=synthesis_instructions,
                        validation_context={
                            "strictness_level": strictness_level,
                            "source_text": user_payload,
                            "persona": persona,
                            "estimated_token_count": step_metadata.get("estimated_token_count", 0)
                            if step_metadata
                            else 0,
                        },
                    )
                    if isinstance(loop_res.result_data, BaseModel):
                        chunk_final = loop_res.result_data.model_dump(mode="json")
                    else:
                        chunk_final = dict(loop_res.result_data)
                    chunk_usage = loop_res.usage if loop_res.usage else None
                    if loop_res.audit_traces:
                        chunk_traces.extend(loop_res.audit_traces)
                else:
                    executor = LLMTaskExecutor(prompt_compiler=compiler)

                    # Milestone 4 Setup: Identify high entropy and negative rule triggers dynamically
                    HIGH_ENTROPY_ATOMS = set()
                    for crit in chunk_criteria:
                        if crit.scales:
                            for scale in crit.scales:
                                for claim in scale.claims:
                                    for tda in claim.tda_assertions:
                                        if getattr(tda, "high_entropy", False):
                                            HIGH_ENTROPY_ATOMS.add(tda.tda_id)

                    is_ensemble_step = False
                    if chunk is not None:
                        for item in chunk.items:
                            aid = item.get("atom_id") if isinstance(item, dict) else getattr(item, "atom_id", None)
                            if aid in HIGH_ENTROPY_ATOMS:
                                is_ensemble_step = True
                    for crit in chunk_criteria:
                        if crit.id in HIGH_ENTROPY_ATOMS:
                            is_ensemble_step = True
                        if crit.scales:
                            for scale in crit.scales:
                                for claim in scale.claims:
                                    for tda in claim.tda_assertions:
                                        if tda.tda_id in HIGH_ENTROPY_ATOMS:
                                            is_ensemble_step = True

                    has_negative_rule = False
                    for crit in chunk_criteria:
                        if crit.scales:
                            for scale in crit.scales:
                                for claim in scale.claims:
                                    for tda in claim.tda_assertions:
                                        if getattr(tda, "inverse_evidence", False):
                                            has_negative_rule = True
                                            break

                    llm_count = 3 if is_ensemble_step else 1

                    async def run_llm_calls(
                        prompt: CompiledPrompt, model_schema: type[BaseModel], count: int
                    ) -> tuple[list[dict[str, Any]], TokenUsage]:
                        """Execute LLM calls using native CompiledPrompt architecture."""
                        results_list = []
                        total_usage = TokenUsage()
                        if count == 3:
                            tasks_list = []
                            async with asyncio.TaskGroup() as tg:
                                for _ in range(3):
                                    t_task = tg.create_task(
                                        executor.execute_structured_task(
                                            client=bound_client,
                                            messages=prompt,
                                            response_model=model_schema,
                                            mock_identity=step_id,
                                            max_schema_retries=SystemConcurrency.FAIL_FAST_MAX_RETRIES.value,
                                            max_logical_retries=SystemConcurrency.FAIL_FAST_MAX_RETRIES.value,
                                            validation_context={
                                                "strictness_level": strictness_level,
                                                "source_text": user_payload,
                                                "persona": persona,
                                                "estimated_token_count": step_metadata.get("estimated_token_count", 0)
                                                if step_metadata
                                                else 0,
                                            },
                                        )
                                    )
                                    tasks_list.append(t_task)
                            for t in tasks_list:
                                res, usg = t.result()
                                results_list.append(res.model_dump(mode="json"))
                                if usg:
                                    total_usage = total_usage + usg
                        else:
                            res, usg = await executor.execute_structured_task(
                                client=bound_client,
                                messages=prompt,
                                response_model=model_schema,
                                mock_identity=step_id,
                                max_schema_retries=SystemConcurrency.FAIL_FAST_MAX_RETRIES.value,
                                max_logical_retries=SystemConcurrency.FAIL_FAST_MAX_RETRIES.value,
                                validation_context={
                                    "strictness_level": strictness_level,
                                    "source_text": user_payload,
                                    "persona": persona,
                                    "estimated_token_count": step_metadata.get("estimated_token_count", 0)
                                    if step_metadata
                                    else 0,
                                },
                            )
                            results_list.append(res.model_dump(mode="json"))
                            if usg:
                                total_usage = total_usage + usg
                        return results_list, total_usage

                    def resolve_majority_vote(
                        res_list: list[dict[str, Any]], is_shuffled: bool, criteria_blocks: list[Any]
                    ) -> dict[str, Any]:
                        if not res_list:
                            return {}
                        if len(res_list) == 1:
                            return res_list[0]
                        merged = copy.deepcopy(res_list[0])

                        if is_shuffled and "evaluations" in merged:
                            num_evals = len(merged["evaluations"])
                            for idx in range(num_evals):
                                atom_id = merged["evaluations"][idx]["atom_id"]
                                votes = []
                                for res in res_list:
                                    if "evaluations" in res and idx < len(res["evaluations"]):
                                        item = res["evaluations"][idx]
                                        if item["atom_id"] == atom_id:
                                            votes.append(item)
                                if votes:
                                    overrides = [v.get("contextual_override", False) for v in votes]
                                    quotes = [v.get("exact_quote") for v in votes]
                                    reasonings = [v.get("semantic_reasoning", "") for v in votes]

                                    final_override = sum(1 for o in overrides if o) >= 2
                                    valid_quotes = [q for q in quotes if q and q != "[CONTEXTUAL_OVERRIDE_APPLIED]"]
                                    if valid_quotes and not final_override:
                                        final_quote = max(set(valid_quotes), key=valid_quotes.count)
                                    elif final_override:
                                        final_quote = "[CONTEXTUAL_OVERRIDE_APPLIED]"
                                    else:
                                        final_quote = None
                                    final_reasoning = max(set(reasonings), key=reasonings.count)

                                    merged["evaluations"][idx]["contextual_override"] = final_override
                                    merged["evaluations"][idx]["exact_quote"] = final_quote
                                    merged["evaluations"][idx]["semantic_reasoning"] = final_reasoning
                        else:
                            for block in criteria_blocks:
                                if block.id in merged and block.category_id != "matrix" and block.type != "instruction":
                                    votes = [res[block.id] for res in res_list if block.id in res]
                                    if votes:
                                        overrides = [v.get("contextual_override", False) for v in votes]
                                        quotes = [v.get("exact_quote") for v in votes]
                                        reasonings = [v.get("semantic_reasoning", "") for v in votes]

                                        final_override = sum(1 for o in overrides if o) >= 2
                                        valid_quotes = [q for q in quotes if q and q != "[CONTEXTUAL_OVERRIDE_APPLIED]"]
                                        if valid_quotes and not final_override:
                                            final_quote = max(set(valid_quotes), key=valid_quotes.count)
                                        elif final_override:
                                            final_quote = "[CONTEXTUAL_OVERRIDE_APPLIED]"
                                        else:
                                            final_quote = None
                                        final_reasoning = max(set(reasonings), key=reasonings.count)

                                        merged[block.id]["contextual_override"] = final_override
                                        merged[block.id]["exact_quote"] = final_quote
                                        merged[block.id]["semantic_reasoning"] = final_reasoning
                        return merged

                    if has_negative_rule:
                        # V3: Falsification passes via model_copy instead of deepcopy
                        # Milestone 3 Pass 1: Presence Detection
                        falsification_1 = (
                            "\n\n<DECOUPLED_FALSIFICATION_PASS>\n"
                            "PRESENCE_DETECTION: Focus on finding any positive occurrence, "
                            "claim, or presence of the target concepts (e.g. X is present). "
                            "Do not look for exceptions or limits.\n"
                            "</DECOUPLED_FALSIFICATION_PASS>"
                        )
                        new_dynamic_1 = [dict(m) for m in compiled_prompt.dynamic_messages]
                        new_dynamic_1[-1] = {
                            **new_dynamic_1[-1],
                            "content": new_dynamic_1[-1]["content"] + falsification_1,
                        }
                        compiled_prompt_1 = compiled_prompt.model_copy(update={"dynamic_messages": new_dynamic_1})

                        # Milestone 3 Pass 2: Exception Detection
                        falsification_2 = (
                            "\n\n<DECOUPLED_FALSIFICATION_PASS>\n"
                            "EXCEPTION_DETECTION: Focus exclusively on finding any exceptions, "
                            "caveats, limits, or mitigating statements that justify or permit "
                            "the target concepts. If none are found, exact_quote MUST be null.\n"
                            "</DECOUPLED_FALSIFICATION_PASS>"
                        )
                        new_dynamic_2 = [dict(m) for m in compiled_prompt.dynamic_messages]
                        new_dynamic_2[-1] = {
                            **new_dynamic_2[-1],
                            "content": new_dynamic_2[-1]["content"] + falsification_2,
                        }
                        compiled_prompt_2 = compiled_prompt.model_copy(update={"dynamic_messages": new_dynamic_2})

                        # Execute with CompiledPrompt architecture
                        res_list_1, usage1 = await run_llm_calls(compiled_prompt_1, local_dynamic_schema, llm_count)
                        res_list_2, usage2 = await run_llm_calls(compiled_prompt_2, local_dynamic_schema, llm_count)

                        chunk_final = resolve_majority_vote(res_list_1, has_shuffled_atoms, chunk_criteria)
                        chunk_final_2 = resolve_majority_vote(res_list_2, has_shuffled_atoms, chunk_criteria)
                        chunk_usage = usage1 + usage2
                    else:
                        target_schema = (
                            SduiResponseList
                            if (output_profile is not None and not criteria_blocks)
                            else local_dynamic_schema
                        )
                        res_list, chunk_usage = await run_llm_calls(compiled_prompt, target_schema, llm_count)
                        chunk_final = resolve_majority_vote(res_list, has_shuffled_atoms, chunk_criteria)

                    # Step 4: Map-Merge Orchestration & Trace Continuity Injection
                    if has_shuffled_atoms and "evaluations" in chunk_final:
                        # Evaluate each flattened atom
                        for i, atom_data in enumerate(chunk_final["evaluations"]):
                            atom_id = atom_data["atom_id"]

                            temp_atom1 = ExtractionPayload(
                                exact_quote=atom_data["exact_quote"],
                                contextual_override=atom_data["contextual_override"],
                                semantic_reasoning=atom_data.get("semantic_reasoning", ""),
                            )
                            status1 = evaluate_extraction(temp_atom1, user_payload, False)

                            if has_negative_rule and "evaluations" in chunk_final_2:
                                atom_data2 = next(
                                    (a for a in chunk_final_2["evaluations"] if a["atom_id"] == atom_id), None
                                )
                                if atom_data2:
                                    temp_atom2 = ExtractionPayload(
                                        exact_quote=atom_data2["exact_quote"],
                                        contextual_override=atom_data2["contextual_override"],
                                        semantic_reasoning=atom_data2.get("semantic_reasoning", ""),
                                    )
                                    status2 = evaluate_extraction(temp_atom2, user_payload, False)

                                    if status1 == "PASS" and status2 != "PASS":
                                        status = "PASS"
                                    else:
                                        status = "FAIL"

                                    atom_data["status"] = status
                                    if status == "PASS":
                                        atom_data["exact_quote"] = atom_data["exact_quote"]
                                        atom_data["semantic_reasoning"] = (
                                            f"Presence detected: {atom_data['semantic_reasoning']}. "
                                            f"Exceptions audit: {atom_data2['semantic_reasoning']}"
                                        )
                                    else:
                                        if status2 == "PASS":
                                            atom_data["exact_quote"] = atom_data2["exact_quote"]
                                            atom_data["semantic_reasoning"] = (
                                                f"Mitigating exception found: {atom_data2['semantic_reasoning']}"
                                            )
                                        else:
                                            atom_data["exact_quote"] = None
                                            atom_data["semantic_reasoning"] = (
                                                "No presence of target concept detected: "
                                                f"{atom_data['semantic_reasoning']}"
                                            )
                                else:
                                    status = status1
                                    atom_data["status"] = status
                            else:
                                status = status1
                                atom_data["status"] = status

                            sr = atom_data["semantic_reasoning"]
                            atom_data["semantic_reasoning"] = f"{sr}\n\n[5. VALIDATION DECISION: {status}]"
                            chunk_final["evaluations"][i] = atom_data

                    else:
                        # Evaluate each standard block (TDA extractions)
                        for crit in chunk_criteria:
                            if crit.id in chunk_final and crit.category_id != "matrix" and crit.type != "instruction":
                                block_data = chunk_final[crit.id]

                                is_negative_rule = False
                                if crit.scales:
                                    for scale in crit.scales:
                                        for claim in scale.claims:
                                            for tda in claim.tda_assertions:
                                                if tda.inverse_evidence:
                                                    is_negative_rule = True
                                                    break

                                temp_block1 = ExtractionPayload(
                                    exact_quote=block_data["exact_quote"],
                                    contextual_override=block_data["contextual_override"],
                                    semantic_reasoning=block_data.get("semantic_reasoning", ""),
                                )
                                status1 = evaluate_extraction(temp_block1, user_payload, False)

                                if is_negative_rule and has_negative_rule and crit.id in chunk_final_2:
                                    block_data2 = chunk_final_2[crit.id]
                                    temp_block2 = ExtractionPayload(
                                        exact_quote=block_data2["exact_quote"],
                                        contextual_override=block_data2["contextual_override"],
                                        semantic_reasoning=block_data2.get("semantic_reasoning", ""),
                                    )
                                    status2 = evaluate_extraction(temp_block2, user_payload, False)

                                    if status1 == "PASS" and status2 != "PASS":
                                        status = "PASS"
                                    else:
                                        status = "FAIL"

                                    block_data["status"] = status
                                    if status == "PASS":
                                        block_data["exact_quote"] = block_data["exact_quote"]
                                        block_data["semantic_reasoning"] = (
                                            f"Presence detected: {block_data['semantic_reasoning']}. "
                                            f"Exceptions audit: {block_data2['semantic_reasoning']}"
                                        )
                                    else:
                                        if status2 == "PASS":
                                            block_data["exact_quote"] = block_data2["exact_quote"]
                                            block_data["semantic_reasoning"] = (
                                                f"Mitigating exception found: {block_data2['semantic_reasoning']}"
                                            )
                                        else:
                                            block_data["exact_quote"] = None
                                            block_data["semantic_reasoning"] = (
                                                "No presence of target concept detected: "
                                                f"{block_data['semantic_reasoning']}"
                                            )
                                else:
                                    status = evaluate_extraction(temp_block1, user_payload, is_negative_rule)
                                    block_data["status"] = status

                                sr = block_data["semantic_reasoning"]
                                block_data["semantic_reasoning"] = f"{sr}\n\n[5. VALIDATION DECISION: {status}]"
                                chunk_final[crit.id] = block_data

                return chunk_final, chunk_usage, chunk_traces

            except (LLMSchemaValidationError, AppException, ExceptionGroup) as e:

                def _unwrap_error(exc: BaseException) -> str:
                    if isinstance(exc, ExceptionGroup):
                        return " | ".join(_unwrap_error(inner) for inner in exc.exceptions)
                    return str(exc)

                reason_str = _unwrap_error(e)

                logger.error(
                    f"[ChunkWorker] Caught error: {reason_str}. Routing to DLQ.",
                    extra={"error_code": "DLQ_ROUTING"},
                    exc_info=True,
                )
                chunk_final = {"_dlq_status": "FAILED/DLQ", "reason": reason_str}
                return chunk_final, None, []
