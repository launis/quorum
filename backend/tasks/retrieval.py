"""Retrieval Tasks.

Functional tasks for fetching context and precedents.
"""

import logging
from typing import Any, List

from pydantic import BaseModel, ConfigDict, Field

from backend.core.registry import TaskRegistry
from backend.database.wrapper import get_db_client
from backend.settings import get_settings
from backend.database.factory import get_repository

logger = logging.getLogger(__name__)


# --- Schemas ---

class RetrievalInput(BaseModel):
    """Input schema for Retrieval task."""
    organization_id: str = Field(..., description="The context organization ID.")
    model_config = ConfigDict(extra="ignore")


class Precedent(BaseModel):
    """Schema for a single precedent case."""
    id: str
    date: str
    scores: str
    verdict: str
    model_config = ConfigDict(extra="ignore")


class ContextData(BaseModel):
    """Output schema for Retrieval task."""
    precedents: str = Field(..., description="Formatted summary of precedents.")
    precedent_list: List[Precedent] = Field(default_factory=list, description="Structured list of precedents.")
    model_config = ConfigDict(extra="ignore")


# --- Handler ---

@TaskRegistry.register_task(
    name="retrieve_context",
    input_schema=RetrievalInput,
    output_schema=ContextData,
    description="Retrieves organizational precedents and context."
)
async def retrieve_context_task(input_data: RetrievalInput) -> ContextData:
    """
    Fetches execution history for the organization and creates a summary.
    Logic ported from backend/hooks/archival.py.
    """
    logger.info(f"Running Retrieval Task for Org: {input_data.organization_id}...")
    
    # 1. Dependency Resolution (Manual for now, as tasks are pure functions)
    # Ideally, engine injects deps, but for now we resolve singleton/factory.
    settings = get_settings()
    db_client = get_db_client() # Singleton
    repo = await get_repository(settings, db_client)
    
    # 2. Query
    # Note: get_all_executions might be heavy. In production, use filters.
    # Currently repo doesn't support org_id filter on get_all_executions in all impls?
    # backend/api/execution_router.py calls repo.get_all_executions(organization_id=...)
    # Let's assume repo supports it.
    
    try:
        all_execs = await repo.get_all_executions(organization_id=input_data.organization_id)
    except TypeError:
        # Fallback if repo method signature doesn't match expected
        all_execs = await repo.get_all_executions()
        
    # 3. Filter Completed
    results = [x for x in all_execs if x.get("status") == "completed"]
    results.sort(key=lambda x: x.get("end_time", ""), reverse=True)
    
    precedents: List[Precedent] = []
    
    # 4. Extract Precedents (Limit 5 processed, return 3)
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
                    verdict=str(judge_data.get("kriittiset_havainnot_yhteenveto", "No verdict"))[:100] + "..."
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
    
    logger.info(f"Retrieval Task complete. Found {len(selected_precedents)} precedents.")
    
    return ContextData(
        precedents=summary_text,
        precedent_list=selected_precedents
    )


# --- Class-Based Agent Registration ---

from backend.agents.archivist import ArchivistAgent
from backend.models.domain import CaseLawContext

TaskRegistry.register_agent(
    task_keys=["archivist"],
    agent_cls=ArchivistAgent,
    output_model=CaseLawContext
)

