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
        state: WorkflowState | None = None,
        system_instruction: str | None = None,
        **kwargs,
    ) -> WorkflowState:
        """Executes the retrieval logic.

        Note: This Agent is unique because it primarily interacts with the DB, not the LLM.
        However, it inherits BaseAgent to ensure consistent metadata, checksums, and lifecycle.

        Input State:
            - state.inputs.organization_id (Required)

        Output State:
            - state.step_context (ContextData)
        """
        if not state:
            raise ValueError("RetrievalAgent requires a valid WorkflowState.")

        # --- STANDARD LOGGING & HOOKS (Manual Implementation) ---
        logger.info(f"[{self.__class__.__name__}] Starting execution...")
        logger.info(f"[{self.__class__.__name__}] Lifecycle Hook: prepare_context")
        await self.prepare_context(state, **kwargs)
        
        logger.info(f"[{self.__class__.__name__}] >>> EXECUTION START <<<")
        # --------------------------------------------------------

        # 1. Access Inputs
        # Primary source: WorkflowState.organization_id
        org_id = getattr(state, "organization_id", None)
        
        # Fallback: Check inputs (legacy)
        if not org_id:
             org_id = getattr(state.inputs, "organization_id", None)
        
        # Fallback: Check metadata if available
        if not org_id and hasattr(state, "metadata") and state.metadata:
             org_id = getattr(state.metadata, "organization_id", None)

        if not org_id:
             # Just logging warning and using default/empty, or failing?
             # Functional task required it field(..., description="The context organization ID.")
             # But for robustness, we might default to "global" or skip.
             logger.warning("[RetrievalAgent] Organization ID not found in state.inputs or state.metadata. Using 'default'.")
             org_id = "default"

        logger.info(f"[{self.__class__.__name__}] Running for Org: {org_id}...")

        # 2. Dependency Resolution
        settings = get_settings()
        db_client = get_db_client()
        repo = await get_repository(settings, db_client)

        try:
            # 3. Query DB
            # Logic ported from backend/tasks/retrieval.py
            try:
                all_execs = await repo.get_all_executions(organization_id=org_id)
            except TypeError:
                # Fallback if repo method signature doesn't match expected
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
            # We must populate BaseJSON required fields manually since we aren't using LLM.
            from backend.models.domain import Metadata
            from datetime import datetime
            
            # Create dummy metadata (will be overwritten by BaseAgent._apply_python_authority)
            dummy_meta = Metadata(
                luontiaika=datetime.utcnow().isoformat(),
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
            
            # Manually invoke state update to get metadata injection
            state = await self._update_state(state, result_data, output_key=self.state_field)
            
            # --- LIFECYCLE HOOK: POST PROCESS ---
            logger.info(f"[{self.__class__.__name__}] Lifecycle Hook: post_process")
            state = self.post_process(state)
            logger.info(f"[{self.__class__.__name__}] Execution completed.")
            # ------------------------------------
            
            return state

        except Exception as e:
            logger.error(f"[RetrievalAgent] Execution failed: {e}", exc_info=True)
            raise AgentExecutionError(detail="RETRIEVAL_FAILED", original_error=e) from e
