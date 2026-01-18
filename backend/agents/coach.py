"""Coach Agent implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.models.domain import CoachingPlan

if TYPE_CHECKING:
    pass

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

    async def execute(
        self,
        input_data: dict,
        execution_context: dict | None = None,
        system_instruction: str | None = None,
        **kwargs,
    ) -> dict:
        """Executes the coaching plan generation.

        Args:
            input_data (dict): Inputs.
            execution_context (dict): Context.
            system_instruction (str): Prompt.
            **kwargs: Args.

        Returns:
            dict: The generated actionable plan.
        """
        return await super().execute(input_data, execution_context, system_instruction, **kwargs)

    async def prepare_context(self, input_data: dict, execution_context: dict | None, **kwargs) -> str:
        """Lifecycle Hook: Pre-Execution.

        Loads Domain Knowledge AND the Judge's Verdict (Tuomio).

        Args:
            input_data (dict): Inputs.
            execution_context (dict): Context.
            **kwargs: Additional arguments.

        Returns:
            str: The formatted context string.
        """
        parts = []

        # 1. Load Knowledge Base
        repository = kwargs.get("repository") # Passed via kwargs from Registry wrapper
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
                    ref_obj = {
                        "citation": item.get("definition"),
                        "short_citation": item.get("term"),
                        "doi": item.get("doi_link"),
                    }
                    references.append(ref_obj)

            # Populate self.knowledge_base
            self.knowledge_base = {
                "concepts": concepts,
                "references": references,
            }
            logger.info(
                f"[CoachAgent] Loaded {len(concepts)} concepts and {len(references)} references from Unified Database."
            )

            # Formulate the Context String for the Prompt
            kb_str = "EXTERNAL SOURCES (KNOWLEDGE BASE):\n"
            for ref in references:
                citation = ref.get("citation", "")
                if citation:
                    kb_str += f"- {citation}\n"
            parts.append(kb_str)

        else:
            logger.warning(
                "COACH_KNOWLEDGE_BASE_UNAVAILABLE: No Repository provided in kwargs. Knowledge Base not loaded from DB."
            )
            self.knowledge_base = {}

        # 2. Inject Verdict (Tuomio)
        # Check kwargs first, then input_data
        tuomio = kwargs.get("tuomio")
        if not tuomio:
            tuomio = input_data.get("step_judge")

        if tuomio:
            # Enhanced Analysis for Unified Evaluation Contract
            content = tuomio.model_dump_json(indent=2) if hasattr(tuomio, "model_dump_json") else str(tuomio)
            parts.append(f"### TUOMIO (VERDICT):\n{content}")

            # Explicitly highlight weak areas (Score < 3) to guide the Coach
            try:
                data = tuomio.model_dump() if hasattr(tuomio, "model_dump") else tuomio
                if isinstance(data, dict):
                    dimensions = data.get("dimensions", [])
                    weak_areas = []
                    
                    # Logic: Check dimensions field (Standard)
                    if dimensions:
                         for dim in dimensions:
                             score = dim.get("score")
                             if isinstance(score, (int, float)) and score < 3:
                                 weak_areas.append(f"- {dim.get('dimension_id')}: Score {score} (Low)")
                    
                    # Fallback Logic: Check legacy pisteet (just in case)
                    elif "pisteet" in data:
                         p = data.get("pisteet", {})
                         for k, v in p.items():
                             if v and isinstance(v, dict):
                                 val = v.get("arvosana")
                                 if isinstance(val, (int, float)) and val < 3:
                                      weak_areas.append(f"- {k}: Score {val} (Low)")

                    if weak_areas:
                        parts.append("### IDENTIFIED WEAK AREAS (FOCUS FOR COACHING):")
                        parts.append("\n".join(weak_areas))
                        logger.info(f"[CoachAgent] Identified {len(weak_areas)} weak areas for coaching focus.")
            except Exception as e:
                logger.warning(f"[CoachAgent] Failed to analyze weak areas: {e}")

        return "\n\n".join(parts)

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
