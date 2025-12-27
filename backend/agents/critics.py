from typing import Any, Optional, Type
import os
import json

from backend.agents.base import BaseAgent
from backend.models.state import WorkflowState
from backend.models.domain import (
    LogiikkaAuditointi, 
    EtiikkaJaFakta, 
    KausaalinenAuditointi, 
    PerformatiivisuusAuditointi
)
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class LogicalFalsifierAgent(BaseAgent):
    """
    Looginen Falsifioija-agentti (Logical Falsifier).
    """
    state_field = "step_falsifier"
    
    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return LogiikkaAuditointi



class FactualOverseerAgent(BaseAgent):
    """
    Faktuaalinen ja Eettinen Valvoja-agentti (Factual & Ethical Overseer).
    """
    state_field = "step_overseer"

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return EtiikkaJaFakta

    def execute_google_search(self, state: WorkflowState) -> WorkflowState:
        """
        HOOK: execute_google_search
        Executes Google Search based on hypotheses.
        Delegates to backend.hooks.search.
        """
        logger.info("[FactualOverseerAgent] Delegating to Search Hook...")
        from backend.hooks.search import execute_google_search
        return execute_google_search(state)


class CausalAnalystAgent(BaseAgent):
    """
    Kausaalinen Analyytikko-agentti (Causal Analyst).
    """
    state_field = "step_causal"

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return KausaalinenAuditointi


class PerformativityDetectorAgent(BaseAgent):
    """
    Performatiivisuuden Tunnistaja-agentti (Performativity Detector).
    """
    state_field = "step_detector"

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return PerformatiivisuusAuditointi

    def detect_performative_patterns(self, state: WorkflowState) -> WorkflowState:
        """
        HOOK: detect_performative_patterns
        Scans input for performative language patterns.
        Delegates to backend.hooks.linguistics.
        """
        logger.info("[PerformativityDetectorAgent] Delegating to Linguistics Hook...")
        from backend.hooks.linguistics import detect_performative_patterns
        return detect_performative_patterns(state)

