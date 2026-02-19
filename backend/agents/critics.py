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
    CausalDTO,
    CausalOutput,
    CausalInput,
    FalsifierDTO,
    FalsifierOutput,
    FalsifierInput,
    OverseerDTO,
    OverseerOutput,
    OverseerInput,
    PerformativityDTO,
    PerformativityOutput,
    PerformativityInput,
)

if TYPE_CHECKING:
    from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)


class LogicalFalsifierAgent(BaseAgent[FalsifierInput, FalsifierOutput]):
    """Looginen Falsifioija-agentti (Logical Falsifier).

    Responsible for identifying logical fallacies and structural weaknesses.
    """

    state_field = "step_falsifier"
    PRODUCES_KEYS = ["step_falsifier"]
    INPUT_SCHEMA = FalsifierInput
    DTO_SCHEMA = FalsifierDTO
    OUTPUT_SCHEMA = FalsifierOutput

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the expected output schema.

        Returns:
            type[BaseModel] | None: FalsifierOutput schema.
        """
        return FalsifierDTO

    async def prepare_context(
        self,
        input_data: FalsifierInput,
        execution_context: dict[str, Any] | None,
        **kwargs: Any
    ) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Args:
            input_data (FalsifierInput): Inputs.
            execution_context (dict[str, Any] | None): Context.
            **kwargs: execution arguments.

        Returns:
            str | None: Formatted context string.
        """
        analyst_output = input_data.step_analyst

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
        input_data: FalsifierInput,
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> FalsifierOutput:
        """Executes logical fallacies analysis.

        Args:
            input_data (FalsifierInput): Inputs.
            execution_context (dict[str, Any] | None, optional): Context.
            system_instruction (str | None, optional): Prompt.
            **kwargs: Args.

        Returns:
            FalsifierOutput: Logical consistency report.

        Raises:
            AgentExecutionError: If mandatory 'step_analyst' input is missing.
        """
        # FAIL FAST: Falsifier requires Evidence Map
        # Checked via Pydantic model (step_analyst can be None in model, but here required?)
        # BaseAgent guarantees input_data matches input schema.
        # But step_analyst is optional in Input schema (None) for flexibility?
        # Let's check logic:
        if not input_data.step_analyst:
                error_msg = "[LogicalFalsifierAgent] Mandatory input 'step_analyst' missing. Analysis aborted."
                logger.error(f"{ErrorCodes.AGENT_EXECUTION_CRITICAL}: {error_msg}")
                raise AgentExecutionError(
                    detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                    original_error=ValueError(error_msg),
                    agent_name="LogicalFalsifierAgent"
                )

        result_obj = await super().execute(input_data, execution_context, system_instruction, **kwargs)

        return result_obj




class FactualOverseerAgent(BaseAgent[OverseerInput, OverseerOutput]):
    """Faktuaalinen ja Eettinen Valvoja-agentti (Factual & Ethical Overseer).

    Responsible for fact-checking and ethical oversight.
    """

    state_field = "step_overseer"
    PRODUCES_KEYS = ["step_overseer"]
    INPUT_SCHEMA = OverseerInput
    DTO_SCHEMA = OverseerDTO
    OUTPUT_SCHEMA = OverseerOutput

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the expected output schema.

        Returns:
            type[BaseModel] | None: OverseerOutput schema.
        """
        return OverseerDTO

    async def prepare_context(
        self,
        input_data: OverseerInput,
        execution_context: dict[str, Any] | None,
        **kwargs: Any
    ) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Args:
            input_data (OverseerInput): Inputs.
            execution_context (dict[str, Any] | None): Context.
            **kwargs: execution arguments.

        Returns:
            str | None: Formatted context string.
        """
        analyst_output = input_data.step_analyst
        context_parts = []

        if analyst_output:
            content = (
                analyst_output.model_dump_json(indent=2)
                if hasattr(analyst_output, "model_dump_json")
                else str(analyst_output)
            )
            context_parts.append(f"### TODISTUSKARTTA (EVIDENCE MAP):\n{content}")

        # Inject Knowledge Base Context
        # OverseerInput doesn't have step_context (as it's generic context).
        # We access via execution_context or perhaps we should have added it to Inputs.
        # But 'knowledge_items' are usually in step_context.
        
        context_data = None
        if execution_context:
             context_data = execution_context.get("step_context")

        if context_data:
             # Precedents
             precedents = getattr(context_data, "precedents", "")
             if isinstance(context_data, dict):
                  precedents = context_data.get("precedents", "")
             
             if precedents:
                  context_parts.append(f"### JÄRJESTELMÄN KONTEKSTI (TIETOPANKKI & ENNAKKOTAPAUKSET):\n{precedents}")

             # Search Results (Knowledge Items)
             items = getattr(context_data, "knowledge_items", [])
             if isinstance(context_data, dict):
                  items = context_data.get("knowledge_items", [])
             
             if items:
                  search_section = "### HAKUTULOKSET (GOOGLE SEARCH / ULKOINEN TOTUUS):\n"
                  for item in items:
                       term = getattr(item, "term", "")
                       defn = getattr(item, "definition", "")
                       source = getattr(item, "source", "Unknown")
                       if isinstance(item, dict):
                            term = item.get("term", "")
                            defn = item.get("definition", "")
                            source = item.get("source", "Unknown")
                       search_section += f"- [{source}] {term}: {defn}\n"
                  context_parts.append(search_section)

        # STRICT MODE: No fallback to dict access if not modeled.

        if context_parts:
            return "\n\n".join(context_parts)

        return None

    async def execute(
        self,
        input_data: OverseerInput,
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> OverseerOutput:
        """Executes factual and ethical oversight.

        Args:
            input_data (OverseerInput): Inputs.
            execution_context (dict[str, Any] | None, optional): Context.
            system_instruction (str | None, optional): Prompt.
            **kwargs: Args.

        Returns:
            OverseerOutput: Factuality report.

        Raises:
            AgentExecutionError: If mandatory 'step_analyst' input is missing.
        """
        # FAIL FAST: Overseer requires Evidence Map
        if not input_data.step_analyst:
                error_msg = "[FactualOverseerAgent] Mandatory input 'step_analyst' missing. Oversight aborted."
                logger.error(f"{ErrorCodes.AGENT_EXECUTION_CRITICAL}: {error_msg}")
                raise AgentExecutionError(
                    detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                    original_error=ValueError(error_msg),
                    agent_name="FactualOverseerAgent"
                )

        result_obj = await super().execute(input_data, execution_context, system_instruction, **kwargs)

        return result_obj






class CausalAnalystAgent(BaseAgent[CausalInput, CausalOutput]):
    """Kausaalinen Analyytikko-agentti (Causal Analyst).

    Responsible for analyzing causal relationships and correlations.
    """

    state_field = "step_causal"
    PRODUCES_KEYS = ["step_causal"]
    INPUT_SCHEMA = CausalInput
    DTO_SCHEMA = CausalDTO
    OUTPUT_SCHEMA = CausalOutput

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the expected output schema.

        Returns:
            type[BaseModel] | None: CausalOutput schema.
        """
        return CausalDTO

    async def prepare_context(
        self,
        input_data: CausalInput,
        execution_context: dict[str, Any] | None,
        **kwargs: Any
    ) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Args:
            input_data (CausalInput): Inputs.
            execution_context (dict[str, Any] | None): Context.
            **kwargs: execution arguments.

        Returns:
            str | None: Formatted context string.
        """
        analyst_output = input_data.step_analyst

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
        input_data: CausalInput,
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> CausalOutput:
        """Executes causal analysis.

        Args:
            input_data (CausalInput): Inputs.
            execution_context (dict[str, Any] | None, optional): Context.
            system_instruction (str | None, optional): Prompt.
            **kwargs: Args.

        Returns:
            CausalOutput: Correlation/Causation report.

        Raises:
            AgentExecutionError: If mandatory 'step_analyst' input is missing.
        """
        # FAIL FAST: Causal Analyst requires Evidence Map
        if not input_data.step_analyst:
                error_msg = "[CausalAnalystAgent] Mandatory input 'step_analyst' missing. Analysis aborted."
                logger.error(f"{ErrorCodes.AGENT_EXECUTION_CRITICAL}: {error_msg}")
                raise AgentExecutionError(
                    detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                    original_error=ValueError(error_msg),
                    agent_name="CausalAnalystAgent"
                )

        result_obj = await super().execute(input_data, execution_context, system_instruction, **kwargs)

        return result_obj




class PerformativityDetectorAgent(BaseAgent[PerformativityInput, PerformativityOutput]):
    """Performatiivisuuden Tunnistaja-agentti (Performativity Detector).

    Responsible for detecting performative language and rhetorical devices.
    """

    state_field = "step_detector"
    PRODUCES_KEYS = ["step_detector"]
    INPUT_SCHEMA = PerformativityInput
    DTO_SCHEMA = PerformativityDTO
    OUTPUT_SCHEMA = PerformativityOutput

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the expected output schema.

        Returns:
            type[BaseModel] | None: PerformativityOutput schema.
        """
        return PerformativityDTO

    async def prepare_context(
        self,
        input_data: PerformativityInput,
        execution_context: dict[str, Any] | None,
        **kwargs: Any
    ) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Args:
            input_data (PerformativityInput): Inputs.
            execution_context (dict[str, Any] | None): Context.
            **kwargs: execution arguments.

        Returns:
            str | None: Formatted context string.
        """
        analyst_output = input_data.step_analyst

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
        input_data: PerformativityInput,
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> PerformativityOutput:
        """Executes performativity detection.

        Args:
            input_data (PerformativityInput): Inputs.
            execution_context (dict[str, Any] | None, optional): Context.
            system_instruction (str | None, optional): Prompt.
            **kwargs: Args.

        Returns:
            PerformativityOutput: Rhetorical analysis.

        Raises:
            AgentExecutionError: If mandatory 'step_analyst' input is missing.
        """
        # FAIL FAST: Detector requires Evidence Map
        if not input_data.step_analyst:
                error_msg = "[PerformativityDetectorAgent] Mandatory input 'step_analyst' missing. Detection aborted."
                logger.error(f"{ErrorCodes.AGENT_EXECUTION_CRITICAL}: {error_msg}")
                raise AgentExecutionError(
                    detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                    original_error=ValueError(error_msg),
                    agent_name="PerformativityDetectorAgent"
                )

        result_obj = await super().execute(input_data, execution_context, system_instruction, **kwargs)

        return result_obj

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


