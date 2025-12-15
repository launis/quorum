from typing import Any, Optional, Type, List, Dict
from backend.agents.base import BaseAgent
from backend.models.state import WorkflowState
from pydantic import BaseModel, Field
from tinydb import Query
import logging
import json

logger = logging.getLogger(__name__)

class Precedents(BaseModel):
    execution_id: str
    score_summary: str
    judge_verdict: Dict[str, Any]

class CaseLawContext(BaseModel):
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

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return CaseLawContext

    def _update_state(self, state: WorkflowState, response_data: Any) -> WorkflowState:
        analysis = CaseLawContext(**response_data)
        state.aux_data['step_archivist'] = analysis.model_dump()
        return state

    # --- PYTHON HOOKS ---

    def retrieve_precedent(self, state: WorkflowState) -> WorkflowState:
        """
        PRE-HOOK: Retrieves the last N completed executions with a valid Judge score.
        Injects this "Case Law" into aux_data for the prompt.
        """
        logger.info("[ArchivistAgent] Running retrieve_precedent hook...")
        
        try:
            # 1. Access DB (Engine has initialized it, but Agent usually doesn't have direct DB access)
            # We need to manually initialize a DB client or use the one if passed.
            # BaseAgent doesn't have self.db_client.
            # We use the wrapper.
            from backend.database.wrapper import get_db_client
            db = get_db_client()
            executions_table = db.table('executions')
            
            # 2. Query Completed Executions
            Execution = Query()
            # Search for completed strings
            results = executions_table.search(Execution.status == 'completed')
            
            # 3. Filter and Format
            precedents = []
            # Sort by end_time desc (if available), or just take last ones
            # TinyDB returns list, let's just take the last 3 (most recent usually at bottom)
            recent_results = results[-5:] # Take 5, might filter down
            
            for res in recent_results:
                # Check if it has judge output
                trace = res.get('trace', {})
                # Try step_8_judge (old) or potentially new keys
                judge_data = trace.get('step_8_judge')
                
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
