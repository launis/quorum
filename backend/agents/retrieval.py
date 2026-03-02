"""Retrieval Agent implementation."""

import logging
from typing import Any

from fastapi import status

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent
from backend.database.factory import get_repository
from backend.database.wrapper import get_db_client
from backend.exceptions import AgentExecutionError, AppException, ErrorCodes
from backend.models.domain import ContextData, ContextDataDTO, Precedent, RetrievalInput

# 3. Local Imports
from backend.settings import get_settings

logger = logging.getLogger(__name__)


class RetrievalAgent(BaseAgent[RetrievalInput, ContextData]):
    """Hakija-agentti (Retrieval Agent).

    Retrieves organizational precedents and context from the database.
    Replaces the functional 'retrieve_context' task to ensure metadata injection.
    """

    state_field = "step_context"

    INPUT_SCHEMA = RetrievalInput
    DTO_SCHEMA = ContextDataDTO
    OUTPUT_SCHEMA = ContextData

    async def execute(
        self,
        input_data: RetrievalInput,
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> ContextData:
        """Executes the retrieval logic (DB Precedents + Knowledge Base).

        Args:
            input_data (RetrievalInput): Inputs containing 'organization_id' and optional 'query'.
            execution_context (dict[str, Any] | None, optional): Access to global state.
            system_instruction (str | None, optional): Legacy prompt (unused).
            **kwargs: Additional parameters.

        Returns:
            ContextData: ContextData model with precedents and knowledge items.

        Raises:
            AgentExecutionError: If 'organization_id' is missing or retrieval fails.
        """
        # --- STANDARD LOGGING & HOOKS (Manual Implementation) ---
        logger.info(f"[{self.__class__.__name__}] Starting execution...")
        # Note: prepare_context usually just logs or formats prompt.
        # RetrievalAgent doesn't use prompt, but we leave hook if needed.

        logger.info(f"[{self.__class__.__name__}] >>> EXECUTION START <<<")
        # --------------------------------------------------------

        # 1. Access Inputs (Fail Fast)
        org_id = input_data.organization_id

        if not org_id:
            msg = "[RetrievalAgent] organization_id missing. Tenant isolation violated."
            logger.error(f"{ErrorCodes.AGENT_EXECUTION_CRITICAL}: {msg}")
            raise AgentExecutionError(
                detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                original_error=ValueError(msg),
                agent_name="RetrievalAgent"
            )

        logger.info(f"[{self.__class__.__name__}] Running for Org: {org_id}...")

        # 2. Dependency Resolution
        settings = get_settings()
        db_client = get_db_client()
        repo = await get_repository(settings, db_client)

        try:
            # 3. Query DB
            try:
                all_execs = await repo.get_all_executions(organization_id=org_id)
            except TypeError:
                all_execs = await repo.get_all_executions()

            # 4. Filter Completed
            # ExecutionRecord is a Pydantic model, not a dict.
            results = [x for x in all_execs if x.status == "completed"]
            # executed_at/end_time is now completed_at in V2 domain
            from datetime import datetime, timezone

            results.sort(key=lambda x: x.completed_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)

            precedents: list[Precedent] = []

            # Use Configured Limits (No Magic Numbers)
            scan_depth = settings.max_precedent_scan_depth
            return_count = settings.max_precedent_return_count

            # 5. Extract Precedents
            for res in results[:scan_depth]:
                # ExecutionRecord -> results (WorkflowState) -> execution_trace (List[TraceEvent])
                wf_state = res.results

                # Zero-Compromise: No Surface-Level Patches.
                # If the DB returns a dict for a Pydantic field, that is a Data Integrity Violation.
                # However, Pydantic V2 often auto-inflates. If it IS a dict here, it means
                # strict typing failed upstream or DB driver is loose.
                # We raise an error instead of patching it silent_ly.

                from backend.models.state import WorkflowState

                # RECOVERY: If Pydantic loaded results as strict Dict (due to Union type), inflate it here.
                if isinstance(wf_state, dict):
                    try:
                        wf_state = WorkflowState.model_validate(wf_state)
                    except Exception as e:
                        # Fallthrough to fail-fast below if inflation fails
                        logger.warning(f"[RetrievalAgent] Failed to auto-inflate execution {res.id}: {e}")

                if not isinstance(wf_state, WorkflowState):
                    # FAIL FAST: Data Corruption detected.
                    raise AppException(
                        message=f"Execution {res.id} has invalid state type: {type(wf_state)}. Expected WorkflowState.",
                        status_code=500,
                        details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR},
                    )

                trace_events = wf_state.execution_trace
                if not trace_events:
                    continue

                judge_outputs = {}

                from backend.models.domain.judge import JudgeOutput
                from backend.utils.pydantic_utils import inflate

                for event in trace_events:
                    if event.event_type == "output" and "judge" in event.step_name:
                        # Attempt strict inflation -> "Quacks like a Judge"
                        try:
                            judge_candidate = inflate(event.content, JudgeOutput)
                            if judge_candidate:
                                # Use step_name as label
                                label = (
                                    event.step_name.replace("step_judge_", "")
                                    .replace("step_judge", "Standard")
                                    .replace("_", " ")
                                    .title()
                                )
                                if label == "Standard":
                                    label = "Standard"

                                judge_outputs[label] = judge_candidate
                        except Exception as e:
                            error_code = ErrorCodes.VALIDATION_FAILED
                            logger.error(f"[RetrievalAgent] {error_code.name}: Output validation failed: {e}", exc_info=True)
                            raise AppException(
                                message=f"Event output validation failed: {e}",
                                status_code=status.HTTP_400_BAD_REQUEST,
                                details={
                                    "error_code": error_code.value,
                                    "original_error": str(e)
                                },
                            ) from e

                if judge_outputs:
                    score_parts = []
                    verdict_parts = []

                    for label, judge_model in judge_outputs.items():
                        avg = judge_model.score_card.total_score
                        score_parts.append(f"{label}: {avg:.2f}")
                        verdict_parts.append(f"{label}: {judge_model.score_card.verdict[:50]}...")

                    score_summary = " | ".join(score_parts)
                    verdict_summary = " || ".join(verdict_parts)

                    precedents.append(
                        Precedent(
                            id=str(res.id),
                            date=str(res.completed_at.isoformat() if res.completed_at else "unknown"),
                            scores=score_summary,
                            verdict=verdict_summary,
                        )
                    )
            # Keep last N (most recent)
            selected_precedents = precedents[:return_count] if precedents else []

            # Format Text (Precedents)
            precedent_text = "=== ENNAKKOTAPAUKSET (PRECEDENTS) ===\n"
            if not selected_precedents:
                precedent_text += "Ei aiempia tapauksia tiedostossa.\n"
            else:
                for p in selected_precedents:
                    precedent_text += f"- Case {p.id} ({p.date}): {p.scores}. Verdict: {p.verdict}\n"

            # 6. Retrieve Knowledge Base Context (Hybrid)
            kb_items = []
            kb_text_summary = ""

            try:
                # Lazy import to avoid circular dep issues at module level if any
                from backend.dependencies import get_agent_registry_dep, get_usage_service
                from backend.services.knowledge_base_service import KnowledgeBaseService

                # Resolve dependencies for Smart Ingestion (Registry + Usage)
                # This fixes the "[KBService] Smart Ingestion Capability Disabled" warning.
                registry = await get_agent_registry_dep(repo)
                usage_service = get_usage_service(repo)

                # Initialize Service with full dependencies
                kb_service = KnowledgeBaseService(repository=repo, registry=registry, usage_service=usage_service)

                # Check for query in input
                query = input_data.query

                # NOW RETURNS List[KnowledgeItem]
                kb_items = await kb_service.retrieve_context(query)

                # Format for textual context (Legacy Compatibility)
                if kb_items:
                    summary_lines = [f"=== TIETOPANKKI (KNOWLEDGE BASE) - {len(kb_items)} matches ==="]
                    for item in kb_items:
                        summary_lines.append(
                            f"[{item.type.upper()}] {item.term}: {item.definition} (Source: {item.source})"
                        )
                    kb_text_summary = "\n".join(summary_lines)
                else:
                    kb_text_summary = "Knowledge Base search returned no results."

            except Exception as e:
                # ZERO-COMPROMISE: 18.1 Generic Exception Handling
                # We catch specific AppExceptions for "Composite UI" partial failure.
                # Everything else must bubble up or be treated as Critical.

                # from backend.exceptions import AppException - REMOVED (Shadows global)

                if isinstance(e, AppException) and e.error_code == ErrorCodes.KNOWLEDGE_RETRIEVAL_FAILED:
                    # Known partial failure (e.g. Pinecone down). Log warning, allow degraded UI.
                    logger.warning(f"[RetrievalAgent] KB Partial Failure: {e}")
                    kb_text_summary = ""
                elif isinstance(e, AppException) and e.error_code == ErrorCodes.KNOWLEDGE_NOT_INGESTED:
                    # Expected state for new orgs. Log info.
                    logger.info(f"[RetrievalAgent] KB Empty: {e}")
                    kb_text_summary = ""
                else:
                    # CRITICAL: Unexpected error (Code bug, Network, etc).
                    # "Fail Fast" implies we should crash, BUT...
                    # If Precedents exist, we might want to return them?
                    # Docs say: "Graceful Degradation are only permitted at Presentation/BFF layer".
                    # This IS a Backend Agent. It should probably fail if it breaks.
                    # However, Part 3.6 says "Composite Dashboard" can handle partials.
                    # DECISION: Raise Critical for unknown errors to force fix.
                    logger.error(f"[RetrievalAgent] KB Critical Failure: {e}", exc_info=True)
                    raise AppException(
                        message="Critical Failure in Knowledge Base Retrieval.",
                        status_code=500,
                        details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL, "original_error": str(e)},
                    )

            # 7. Combine Contexts
            final_summary_text = f"{precedent_text}\n\n{kb_text_summary}"

            logger.info(
                f"[{self.__class__.__name__}] Complete. Found {len(selected_precedents)} precedents and {len(kb_items)} KB items."
            )

            # FAIL FAST: If NO context is available at all (fresh install), block execution.
            # This aligns with the "Explicit Ingestion" requirement.
            if not selected_precedents and not kb_items:
                raise AgentExecutionError(
                    detail=ErrorCodes.KNOWLEDGE_NOT_INGESTED,
                    agent_name="RetrievalAgent",
                    original_error=ValueError("No precedents or knowledge base items found."),
                )

            # 6. Construct Output DTO
            dto_data = ContextDataDTO(
                thought_process="Retrieved relevant precedents.",
                conclusion="Context gathering complete.",
                confidence_score=1.0,
                precedents=final_summary_text,
                precedent_list=selected_precedents,
                knowledge_items=kb_items,
            )

            context_dict = execution_context or {}
            
            # Promote to full Domain Model and apply metadata authority
            result_data = self._apply_python_authority(
                self.OUTPUT_SCHEMA(**dto_data.model_dump()),
                organization_id=context_dict.get("organization_id") or input_data.organization_id,
                workflow=context_dict.get("workflow") or kwargs.get("workflow"),
                user_id=context_dict.get("user_id") or kwargs.get("user_id"),
                execution_id=context_dict.get("execution_id") or kwargs.get("execution_id"),
                step_id=context_dict.get("step_id") or kwargs.get("step_id"),
                model="RetrievalEngine",
                provider="Database"
            )

            # IMPORTANT: Return ContextData model. Engine handles storage.
            return result_data

        except Exception as e:
            logger.error(f"[RetrievalAgent] Execution failed: {e}", exc_info=True)

            # Don't wrap specific AppExceptions (like KNOWLEDGE_NOT_INGESTED)
            # This allows the specific error code to reach the client.
            # from backend.exceptions import AppException - REMOVED (Shadows global)
            if isinstance(e, AppException):
                raise e

            # Use SSOT ErrorCode for generic/unexpected errors
            raise AgentExecutionError(
                detail=ErrorCodes.AGENT_EXECUTION_CRITICAL, original_error=e, agent_name="RetrievalAgent"
            ) from e
