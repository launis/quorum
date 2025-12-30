
import logging
from typing import Any, List, Dict
from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)

async def retrieve_precedent(state: WorkflowState, repository: Any = None) -> WorkflowState:
    """
    HOOK: retrieve_precedent
    Retrieves the last N completed executions with a valid Judge score (Case Law).
    Injects a textual summary of these precedents into 'aux_data.archivist_precedents'.
    Designed to allow agents to learn from past performance.

    Args:
        state (WorkflowState): Current workflow state.
        repository (Any, optional): Data access layer. Defaults to None.

    Returns:
        WorkflowState: Updated state with injected precedents.
    """
    logger.info("[ArchivalHook] Running retrieve_precedent hook...")
    
    if not repository:
         logger.warning("[ArchivalHook] Repository not injected. Cannot retrieve precedents.")
         return state

    try:
        # 1. Use Repository to get executions
        all_executions = await repository.get_all_executions()
        
        # 2. Query Completed Executions (Memory Filter)
        results = [x for x in all_executions if x.get('status') == 'completed']
        
        # 3. Filter and Format
        precedents = []
        # Sort by end_time desc
        results.sort(key=lambda x: x.get('end_time', ''), reverse=True)
        recent_results = results[:5]
        
        for res in recent_results:
            # Check if it has judge output
            trace = res.get('trace', {})
            # Try step_judge (new) or step_8_judge (legacy)
            judge_data = trace.get('step_judge') or trace.get('step_8_judge')
            
            if judge_data:
                # Extract score
                pisteet = judge_data.get('pisteet', {})
                # Calc primitive summary if not present
                score_summary = "N/A"
                if pisteet:
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
        
        logger.info(f"[ArchivalHook] Found {len(precedents)} precedents.")
        
        # 4. Inject
        state.aux_data['archivist_precedents'] = summary_text
        
    except Exception as e:
        logger.error(f"[ArchivalHook] Failed to retrieve precedents: {e}")
        state.aux_data['archivist_precedents'] = "Error retrieving precedents."
        
    return state
