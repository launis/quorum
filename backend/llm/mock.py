import json
import random
import logging
import os
from typing import Dict, Any, Optional
from backend.settings import get_settings
# from backend.config import get_mock_responses_path # Removed
from backend.llm.mock_data import get_fallback_data, AGENT_CLASS_TO_MOCK_KEY

logger = logging.getLogger(__name__)

class MockLLMService:
    """
    Simulates LLM responses for testing and development without API costs.
    """
    
    def __init__(self):
        settings = get_settings()
        self.mock_data_path = settings.mock_responses_path
        self.mock_responses = self._load_mock_responses()
        
        # MAPPING: Agent Class Name -> Mock Key in JSON
        # Centralized in mock_data.py
        self.agent_identity_map = AGENT_CLASS_TO_MOCK_KEY

    def _load_mock_responses(self) -> Dict[str, Any]:
        """Loads mock responses from the JSON file."""
        if not os.path.exists(self.mock_data_path):
            logger.warning(f"[MockLLM] Mock data file not found at {self.mock_data_path}. Using empty defaults.")
            return {}
        
        try:
            with open(self.mock_data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"[MockLLM] Error loading mock data: {e}")
            return {}

    def generate_content(self, prompt: str, system_instruction: str = None, agent_identity: str = None) -> str:

        logger.info(f"[MockLLM] Intercepted call. Prompt length: {len(prompt)}")
        
        # 1. Determine Identity
        key = None
        
        # A) Explicit Identity (Robust)
        if agent_identity:
            key = self.agent_identity_map.get(agent_identity)
            if key:
                logger.info(f"[MockLLM] Identified agent via explicit identity: '{agent_identity}' -> '{key}'")
            else:
                 logger.warning(f"[MockLLM] Explicit identity '{agent_identity}' not found in map. Falling back to heuristics.")

        # B) Heuristics (Legacy/Fallback)
        if not key:
            key = self._identify_prompt_type(prompt, system_instruction)
            logger.info(f"[MockLLM] Identified agent via heuristics: '{key}'")
        
        with open("mock_debug.log", "a", encoding="utf-8") as f:
            f.write(f"\n--- NEW CALL ---\n")
            f.write(f"Agent Identity: {agent_identity}\n")
            f.write(f"Resolved Key: {key}\n")
            
        logger.info(f"[MOCK RESPONSE] Generating response for: {key}")
        
        # 2. Retrieve mock response
        response_template = self.mock_responses.get(key)
        
        if response_template:
            # If it's a list, pick a random variation
            if isinstance(response_template, list):
                return json.dumps(random.choice(response_template), ensure_ascii=False)
            # If it's a dict (JSON object), return as string
            elif isinstance(response_template, dict):
                return json.dumps(response_template, ensure_ascii=False)
            # If it's a string, return as is
            return str(response_template)
            
        # 3. Fallback: Generate generic valid JSON if possible
        logger.info(f"[MockLLM] No specific mock found for '{key}'. Returning generic fallback.")
        return self._generate_fallback(key)

    def _identify_prompt_type(self, prompt: str, system_instruction: str) -> str:
        # 0. Check for explicit STEP_ID injected into prompt
        import re
        step_id_match = re.search(r"STEP_ID: (\w+)", prompt)
        if step_id_match:
            return step_id_match.group(1)
        
        # Also check system instruction just in case
        if system_instruction:
            step_id_match_sys = re.search(r"STEP_ID: (\w+)", system_instruction)
            if step_id_match_sys:
                return step_id_match_sys.group(1)

        """
        Heuristics to identify the prompt type.
        Prioritizes system_instruction as it defines the agent's persona.
        """
        # 1. Check System Instruction First (Most Reliable)
        if system_instruction:
            sys_lower = system_instruction.lower()
            
            # Check for Output Schema names (Most Reliable)
            # PRIORITIZE LATE STAGE AGENTS (Judge, XAI) because they consume previous agents' outputs
            if "tuomiojapisteet" in sys_lower: return "judge_agent"
            if "xaireport" in sys_lower: return "xai_agent"
            
            if "tainteddata" in sys_lower: return "guard_agent"
            # Move Logician/Falsifier checks UP because they might reference 'todistuskartta' as input
            if "argumentaatioanalyysi" in sys_lower: return "logician_agent"
            if "logiikkaauditointi" in sys_lower: return "falsifier_agent"
            
            # Now check for Analyst (which produces todistuskartta)
            if "todistuskartta" in sys_lower: return "analyst_agent"
            
            if "kausaalinenauditointi" in sys_lower: return "causal_agent"
            if "performatiivisuusauditointi" in sys_lower: return "performativity_agent"
            if "etiikkajafakta" in sys_lower: return "fact_checker_agent"

            # Robust Agent Identity Checks (V2) - Reordered to prevent substring collisions
            if "causalanalystagent" in sys_lower or "causal analyst" in sys_lower: return "causal_agent"
            if "performativitydetectoragent" in sys_lower or "performativity detector" in sys_lower: return "performativity_agent"
            if "factualoverseeragent" in sys_lower or "factual overseer" in sys_lower: return "fact_checker_agent"
            
            if "guardagent" in sys_lower or "guard agent" in sys_lower: return "guard_agent"
            if "analystagent" in sys_lower or "analyst agent" in sys_lower: return "analyst_agent"
            if "logicianagent" in sys_lower or "logician agent" in sys_lower: return "logician_agent"
            if "falsifieragent" in sys_lower or "falsifier agent" in sys_lower: return "falsifier_agent"
            if "judgeagent" in sys_lower or "judge agent" in sys_lower: return "judge_agent"
            if "xaireporteragent" in sys_lower or "xai reporter" in sys_lower: return "xai_agent"
            # Courtroom 2.0 Agents
            if "profileragent" in sys_lower: return "profiler_agent"
            if "archivistagent" in sys_lower: return "archivist_agent"
            if "coachagent" in sys_lower: return "coach_agent"

            # Fallback: Check for specific Phase/Agent headers matching db_mock.json
            if "logician agent" in sys_lower: return "logician_agent" 
            if "vaihe 1: vartija" in sys_lower: return "guard_agent"
            if "vaihe 2: analyytikko" in sys_lower: return "analyst_agent"
            # Interaction is typically Step 3
            if "vaihe 3: vuorovaikutus" in sys_lower: return "interaction_agent"
            if "vaihe 4: profiloija" in sys_lower: return "profiler_agent"
            if "vaihe 5: loogikko" in sys_lower: return "logician_agent"
            if "vaihe 6: falsifioija" in sys_lower: return "falsifier_agent"
            if "vaihe 7: kausaalinen" in sys_lower: return "causal_agent"
            if "vaihe 8: tunnistaja" in sys_lower: return "performativity_agent"
            if "vaihe 9: valvoja" in sys_lower: return "fact_checker_agent"
            # Note: IDs in db_mock might vary, but we match loose keywords
            if "tuomari (judge)" in sys_lower or "vaihe 9: tuomari" in sys_lower or "vaihe 11: tuomari" in sys_lower: return "judge_agent"
            if "arkistonhoitaja" in sys_lower: return "archivist_agent"
            if "valmentaja" in sys_lower: return "coach_agent"
            if "xai-raportoija" in sys_lower or "vaihe 13" in sys_lower: return "xai_agent"


        # 2. Check Prompt Content (V2 & V1)
        prompt_lower = prompt.lower()
        
        # V2 Specific Headers (Strong Signal)
        if "input data to validate" in prompt_lower: return "guard_agent"
        if "input data for analysis" in prompt_lower: return "analyst_agent"
        
        # Identity-based matching (Strongest for Agents)
        if "loogikko-agentti" in prompt_lower or "logician agent" in prompt_lower: return "logician_agent"
        if "analyytikko-agentti" in prompt_lower or "analyst agent" in prompt_lower: return "analyst_agent"
        if "vartija-agentti" in prompt_lower or "guard agent" in prompt_lower: return "guard_agent"
        
        # Context-based matching
        if "todistuskartta" in prompt_lower and "edellisestä vaiheesta" in prompt_lower: return "logician_agent" # Fixed casing from LogicianAgent.py
        if "todistuskartta" in prompt_lower and "edellisen vaiheen" in prompt_lower: return "logician_agent" 
        if "argumentaatioanalyysi" in prompt_lower: return "logician_agent"
        
        if "argumentaatioanalyysi (edellisestä vaiheesta)" in prompt_lower: return "falsifier_agent"
        if "ulkoisen faktantarkistuksen tulokset" in prompt_lower: return "fact_checker_agent"
        if "kausaalinen analyytikko" in prompt_lower: return "causal_agent" # System instruction check fallback
        if "performatiivisuuden tunnistaja" in prompt_lower: return "performativity_agent" # System instruction check fallback
        if "input data (auditointiraportit)" in prompt_lower: return "judge_agent"
        if "input data (tuomio ja pisteet)" in prompt_lower: return "xai_agent"

        # V1 / Generic Headers
        if "vaihe 9" in prompt_lower or "xai-raportoija" in prompt_lower: return "xai_agent"
        if "vaihe 8" in prompt_lower or "tuomari-agentti" in prompt_lower: return "judge_agent"
        if "vaihe 7" in prompt_lower or "valvoja-agentti" in prompt_lower: return "fact_checker_agent"
        if "vaihe 6" in prompt_lower or "performatiivisuus" in prompt_lower: return "performativity_agent"
        if "vaihe 5" in prompt_lower or "kausaalinen" in prompt_lower: return "causal_agent"
        if "vaihe 4" in prompt_lower or "falsifioija-agentti" in prompt_lower: return "falsifier_agent"
        if "vaihe 3" in prompt_lower or "loogikko-agentti" in prompt_lower: return "logician_agent"
        if "vaihe 2" in prompt_lower or "analyytikko-agentti" in prompt_lower: return "analyst_agent"
        if "vaihe 1" in prompt_lower or "vartija-agentti" in prompt_lower: return "guard_agent"
        # New Agents (V2.1)
        if "profiler" in prompt_lower or "profiloija" in prompt_lower: return "profiler_agent"
        if "archivist" in prompt_lower or "arkistonhoitaja" in prompt_lower: return "archivist_agent"
        if "coach" in prompt_lower or "valmentaja" in prompt_lower: return "coach_agent"
        
        # 3. Broad Keyword Matching (Last Resort)
        if "argumentaatioanalyysi" in prompt_lower: return "logician_agent"
        if "logiikkaauditointi" in prompt_lower: return "falsifier_agent"
        if "kausaalinenauditointi" in prompt_lower: return "causal_agent"
        if "performatiivisuusauditointi" in prompt_lower: return "performativity_agent"
        if "etiikkajafakta" in prompt_lower: return "fact_checker_agent"
        if "tuomiojapisteet" in prompt_lower: return "judge_agent"
        
        # Broader checks (Order matters!)
        if "todistuskartta" in prompt_lower and "edellisestä vaiheesta" in prompt_lower: return "logician_agent"
        if "todistuskartta" in prompt_lower: return "analyst_agent"
        if "tainteddata" in prompt_lower: return "guard_agent"
        
        return "unknown"

    def _generate_fallback(self, key: str) -> str:
        """
        Generates a minimal valid JSON response for the identified key, strictly matching backend/schemas.py.
        Delegates precise data generation to `mock_data.py`.
        """
        data = get_fallback_data(key)
        # Assuming get_fallback_data returns a dict; we need to stringify it for the 'LLM response'
        return json.dumps(data, ensure_ascii=False)
