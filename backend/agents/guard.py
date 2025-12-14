from typing import Any, Optional, Type
from backend.agents.base import BaseAgent
from backend.models.state import WorkflowState
from backend.models.domain import TaintedData, SecurityCheck, TaintedDataContent
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class GuardAgent(BaseAgent):
    """
    Vartija-agentti (Guard Agent).
    Responsible for:
    1. Input Sanitization (Syötteen puhdistus)
    2. Security Check (Tietoturvatarkistus)
    3. Anonymization (Anonymisointi)
    """

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        # This tells the LLM Provider (Gemini/OpenAI) exactly what JSON structure to enforce.
        return TaintedData

    def _update_state(self, state: WorkflowState, response_data: Any) -> WorkflowState:
        logger.info(f"[GuardAgent] Updating state with response keys: {response_data.keys() if isinstance(response_data, dict) else 'Not a dict'}")
        
        try:
            # Validate using Pydantic (double check, or cast dict to model)
            # The Provider already returns a dict matching the schema, but we cast to Model for type safety
            validated_data = TaintedData(**response_data)
            
            # --- Python Banned Phrases Check Overlay ---
            # Even if LLM missed it, we check strictly here.
            # We must load the banned phrases from the DB or a known source.
            # Ideally this is a pre-hook, but we can also enforce it post-LLM to override the verdict.
            from backend.database.wrapper import get_db_client
            
            try:
                # Use wrapper to get client
                db_client = get_db_client()
                banned_table = db_client.table('banned_phrases')
                banned_phrases = [r['phrase'].lower() for r in banned_table.all()]
                
                detected = []
                # Scan all inputs
                inputs_to_scan = [
                    state.inputs.history_text,
                    state.inputs.product_text,
                    state.inputs.reflection_text
                ]
                
                for text in inputs_to_scan:
                    if not text: continue
                    text_lower = text.lower()
                    for phrase in banned_phrases:
                        if phrase in text_lower:
                            detected.append(phrase)
                
                if detected:
                    logger.warning(f"[GuardAgent] STRICT CHECK: Found banned phrases: {detected}")
                    validated_data.security_check.uhka_havaittu = True
                    validated_data.security_check.adversariaalinen_simulaatio_tulos += f"\n[SYSTEM ALERT] Banned phrases detected by strict filter: {', '.join(detected)}"
                    
            except Exception as e:
                logger.error(f"[GuardAgent] Banned phrase check failed: {e}")
            
            # Update the Blackboard
            state.step_1_guard = validated_data
            
            # Logic: If threat detected, we might want to flag execution (future feature)
            if validated_data.security_check.uhka_havaittu:
                logger.warning("[GuardAgent] THREAT DETECTED! Marking state potentially unsafe.")
                
        except Exception as e:
            logger.error(f"[GuardAgent] State update failed: {e}")
            raise e
            
        return state

    def extract_text_from_inputs(self, state: WorkflowState) -> WorkflowState:
        """
        Public hook method (Pre-Hook).
        (Deprecated Logic) PDF extraction is now handled upstream by WorkflowEngine (create_execution).
        This hook is kept for backward compatibility with step configuration but is effectively a pass-through.
        """
        logger.info("[GuardAgent] PDF Extraction Pre-Hook: Pass-through (Handled by Engine).")
        return state

    def check_banned_phrases_python(self, state: WorkflowState) -> WorkflowState:
        """
        Public hook method (Pre-Hook).
        Scans inputs for banned phrases BEFORE the LLM sees them.
        If found, injects a system alert into the inputs to ensure the LLM flags it.
        """
        logger.info("[GuardAgent] Executing Python-based Banned Phrases Scan (Pre-Hook)...")
        
        from backend.database.wrapper import get_db_client
        
        try:
            # Load banned phrases
            db_client = get_db_client()
            banned_table = db_client.table('banned_phrases')
            banned_phrases = [r['phrase'].lower() for r in banned_table.all()]
            
            detected = []
            inputs_to_scan = {
                "History": state.inputs.history_text,
                "Product": state.inputs.product_text, 
                "Reflection": state.inputs.reflection_text
            }
            
            for key, text in inputs_to_scan.items():
                if not text: continue
                text_lower = text.lower()
                for phrase in banned_phrases:
                    if phrase in text_lower:
                        detected.append(f"{phrase} ({key})")
            
            if detected:
                distinct_phrases = list(set(detected))
                logger.warning(f"[GuardAgent] PRE-HOOK: Found banned phrases: {distinct_phrases}")
                
                # INJECT WARNING into the product text so the LLM sees it clearly
                injection = f"\n\n[SYSTEM SECURITY ALERT]: The following BANNED PHRASES were detected in the input via strict regex scan: {', '.join(distinct_phrases)}. You MUST reject this and flag 'uhka_havaittu' as True."
                
                # We append it to product_text ensures it's part of the analyzed content
                state.inputs.product_text += injection
                
        except Exception as e:
            logger.error(f"[GuardAgent] Pre-hook scan failed: {e}")
            
            
        return state

    def ensure_tainted_data(self, state: WorkflowState) -> WorkflowState:
        """
        HOOK: ensure_tainted_data
        Post-Hook. Ensures that the tainted data structure is correctly populated.
        """
        logger.info("[GuardAgent] Running ensure_tainted_data...")
        # Since the LLM output (TaintedData) is already validated in _update_state,
        # checking specifically for the placeholder values might be what's intended.
        # For now, we just pass through.
        return state
