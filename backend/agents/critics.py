"""Critics Agents implementation (Falsifier, Overseer, Causal, Detector)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.models.domain import (
    EtiikkaJaFakta,
    KausaalinenAuditointi,
    LogiikkaAuditointi,
    PerformatiivisuusAuditointi,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class LogicalFalsifierAgent(BaseAgent):
    """Looginen Falsifioija-agentti (Logical Falsifier).

    Responsible for identifying logical fallacies and structural weaknesses.
    """

    state_field = "step_falsifier"
    PRODUCES_KEYS = ["step_falsifier"]

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the expected output schema.

        Returns:
            Optional[Type[BaseModel]]: LogiikkaAuditointi schema.

        """
        return LogiikkaAuditointi

    async def prepare_context(self, input_data: dict, execution_context: dict | None, **kwargs) -> str | None:
        """Lifecycle Hook: Pre-Execution."""
        todistus_kartta = kwargs.get("todistus_kartta")
        if not todistus_kartta:
            todistus_kartta = input_data.get("step_analyst")

        if todistus_kartta:
            content = (
                todistus_kartta.model_dump_json(indent=2)
                if hasattr(todistus_kartta, "model_dump_json")
                else str(todistus_kartta)
            )
            return f"### TODISTUSKARTTA (EVIDENCE MAP):\n{content}"

        return None

    async def execute(
        self,
        input_data: dict,
        execution_context: dict | None = None,
        system_instruction: str | None = None,
        **kwargs,
    ) -> dict:
        """Executes logical fallacies analysis.

        Args:
            input_data (dict): Inputs.
            execution_context (dict): Context.
            system_instruction (str): Prompt.
            **kwargs: Args.

        Returns:
            dict: Logical consistency report.
        """
        return await super().execute(input_data, execution_context, system_instruction, **kwargs)


class FactualOverseerAgent(BaseAgent):
    """Faktuaalinen ja Eettinen Valvoja-agentti (Factual & Ethical Overseer).

    Responsible for fact-checking and ethical oversight.
    """

    state_field = "step_overseer"
    PRODUCES_KEYS = ["step_overseer"]

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the expected output schema.

        Returns:
            Optional[Type[BaseModel]]: EtiikkaJaFakta schema.

        """
        return EtiikkaJaFakta

    async def prepare_context(self, input_data: dict, execution_context: dict | None, **kwargs) -> str | None:
        """Lifecycle Hook: Pre-Execution."""
        todistus_kartta = kwargs.get("todistus_kartta")
        if not todistus_kartta:
            todistus_kartta = input_data.get("step_analyst")

        context_parts = []

        if todistus_kartta:
            content = (
                todistus_kartta.model_dump_json(indent=2)
                if hasattr(todistus_kartta, "model_dump_json")
                else str(todistus_kartta)
            )
            context_parts.append(f"### TODISTUSKARTTA (EVIDENCE MAP):\n{content}")

        # Inject Google Search Results if available in input_data
        if "google_search_results" in input_data:
            search_results = input_data["google_search_results"]
            context_parts.append(f"### HAKUTULOKSET (GOOGLE SEARCH RESULTS):\n{search_results}")
        # Legacy/Fallback check in execution_context
        elif execution_context and "google_search_results" in execution_context:
             search_results = execution_context["google_search_results"]
             context_parts.append(f"### HAKUTULOKSET (GOOGLE SEARCH RESULTS):\n{search_results}")


        if context_parts:
            return "\n\n".join(context_parts)

        return None

    async def execute(
        self,
        input_data: dict,
        execution_context: dict | None = None,
        system_instruction: str | None = None,
        **kwargs,
    ) -> dict:
        """Executes factual and ethical oversight.

        Args:
            input_data (dict): Inputs.
            execution_context (dict): Context.
            system_instruction (str): Prompt.
            **kwargs: Args.

        Returns:
            dict: Factuality report.
        """
        return await super().execute(input_data, execution_context, system_instruction, **kwargs)

    def execute_google_search(self, state: Any) -> Any:
        """HOOK: execute_google_search."""
        # This hook is likely handled by Engine/Registry before input injection
        pass


class CausalAnalystAgent(BaseAgent):
    """Kausaalinen Analyytikko-agentti (Causal Analyst).

    Responsible for analyzing causal relationships and correlations.
    """

    state_field = "step_causal"
    PRODUCES_KEYS = ["step_causal"]

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the expected output schema.

        Returns:
            Optional[Type[BaseModel]]: KausaalinenAuditointi schema.

        """
        return KausaalinenAuditointi

    async def prepare_context(self, input_data: dict, execution_context: dict | None, **kwargs) -> str | None:
        """Lifecycle Hook: Pre-Execution."""
        todistus_kartta = kwargs.get("todistus_kartta")
        if not todistus_kartta:
            todistus_kartta = input_data.get("step_analyst")

        if todistus_kartta:
            content = (
                todistus_kartta.model_dump_json(indent=2)
                if hasattr(todistus_kartta, "model_dump_json")
                else str(todistus_kartta)
            )
            return f"### TODISTUSKARTTA (EVIDENCE MAP):\n{content}"

        return None

    async def execute(
        self,
        input_data: dict,
        execution_context: dict | None = None,
        system_instruction: str | None = None,
        **kwargs,
    ) -> dict:
        """Executes causal analysis.

        Args:
            input_data (dict): Inputs.
            execution_context (dict): Context.
            system_instruction (str): Prompt.
            **kwargs: Args.

        Returns:
            dict: Correlation/Causation report.
        """
        return await super().execute(input_data, execution_context, system_instruction, **kwargs)


class PerformativityDetectorAgent(BaseAgent):
    """Performatiivisuuden Tunnistaja-agentti (Performativity Detector).

    Responsible for detecting performative language and rhetorical devices.
    """

    state_field = "step_detector"
    PRODUCES_KEYS = ["step_detector"]

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the expected output schema.

        Returns:
            Optional[Type[BaseModel]]: PerformatiivisuusAuditointi schema.

        """
        return PerformatiivisuusAuditointi

    async def prepare_context(self, input_data: dict, execution_context: dict | None, **kwargs) -> str | None:
        """Lifecycle Hook: Pre-Execution."""
        todistus_kartta = kwargs.get("todistus_kartta")
        if not todistus_kartta:
            todistus_kartta = input_data.get("step_analyst")

        if todistus_kartta:
            content = (
                todistus_kartta.model_dump_json(indent=2)
                if hasattr(todistus_kartta, "model_dump_json")
                else str(todistus_kartta)
            )
            return f"### TODISTUSKARTTA (EVIDENCE MAP):\n{content}"

        return None

    async def execute(
        self,
        input_data: dict,
        execution_context: dict | None = None,
        system_instruction: str | None = None,
        **kwargs,
    ) -> dict:
        """Executes performativity detection.

        Args:
            input_data (dict): Inputs.
            execution_context (dict): Context.
            system_instruction (str): Prompt.
            **kwargs: Args.

        Returns:
            dict: Rhetorical analysis.
        """
        return await super().execute(input_data, execution_context, system_instruction, **kwargs)

    def detect_performative_patterns(self, state: WorkflowState) -> WorkflowState:
        """HOOK: detect_performative_patterns.

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
