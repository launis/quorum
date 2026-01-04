import logging
from typing import Optional, Type, TYPE_CHECKING

from pydantic import BaseModel

from backend.agents.base import BaseAgent
from backend.models.domain import EtiikkaJaFakta, KausaalinenAuditointi, LogiikkaAuditointi, PerformatiivisuusAuditointi

if TYPE_CHECKING:
    from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)


class LogicalFalsifierAgent(BaseAgent):
    """
    Looginen Falsifioija-agentti (Logical Falsifier).

    Responsible for identifying logical fallacies and structural weaknesses.
    """

    state_field = "step_falsifier"
    PRODUCES_KEYS = ["step_falsifier"]

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        """
        Returns the expected output schema.

        Returns:
            Optional[Type[BaseModel]]: LogiikkaAuditointi schema.
        """
        return LogiikkaAuditointi


class FactualOverseerAgent(BaseAgent):
    """
    Faktuaalinen ja Eettinen Valvoja-agentti (Factual & Ethical Overseer).

    Responsible for fact-checking and ethical oversight.
    """

    state_field = "step_overseer"
    PRODUCES_KEYS = ["step_overseer"]

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        """
        Returns the expected output schema.

        Returns:
            Optional[Type[BaseModel]]: EtiikkaJaFakta schema.
        """
        return EtiikkaJaFakta

    def execute_google_search(self, state: WorkflowState) -> WorkflowState:
        """
        HOOK: execute_google_search.

        Executes Google Search based on hypotheses generated during the oversight process.
        Delegates underlying logic to 'backend.hooks.search.execute_google_search'.

        Args:
            state (WorkflowState): The current workflow state.

        Returns:
            WorkflowState: The updated state with search results.
        """
        logger.info("[FactualOverseerAgent] Delegating to Search Hook...")
        from backend.hooks.search import execute_google_search

        return execute_google_search(state)


class CausalAnalystAgent(BaseAgent):
    """
    Kausaalinen Analyytikko-agentti (Causal Analyst).

    Responsible for analyzing causal relationships and correlations.
    """

    state_field = "step_causal"
    PRODUCES_KEYS = ["step_causal"]

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        """
        Returns the expected output schema.

        Returns:
            Optional[Type[BaseModel]]: KausaalinenAuditointi schema.
        """
        return KausaalinenAuditointi


class PerformativityDetectorAgent(BaseAgent):
    """
    Performatiivisuuden Tunnistaja-agentti (Performativity Detector).

    Responsible for detecting performative language and rhetorical devices.
    """

    state_field = "step_detector"
    PRODUCES_KEYS = ["step_detector"]

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        """
        Returns the expected output schema.

        Returns:
            Optional[Type[BaseModel]]: PerformatiivisuusAuditointi schema.
        """
        return PerformatiivisuusAuditointi

    def detect_performative_patterns(self, state: WorkflowState) -> WorkflowState:
        """
        HOOK: detect_performative_patterns.

        Scans input for performative language patterns using linguistic analysis.
        Delegates underlying logic to 'backend.hooks.linguistics.detect_performative_patterns'.

        Args:
            state (WorkflowState): The current workflow state.

        Returns:
            WorkflowState: The updated state with detected patterns.
        """
        logger.info("[PerformativityDetectorAgent] Delegating to Linguistics Hook...")
        from backend.hooks.linguistics import detect_performative_patterns

        return detect_performative_patterns(state)
