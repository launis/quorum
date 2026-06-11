import asyncio
import copy
import json
import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes, LLMSchemaValidationError, SemanticEvidenceError
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.enums import EvaluationRunCount, SystemConcurrency
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
    premise_1_quote: str | None = None
    premise_2_quote: str | None = None
    semantic_reasoning: str | None = ""


def evaluate_extraction(extraction: Any, source_text: str, is_negative_rule: bool, strictness_level: int = 50) -> str:
    """Evaluates the deterministic extraction with dual-track validation.
    Returns PASS, FAIL, or DLQ.
    """
    exact_quote = getattr(extraction, "exact_quote", None)
    contextual_override = getattr(extraction, "contextual_override", False)
    premise_1_quote = getattr(extraction, "premise_1_quote", None)
    semantic_reasoning = getattr(extraction, "semantic_reasoning", None)

    # Track A: Physical Match
    if exact_quote:
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
            if strictness_level >= 100:
                status = "FAIL"
            elif premise_1_quote:
                try:
                    AnchorValidationService.validate_evidence(
                        pdf_text=source_text,
                        exact_quote=premise_1_quote,
                        reasoning_trace=semantic_reasoning,
                        contextual_override=True,
                    )
                    status = "PASS"
                except SemanticEvidenceError:
                    status = "FAIL"
            else:
                status = "FAIL"
        else:
            status = "FAIL"

    # Negative condition handling
    if is_negative_rule:
        if status == "PASS":
            status = "FAIL"
        elif status == "FAIL":
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
    source_text: str,
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
            premise_1_quote=v.get("premise_1_quote"),
            premise_2_quote=v.get("premise_2_quote"),
            semantic_reasoning=v.get("semantic_reasoning", ""),
        )
        status = evaluate_extraction(payload, source_text, is_inverse_evidence, strictness_level)
        statuses.append(status)

    # Minority Veto: One FAIL on an inverse_evidence atom overrules all
    if is_inverse_evidence and "FAIL" in statuses:
        return "FAIL", statuses

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
                final_status, statuses = _apply_minority_veto(votes, user_payload, is_inverse, strictness_level)
                confidence = _calculate_confidence(statuses, final_status)

                # Keep quotes and overrides from PASS votes if available, else from all votes
                valid_votes = [v for i, v in enumerate(votes) if statuses[i] in ("PASS", "DLQ")]
                if not valid_votes:  # fallback if all are FAIL
                    valid_votes = votes

                overrides = [v.get("contextual_override", False) for v in valid_votes]
                quotes = [v.get("exact_quote") for v in valid_votes]
                p1_quotes = [v.get("premise_1_quote") for v in valid_votes]
                p2_quotes = [v.get("premise_2_quote") for v in valid_votes]
                reasonings = [v.get("semantic_reasoning", "") for v in valid_votes]

                final_override = sum(1 for o in overrides if o) >= 2
                valid_quotes = [q for q in quotes if q and q != "[CONTEXTUAL_OVERRIDE_APPLIED]"]
                if valid_quotes and not final_override:
                    final_quote = max(set(valid_quotes), key=valid_quotes.count)
                else:
                    final_quote = None

                valid_p1_quotes = [q for q in p1_quotes if q]
                final_p1 = max(set(valid_p1_quotes), key=valid_p1_quotes.count) if valid_p1_quotes else None
                valid_p2_quotes = [q for q in p2_quotes if q]
                final_p2 = max(set(valid_p2_quotes), key=valid_p2_quotes.count) if valid_p2_quotes else None
                final_reasoning = max(set(reasonings), key=reasonings.count)

                merged["evaluations"][idx]["contextual_override"] = final_override
                merged["evaluations"][idx]["exact_quote"] = final_quote
                merged["evaluations"][idx]["premise_1_quote"] = final_p1
                merged["evaluations"][idx]["premise_2_quote"] = final_p2
                merged["evaluations"][idx]["semantic_reasoning"] = final_reasoning
                merged["evaluations"][idx]["status"] = final_status
                merged["evaluations"][idx]["confidence"] = confidence
    else:
        for block in criteria_blocks:
            if block.id in merged and block.category_id != "matrix" and block.type != "instruction":
                votes = [res[block.id] for res in res_list if block.id in res]
                if votes:
                    is_inverse = False  # Block level is_inverse doesn't map cleanly to TDA level here, assumed false for standard blocks
                    final_status, statuses = _apply_minority_veto(votes, user_payload, is_inverse, strictness_level)
                    confidence = _calculate_confidence(statuses, final_status)

                    valid_votes = [v for i, v in enumerate(votes) if statuses[i] in ("PASS", "DLQ")]
                    if not valid_votes:
                        valid_votes = votes

                    overrides = [v.get("contextual_override", False) for v in valid_votes]
                    quotes = [v.get("exact_quote") for v in valid_votes]
                    p1_quotes = [v.get("premise_1_quote") for v in valid_votes]
                    p2_quotes = [v.get("premise_2_quote") for v in valid_votes]
                    reasonings = [v.get("semantic_reasoning", "") for v in valid_votes]

                    final_override = sum(1 for o in overrides if o) >= 2
                    valid_quotes = [q for q in quotes if q and q != "[CONTEXTUAL_OVERRIDE_APPLIED]"]
                    if valid_quotes and not final_override:
                        final_quote = max(set(valid_quotes), key=valid_quotes.count)
                    else:
                        final_quote = None

                    valid_p1_quotes = [q for q in p1_quotes if q]
                    final_p1 = max(set(valid_p1_quotes), key=valid_p1_quotes.count) if valid_p1_quotes else None
                    valid_p2_quotes = [q for q in p2_quotes if q]
                    final_p2 = max(set(valid_p2_quotes), key=valid_p2_quotes.count) if valid_p2_quotes else None
                    final_reasoning = max(set(reasonings), key=reasonings.count)

                    merged[block.id]["contextual_override"] = final_override
                    merged[block.id]["exact_quote"] = final_quote
                    merged[block.id]["premise_1_quote"] = final_p1
                    merged[block.id]["premise_2_quote"] = final_p2
                    merged[block.id]["semantic_reasoning"] = final_reasoning
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

            is_lightweight = False
            if step_metadata and step_metadata.get("is_lightweight_extraction"):
                is_lightweight = True

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
                            "is_lightweight_extraction": is_lightweight,
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

                    llm_count = (
                        EvaluationRunCount.ENSEMBLE.value if is_lightweight else EvaluationRunCount.STANDARD.value
                    )

                    async def run_llm_calls(
                        prompt: CompiledPrompt, model_schema: type[BaseModel], count: int
                    ) -> tuple[list[dict[str, Any]], TokenUsage]:
                        """Execute LLM calls using native CompiledPrompt architecture."""
                        results_list = []
                        total_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)

                        async def _safe_execute() -> tuple[Any, Any]:
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
                                        "source_text": user_payload,
                                        "is_lightweight_extraction": is_lightweight,
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
                        SduiResponseList
                        if (output_profile is not None and not criteria_blocks)
                        else local_dynamic_schema
                    )
                    res_list, chunk_usage = await run_llm_calls(compiled_prompt, target_schema, llm_count)
                    chunk_final = resolve_majority_vote(
                        res_list, has_shuffled_atoms, chunk_criteria, user_payload, strictness_level
                    )

                    # Step 4: Map-Merge Orchestration & Trace Continuity Injection
                    if has_shuffled_atoms and "evaluations" in chunk_final:
                        # Evaluate each flattened atom
                        for i, atom_data in enumerate(chunk_final["evaluations"]):
                            atom_id = atom_data["atom_id"]

                            temp_atom1 = ExtractionPayload(
                                exact_quote=atom_data.get("exact_quote"),
                                contextual_override=atom_data.get("contextual_override", False),
                                premise_1_quote=atom_data.get("premise_1_quote"),
                                premise_2_quote=atom_data.get("premise_2_quote"),
                                semantic_reasoning=atom_data.get("semantic_reasoning", ""),
                            )
                            is_negative_rule = False
                            for crit in chunk_criteria:
                                if crit.scales:
                                    for scale in crit.scales:
                                        for claim in scale.claims:
                                            for tda in claim.tda_assertions:
                                                if tda.tda_id == atom_id and tda.inverse_evidence:
                                                    is_negative_rule = True
                                                    break

                            status = evaluate_extraction(temp_atom1, user_payload, is_negative_rule, strictness_level)
                            atom_data["status"] = status
                            if temp_atom1.contextual_override and temp_atom1.semantic_reasoning:
                                atom_data["exact_quote"] = f"[INFERRED] {temp_atom1.semantic_reasoning}"
                            sr = atom_data.get("semantic_reasoning", "")
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
                                    exact_quote=block_data.get("exact_quote"),
                                    contextual_override=block_data.get("contextual_override", False),
                                    premise_1_quote=block_data.get("premise_1_quote"),
                                    premise_2_quote=block_data.get("premise_2_quote"),
                                    semantic_reasoning=block_data.get("semantic_reasoning", ""),
                                )
                                status = evaluate_extraction(
                                    temp_block1, user_payload, is_negative_rule, strictness_level
                                )
                                block_data["status"] = status
                                if temp_block1.contextual_override and temp_block1.semantic_reasoning:
                                    block_data["exact_quote"] = f"[INFERRED] {temp_block1.semantic_reasoning}"

                                sr = block_data.get("semantic_reasoning", "")
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

                return chunk_final, None, []
