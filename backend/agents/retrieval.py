"""Retrieval Agent implementation."""

import logging
from typing import Any

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent
from backend.database.factory import get_repository
from backend.database.wrapper import get_db_client
from backend.exceptions import AgentExecutionError, ErrorCodes
from backend.models.domain import ContextData, Precedent
from backend.services.localization import LocalizationService

# 3. Local Imports
from backend.settings import get_settings

logger = logging.getLogger(__name__)


class RetrievalAgent(BaseAgent):
    """Hakija-agentti (Retrieval Agent).

    Retrieves organizational precedents and context from the database.
    Replaces the functional 'retrieve_context' task to ensure metadata injection.
    """

    state_field = "step_context"

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the expected response schema for the Retrieval agent."""
        return ContextData

    async def execute(
        self,
        input_data: dict[str, Any],
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> ContextData:
        """Executes the retrieval logic (DB Precedents + Knowledge Base).

        Args:
            input_data (dict[str, Any]): Inputs containing 'organization_id' and optional 'query'.
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

        # 1. Access Inputs
        org_id = input_data.get("organization_id")

        # Fallback: Check inputs
        if not org_id and "inputs" in input_data:
             org_id = input_data["inputs"].get("organization_id")

        # Check execution_context
        if not org_id and execution_context:
             org_id = execution_context.get("organization_id")

        # FAIL FAST: Valid context requires Organization ID
        if not org_id:
             error_msg = "Mandatory input 'organization_id' missing. Retrieval aborted."
             logger.error(f"[{self.__class__.__name__}] {error_msg}")
             raise AgentExecutionError(
                 detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                 original_error=ValueError(error_msg),
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
            results = [x for x in all_execs if x.get("status") == "completed"]
            results.sort(key=lambda x: x.get("end_time", ""), reverse=True)

            precedents: list[Precedent] = []

            # 5. Extract Precedents (Limit 5 processed, return 3)
            for res in results[:5]:
                trace = res.get("trace", {})
                judge_data = trace.get("step_judge") or trace.get("step_8_judge")

                if judge_data:
                    pisteet = judge_data.get("pisteet", {})
                    score_summary = "N/A"
                    if pisteet:
                        # Fail Fast / Transparency: Don't swallow errors blindly.
                        # If structure matches, calculate. If not, log specific warning.
                        try:
                            # Strict Dictionary Access (Fail if keys changed)
                            scores: list[float] = []
                            for dim in ["analyysi", "arviointi", "synteesi"]:
                                dim_data = pisteet.get(dim)
                                if not dim_data:
                                     # Partial score is valid? Or should we skip?
                                     # Let's assume 0 if missing, but log it.
                                     continue

                                val = dim_data.get("arvosana")
                                if isinstance(val, (int, float)):
                                    scores.append(val)

                            if len(scores) == 3:
                                avg = sum(scores) / 3
                                score_summary = f"Avg: {avg:.2f}"
                            else:
                                score_summary = "Incomplete Scores"
                                logger.warning(f"[RetrievalAgent] Case {res.get('execution_id')} has incomplete scores: {scores}")

                        except Exception as e:
                            logger.error(f"[RetrievalAgent] Failed to calc scores for {res.get('execution_id')}: {e}")
                            score_summary = "Calc Error"
                            # We don't crash the whole retrieval for one bad historical record,
                            # but we log it loudly. This adheres to "Robustness" for historical data.

                    precedents.append(
                        Precedent(
                            id=str(res.get("execution_id", "unknown")),
                            date=str(res.get("end_time", "unknown")),
                            scores=score_summary,
                            verdict=str(judge_data.get("kriittiset_havainnot_yhteenveto", "No verdict"))[:100] + "...",
                        )
                    )

            # Keep last 3 (most recent)
            selected_precedents = precedents[:3]

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
                from backend.services.knowledge_base_service import KnowledgeBaseService

                # We don't have an LLM config for Retrieval yet, but Service works without it for retrieval-only
                kb_service = KnowledgeBaseService(repo)

                # Check for query in input
                query = input_data.get("query") or input_data.get("inputs", {}).get("query")

                # NOW RETURNS List[KnowledgeItem]
                kb_items = await kb_service.retrieve_context(query)

                # Format for textual context (Legacy Compatibility)
                if kb_items:
                    summary_lines = [f"=== TIETOPANKKI (KNOWLEDGE BASE) - {len(kb_items)} matches ==="]
                    for item in kb_items:
                        summary_lines.append(f"[{item.type.upper()}] {item.term}: {item.definition} (Source: {item.source})")
                    kb_text_summary = "\n".join(summary_lines)
                else:
                     kb_text_summary = "Knowledge Base search returned no results."

            except Exception as e:
                # STRICT AUDIT: If KB Service fails, we should log critical.
                # But is it specific?
                # Check for specific KB Error Codes if raised by Service.
                from backend.exceptions import AppException
                if isinstance(e, AppException) and e.error_code == ErrorCodes.KNOWLEDGE_RETRIEVAL_FAILED:
                     logger.warning(f"[RetrievalAgent] KB Retrieval failed (Expected): {e}")
                else:
                     logger.error(f"[RetrievalAgent] KB Retrieval Unexpected Failure: {e}", exc_info=True)

                kb_text_summary = "Knowledge Base retrieval error."
                # We do NOT re-raise here for Hybrid resilience (as per instructions: "Rarely... only if partial failure strictly better")
                # RetrievalAgent provides *context*. Missing context is better than crash?
                # Actually, "Fail Fast" says "Don't patch with empty lists".
                # BUT, Precedents might be enough.
                # Decision: Log Error, return empty KB items (Partial Success).
                # This aligns with "Composite Dashboard" rule 3.6.3.

            # 7. Combine Contexts
            final_summary_text = f"{precedent_text}\n\n{kb_text_summary}"

            logger.info(f"[{self.__class__.__name__}] Complete. Found {len(selected_precedents)} precedents and {len(kb_items)} KB items.")

            # FAIL FAST: If NO context is available at all (fresh install), block execution.
            # This aligns with the "Explicit Ingestion" requirement.
            if not selected_precedents and not kb_items:
                 raise AgentExecutionError(
                     detail=ErrorCodes.KNOWLEDGE_NOT_INGESTED,
                     agent_name="RetrievalAgent",
                     original_error=ValueError("No precedents or knowledge base items found.")
                 )

            # 6. Construct Output
            from datetime import datetime, timezone

            from backend.models.domain import Metadata

            # Create dummy metadata (will be overwritten by BaseAgent._apply_python_authority)
            dummy_meta = Metadata(
                luontiaika=datetime.now(timezone.utc),
                agentti="RetrievalAgent",
                vaihe=0,
                versio="2.0",
                suoritus_ymparisto=LocalizationService().get("Environment.Unknown", default="Unknown")
            )

            result_data = ContextData(
                precedents=final_summary_text,
                precedent_list=selected_precedents,
                knowledge_items=kb_items,
                metadata=dummy_meta,
                metodologinen_loki="Database Query: Fetched top 3 completed executions + Knowledge Base.",
                edellisen_vaiheen_validointi="System Logic: Deterministic fetch.",
                semanttinen_tarkistussumma="calc_pending", # Will be updated by authority
                reasoning_trace="Deterministic retrieval of organizational precedents and KB context."
            )

            # IMPORTANT: Return ContextData model. Engine handles storage.
            return result_data

        except Exception as e:
            logger.error(f"[RetrievalAgent] Execution failed: {e}", exc_info=True)
            
            # Don't wrap specific AppExceptions (like KNOWLEDGE_NOT_INGESTED)
            # This allows the specific error code to reach the client.
            from backend.exceptions import AppException
            if isinstance(e, AppException):
                raise e

            # Use SSOT ErrorCode for generic/unexpected errors
            raise AgentExecutionError(
                detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                original_error=e,
                agent_name="RetrievalAgent"
            ) from e
