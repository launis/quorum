"""Critics Agents implementation (Falsifier, Overseer, Causal, Detector)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.exceptions import AgentExecutionError, ErrorCodes
from backend.models.domain import (
    CausalOutput,
    FalsifierOutput,
    OverseerOutput,
    PerformativityOutput,
)

if TYPE_CHECKING:
    from backend.models.workflow import WorkflowState

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
            type[BaseModel] | None: FalsifierOutput schema.
        """
        return FalsifierOutput

    async def prepare_context(
        self,
        input_data: dict[str, Any],
        execution_context: dict[str, Any] | None,
        **kwargs: Any
    ) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Args:
            input_data (dict[str, Any]): Inputs.
            execution_context (dict[str, Any] | None): Context.
            **kwargs: execution arguments.

        Returns:
            str | None: Formatted context string.
        """
        analyst_output = input_data.get("step_analyst")

        if analyst_output:
            content = (
                analyst_output.model_dump_json(indent=2)
                if hasattr(analyst_output, "model_dump_json")
                else str(analyst_output)
            )
            return f"### TODISTUSKARTTA (EVIDENCE MAP):\n{content}"

        return None

    async def execute(
        self,
        input_data: dict[str, Any],
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> FalsifierOutput:
        """Executes logical fallacies analysis.

        Args:
            input_data (dict[str, Any]): Inputs.
            execution_context (dict[str, Any] | None, optional): Context.
            system_instruction (str | None, optional): Prompt.
            **kwargs: Args.

        Returns:
            dict[str, Any] | BaseModel: Logical consistency report.

        Raises:
            AgentExecutionError: If mandatory 'step_analyst' input is missing.
        """
        # FAIL FAST: Falsifier requires Evidence Map
        if not input_data.get("step_analyst"):
                error_msg = "[LogicalFalsifierAgent] Mandatory input 'step_analyst' missing. Analysis aborted."
                logger.error(f"{ErrorCodes.AGENT_EXECUTION_CRITICAL}: {error_msg}")
                raise AgentExecutionError(
                    detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                    original_error=ValueError(error_msg),
                    agent_name="LogicalFalsifierAgent"
                )

        result_obj = await super().execute(input_data, execution_context, system_instruction, **kwargs)

        if isinstance(result_obj, FalsifierOutput):
            return result_obj
        elif isinstance(result_obj, dict):
            return FalsifierOutput(**result_obj)
        else:
             raise AgentExecutionError(
                 detail=ErrorCodes.INVALID_JSON_PAYLOAD,
                 original_error=TypeError(f"LogicalFalsifierAgent returned {type(result_obj)} instead of FalsifierOutput"),
                 agent_name="LogicalFalsifierAgent"
             )




class FactualOverseerAgent(BaseAgent):
    """Faktuaalinen ja Eettinen Valvoja-agentti (Factual & Ethical Overseer).

    Responsible for fact-checking and ethical oversight.
    """

    state_field = "step_overseer"
    PRODUCES_KEYS = ["step_overseer"]

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the expected output schema.

        Returns:
            type[BaseModel] | None: OverseerOutput schema.
        """
        return OverseerOutput

    async def prepare_context(
        self,
        input_data: dict[str, Any],
        execution_context: dict[str, Any] | None,
        **kwargs: Any
    ) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Args:
            input_data (dict[str, Any]): Inputs.
            execution_context (dict[str, Any] | None): Context.
            **kwargs: execution arguments.

        Returns:
            str | None: Formatted context string.
        """
        analyst_output = input_data.get("step_analyst")
        context_parts = []

        if analyst_output:
            content = (
                analyst_output.model_dump_json(indent=2)
                if hasattr(analyst_output, "model_dump_json")
                else str(analyst_output)
            )
            context_parts.append(f"### TODISTUSKARTTA (EVIDENCE MAP):\n{content}")

        # Inject Knowledge Base Context (step_context)
        context_data = input_data.get("step_context")
        if context_data:
             if isinstance(context_data, dict) and "precedents" in context_data:
                  context_parts.append(f"### JÄRJESTELMÄN KONTEKSTI (TIETOPANKKI & ENNAKKOTAPAUKSET):\n{context_data['precedents']}")
             else:
                  context_parts.append(f"### JÄRJESTELMÄN KONTEKSTI:\n{str(context_data)}")

        # Inject Google Search Results if available in input_data
        if "google_search_results" in input_data:
            search_results = input_data["google_search_results"]
            context_parts.append(f"### HAKUTULOKSET (GOOGLE SEARCH RESULTS):\n{search_results}")
        # STRICT MODE: No fallback to execution_context for data inputs.


        if context_parts:
            return "\n\n".join(context_parts)

        return None

    async def execute(
        self,
        input_data: dict[str, Any],
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> OverseerOutput:
        """Executes factual and ethical oversight.

        Args:
            input_data (dict[str, Any]): Inputs.
            execution_context (dict[str, Any] | None, optional): Context.
            system_instruction (str | None, optional): Prompt.
            **kwargs: Args.

        Returns:
            dict[str, Any] | BaseModel: Factuality report.

        Raises:
            AgentExecutionError: If mandatory 'step_analyst' input is missing.
        """
        # FAIL FAST: Overseer requires Evidence Map
        if not input_data.get("step_analyst"):
                error_msg = "[FactualOverseerAgent] Mandatory input 'step_analyst' missing. Oversight aborted."
                logger.error(f"{ErrorCodes.AGENT_EXECUTION_CRITICAL}: {error_msg}")
                raise AgentExecutionError(
                    detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                    original_error=ValueError(error_msg),
                    agent_name="FactualOverseerAgent"
                )

        result_obj = await super().execute(input_data, execution_context, system_instruction, **kwargs)

        if isinstance(result_obj, OverseerOutput):
            return result_obj
        elif isinstance(result_obj, dict):
            return OverseerOutput(**result_obj)
        else:
             raise AgentExecutionError(
                 detail=ErrorCodes.INVALID_JSON_PAYLOAD,
                 original_error=TypeError(f"FactualOverseerAgent returned {type(result_obj)} instead of OverseerOutput"),
                 agent_name="FactualOverseerAgent"
             )






class CausalAnalystAgent(BaseAgent):
    """Kausaalinen Analyytikko-agentti (Causal Analyst).

    Responsible for analyzing causal relationships and correlations.
    """

    state_field = "step_causal"
    PRODUCES_KEYS = ["step_causal"]

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the expected output schema.

        Returns:
            type[BaseModel] | None: CausalOutput schema.
        """
        return CausalOutput

    async def prepare_context(
        self,
        input_data: dict[str, Any],
        execution_context: dict[str, Any] | None,
        **kwargs: Any
    ) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Args:
            input_data (dict[str, Any]): Inputs.
            execution_context (dict[str, Any] | None): Context.
            **kwargs: execution arguments.

        Returns:
            str | None: Formatted context string.
        """
        analyst_output = input_data.get("step_analyst")

        if analyst_output:
            content = (
                analyst_output.model_dump_json(indent=2)
                if hasattr(analyst_output, "model_dump_json")
                else str(analyst_output)
            )
            return f"### TODISTUSKARTTA (EVIDENCE MAP):\n{content}"

        return None

    async def execute(
        self,
        input_data: dict[str, Any],
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> CausalOutput:
        """Executes causal analysis.

        Args:
            input_data (dict[str, Any]): Inputs.
            execution_context (dict[str, Any] | None, optional): Context.
            system_instruction (str | None, optional): Prompt.
            **kwargs: Args.

        Returns:
            dict[str, Any] | BaseModel: Correlation/Causation report.

        Raises:
            AgentExecutionError: If mandatory 'step_analyst' input is missing.
        """
        # FAIL FAST: Causal Analyst requires Evidence Map
        if not input_data.get("step_analyst"):
                error_msg = "[CausalAnalystAgent] Mandatory input 'step_analyst' missing. Analysis aborted."
                logger.error(f"{ErrorCodes.AGENT_EXECUTION_CRITICAL}: {error_msg}")
                raise AgentExecutionError(
                    detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                    original_error=ValueError(error_msg),
                    agent_name="CausalAnalystAgent"
                )

        result_obj = await super().execute(input_data, execution_context, system_instruction, **kwargs)

        if isinstance(result_obj, CausalOutput):
            return result_obj
        elif isinstance(result_obj, dict):
            return CausalOutput(**result_obj)
        else:
             raise AgentExecutionError(
                 detail=ErrorCodes.INVALID_JSON_PAYLOAD,
                 original_error=TypeError(f"CausalAnalystAgent returned {type(result_obj)} instead of CausalOutput"),
                 agent_name="CausalAnalystAgent"
             )




class PerformativityDetectorAgent(BaseAgent):
    """Performatiivisuuden Tunnistaja-agentti (Performativity Detector).

    Responsible for detecting performative language and rhetorical devices.
    """

    state_field = "step_detector"
    PRODUCES_KEYS = ["step_detector"]

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the expected output schema.

        Returns:
            type[BaseModel] | None: PerformativityOutput schema.
        """
        return PerformativityOutput

    async def prepare_context(
        self,
        input_data: dict[str, Any],
        execution_context: dict[str, Any] | None,
        **kwargs: Any
    ) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Args:
            input_data (dict[str, Any]): Inputs.
            execution_context (dict[str, Any] | None): Context.
            **kwargs: execution arguments.

        Returns:
            str | None: Formatted context string.
        """
        analyst_output = input_data.get("step_analyst")

        if analyst_output:
            content = (
                analyst_output.model_dump_json(indent=2)
                if hasattr(analyst_output, "model_dump_json")
                else str(analyst_output)
            )
            return f"### TODISTUSKARTTA (EVIDENCE MAP):\n{content}"

        return None

    async def execute(
        self,
        input_data: dict[str, Any],
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> PerformativityOutput:
        """Executes performativity detection.

        Args:
            input_data (dict[str, Any]): Inputs.
            execution_context (dict[str, Any] | None, optional): Context.
            system_instruction (str | None, optional): Prompt.
            **kwargs: Args.

        Returns:
            dict[str, Any] | BaseModel: Rhetorical analysis.

        Raises:
            AgentExecutionError: If mandatory 'step_analyst' input is missing.
        """
        # FAIL FAST: Detector requires Evidence Map
        if not input_data.get("step_analyst"):
                error_msg = "[PerformativityDetectorAgent] Mandatory input 'step_analyst' missing. Detection aborted."
                logger.error(f"{ErrorCodes.AGENT_EXECUTION_CRITICAL}: {error_msg}")
                raise AgentExecutionError(
                    detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                    original_error=ValueError(error_msg),
                    agent_name="PerformativityDetectorAgent"
                )

        result_obj = await super().execute(input_data, execution_context, system_instruction, **kwargs)

        if isinstance(result_obj, PerformativityOutput):
            return result_obj
        elif isinstance(result_obj, dict):
            return PerformativityOutput(**result_obj)
        else:
             raise AgentExecutionError(
                 detail=ErrorCodes.INVALID_JSON_PAYLOAD,
                 original_error=TypeError(f"PerformativityDetectorAgent returned {type(result_obj)} instead of PerformativityOutput"),
                 agent_name="PerformativityDetectorAgent"
             )

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


