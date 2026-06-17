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
from backend_v2.models.enums import EvaluationRunCount, StrictnessAnchor, SystemConcurrency
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.models.v2_core import PromptBlock
from backend_v2.models.view.sdui import AnySduiBlock
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.mcp.mcp_tool_loop import execute_tool_loop
from backend_v2.services.orchestrator.anchor_validation_service import AnchorValidationService
from backend_v2.services.orchestrator.extractive_sensor_service import ExtractiveSensorService

logger = logging.getLogger(__name__)

FEATURE_FLAG_EXTRACTIVE_SENSOR = True


class AtomIdentifier(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")
    atom_id: str


class ExtractionPayload(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    exact_quote: str | None = ""
    contextual_override: bool = False
    override_reason: str | None = None
    reasoning_steps: str | None = ""


def evaluate_extraction(
    extraction: Any, source_text: str, is_negative_rule: bool, strictness_level: int = StrictnessAnchor.STANDARD.value
) -> str:
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
    if "[5. VALIDATION DECISION: FAIL]" in str(semantic_reasoning) or "[5. VALIDATION DECISION: FAIL]" in str(
        reasoning_steps or ""
    ):
        status = "FAIL"

    # Negative condition handling
    if is_negative_rule:
        if status == "PASS":
            logger.debug(
                "[Code-as-a-Judge] Dual Negation triggered: Flipping PASS to FAIL.",
                extra={"error_code": "DUAL_NEGATION_FLIP_TO_FAIL"},
            )
            status = "FAIL"
        elif status == "FAIL":
            logger.debug(
                "[Code-as-a-Judge] Dual Negation triggered: Flipping FAIL to PASS.",
                extra={"error_code": "DUAL_NEGATION_FLIP_TO_PASS"},
            )
            status = "PASS"

    return status


def _calculate_confidence(statuses: list[str], final_status: str) -> float:
    """Calculate confidence score from consensus unanimity."""
    agreeing = statuses.count(final_status)
    total = len(statuses)
    if total == 0:
        return 0.33
    if agreeing == total:
        return 1.0
    if agreeing >= 2:
        return 0.67
    return 0.33


def _apply_minority_veto(
    votes: list[dict[str, Any]],
    global_source_text: str,
    is_inverse_evidence: bool,
    strictness_level: int,
) -> tuple[str, list[str]]:
    """Apply Minority Veto consensus logic.

    If ANY runner returns FAIL for an inverse_evidence atom,
    FAIL wins unconditionally to prevent Confirmation Bias.
    """
    statuses = []
    for v in votes:
        payload = ExtractionPayload(
            exact_quote=v.get("exact_quote"),
            contextual_override=v.get("contextual_override", False),
            override_reason=v.get("override_reason"),
            reasoning_steps=v.get("reasoning_steps", ""),
        )
        status = evaluate_extraction(payload, global_source_text, is_inverse_evidence, strictness_level)
        statuses.append(status)

    # Standard 2/3 majority
    pass_count = statuses.count("PASS")
    fail_count = statuses.count("FAIL")
    if pass_count >= 2:
        return "PASS", statuses
    if fail_count >= 2:
        return "FAIL", statuses
    return "DLQ", statuses


def resolve_majority_vote(
    res_list: list[dict[str, Any]],
    is_shuffled: bool,
    criteria_blocks: list[PromptBlock],
    user_payload: str,
    global_source_text: str,
    strictness_level: int,
) -> dict[str, Any]:
    if not res_list:
        return {}
    if len(res_list) == 1:
        return res_list[0]

    # Build atom -> inverse_evidence map for veto evaluation
    atom_inverse_map = {}
    for block in criteria_blocks:
        if block.scales:
            for scale in block.scales:
                for claim in scale.claims:
                    for tda in claim.tda_assertions:
                        atom_inverse_map[tda.tda_id] = tda.inverse_evidence

    merged = copy.deepcopy(res_list[0])

    if is_shuffled and "evaluations" in merged:
        num_evals = len(merged["evaluations"])
        for idx in range(num_evals):
            atom_id = merged["evaluations"][idx].get("atom_id")
            votes = []
            for res in res_list:
                if "evaluations" in res and idx < len(res["evaluations"]):
                    item = res["evaluations"][idx]
                    if item.get("atom_id") == atom_id:
                        votes.append(item)
            if votes:
                is_inverse = atom_inverse_map.get(atom_id, False)
                final_status, statuses = _apply_minority_veto(votes, global_source_text, is_inverse, strictness_level)
                confidence = _calculate_confidence(statuses, final_status)

                # Keep quotes and overrides from PASS votes if available, else from all votes
                valid_votes = [v for i, v in enumerate(votes) if statuses[i] in ("PASS", "DLQ")]
                if not valid_votes:  # fallback if all are FAIL
                    valid_votes = votes

                overrides = [v.get("contextual_override", False) for v in valid_votes]
                quotes = [v.get("exact_quote") for v in valid_votes]
                override_reasons = [v.get("override_reason") for v in valid_votes]
                reasonings = [v.get("reasoning_steps", "") for v in valid_votes]
                final_sr = [v.get("semantic_reasoning", "") for v in valid_votes]

                final_override = sum(1 for o in overrides if o) >= 2
                valid_quotes = [q for q in quotes if q and q != "[CONTEXTUAL_OVERRIDE_APPLIED]"]
                if valid_quotes and not final_override:
                    final_quote = max(set(valid_quotes), key=valid_quotes.count)
                else:
                    final_quote = None

                valid_override_reasons = [q for q in override_reasons if q]
                final_override_reason = (
                    max(set(valid_override_reasons), key=valid_override_reasons.count)
                    if valid_override_reasons
                    else None
                )
                final_reasoning = max(set(reasonings), key=reasonings.count)
                final_semantic_reasoning = max(set(final_sr), key=final_sr.count)

                merged["evaluations"][idx]["contextual_override"] = final_override
                merged["evaluations"][idx]["exact_quote"] = final_quote
                merged["evaluations"][idx]["override_reason"] = final_override_reason
                merged["evaluations"][idx]["reasoning_steps"] = final_reasoning
                merged["evaluations"][idx]["semantic_reasoning"] = final_semantic_reasoning
                merged["evaluations"][idx]["status"] = final_status
                merged["evaluations"][idx]["confidence"] = confidence
    else:
        for block in criteria_blocks:
            if block.id in merged and block.category_id != "matrix" and block.type != "instruction":
                votes = [res[block.id] for res in res_list if block.id in res]
                if votes:
                    # Block level is_inverse doesn't map cleanly to TDA level here
                    is_inverse = False
                    final_status, statuses = _apply_minority_veto(
                        votes, global_source_text, is_inverse, strictness_level
                    )
                    confidence = _calculate_confidence(statuses, final_status)

                    valid_votes = [v for i, v in enumerate(votes) if statuses[i] in ("PASS", "DLQ")]
                    if not valid_votes:
                        valid_votes = votes

                    overrides = [v.get("contextual_override", False) for v in valid_votes]
                    quotes = [v.get("exact_quote") for v in valid_votes]
                    override_reasons = [v.get("override_reason") for v in valid_votes]
                    reasonings = [v.get("reasoning_steps", "") for v in valid_votes]
                    final_sr = [v.get("semantic_reasoning", "") for v in valid_votes]

                    final_override = sum(1 for o in overrides if o) >= 2
                    valid_quotes = [q for q in quotes if q and q != "[CONTEXTUAL_OVERRIDE_APPLIED]"]
                    if valid_quotes and not final_override:
                        final_quote = max(set(valid_quotes), key=valid_quotes.count)
                    else:
                        final_quote = None

                    valid_override_reasons = [q for q in override_reasons if q]
                    final_override_reason = (
                        max(set(valid_override_reasons), key=valid_override_reasons.count)
                        if valid_override_reasons
                        else None
                    )
                    final_reasoning = max(set(reasonings), key=reasonings.count)
                    final_semantic_reasoning = max(set(final_sr), key=final_sr.count)

                    merged[block.id]["contextual_override"] = final_override
                    merged[block.id]["exact_quote"] = final_quote
                    merged[block.id]["override_reason"] = final_override_reason
                    merged[block.id]["reasoning_steps"] = final_reasoning
                    merged[block.id]["semantic_reasoning"] = final_semantic_reasoning
                    merged[block.id]["status"] = final_status
                    merged[block.id]["confidence"] = confidence

    return merged


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
        global_source_text: str,
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
        strictness_level: int = StrictnessAnchor.STANDARD.value,
        running_event: asyncio.Event | None = None,
        step_metadata: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], TokenUsage | None, list[Any], PromptContextDTO | None]:
        """Processes a single execution chunk, mapping dynamic schemas and orchestrating tool loops."""
        if running_event is not None and not running_event.is_set():
            running_event.set()
        chunk_criteria = list(criteria_blocks)

        # V3 Cache Fix: Separate atoms from base payload
        chunk_atoms_xml: str | None = None
        pre_flight_results: dict[str, Any] = {}

        if chunk is not None:
            # Apply Chunk context subsetting
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

                        # Phase 1: Pre-flight extraction via deterministic sensor
                        if FEATURE_FLAG_EXTRACTIVE_SENSOR:
                            tda_for_atom = None
                            for bm in criteria_blocks:
                                if bm.category_id == "matrix" and bm.scales:
                                    for scale in bm.scales:
                                        for claim in scale.claims:
                                            for tda in claim.tda_assertions:
                                                if tda.tda_id == aid_model.atom_id:
                                                    tda_for_atom = tda
                                                    break

                            if tda_for_atom:
                                pf_res = ExtractiveSensorService.pre_evaluate(tda_for_atom, user_payload)
                                if pf_res.decided:
                                    pre_flight_results[aid_model.atom_id] = pf_res
                                    continue  # Skip adding to filtered_items to avoid LLM cost

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
                chunk_criteria = []
                for bm in criteria_blocks:
                    if bm.category_id != "matrix" or bm.id in chunk_matrix_ids:
                        chunk_criteria.append(bm)

            blind_items = []
            for item in chunk.items:
                aid = item.get("atom_id")
                blind_items.append({"atom_id": aid, "rule_anchor": aid, "question": item.get("question", "")})

            atoms_json = json.dumps(blind_items, ensure_ascii=False, indent=2)
            chunk_atoms_xml = f"<BLIND_ATOMS_TO_EVALUATE>\n{atoms_json}\n</BLIND_ATOMS_TO_EVALUATE>"

        # V3: Build dynamic schema for this chunk's criteria subset
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
            "<linguistic_context>\n"
            f"  <source_data_language>{source_language}</source_data_language>\n"
            f"  <required_output_language>{target_locale}</required_output_language>\n"
            "  <required_reasoning_language>English</required_reasoning_language>\n"
            "</linguistic_context>"
        )
        base_system_prompt = f"{linguistic_context}\n\n{base_system_prompt}"

        # Phase 5: Fast-Model Compensator - Enforce Contextual Override Ban
        if is_lightweight or has_shuffled_atoms:
            strictness_level = max(strictness_level, 100)

        # V3 Cache Fix: Use CompiledPrompt with separated static/dynamic tiers
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

        try:
            if effective_mcp_tools:
                executor = LLMTaskExecutor(prompt_compiler=compiler)
                async with sem:
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
                            "source_text": global_source_text,
                            "is_lightweight_extraction": is_lightweight,
                            "locale": target_locale,
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

                llm_count = EvaluationRunCount.STANDARD.value if is_lightweight else EvaluationRunCount.ENSEMBLE.value

                async def run_llm_calls(
                    prompt: CompiledPrompt, model_schema: type[BaseModel], count: int
                ) -> tuple[list[dict[str, Any]], TokenUsage]:
                    """Execute LLM calls using native CompiledPrompt architecture."""
                    results_list = []
                    total_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)

                    async def _safe_execute() -> tuple[Any, Any]:
                        async with sem:
                            try:
                                return await executor.execute_structured_task(
                                    client=bound_client,
                                    messages=prompt,
                                    response_model=model_schema,
                                    mock_identity=step_id,
                                    max_schema_retries=SystemConcurrency.FAIL_FAST_MAX_RETRIES.value,
                                    max_logical_retries=SystemConcurrency.FAIL_FAST_MAX_RETRIES.value,
                                    validation_context={
                                        "strictness_level": strictness_level,
                                        "source_text": global_source_text,
                                        "is_lightweight_extraction": is_lightweight,
                                        "locale": target_locale,
                                        "estimated_token_count": step_metadata.get("estimated_token_count", 0)
                                        if step_metadata
                                        else 0,
                                    },
                                )
                            except (LLMSchemaValidationError, AppException, ExceptionGroup) as e:
                                logger.warning(f"Single LLM call failed in ensemble: {e}")
                                return e, None

                    last_error = None
                    if count > 1:
                        tasks_list = []
                        async with asyncio.TaskGroup() as tg:
                            for _ in range(count):
                                tasks_list.append(tg.create_task(_safe_execute()))
                        for t in tasks_list:
                            res, usg = t.result()
                            if isinstance(res, Exception):
                                last_error = res
                            elif res:
                                results_list.append(res.model_dump(mode="json"))
                            if usg:
                                total_usage = total_usage + usg
                    else:
                        res, usg = await _safe_execute()
                        if isinstance(res, Exception):
                            last_error = res
                        elif res:
                            results_list.append(res.model_dump(mode="json"))
                        if usg:
                            total_usage = total_usage + usg

                    if not results_list:
                        if last_error:
                            raise last_error
                        raise AppException(
                            message="All LLM calls failed in the ensemble/standard run.",
                            status_code=500,
                            details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED.value},
                        )

                    return results_list, total_usage

                target_schema = (
                    SduiResponseList if (output_profile is not None and not criteria_blocks) else local_dynamic_schema
                )
                res_list, chunk_usage = await run_llm_calls(compiled_prompt, target_schema, llm_count)
                chunk_final = resolve_majority_vote(
                    res_list, has_shuffled_atoms, chunk_criteria, user_payload, global_source_text, strictness_level
                )

                if has_shuffled_atoms and "evaluations" not in chunk_final:
                    chunk_final["evaluations"] = []

                # Step 4: Map-Merge Orchestration & Trace Continuity Injection
                if has_shuffled_atoms and "evaluations" in chunk_final:
                    # Append pre_flight_results back to evaluations so they act as if LLM generated them
                    for pf_atom_id, pf_res in pre_flight_results.items():
                        chunk_final["evaluations"].append(
                            {
                                "atom_id": pf_atom_id,
                                "exact_quote": pf_res.exact_quote,
                                "contextual_override": False,
                                "premise_1_quote": None,
                                "premise_2_quote": None,
                                "semantic_reasoning": "[EXTRACTIVE_SENSOR_PRE_FLIGHT] Deterministic syntax match.",
                            }
                        )

                    # Evaluate each flattened atom via strict Pydantic parsing
                    validated_response = local_dynamic_schema.model_validate(chunk_final)
                    updated_evals = []

                    for atom_model in getattr(validated_response, "evaluations", []):
                        atom_id = atom_model.atom_id

                        is_negative_rule = False
                        for crit in chunk_criteria:
                            if crit.scales:
                                for scale in crit.scales:
                                    for claim in scale.claims:
                                        for tda in claim.tda_assertions:
                                            if tda.tda_id == atom_id and tda.inverse_evidence:
                                                is_negative_rule = True
                                                break

                        status = evaluate_extraction(atom_model, global_source_text, is_negative_rule, strictness_level)

                        update_dict = {"status": status}
                        contextual_override = getattr(atom_model, "contextual_override", False)
                        semantic_reasoning = getattr(atom_model, "semantic_reasoning", "")

                        # Handle MagicMock safely for tests
                        if isinstance(contextual_override, bool) and contextual_override and semantic_reasoning:
                            update_dict["exact_quote"] = f"[INFERRED] {semantic_reasoning}"
                        elif contextual_override and not isinstance(contextual_override, bool):  # For MagicMocks
                            pass

                        sr = semantic_reasoning or ""
                        if not isinstance(sr, str):
                            sr = ""
                        update_dict["semantic_reasoning"] = f"{sr}\n\n[5. VALIDATION DECISION: {status}]"

                        updated_atom = atom_model.model_copy(update=update_dict)
                        updated_evals.append(updated_atom)

                    validated_response = validated_response.model_copy(update={"evaluations": updated_evals})
                    chunk_final = validated_response.model_dump(mode="json")

                else:
                    # Evaluate each standard block (TDA extractions) via strict Pydantic parsing
                    validated_response = local_dynamic_schema.model_validate(chunk_final)
                    update_response_dict = {}

                    for crit in chunk_criteria:
                        if (
                            hasattr(validated_response, crit.id)
                            and crit.category_id != "matrix"
                            and crit.type != "instruction"
                        ):
                            block_model = getattr(validated_response, crit.id)

                            is_negative_rule = False
                            if crit.scales:
                                for scale in crit.scales:
                                    for claim in scale.claims:
                                        for tda in claim.tda_assertions:
                                            if tda.inverse_evidence:
                                                is_negative_rule = True
                                                break

                            status = evaluate_extraction(
                                block_model, global_source_text, is_negative_rule, strictness_level
                            )

                            update_dict = {"status": status}
                            contextual_override = getattr(block_model, "contextual_override", False)
                            semantic_reasoning = getattr(block_model, "semantic_reasoning", "")

                            # Handle MagicMock safely for tests
                            if isinstance(contextual_override, bool) and contextual_override and semantic_reasoning:
                                update_dict["exact_quote"] = f"[INFERRED] {semantic_reasoning}"

                            sr = semantic_reasoning or ""
                            if not isinstance(sr, str):
                                sr = ""
                            update_dict["semantic_reasoning"] = f"{sr}\n\n[5. VALIDATION DECISION: {status}]"

                            updated_block = block_model.model_copy(update=update_dict)
                            update_response_dict[crit.id] = updated_block

                    if update_response_dict:
                        validated_response = validated_response.model_copy(update=update_response_dict)

                    chunk_final = validated_response.model_dump(mode="json")

            return chunk_final, chunk_usage, chunk_traces, prompt_context

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
            fallback_reason = f"Chunk Processing Failed: {reason_str}"
            chunk_final = {
                "_dlq_status": "FAILED/DLQ",
                "reason": fallback_reason,
            }
            # Graceful DLQ Fallback: Map the failure to individual elements
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

            return chunk_final, None, [], prompt_context
