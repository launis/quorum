from typing import Dict, Any
from backend.agents.base import BaseAgent

class AnalystAgent(BaseAgent):
    """
    Analyytikko-agentti (Analyst Agent).
    Responsible for:
    1. Evidence Anchoring (Todistepohjainen Ankkurointi)
    2. Creating an 'Evidence Map' (Todistuskartta)
    """

    def _process(self, safe_data: Dict[str, str], **kwargs) -> Dict[str, Any]:
        # safe_data comes from GuardAgent
        
        # Mock RAG process:
        # In reality, this would chunk the text, embed it, and retrieve relevant parts.
        # For now, we just pass the full text but structured as "Evidence".
        
        evidence_map = {
            "prompt_evidence": safe_data['prompt'][:1000] + "...", # Truncated for mock
            "history_evidence": safe_data['history'][:1000] + "...",
            "product_evidence": safe_data['product'][:1000] + "...",
            "reflection_evidence": safe_data['reflection'][:1000] + "..."
        }
        
        # Simulate LLM analysis to find key evidence
        sys_instr = kwargs.get('system_instruction', "You are an Analyst.")
        
        analysis_result = self._call_llm(
            prompt=f"Extract key evidence from: {str(evidence_map)}",
            system_instruction=sys_instr
        )

        return {
            "evidence_map": evidence_map,
            "analysis_summary": analysis_result
        }
