"""Mock LLM Service for testing and offline development."""
import json
import logging
import random
import re

from backend.llm.mock_data import AGENT_CLASS_TO_MOCK_KEY, get_fallback_data

logger = logging.getLogger(__name__)


class MockLLMService:
    """Simulates LLM responses for testing and development without API costs.

    Intercepts calls and returns pre-defined JSON responses based on agent identity or prompt heuristics.
    """

    def __init__(self):
        """Initializes the Mock Service."""
        # MAPPING: Agent Class Name -> Mock Key
        # Centralized in mock_data.py
        self.agent_identity_map = AGENT_CLASS_TO_MOCK_KEY

    def generate_content(
        self, prompt: str, system_instruction: str | None = None, agent_identity: str | None = None
    ) -> str:
        """Generates mocked content based on the input prompt and identity.

        Args:
            prompt (str): The user prompt.
            system_instruction (Optional[str]): The system instruction prompting the specific agent persona.
            agent_identity (Optional[str]): Explicit agent identifier (e.g. 'AnalystAgent') to bypass heuristics.

        Returns:
            str: JSON string representing the mocked agent output.

        """
        logger.info(f"[MockLLM] Intercepted call. Prompt length: {len(prompt)}")

        # 1. Determine Identity
        key = None

        # A) Explicit Identity (Robust)
        if agent_identity:
            key = self.agent_identity_map.get(agent_identity)
            if key:
                logger.info(f"[MockLLM] Identified agent via explicit identity: '{agent_identity}' -> '{key}'")
            else:
                logger.warning(
                    f"[MockLLM] Explicit identity '{agent_identity}' not found in map. Falling back to heuristics."
                )

        # B) Heuristics (Legacy/Fallback)
        if not key:
            key = self._identify_prompt_type(prompt, system_instruction)
            logger.info(f"[MockLLM] Identified agent via heuristics: '{key}'")

        # Replaced manual file write with logger.debug to use standard logging infrastructure
        logger.debug(f"--- NEW CALL ---\nAgent Identity: {agent_identity}\nResolved Key: {key}")

        logger.info(f"[MOCK RESPONSE] Generating response for: {key}")

        return self._generate_fallback(key, prompt, system_instruction)

    def _identify_prompt_type(self, prompt: str, system_instruction: str | None) -> str:
        """Heuristics to identify the prompt type/agent key.

        Prioritizes explicit STEP_ID injection, then system instruction keywords, then prompt keywords.

        Args:
            prompt (str): User prompt.
            system_instruction (Optional[str]): System prompt.

        Returns:
            str: The identified mock key (e.g., 'analyst_agent') or 'unknown'.

        """
        # 0. Check for explicit STEP_ID injected into prompt
        step_id_match = re.search(r"STEP_ID: (\w+)", prompt)
        if step_id_match:
            return step_id_match.group(1)

        # Also check system instruction just in case
        if system_instruction:
            step_id_match_sys = re.search(r"STEP_ID: (\w+)", system_instruction)
            if step_id_match_sys:
                return step_id_match_sys.group(1)

        # 1. Check System Instruction First (Most Reliable)
        if system_instruction:
            sys_lower = system_instruction.lower()

            # Check for Output Schema names (Most Reliable)
            # PRIORITIZE LATE STAGE AGENTS (Judge, XAI) because they consume previous agents' outputs
            if "tuomiojapisteet" in sys_lower:
                return "judge_agent"
            if "xaireport" in sys_lower:
                return "xai_agent"

            if "tainteddata" in sys_lower:
                return "guard_agent"
            # Move Logician/Falsifier checks UP because they might reference 'todistuskartta' as input
            if "argumentaatioanalyysi" in sys_lower:
                return "logician_agent"
            if "logiikkaauditointi" in sys_lower:
                return "falsifier_agent"

            # Now check for Analyst (which produces todistuskartta)
            if "todistuskartta" in sys_lower:
                return "analyst_agent"

            if "kausaalinenauditointi" in sys_lower:
                return "causal_agent"
            if "performatiivisuusauditointi" in sys_lower:
                return "performativity_agent"
            if "etiikkajafakta" in sys_lower:
                return "fact_checker_agent"

            # Robust Agent Identity Checks (V2) - Reordered to prevent substring collisions
            if "causalanalystagent" in sys_lower or "causal analyst" in sys_lower:
                return "causal_agent"
            if "performativitydetectoragent" in sys_lower or "performativity detector" in sys_lower:
                return "performativity_agent"
            if "factualoverseeragent" in sys_lower or "factual overseer" in sys_lower:
                return "fact_checker_agent"

            if "guardagent" in sys_lower or "guard agent" in sys_lower:
                return "guard_agent"
            if "analystagent" in sys_lower or "analyst agent" in sys_lower:
                return "analyst_agent"
            if "logicianagent" in sys_lower or "logician agent" in sys_lower:
                return "logician_agent"
            if "falsifieragent" in sys_lower or "falsifier agent" in sys_lower:
                return "falsifier_agent"
            if "judgeagent" in sys_lower or "judge agent" in sys_lower:
                return "judge_agent"
            if "xaireporteragent" in sys_lower or "xai reporter" in sys_lower:
                return "xai_agent"
            # Courtroom 2.0 Agents
            if "profileragent" in sys_lower:
                return "profiler_agent"
            if "archivistagent" in sys_lower:
                return "archivist_agent"
            if "coachagent" in sys_lower:
                return "coach_agent"

            # Fallback: Check for specific Phase/Agent headers matching db_mock.json
            if "logician agent" in sys_lower:
                return "logician_agent"
            if "vaihe 1: vartija" in sys_lower:
                return "guard_agent"
            if "vaihe 2: analyytikko" in sys_lower:
                return "analyst_agent"
            # Interaction is typically Step 3
            if "vaihe 3: vuorovaikutus" in sys_lower:
                return "interaction_agent"
            if "vaihe 4: profiloija" in sys_lower:
                return "profiler_agent"
            if "vaihe 5: loogikko" in sys_lower:
                return "logician_agent"
            if "vaihe 6: falsifioija" in sys_lower:
                return "falsifier_agent"
            if "vaihe 7: kausaalinen" in sys_lower:
                return "causal_agent"
            if "vaihe 8: tunnistaja" in sys_lower:
                return "performativity_agent"
            if "vaihe 9: valvoja" in sys_lower:
                return "fact_checker_agent"
            # Note: IDs in db_mock might vary, but we match loose keywords
            if "tuomari (judge)" in sys_lower or "vaihe 9: tuomari" in sys_lower or "vaihe 11: tuomari" in sys_lower:
                return "judge_agent"
            if "arkistonhoitaja" in sys_lower:
                return "archivist_agent"
            if "valmentaja" in sys_lower:
                return "coach_agent"
            if "xai-raportoija" in sys_lower or "vaihe 13" in sys_lower:
                return "xai_agent"
            if "panel" in sys_lower or "coordinator" in sys_lower or "tiedepaneeli" in sys_lower:
                return "panel_agent"

        # 2. Check Prompt Content (V2 & V1)
        prompt_lower = prompt.lower()

        # V2 Specific Headers (Strong Signal)
        if "input data to validate" in prompt_lower:
            return "guard_agent"
        if "input data for analysis" in prompt_lower:
            return "analyst_agent"

        # Identity-based matching (Strongest for Agents)
        if "loogikko-agentti" in prompt_lower or "logician agent" in prompt_lower:
            return "logician_agent"
        if "analyytikko-agentti" in prompt_lower or "analyst agent" in prompt_lower:
            return "analyst_agent"
        if "vartija-agentti" in prompt_lower or "guard agent" in prompt_lower:
            return "guard_agent"

        # Context-based matching
        if "todistuskartta" in prompt_lower and "edellisestä vaiheesta" in prompt_lower:
            return "logician_agent"  # Fixed casing from LogicianAgent.py
        if "todistuskartta" in prompt_lower and "edellisen vaiheen" in prompt_lower:
            return "logician_agent"
        if "argumentaatioanalyysi" in prompt_lower:
            return "logician_agent"

        if "argumentaatioanalyysi (edellisestä vaiheesta)" in prompt_lower:
            return "falsifier_agent"
        if "ulkoisen faktantarkistuksen tulokset" in prompt_lower:
            return "fact_checker_agent"
        if "kausaalinen analyytikko" in prompt_lower:
            return "causal_agent"  # System instruction check fallback
        if "performatiivisuuden tunnistaja" in prompt_lower:
            return "performativity_agent"  # System instruction check fallback
        if "input data (auditointiraportit)" in prompt_lower:
            return "judge_agent"
        if "input data (tuomio ja pisteet)" in prompt_lower:
            return "xai_agent"

        # V1 / Generic Headers
        if "vaihe 9" in prompt_lower or "xai-raportoija" in prompt_lower:
            return "xai_agent"
        if "vaihe 8" in prompt_lower or "tuomari-agentti" in prompt_lower:
            return "judge_agent"
        if "vaihe 7" in prompt_lower or "valvoja-agentti" in prompt_lower:
            return "fact_checker_agent"
        if "vaihe 6" in prompt_lower or "performatiivisuus" in prompt_lower:
            return "performativity_agent"
        if "vaihe 5" in prompt_lower or "kausaalinen" in prompt_lower:
            return "causal_agent"
        if "vaihe 4" in prompt_lower or "falsifioija-agentti" in prompt_lower:
            return "falsifier_agent"
        if "vaihe 3" in prompt_lower or "loogikko-agentti" in prompt_lower:
            return "logician_agent"
        if "vaihe 2" in prompt_lower or "analyytikko-agentti" in prompt_lower:
            return "analyst_agent"
        if "vaihe 1" in prompt_lower or "vartija-agentti" in prompt_lower:
            return "guard_agent"
        # New Agents (V2.1)
        if "profiler" in prompt_lower or "profiloija" in prompt_lower:
            return "profiler_agent"
        if "archivist" in prompt_lower or "arkistonhoitaja" in prompt_lower:
            return "archivist_agent"
        if "coach" in prompt_lower or "valmentaja" in prompt_lower:
            return "coach_agent"

        # 3. Broad Keyword Matching (Last Resort)
        if "argumentaatioanalyysi" in prompt_lower:
            return "logician_agent"
        if "logiikkaauditointi" in prompt_lower:
            return "falsifier_agent"
        if "kausaalinenauditointi" in prompt_lower:
            return "causal_agent"
        if "performatiivisuusauditointi" in prompt_lower:
            return "performativity_agent"
        if "etiikkajafakta" in prompt_lower:
            return "fact_checker_agent"
        if "tuomiojapisteet" in prompt_lower:
            return "judge_agent"

        # Broader checks (Order matters!)
        if "todistuskartta" in prompt_lower and "edellisestä vaiheesta" in prompt_lower:
            return "logician_agent"
        if "todistuskartta" in prompt_lower:
            return "analyst_agent"
        if "tainteddata" in prompt_lower:
            return "guard_agent"

        return "unknown"

    def _generate_fallback(self, key: str, prompt: str = "", system_instruction: str | None = None) -> str:
        """Generates a minimal valid JSON response for the identified key, strictly matching backend/schemas.py.

        Delegates precise data generation to `mock_data.py`.

        Args:
            key (str): The mock key identifying the agent/type.
            prompt (str): The original prompt, used for dynamic value extraction (e.g. Judge dimensions).
            system_instruction (Optional[str]): System prompt, often containing schema/context.

        Returns:
            str: JSON string of the fallback data.

        """
        data = get_fallback_data(key)

        # --- DYNAMIC JUDGE HYDRATION ---
        # If we are mocking the Judge, we try to detect which dimensions were requested in the JSON schema or text.
        # We scan BOTH prompt and system_instruction.
        scan_text = (prompt or "") + "\n" + (system_instruction or "")

        if key == "judge_agent" and scan_text.strip():
            try:
                # Strategy A: Extract from Human Text (JudgeAgent prompt format: "- Label (ID: key):")
                keys_found = re.findall(r"\(ID:\s*([a-zA-Z0-9_]+)\)", scan_text)

                # Strategy B: Extract from JSON Schema (Backup)
                if not keys_found:
                    match = re.search(r'"scores"\s*:\s*\{.*?"properties"\s*:\s*\{(.*?)\}\s*,', scan_text, re.DOTALL)
                    if match:
                        props_inner = match.group(1)
                        keys_found = re.findall(r'"([a-z0-9_]+)"\s*:\s*\{', props_inner)

                if keys_found:
                    logger.info(f"[MockLLM] Dynamic Judge Keys Found: {keys_found}")
                    dynamic_scores = {}
                    for k in keys_found:
                        dynamic_scores[k] = {
                            "arvosana": random.randint(2, 4),
                            "perustelu": f"[MOCK] Dynamic evaluation for '{k}'.",
                        }
                    data["pisteet"] = dynamic_scores
            except Exception as e:
                logger.warning(f"[MockLLM] Failed hydration: {e}")

        # Assuming get_fallback_data returns a dict; we need to stringify it for the 'LLM response'
        return json.dumps(data, ensure_ascii=False)
