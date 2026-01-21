"""Retrieval Agent implementation."""

import logging
from typing import Any

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.models.state import WorkflowState
from backend.models.domain import ContextData, Precedent
from backend.settings import get_settings
from backend.database.wrapper import get_db_client
from backend.database.factory import get_repository
from backend.exceptions import AgentExecutionError

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
        input_data: dict,
        execution_context: dict | None = None,
        system_instruction: str | None = None,
        **kwargs,
    ) -> dict:
        """Executes the retrieval logic.

        Args:
            input_data (dict): Inputs containing organization_id.
            execution_context (dict): Context.
            system_instruction (str): Prompt.
            **kwargs: Args.

        Returns:
             dict: ContextData with precedents.
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

        # Stateless Execution: No warning if missing.
        if org_id:
             logger.info(f"[{self.__class__.__name__}] Running for Org: {org_id}...")
        else:
             logger.debug(f"[{self.__class__.__name__}] No Organization ID provided (Stateless/Global Mode).")

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
                        try:
                            scores = [
                                pisteet.get("analyysi", {}).get("arvosana", 0),
                                pisteet.get("arviointi", {}).get("arvosana", 0),
                                pisteet.get("synteesi", {}).get("arvosana", 0),
                            ]
                            avg = sum(scores) / 3
                            score_summary = f"Avg: {avg:.2f}"
                        except Exception:
                            score_summary = "Error calc scores"

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

            # Format Text
            summary_text = "=== ENNAKKOTAPAUKSET (PRECEDENTS) ===\n"
            if not selected_precedents:
                summary_text += "Ei aiempi tapauksia tiedostossa."
            else:
                for p in selected_precedents:
                    summary_text += f"- Case {p.id} ({p.date}): {p.scores}. Verdict: {p.verdict}\n"
            summary_text += "====================================="

            logger.info(f"[{self.__class__.__name__}] Complete. Found {len(selected_precedents)} precedents.")

            # 6. Construct Output
            from backend.models.domain import Metadata
            from datetime import datetime
            from datetime import timezone
            
            # Create dummy metadata (will be overwritten by BaseAgent._apply_python_authority)
            dummy_meta = Metadata(
                luontiaika=datetime.now(timezone.utc),
                agentti="RetrievalAgent",
                vaihe=0,
                versio="2.0"
            )

            result_data = ContextData(
                precedents=summary_text,
                precedent_list=selected_precedents,
                metadata=dummy_meta,
                metodologinen_loki="Database Query: Fetched top 3 completed executions.",
                edellisen_vaiheen_validointi="System Logic: Deterministic fetch.",
                semanttinen_tarkistussumma="calc_pending", # Will be updated by authority
                reasoning_trace="Deterministic retrieval of organizational precedents."
            )
            
            # IMPORTANT: Return dict (or model). Engine handles storage.
            return result_data.model_dump()

        except Exception as e:
            logger.error(f"[RetrievalAgent] Execution failed: {e}", exc_info=True)
            raise AgentExecutionError(detail="RETRIEVAL_FAILED", original_error=e) from e
