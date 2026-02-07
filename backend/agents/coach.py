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
        """Lifecycle Hook: Pre-Execution with INTELLIGENT FILTERING.

        Loads Knowledge Base but filters it dynamically based on the Judge's Verdict (Tuomio).
        This prevents context window bloat (TimeoutError) by only including relevant references.

        Args:
            input_data (dict): Inputs.
            execution_context (dict): Context.
            **kwargs: Additional arguments.

        Returns:
            str: The formatted context string.
        """
        parts = []

        # 1. Inject Verdict (Tuomio) FIRST to determine filtering needs
        # Aggregate multiple judges if present
        weak_areas = []
        focus_keywords = set()

        judge_inputs = []
        for key, value in input_data.items():
             if (key.startswith("step_judge") or key == "tuomio") and value:
                 judge_inputs.append((key, value))
        
        # Add explicit 'tuomio' kwarg if passed separately (rare/legacy)
        if kwargs.get("tuomio"):
             judge_inputs.append(("kwargs_tuomio", kwargs.get("tuomio")))

        if judge_inputs:
            for key, tuomio in judge_inputs:
                try:
                    # Header
                    content = tuomio.model_dump_json(indent=2) if hasattr(tuomio, "model_dump_json") else str(tuomio)
                    parts.append(f"### TUOMIO (VERDICT from {key}):\n{content}")

                    data = tuomio.model_dump() if hasattr(tuomio, "model_dump") else tuomio
                    if isinstance(data, dict):
                        # Check dimensions field (Standard)
                        dimensions = data.get("dimensions", [])
                        if dimensions:
                             for dim in dimensions:
                                 # Normalize
                                 d_data = dim if isinstance(dim, dict) else dim.__dict__
                                 score = d_data.get("score")
                                 dim_id = d_data.get("dimension_id", "").lower()
                                 if isinstance(score, (int, float)) and score < 3:
                                     weak_areas.append(f"- [{key}] {dim_id}: Score {score} (Low)")
                                     focus_keywords.add(dim_id)
                                     # Add related keywords based on dimension
                                     if "analy" in dim_id:
                                         focus_keywords.update(["bias", "analy", "cognitive", "heuristic"])
                                     elif "logi" in dim_id:
                                         focus_keywords.update(["logic", "fallacy", "argument", "toulmin", "deduct"])
                                     elif "falsi" in dim_id:
                                         focus_keywords.update(["falsif", "popp", "scien", "test"])

                        # Fallback Logic: Check legacy pisteet
                        elif "pisteet" in data:
                             p = data.get("pisteet", {})
                             for k, v in p.items():
                                 if v and isinstance(v, dict):
                                     val = v.get("arvosana")
                                     k_lower = k.lower()
                                     if isinstance(val, (int, float)) and val < 3:
                                          weak_areas.append(f"- [{key}] {k}: Score {val} (Low)")
                                          focus_keywords.add(k_lower)
                                          if "analy" in k_lower:
                                              focus_keywords.update(["bias", "analy"])
                                          elif "arvio" in k_lower:
                                              focus_keywords.update(["eval", "assess"])
                                          elif "syn" in k_lower:
                                              focus_keywords.update(["synth", "integ"])
                except Exception as e:
                    logger.warning(f"[CoachAgent] Failed to analyze weak areas for {key}: {e}")

            if weak_areas:
                parts.append("### IDENTIFIED WEAK AREAS (FOCUS FOR COACHING):")
                parts.append("\n".join(weak_areas))
                logger.info(f"[CoachAgent] Identified {len(weak_areas)} weak areas across judges. Filtering KB for keywords: {focus_keywords}")

        # 2. Intelligent Knowledge Base Loading
        repository = kwargs.get("repository")
        if repository:
            # Load items from DB
            items = await repository.get_knowledge_base_items()

            concepts = {}
            references = []

            # --- FILTERING LOGIC ---
            # If we have focus keywords, score items by relevance.
            # If no weak areas (perfect score), include general "Advancement" references.

            MAX_REFS = 15  # Strict limit to prevent bloat
            filtered_refs = []

            for item in items:
                i_type = item.get("type")
                term = item.get("term", "").lower()
                definition = item.get("definition", "").lower()
                combined_text = f"{term} {definition}"

                # Concept Handling (Always include Core Concepts if small enough, or filter)
                if i_type == "concept":
                     # For now, include all concepts as they are usually small definitions? SCM says "Context Bloat".
                     # Let's filter concepts too if list is huge.
                     if not focus_keywords or any(k in combined_text for k in focus_keywords):
                        if item.get("term") and item.get("definition"):
                             concepts[item.get("term")] = item.get("definition")

                # Reference Handling (The main bloat source)
                elif i_type == "reference":
                    relevance = 0
                    if focus_keywords:
                        # Higher score for matches
                        for k in focus_keywords:
                            if k in combined_text:
                                relevance += 1
                    else:
                        # No weak areas? "General/Advanced" mode.
                        relevance = 1 # Keep some generic ones

                    if relevance > 0:
                        ref_obj = {
                            "citation": item.get("definition"), # Definition often holds the citation text
                            "short_citation": item.get("term"),
                            "doi": item.get("doi_link"),
                            "_score": relevance
                        }
                        filtered_refs.append(ref_obj)

            # Sort by relevance and take top N
            filtered_refs.sort(key=lambda x: x["_score"], reverse=True)
            selected_refs = filtered_refs[:MAX_REFS]

            # Populate self.knowledge_base (for post_process bibliography)
            # We store ALL loaded concepts but only SELECTED references to keep bibliography consistent with prompt?
            # Actually, bibliography should reflect what *could* be used.
            # But prompt should be small.

            self.knowledge_base = {
                "concepts": concepts,
                "references": selected_refs,
            }

            logger.info(
                f"[CoachAgent] Intelligent Filtering: Selected {len(selected_refs)} references (from {len(items)}) based on keywords: {list(focus_keywords)[:5]}..."
            )

            # Formulate the Context String
            kb_str = "EXTERNAL SOURCES (KNOWLEDGE BASE - RELEVANT ONLY):\n"
            if not selected_refs:
                 kb_str += "(No specific references found for these weak areas. Rely on general pedagogical principles.)"
            else:
                for ref in selected_refs:
                    citation = ref.get("citation", "")
                    if citation:
                        kb_str += f"- {citation}\n"
            parts.append(kb_str)

        else:
            logger.warning("COACH_KNOWLEDGE_BASE_UNAVAILABLE: No Repository provided.")
            self.knowledge_base = {}

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
