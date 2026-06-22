import asyncio
import copy
import json
import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes, LLMSchemaValidationError, SemanticEvidenceError
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.report import PromptContextDTO
from backend_v2.models.enums import EvaluationRunCount, SystemConcurrency
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.models.v2_core import PromptBlock
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.mcp.mcp_tool_loop import execute_tool_loop
from backend_v2.services.orchestrator.anchor_validation_service import AnchorValidationService
from backend_v2.services.orchestrator.extractive_sensor_service import ExtractiveSensorService

logger = logging.getLogger(__name__)

FEATURE_FLAG_EXTRACTIVE_SENSOR = True


def _is_transient_chunk_error(exc: BaseException) -> bool:
    """Classify whether a chunk-level error is transient (retryable) or structural (terminal)."""
    import asyncio

    import litellm

    TRANSIENT_TYPES = (
        asyncio.TimeoutError,
        ConnectionError,
        getattr(litellm, "APIConnectionError", type(None)),
        getattr(litellm, "RateLimitError", type(None)),
        getattr(litellm, "ServiceUnavailableError", type(None)),
        getattr(litellm, "Timeout", type(None)),
    )
    TRANSIENT_KEYWORDS = ("APIConnectionError", "ServiceUnavailable", "Timeout", "Resource exhausted")

    if isinstance(exc, ExceptionGroup):
        return all(_is_transient_chunk_error(inner) for inner in exc.exceptions)

    if isinstance(exc, TRANSIENT_TYPES):
        return True

    error_str = str(exc)
    return any(keyword in error_str for keyword in TRANSIENT_KEYWORDS)


class AtomIdentifier(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")
    atom_id: str


class ConsensusVotePayload(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")
    exact_quotes: list[str] = []
    contextual_override: bool = False
    override_reason: str | None = None
    reasoning_steps: str | None = ""
    semantic_reasoning: str | None = ""


def evaluate_extraction(extraction: Any, source_text: str, strictness_level: int = 1) -> str:
    """Evaluates the deterministic extraction with dual-track validation.
    Returns PASS, FAIL, or DLQ.
    """
    exact_quotes = getattr(extraction, "exact_quotes", [])
    if not isinstance(exact_quotes, list):
        exact_quotes = []
    contextual_override = getattr(extraction, "contextual_override", False)
    if not isinstance(contextual_override, bool):
        contextual_override = False
    override_reason = getattr(extraction, "override_reason", None)
    if not isinstance(override_reason, str) or override_reason == "":
        override_reason = None
    reasoning_steps = getattr(extraction, "reasoning_steps", None)
    if not isinstance(reasoning_steps, str):
        reasoning_steps = None

    # Track A: Physical Match
    if exact_quotes and len(exact_quotes) > 0:
        try:
            AnchorValidationService.validate_evidence(
                pdf_text=source_text,
                exact_quotes=exact_quotes,
                reasoning_trace=reasoning_steps,
                contextual_override=contextual_override,
                strictness_level=strictness_level,
            )
            status = "PASS"
        except SemanticEvidenceError:
            status = "FAIL"
    # Track B: Semantic Override
    else:
        if contextual_override:
            status = "PASS"
        else:
            status = "FAIL"

    semantic_reasoning = getattr(extraction, "semantic_reasoning", "") or ""
    # Conservative Safety Principle: We allow the LLM to override a PASS to a FAIL
    # based on semantic reasoning, but never a FAIL to a PASS.
    if "[5. VALIDATION DECISION: FAIL]" in str(semantic_reasoning) or "[5. VALIDATION DECISION: FAIL]" in str(
        reasoning_steps or ""
    ):
        status = "FAIL"

    counter_quote = getattr(extraction, "counter_quote", None)
    if counter_quote and isinstance(counter_quote, str) and counter_quote.strip() and status == "PASS":
        status = "CONTESTED"

    return status


def resolve_majority_vote(
    results: list[dict[str, Any]],
    has_shuffled_atoms: bool,
    chunk_criteria: list[PromptBlock],
    user_payload: str,
    global_source_text: str,
    strictness_level: int,
) -> dict[str, Any]:
    if not results:
        return {}

    if len(results) == 1:
        return copy.deepcopy(results[0])

    if has_shuffled_atoms:
        atom_votes: dict[str, list[dict[str, Any]]] = {}
        for res in results:
            evals = res.get("evaluations", [])
            for ev in evals:
                aid = ev.get("atom_id")
                if aid:
                    if aid not in atom_votes:
                        atom_votes[aid] = []
                    atom_votes[aid].append(ev)

        final_evals = []
        for aid, votes in atom_votes.items():
            pass_votes = 0
            fail_votes = 0
            best_pass = None
            best_fail = None

            for v in votes:
                try:
                    payload = ConsensusVotePayload.model_validate(v)
                    status = evaluate_extraction(payload, global_source_text, strictness_level)
                    if status == "PASS":
                        pass_votes += 1
                        if best_pass is None:
                            best_pass = v
                    else:
                        fail_votes += 1
                        if best_fail is None:
                            best_fail = v
                except Exception as e:
                    logger.warning(f"Failed to parse consensus vote for {aid}: {e}")
                    fail_votes += 1

            if pass_votes > fail_votes:
                chosen = best_pass if best_pass else votes[0]
                chosen["status"] = "PASS"
                chosen["confidence"] = pass_votes / len(votes)
            else:
                chosen = best_fail if best_fail else votes[0]
                chosen["status"] = "FAIL"
                chosen["confidence"] = fail_votes / len(votes) if fail_votes > 0 else 1.0

            final_evals.append(chosen)

        base_res = copy.deepcopy(results[0])
        base_res["evaluations"] = final_evals
        return base_res

    else:
        final_res: dict[str, Any] = copy.deepcopy(results[0])
        for crit in chunk_criteria:
            if crit.category_id == "matrix" or crit.type == "instruction":
                continue

            pass_votes = 0
            fail_votes = 0
            best_pass = None
            best_fail = None

            # Fix list comprehension Any | None typing
            votes_raw = [r.get(crit.id) for r in results]
            block_votes: list[dict[str, Any]] = [v for v in votes_raw if v is not None and isinstance(v, dict)]

            for v in block_votes:
                try:
                    payload = ConsensusVotePayload.model_validate(v)
                    status = evaluate_extraction(payload, global_source_text, strictness_level)
                    if status == "PASS":
                        pass_votes += 1
                        if best_pass is None:
                            best_pass = v
                    else:
                        fail_votes += 1
                        if best_fail is None:
                            best_fail = v
                except Exception as e:
                    logger.warning(f"Failed to parse consensus vote for {crit.id}: {e}")
                    fail_votes += 1

            if pass_votes > fail_votes:
                chosen = best_pass if best_pass else (block_votes[0] if block_votes else {})
                chosen["status"] = "PASS"
                chosen["confidence"] = pass_votes / len(block_votes) if block_votes else 0.0
            else:
                chosen = best_fail if best_fail else (block_votes[0] if block_votes else {})
                chosen["status"] = "FAIL"
                chosen["confidence"] = fail_votes / len(block_votes) if block_votes and fail_votes > 0 else 1.0

            final_res[crit.id] = chosen

        return final_res


class ChunkWorker:
    @staticmethod
    async def process_chunk(
        chunk: Any,
        sem: asyncio.Semaphore | None,
        compiler: Any,
        criteria_blocks: list[PromptBlock],
        user_payload: str,
        global_source_text: str,
        base_system_prompt: str,
        has_search: bool,
        has_shuffled_atoms: bool,
        atom_to_block_ids: dict[str, set[str]],
        effective_mcp_tools: list[Any] | None,
        bound_client: LLMClient,
        step_id: str,
        target_locale: str,
        synthesis_instructions: dict[str, Any] | None,
        output_profile: Any | None,
        strictness_level: int = 1,
        running_event: asyncio.Event | None = None,
        step_metadata: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], TokenUsage | None, list[Any], PromptContextDTO | None]:
        if running_event is not None and not running_event.is_set():
            running_event.set()

        sem = sem or asyncio.Semaphore(1)

        return await ChunkWorker._orchestrate_chunk_with_retry(
            chunk_criteria=criteria_blocks,
            compiler=compiler,
            global_source_text=global_source_text,
            bound_client=bound_client,
            target_locale=target_locale,
            has_shuffled_atoms=has_shuffled_atoms,
            chunk=chunk,
            effective_mcp_tools=effective_mcp_tools,
            synthesis_instructions=synthesis_instructions,
            strictness_level=strictness_level,
            sem=sem,
            step_id=step_id,
            mcp_system_tools=None,
            tool_loop_max_iterations=5,
            step_metadata=step_metadata,
            has_search=has_search,
            atom_to_block_ids=atom_to_block_ids,
            base_system_prompt=base_system_prompt,
            user_payload=user_payload,
            output_profile=output_profile,
        )

    @staticmethod
    async def _orchestrate_chunk_with_retry(
        chunk_criteria: list[PromptBlock],
        compiler: Any,
        global_source_text: str,
        bound_client: LLMClient,
        target_locale: str,
        has_shuffled_atoms: bool,
        chunk: Any,
        effective_mcp_tools: list[Any] | None,
        synthesis_instructions: dict[str, Any] | None,
        strictness_level: int,
        sem: asyncio.Semaphore,
        step_id: str,
        mcp_system_tools: list[Any] | None,
        tool_loop_max_iterations: int,
        step_metadata: dict[str, Any] | None,
        has_search: bool,
        atom_to_block_ids: dict[str, set[str]],
        base_system_prompt: str,
        user_payload: str,
        output_profile: Any | None,
    ) -> tuple[dict[str, Any], TokenUsage | None, list[Any], PromptContextDTO | None]:
        MAX_CHUNK_RETRIES = 2
        attempt = 0

        while attempt <= MAX_CHUNK_RETRIES:
            try:
                chunk_final, chunk_usage, chunk_traces, prompt_context = await ChunkWorker._execute_chunk_logic(
                    chunk_criteria=chunk_criteria,
                    compiler=compiler,
                    global_source_text=global_source_text,
                    bound_client=bound_client,
                    target_locale=target_locale,
                    has_shuffled_atoms=has_shuffled_atoms,
                    chunk=chunk,
                    effective_mcp_tools=effective_mcp_tools,
                    synthesis_instructions=synthesis_instructions,
                    strictness_level=strictness_level,
                    sem=sem,
                    step_id=step_id,
                    mcp_system_tools=mcp_system_tools,
                    tool_loop_max_iterations=tool_loop_max_iterations,
                    step_metadata=step_metadata,
                    has_search=has_search,
                    atom_to_block_ids=atom_to_block_ids,
                    base_system_prompt=base_system_prompt,
                    user_payload=user_payload,
                    output_profile=output_profile,
                )

                if attempt > 0:
                    chunk_final["_dlq_retry_count"] = attempt

                return chunk_final, chunk_usage, chunk_traces, prompt_context

            except (LLMSchemaValidationError, AppException, ExceptionGroup, Exception) as e:

                def _is_structural(exc: BaseException) -> bool:
                    if isinstance(exc, ExceptionGroup):
                        return any(_is_structural(inner) for inner in exc.exceptions)
                    return isinstance(exc, (LLMSchemaValidationError, AppException)) or not _is_transient_chunk_error(
                        exc
                    )

                if attempt < MAX_CHUNK_RETRIES and _is_transient_chunk_error(e) and not _is_structural(e):
                    attempt += 1
                    backoff_seconds = min(10 * (2 ** (attempt - 1)), 60)
                    logger.warning(
                        "[ChunkWorker] Transient error detected. Retrying chunk (attempt %d/%d)...",
                        attempt,
                        MAX_CHUNK_RETRIES,
                    )
                    await asyncio.sleep(backoff_seconds)
                    continue

                # Structural errors are no longer raised, they fall through to DLQ routing

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

                fallback_reason = f"Chunk Processing Failed: {reason_str}"
                chunk_final = {
                    "_dlq_status": "FAILED/DLQ",
                    "reason": fallback_reason,
                }
                if attempt > 0:
                    chunk_final["_dlq_retry_count"] = attempt

                if has_shuffled_atoms and chunk is not None:
                    chunk_final["evaluations"] = []
                    for item in getattr(chunk, "items", []):
                        aid = item.get("atom_id") if isinstance(item, dict) else None
                        if aid:
                            chunk_final["evaluations"].append(
                                {
                                    "atom_id": aid,
                                    "status": "DLQ",
                                    "exact_quote": None,
                                    "contextual_override": False,
                                    "semantic_reasoning": fallback_reason,
                                }
                            )
                else:
                    for crit in chunk_criteria:
                        chunk_final[crit.id] = {
                            "status": "DLQ",
                            "exact_quote": None,
                            "contextual_override": False,
                            "semantic_reasoning": fallback_reason,
                        }

                return chunk_final, None, [], None

        return {}, None, [], None

    @staticmethod
    async def _execute_chunk_logic(
        chunk_criteria: list[PromptBlock],
        compiler: Any,
        global_source_text: str,
        bound_client: LLMClient,
        target_locale: str,
        has_shuffled_atoms: bool,
        chunk: Any,
        effective_mcp_tools: list[Any] | None,
        synthesis_instructions: dict[str, Any] | None,
        strictness_level: int,
        sem: asyncio.Semaphore,
        step_id: str,
        mcp_system_tools: list[Any] | None,
        tool_loop_max_iterations: int,
        step_metadata: dict[str, Any] | None,
        has_search: bool,
        atom_to_block_ids: dict[str, set[str]],
        base_system_prompt: str,
        user_payload: str,
        output_profile: Any | None,
    ) -> tuple[dict[str, Any], TokenUsage | None, list[Any], PromptContextDTO | None]:
        chunk_criteria = list(chunk_criteria)
        chunk_atoms_xml: str | None = None
        pre_flight_results: dict[str, Any] = {}

        if chunk is not None:
            allowed_atom_ids = set()
            if has_shuffled_atoms:
                chunk_matrix_ids = set()
                filtered_items = []
                for item in chunk.items:
                    try:
                        aid_model = AtomIdentifier.model_validate(item)
                        allowed_atom_ids.add(aid_model.atom_id)

                        if aid_model.atom_id in atom_to_block_ids:
                            chunk_matrix_ids.update(atom_to_block_ids[aid_model.atom_id])

                        if FEATURE_FLAG_EXTRACTIVE_SENSOR:
                            tda_for_atom = None
                            for bm in chunk_criteria:
                                if bm.category_id == "matrix" and bm.scales:
                                    for scale in bm.scales:
                                        for claim in scale.claims:
                                            for tda in claim.tda_assertions:
                                                if tda.tda_id == aid_model.atom_id:
                                                    tda_for_atom = tda
                                                    break

                            if tda_for_atom:
                                pf_res = ExtractiveSensorService.pre_evaluate(tda_for_atom, global_source_text)
                                if pf_res.decided:
                                    pre_flight_results[aid_model.atom_id] = pf_res
                                    continue

                        filtered_items.append(item)
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

                chunk = chunk.model_copy(update={"items": filtered_items})
                filtered_criteria = []
                for bm in chunk_criteria:
                    if bm.category_id != "matrix" or bm.id in chunk_matrix_ids:
                        filtered_criteria.append(bm)
                chunk_criteria = filtered_criteria

            blind_items = []
            for item in chunk.items:
                aid = item.get("atom_id")
                blind_items.append({"atom_id": aid, "rule_anchor": aid, "question": item.get("question", "")})

            atoms_json = json.dumps(blind_items, ensure_ascii=False, indent=2)
            chunk_atoms_xml = f"<BLIND_ATOMS_TO_EVALUATE>\\n{atoms_json}\\n</BLIND_ATOMS_TO_EVALUATE>"

        local_dynamic_schema = compiler.build_dynamic_schema(
            schema_name=f"Step_{step_id}_Response",
            criteria=chunk_criteria,
            has_search_result=has_search,
            has_shuffled_atoms=has_shuffled_atoms,
            target_locale=target_locale,
            strictness_level=strictness_level,
        )

        is_lightweight = False
        source_language = "Unknown/Original"
        if step_metadata:
            if step_metadata.get("is_lightweight_extraction"):
                is_lightweight = True
            doc_lang = step_metadata.get("document_language", "Unknown/Original")
            source_language = step_metadata.get("source_language", doc_lang)

        linguistic_context = (
            "<linguistic_context>\\n"
            f"  <source_data_language>{source_language}</source_data_language>\\n"
            f"  <required_output_language>{target_locale}</required_output_language>\\n"
            "  <required_reasoning_language>English</required_reasoning_language>\\n"
            "</linguistic_context>"
        )

        base_system_prompt = f"{linguistic_context}\\n\\n{base_system_prompt}"

        allowed_atom_ids = set()
        if has_shuffled_atoms and chunk is not None:
            for item in chunk.items:
                aid = item.get("atom_id")
                if aid:
                    allowed_atom_ids.add(aid)

        compiled_prompt = compiler.compile_chunk_prompt(
            base_system_prompt=base_system_prompt,
            chunk_criteria=chunk_criteria,
            base_payload=user_payload,
            chunk_atoms_xml=chunk_atoms_xml,
            strictness_level=strictness_level,
            target_locale=target_locale,
            allowed_atom_ids=allowed_atom_ids if has_shuffled_atoms else None,
        )

        prompt_context = PromptContextDTO(
            static_messages=list(compiled_prompt.static_messages),
            dynamic_messages=list(compiled_prompt.dynamic_messages),
            metadata=dict(compiled_prompt.metadata),
        )

        chunk_final: dict[str, Any] = {}
        chunk_usage: TokenUsage | None = None
        chunk_traces: list[Any] = []

        executor = LLMTaskExecutor(prompt_compiler=compiler)
        llm_count = EvaluationRunCount.STANDARD.value if is_lightweight else EvaluationRunCount.ENSEMBLE.value

        async def run_llm_calls(
            prompt: CompiledPrompt, model_schema: type[BaseModel], count: int
        ) -> tuple[list[dict[str, Any]], TokenUsage]:
            results_list: list[dict[str, Any]] = []
            total_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)

            async def _safe_execute(index: int = 0) -> tuple[Any, Any, list[Any]]:
                if index > 0:
                    import random

                    from backend_v2.models.enums import EnsembleJitter

                    base_delay = index * EnsembleJitter.BASE_DELAY.value
                    random_jitter = random.uniform(0.0, EnsembleJitter.BASE_DELAY.value)
                    await asyncio.sleep(base_delay + random_jitter)
                async with sem:
                    try:
                        if effective_mcp_tools:
                            loop_res = await execute_tool_loop(
                                llm_client=bound_client,
                                executor=executor,
                                messages=prompt.to_flat_messages(),
                                response_model=model_schema,
                                allowed_tools=effective_mcp_tools,
                                step_name=step_id,
                                mock_identity=step_id,
                                target_language=target_locale,
                                synthesis_instructions=synthesis_instructions,
                                validation_context={
                                    "strictness_level": strictness_level,
                                    "source_text": global_source_text,
                                    "is_lightweight_extraction": is_lightweight,
                                    "locale": target_locale,
                                    "estimated_token_count": step_metadata.get("estimated_token_count", 0)
                                    if step_metadata
                                    else 0,
                                },
                                source_context=global_source_text,
                            )
                            return (
                                loop_res.result_data,
                                loop_res.usage,
                                loop_res.audit_traces if loop_res.audit_traces else [],
                            )
                        else:
                            res, usg = await executor.execute_structured_task(
                                client=bound_client,
                                messages=prompt,
                                response_model=model_schema,
                                mock_identity=step_id,
                                max_schema_retries=SystemConcurrency.LLM_MAX_RETRIES.value,
                                max_logical_retries=SystemConcurrency.LLM_MAX_RETRIES.value,
                                validation_context={
                                    "strictness_level": strictness_level,
                                    "source_text": global_source_text,
                                    "is_lightweight_extraction": is_lightweight,
                                    "locale": target_locale,
                                    "estimated_token_count": step_metadata.get("estimated_token_count", 0)
                                    if step_metadata
                                    else 0,
                                    "has_mcp_tools": bool(effective_mcp_tools),
                                },
                            )
                            return res, usg, []
                    except (LLMSchemaValidationError, AppException, ExceptionGroup) as e:
                        logger.warning(f"Single LLM call failed in ensemble: {e}")
                        return e, None, []

            last_error = None
            if count > 1:
                tasks_list = []
                async with asyncio.TaskGroup() as tg:
                    for i in range(count):
                        tasks_list.append(tg.create_task(_safe_execute(i)))
                for t in tasks_list:
                    res, usg, trc = t.result()
                    if isinstance(res, Exception):
                        last_error = res
                    elif res:
                        if isinstance(res, BaseModel):
                            results_list.append(res.model_dump(mode="json"))
                        else:
                            results_list.append(dict(res))
                    if usg:
                        total_usage = total_usage + usg
                    if trc:
                        chunk_traces.extend(trc)
            else:
                res, usg, trc = await _safe_execute()
                if isinstance(res, Exception):
                    last_error = res
                elif res:
                    if isinstance(res, BaseModel):
                        results_list.append(res.model_dump(mode="json"))
                    else:
                        results_list.append(dict(res))
                if usg:
                    total_usage = total_usage + usg
                if trc:
                    chunk_traces.extend(trc)

            if not results_list:
                if last_error:
                    raise last_error
                raise AppException(
                    message="All LLM calls failed in the ensemble/standard run.",
                    status_code=500,
                    details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED.value},
                )

            return results_list, total_usage

        target_schema = local_dynamic_schema

        res_list, chunk_usage = await run_llm_calls(compiled_prompt, target_schema, llm_count)
        chunk_final = resolve_majority_vote(
            res_list, has_shuffled_atoms, chunk_criteria, user_payload, global_source_text, strictness_level
        )

        if has_shuffled_atoms and "evaluations" not in chunk_final:
            chunk_final["evaluations"] = []

        if has_shuffled_atoms and "evaluations" in chunk_final:
            for pf_atom_id, pf_res in pre_flight_results.items():
                chunk_final["evaluations"].append(
                    {
                        "atom_id": pf_atom_id,
                        "exact_quotes": [pf_res.exact_quote] if getattr(pf_res, "exact_quote", None) else [],
                        "contextual_override": False,
                        "override_reason": None,
                        "reasoning_steps": "[EXTRACTIVE_SENSOR_PRE_FLIGHT] Fast match.",
                        "falsification_argument": "N/A",
                        "structural_location": "N/A",
                        "localized_anchors_found": [],
                        "decision": True,
                        "semantic_reasoning": "[EXTRACTIVE_SENSOR_PRE_FLIGHT] Deterministic syntax match.",
                    }
                )

            atom_consensus_data: dict[int, dict[str, Any]] = {}
            for idx, atom_dict in enumerate(chunk_final.get("evaluations", [])):
                atom_consensus_data[idx] = {
                    "status": atom_dict.pop("status", None),
                    "confidence": atom_dict.pop("confidence", None),
                }

            validated_response = local_dynamic_schema.model_validate(chunk_final)
            chunk_final = validated_response.model_dump(mode="json")

            for idx, atom_model in enumerate(getattr(validated_response, "evaluations", [])):
                atom_dict = chunk_final["evaluations"][idx]

                c_status = atom_consensus_data.get(idx, {}).get("status")
                c_conf = atom_consensus_data.get(idx, {}).get("confidence")

                if c_status is not None:
                    status = c_status
                    confidence = c_conf
                else:
                    status = evaluate_extraction(atom_model, global_source_text, strictness_level)
                    confidence = None

                atom_dict["status"] = status
                if confidence is not None:
                    atom_dict["confidence"] = confidence

                contextual_override = getattr(atom_model, "contextual_override", False)
                semantic_reasoning = getattr(atom_model, "semantic_reasoning", "")

                if isinstance(contextual_override, bool) and contextual_override and semantic_reasoning:
                    atom_dict["exact_quote"] = f"[INFERRED] {semantic_reasoning}"
                elif contextual_override and not isinstance(contextual_override, bool):
                    pass

                sr = semantic_reasoning or ""
                if not isinstance(sr, str):
                    sr = ""
                atom_dict["semantic_reasoning"] = f"{sr}\\n\\n[5. VALIDATION DECISION: {status}]"

        else:
            block_consensus_data: dict[str, dict[str, Any]] = {}
            for crit in chunk_criteria:
                if crit.id in chunk_final and crit.category_id != "matrix" and crit.type != "instruction":
                    block_dict = chunk_final[crit.id]
                    block_consensus_data[crit.id] = {
                        "status": block_dict.pop("status", None),
                        "confidence": block_dict.pop("confidence", None),
                    }

            validated_response = local_dynamic_schema.model_validate(chunk_final)
            chunk_final = validated_response.model_dump(mode="json")

            for crit in chunk_criteria:
                if hasattr(validated_response, crit.id) and crit.category_id != "matrix" and crit.type != "instruction":
                    block_model = getattr(validated_response, crit.id)
                    block_dict = chunk_final[crit.id]

                    c_status = block_consensus_data.get(crit.id, {}).get("status")
                    c_conf = block_consensus_data.get(crit.id, {}).get("confidence")

                    if c_status is not None:
                        status = c_status
                        confidence = c_conf
                    else:
                        status = evaluate_extraction(block_model, global_source_text, strictness_level)
                        confidence = None

                    block_dict["status"] = status
                    if confidence is not None:
                        block_dict["confidence"] = confidence

                    contextual_override = getattr(block_model, "contextual_override", False)
                    semantic_reasoning = getattr(block_model, "semantic_reasoning", "")

                    if isinstance(contextual_override, bool) and contextual_override and semantic_reasoning:
                        block_dict["exact_quote"] = f"[INFERRED] {semantic_reasoning}"

                    sr = semantic_reasoning or ""
                    if not isinstance(sr, str):
                        sr = ""
                    block_dict["semantic_reasoning"] = f"{sr}\\n\\n[5. VALIDATION DECISION: {status}]"

        return chunk_final, chunk_usage, chunk_traces, prompt_context
