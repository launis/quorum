from typing import Any, Optional, Type, List, Dict
from backend.agents.base import BaseAgent
from backend.models.state import WorkflowState
from pydantic import BaseModel, Field
from tinydb import Query
import logging
import json

logger = logging.getLogger(__name__)

from backend.models.domain import BaseJSON

class CaseLawContext(BaseJSON):
    """
    Schema for the Archivist (Clerk) Agent.
    Ensures consistency with previous rulings.
    """
    linjakkuus_analyysi: str = Field(..., description="Analysis of how this case compares to precedents")
    poikkeamat_linjasta: str = Field(..., description="Notable deviations from established consistency")
    suositus_tuomarille: str = Field(..., description="Recommendation to the Judge regarding severity/leniency")
    viitatut_ennakkotapaukset: List[str] = Field(..., description="IDs of cases referenced")

class ArchivistAgent(BaseAgent):
    """
    Arkistonhoitaja (Archivist) Agent.
    Step 8.5: Retrieves past cases to ensure consistency (Stare Decisis).
    """

    state_field = "step_archivist"

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return CaseLawContext

    # --- PYTHON HOOKS ---

    def retrieve_precedent(self, state: WorkflowState, repository: Any = None) -> WorkflowState:
        """
        PRE-HOOK: Retrieves the last N completed executions with a valid Judge score.
        Injects this "Case Law" into aux_data for the prompt.
        Requires 'repository' to be injected by the Engine.
        """
        logger.info("[ArchivistAgent] Running retrieve_precedent hook...")
        
        if not repository:
             logger.warning("[ArchivistAgent] Repository not injected. Cannot retrieve precedents.")
             return state

        try:
            # 1. Use Repository Abstraction
            # We need raw access to execution query, but repository abstraction relies on id.
            # However, TinyDBRepository exposes tables if we cheat, but let's try to use generic get_all_executions 
            # and filter in memory if the repository doesn't support complex searching.
            # Proper DDD: Repository should have 'find_completed_executions()'.
            # For now, we use get_all_executions() and filter python-side.
            
            all_executions = repository.get_all_executions()
            
            # 2. Query Completed Executions (Memory Filter)
            # This might be slow if 10k items, but fine for prototype.
            results = [x for x in all_executions if x.get('status') == 'completed']
            
            
            # 3. Filter and Format
            precedents = []
            # Sort by end_time desc (string compare is okay for isoformat)
            results.sort(key=lambda x: x.get('end_time', ''), reverse=True)
            recent_results = results[:5]
            
            for res in recent_results:
                # Check if it has judge output
                trace = res.get('trace', {})
                # Try step_judge (new) or step_8_judge (legacy)
                judge_data = trace.get('step_judge') or trace.get('step_8_judge')
                
                if judge_data:
                    # Extract score
                    # Assuming TupleJaPisteet schema
                    pisteet = judge_data.get('pisteet', {})
                    # Calc primitive summary if not present
                    score_summary = "N/A"
                    if pisteet:
                         # Simplified extraction
                         scores = [
                             pisteet.get('analyysi', {}).get('arvosana', 0),
                             pisteet.get('arviointi', {}).get('arvosana', 0),
                             pisteet.get('synteesi', {}).get('arvosana', 0)
                         ]
                         avg = sum(scores)/3
                         score_summary = f"Avg: {avg:.2f} | Arvosanat: {scores}"
                    
                    precedents.append({
                        "id": res.get('execution_id'),
                        "date": res.get('end_time'),
                        "scores": score_summary,
                        "verdict": judge_data.get('kriittiset_havainnot_yhteenveto', 'No summary')
                    })
            
            # Keep only last 3
            precedents = precedents[-3:]
            
            summary_text = "=== ENNAKKOTAPAUKSET (PRECEDENTS) ===\n"
            if not precedents:
                summary_text += "Ei aiempi tapauksia tiedostossa."
            else:
                for p in precedents:
                    summary_text += f"- Case {p['id']} ({p['date']}): {p['scores']}. Verdict: {p['verdict'][:100]}...\n"
            summary_text += "====================================="
            
            logger.info(f"[ArchivistAgent] Found {len(precedents)} precedents.")
            
            # 4. Inject
            state.aux_data['archivist_precedents'] = summary_text
            
        except Exception as e:
            logger.error(f"[ArchivistAgent] Failed to retrieve precedents: {e}")
            state.aux_data['archivist_precedents'] = "Error retrieving precedents."
            
        return state
