from typing import Dict, Any
from backend.agents.base import BaseAgent

class LogicianAgent(BaseAgent):
    """
    Loogikko-agentti (Logician Agent).
    Responsible for:
    1. Argument Construction (Argumentaation Rakentaminen)
    2. Applying Cognitive Assessment Matrix (Bloom/Toulmin)
    """

    def _process(self, evidence_map: Dict[str, str], analysis_summary: str, **kwargs) -> Dict[str, Any]:
        
        # Construct Toulmin Argument
        # Claim: Competence Level
        # Data: Evidence Map
        # Warrant: Assessment Matrix Rules
        
        argument = self._call_llm(
            prompt=f"Construct a Toulmin argument based on: {analysis_summary}",
            system_instruction=kwargs.get('system_instruction', "You are a Logician.")
        )

        return {
            "hypothesis_argument": argument,
            "toulmin_structure": {
                "claim": "Level 3 (Example)",
                "data": "See evidence map...",
                "warrant": "According to the matrix..."
            }
        }
