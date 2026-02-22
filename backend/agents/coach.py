from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.exceptions import AgentExecutionError, ErrorCodes
from backend.models.domain import CoachingPlan, CoachingPlanDTO, CoachInput

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class CoachAgent(BaseAgent[CoachInput, CoachingPlan]):
    """Coach Agent (Valmentaja).

    Responsible for generating coaching plans and managing the bibliography.
    Configured to run as 'step_coach' in the workflow.
    """

    state_field = "step_coach"
    REQUIRES_KEYS = ["step_judge"]

    INPUT_SCHEMA = CoachInput
    OUTPUT_SCHEMA = CoachingPlan
    DTO_SCHEMA = CoachingPlanDTO

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the Pydantic model for the agent's expected output.

        Returns:
            type[BaseModel] | None: The CoachingPlanDTO schema.
        """
        return CoachingPlanDTO

    async def execute(
        self,
        input_data: CoachInput,
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> CoachingPlan:
        """Executes the coaching plan generation and enriches it with bibliography.

        Args:
            input_data (CoachInput): Inputs.
            execution_context (dict[str, Any] | None, optional): Context.
            system_instruction (str | None, optional): Prompt.
            **kwargs: Args.

        Returns:
            CoachingPlan: The generated actionable plan with bibliography.
        """
        # 1. Run Standard Execution (LLM Generation)
        # This triggers prepare_context (loading KB)
        result = await super().execute(input_data, execution_context, system_instruction, **kwargs)

        # 2. Enrichment (Bibliography)
        if not hasattr(self, "knowledge_base") or self.knowledge_base is None:
            # If prepare_context failed or didn't run? (Should be caught in super)
            logger.warning("[CoachAgent] Knowledge Base missing during enrichment. Bibliography will be empty.")

            # Early return (BaseAgent ensures it's CoachingPlan)
            return result

        logger.info("[CoachAgent] Running post-execution enrichment (Bibliography)...")

        # Prepare Scan Data
        try:
            # Combine relevant inputs and result for scanning
            # We know result is a BaseModel
            scan_target = {
                "inputs": input_data.model_dump(),  # Convert to dict
                "result": result.model_dump(),
            }
            text_dump = str(scan_target)
        except Exception as e:
            logger.warning(f"[CoachAgent] Failed to serialize state for bibliography scan: {e}")
            text_dump = str(input_data) + str(result)

        # Delegate to Hook
        from backend.hooks.references import generate_bibliography

        formatted_list = generate_bibliography(text_dump, self.knowledge_base)

        # SCHEMA ADAPTER: CoachingPlan expects list[dict], but hook returns list[str].
        final_bib = []
        for ref_str in formatted_list:
            final_bib.append(
                {
                    "source_id": "ref_generated",  # Placeholder or hash?
                    "title": ref_str,
                    "url": None,
                    "snippet": None,
                }
            )

        # 3. Update Result
        # Handle strict Pydantic Model return
        # Create a copy with updated bibliography
        if hasattr(result, "bibliography"):
            # If mutable (unlikely for frozen model)
            try:
                result_dict = result.model_dump()
                result_dict["bibliography"] = final_bib
                final_result = type(result)(**result_dict)
            except Exception:
                final_result = result
        else:
            final_result = result

        logger.info(f"[CoachAgent] Populated bibliography with {len(final_bib)} references.")

        return final_result

    async def prepare_context(
        self, input_data: CoachInput, execution_context: dict[str, Any] | None, **kwargs: Any
    ) -> str | None:
        """Lifecycle Hook: Pre-Execution with INTELLIGENT FILTERING.

        Loads Knowledge Base but filters it dynamically based on the Judge's Verdict (Tuomio).
        This prevents context window bloat (TimeoutError) by only including relevant references.

        Args:
            input_data (CoachInput): Inputs.
            execution_context (dict[str, Any] | None): Context.
            **kwargs: Additional arguments.

        Returns:
            str | None: The formatted context string.

        Raises:
            ValueError: If mandatory 'step_judge' is missing.
            AgentExecutionError: If verdict parsing or repo access fails.
        """
        parts = []

        # 1. Inject Verdict (Tuomio) FIRST to determine filtering needs
        weak_areas = []
        focus_keywords = set()

        judge_inputs = []
        # Convert Pydantic model to dict to iterate over all fields (including extras)
        input_dict = input_data.model_dump()

        for key, value in input_dict.items():
            if key.startswith("step_judge") and value:
                judge_inputs.append((key, value))

        if kwargs.get("verdict"):
            judge_inputs.append(("kwargs_verdict", kwargs.get("verdict")))

        if not judge_inputs:
            # STRICT FAIL FAST: Coach requires a Verdict (step_judge) to function.
            error_code = ErrorCodes.SERVICE_DEPENDENCY_MISSING
            error_msg = (
                "[CoachAgent] Missing mandatory input 'step_judge' (Judge Verdict). "
                "Cannot generate coaching plan without legal basis."
            )
            logger.error(f"{error_code}: {error_msg}")
            raise AgentExecutionError(detail=error_code, original_error=ValueError(error_msg), agent_name="CoachAgent")

        if judge_inputs:
            for key, tuomio in judge_inputs:
                try:
                    # tuomio could be a dict or a Model (if Pydantic validated it as Any)
                    # If it came from input_data (CoachInput), it's either dict or Any.
                    content = str(tuomio)
                    if hasattr(tuomio, "model_dump_json"):
                        content = tuomio.model_dump_json(indent=2)
                    elif isinstance(tuomio, dict):
                        import json

                        content = json.dumps(tuomio, indent=2, default=str)

                    parts.append(f"### VERDICT (from {key}):\n{content}")

                    data = tuomio
                    if hasattr(tuomio, "model_dump"):
                        data = tuomio.model_dump()

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

                except Exception as e:
                    # FAIL FAST
                    error_code = ErrorCodes.AGENT_EXECUTION_CRITICAL
                    logger.error(
                        f"[CoachAgent] {error_code}: Failed to analyze weak areas for {key}: {e}", exc_info=True
                    )
                    raise AgentExecutionError(detail=error_code, original_error=e, agent_name="CoachAgent") from e

            if weak_areas:
                parts.append("### IDENTIFIED WEAK AREAS (FOCUS FOR COACHING):")
                parts.append("\n".join(weak_areas))
                parts.append(
                    "\nNOTE: Use the provided Knowledge Base to suggest specific improvements for these weak areas."
                )
                logger.info(
                    f"[CoachAgent] Identified {len(weak_areas)} weak areas across judges. "
                    f"Filtering KB for keywords: {focus_keywords}"
                )

        # 2. Intelligent Knowledge Base Loading
        repository = kwargs.get("repository")

        # If no repository in kwargs, check execution_context?
        if not repository and execution_context:
            # Some engines pass repository in execution_context
            repository = execution_context.get("repository")

        if not repository:
            # FAIL FAST: Repository is critical for Coach functionality (Knowledge Base)
            error_code = ErrorCodes.SERVICE_DEPENDENCY_MISSING
            msg = "Repository not injected. Coach Agent cannot load Knowledge Base."
            logger.error(f"[CoachAgent] {error_code}: {msg}")
            raise AgentExecutionError(detail=error_code, original_error=ValueError(msg), agent_name="CoachAgent")

        # Load items from DB
        try:
            # STRICT: Fetch specific collections directly
            references = await repository.get_references()
            concepts = await repository.get_concepts()

            # Store structured KB for ReferenceManager compatibility
            self.knowledge_base = {"references": references, "concepts": concepts}

            # ROOT CAUSE FIX: Inject into execution_context so global ReferenceHook can see it
            if execution_context is not None:
                execution_context["knowledge_base"] = self.knowledge_base

            if not references and not concepts:
                logger.warning("[CoachAgent] Knowledge Base is empty (no refs/concepts). Bibliography will be empty.")

            # Simple format for Promopt Context using the structured data
            parts.append("### KNOWLEDGE BASE (TIETOPANKKI):")

            if references:
                parts.append("\n**LÄHTEET (REFERENCES):**")
                for ref in references[:20]:  # Limit for context window
                    parts.append(f"- {ref.get('short_citation', 'Ref')}: {ref.get('citation', '')[:200]}...")

            if concepts:
                parts.append("\n**KÄSITTEET (CONCEPTS):**")
                for con in concepts[:20]:
                    parts.append(f"- {con.get('term', 'Term')}: {con.get('definition', '')[:200]}...")

        except Exception as e:
            error_code = ErrorCodes.KNOWLEDGE_RETRIEVAL_FAILED
            logger.error(f"[CoachAgent] {error_code}: {e}", exc_info=True)
            raise AgentExecutionError(detail=error_code, original_error=e, agent_name="CoachAgent") from e

        return "\n\n".join(parts) if parts else None

    def post_process(self, response_data: Any) -> Any:
        """Lifecycle Hook: Post-Execution (Healing & Python Authority).

        Enforces:
        1. DEDUPLICATION: Removes duplicate bibliography items and actionable steps.
        2. FAIL FAST: Ensures actionable_steps is not empty.
        """
        # 1. Access Data
        is_dict = isinstance(response_data, dict)

        actionable_steps = []
        bibliography = []

        if is_dict:
            actionable_steps = response_data.get("actionable_steps", [])
            bibliography = response_data.get("bibliography", [])
        else:
            actionable_steps = getattr(response_data, "actionable_steps", [])
            bibliography = getattr(response_data, "bibliography", [])

        # 2. FAIL FAST: Empty Steps (Coach MUST advise)
        if not actionable_steps:
            raise AgentExecutionError(
                detail=ErrorCodes.INVALID_OUTPUT_SCHEMA,
                original_error=ValueError("Coach returned empty 'actionable_steps'. Assistance failed."),
                agent_name="CoachAgent",
            )

        # 3. DEDUPLICATION AUTHORITY
        logger.info(
            f"[CoachAgent] Deduplicating Steps ({len(actionable_steps)}) and Bibliography ({len(bibliography)})..."
        )

        # Steps (Simple String Dedup)
        unique_steps = []
        seen_steps = set()
        for step in actionable_steps:
            # Normalize whitespace/case? strict string equality for now.
            if step not in seen_steps:
                unique_steps.append(step)
                seen_steps.add(step)

        # Bibliography (Dict/Object Dedup)
        unique_bib = []
        seen_bib = set()

        for item in bibliography:
            # Hash by Title (or URL if robust)
            title = ""
            url = ""

            if isinstance(item, dict):
                title = item.get("title", "")
                url = item.get("url", "")
            else:
                title = getattr(item, "title", "")
                url = getattr(item, "url", "")

            # Key: Title + URL (Handle variants?)
            # Just Title is often enough for duplicate suppression
            key = (title, url)

            if key not in seen_bib:
                unique_bib.append(item)
                seen_bib.add(key)

        # 4. Apply Updates
        changes_necessary = (len(unique_steps) != len(actionable_steps)) or (len(unique_bib) != len(bibliography))

        if changes_necessary:
            logger.info(
                f"[CoachAgent] Dedup Complete: Steps {len(actionable_steps)}->{len(unique_steps)}, Bib {len(bibliography)}->{len(unique_bib)}"
            )

            if is_dict:
                response_data["actionable_steps"] = unique_steps
                response_data["bibliography"] = unique_bib
                return response_data
            else:
                # Pydantic Copy
                return response_data.model_copy(update={"actionable_steps": unique_steps, "bibliography": unique_bib})

        return response_data
