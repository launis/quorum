"""Coach Agent implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pydantic import BaseModel

from backend.agents.base import BaseAgent
from backend.models.domain import CoachingPlan

if TYPE_CHECKING:
    from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)


class CoachAgent(BaseAgent):
    """Coach Agent (Valmentaja).

    Responsible for generating coaching plans and managing the bibliography.
    Configured to run as 'step_coach' in the workflow.
    """

    state_field = "step_coach"
    REQUIRES_KEYS = ["step_judge"]

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the Pydantic model for the agent's expected output.

        Returns:
            Optional[Type[BaseModel]]: The CoachingPlan schema.

        """
        return CoachingPlan

    async def execute(self, state: WorkflowState | None = None, system_instruction: str | None = None, **kwargs) -> WorkflowState:
        """Executes the coaching plan generation.

        Input State:
            - state.step_judge (Required context).
            - state.inputs (Product, Reflection).
            - External knowledge base via `prepare_context`.

        Output State:
            - state.step_coach (CoachingPlan): The generated actionable plan.
            - state.step_coach.lahdeluettelo (Populated via post-hook).

        Exceptions:
            - AgentExecutionError: If LLM fails or schema validation fails.
        """
        return await super().execute(state, system_instruction, **kwargs)

    async def prepare_context(self, state: WorkflowState, **kwargs) -> str:
        """PRE-HOOK: prepare_context.

        Loads Domain Knowledge from the Repository (Database) into the Agent instance.
        This ensures the CoachAgent uses the same Unified DB as the Ingestion Service.

        Args:
            state (WorkflowState): The current workflow state.
            **kwargs: Additional arguments, expected to contain 'repository'.

        Returns:
            str: The formatted context string containing external sources.

        """
        repository = kwargs.get("repository")
        if repository:
            # Load items from DB
            items = await repository.get_knowledge_base_items()

            # Transform to expected structure
            concepts = {}
            references = []

            for item in items:
                i_type = item.get("type")
                if i_type == "concept":
                    term = item.get("term")
                    defn = item.get("definition")
                    if term and defn:
                        concepts[term] = defn
                elif i_type == "reference":
                    # Support both old string format and new dict format
                    # enrich_learning_plan expects list of strings OR list of dicts.
                    # Let's populate list of dicts for better data.
                    ref_obj = {
                        "citation": item.get("definition"),  # Full citation stored in definition
                        "short_citation": item.get("term"),  # Short citation stored in term (e.g. "Smith 2020...")
                        "doi": item.get("doi_link"),
                    }
                    references.append(ref_obj)

            # Populate self.knowledge_base
            self.knowledge_base = {
                "concepts": concepts,
                "references": references,  # List of dicts
            }
            logger.info(
                f"[CoachAgent] Loaded {len(concepts)} concepts and {len(references)} references from Unified Database."
            )

            # Formulate the Context String for the Prompt
            context_output = "\nEXTERNAL SOURCES (KNOWLEDGE BASE):\n"
            for ref in references:
                citation = ref.get("citation", "")
                if citation:
                    context_output += f"- {citation}\n"

            return context_output

        else:
            logger.warning("[CoachAgent] No Repository provided in kwargs. Knowledge Base not loaded from DB.")
            self.knowledge_base = {}
            return ""

    def post_process(self, state: WorkflowState) -> WorkflowState:
        """Lifecycle Hook: Post-Execution.

        Triggers bibliography validation and enrichment by calling enrich_learning_plan.

        Args:
            state (WorkflowState): The current workflow state.

        Returns:
            WorkflowState: The updated state.

        """
        return self.enrich_learning_plan(state)

    def enrich_learning_plan(self, state: WorkflowState) -> WorkflowState:
        """POST-HOOK: enrich_learning_plan.

        Scans the ENTIRE Workflow State and populates bibliography using
        backend.hooks.references.generate_bibliography.

        Args:
            state (WorkflowState): The current workflow state.

        Returns:
            WorkflowState: The updated state with populated bibliography.

        """
        logger.info("[CoachAgent] Running enrich_learning_plan hook...")

        if not hasattr(self, "knowledge_base") or not self.knowledge_base:
            return state

        coach_plan_data = getattr(state, self.state_field, None)
        if not coach_plan_data:
            return state

        # Prepare Scan Data (Global)
        try:
            full_state_dict = state.model_dump()
            text_dump = str(full_state_dict)
        except Exception:
            text_dump = str(state.__dict__)

        # Delegate to Hook
        from backend.hooks.references import generate_bibliography

        formatted_list = generate_bibliography(text_dump, self.knowledge_base)

        if hasattr(coach_plan_data, "lahdeluettelo"):
            coach_plan_data.lahdeluettelo = formatted_list

        logger.info(f"[CoachAgent] Populated bibliography with {len(formatted_list)} references found in global state.")

        return state
