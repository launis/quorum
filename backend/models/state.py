"""Workflow State Management.

This module defines the `WorkflowState` and `InputData` models, which serve as the
"blackboard" or shared memory for the entire execution pipeline. It handles
the persistence of agent outputs and the continuity of the reasoning process.
"""

from datetime import datetime, timezone
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field

from backend.models.domain import (
    EvaluationResult,
    XAIReport,
    ContextData,
)


class InputData(BaseModel):
    """Raw input data received from the user/API.

    Attributes:
        history_text (str): Historical context (chat logs, previous events).
        product_text (str): The primary artifact or text to be analyzed.
        reflection_text (str): Self-reflection or meta-commentary provided by the user.
        bibliography_context (Optional[list[str]]): Optional list of reference citations.
    """

    history_text: Annotated[str, Field(description="Historical context (chat logs, previous events).")]
    product_text: Annotated[str, Field(description="The primary artifact or text to be analyzed.")]
    reflection_text: Annotated[str, Field(description="Self-reflection or meta-commentary provided by the user.")]

    # Optional bibliography context
    bibliography_context: Annotated[list[str] | None, Field(description="Optional list of reference citations.")] = None

    model_config = ConfigDict(validate_assignment=True)


class WorkflowState(BaseModel):
    """Represents the central "Blackboard" state for a workflow execution.

    This state object persists in memory throughout the lifecycle of an execution,
    serving as the shared data repository for all agents. It contains input data,
    metadata, and the cumulative outputs of all executed steps.

    Attributes:
        execution_id (str): Unique UUID for this execution instance.
        workflow_id (Optional[str]): ID of the workflow definition being executed.
        workflow_name (Optional[str]): Human-readable name of the workflow.
        start_time (datetime): Timestamp when the execution began.
        current_step_name (str): The identifier of the currently active step/agent.
        version (int): Optimistic locking version.
        organization_id (Optional[str]): Organization ID executing this workflow.
        user_id (Optional[str]): User ID initiating this workflow.
        inputs (InputData): Immutable input data provided at initialization.
        step_results (Dict[str, Any]): Dynamic container for agent outputs.
        xai_report_formatted (Optional[str]): Final markdown report cache.
        audit_results (dict[str, EvaluationResult]): Dynamic container for matrix-based evaluations.
        reasoning_context (dict): Storage for encrypted reasoning blobs with metadata.
        last_reasoning_trace (Optional[str]): The encrypted reasoning token from the immediately preceding step.
        aux_data (dict): Temporary storage for hooks and side-effects.
    """

    # Metadata
    execution_id: Annotated[str, Field(description="Unique UUID for this execution instance.")]
    workflow_id: Annotated[str | None, Field(description="ID of the workflow being executed.")] = None
    workflow_name: Annotated[str | None, Field(description="Name of the workflow being executed.")] = None
    start_time: Annotated[datetime, Field(default_factory=lambda: datetime.now(timezone.utc), description="Execution start timestamp.")]
    current_step_name: Annotated[str, Field(description="Name of the currently executing step/agent.")] = "init"
    version: Annotated[int, Field(default=1, description="Optimistic locking version.")] = 1

    # Identity Context (New Jan 2026)
    organization_id: Annotated[str | None, Field(description="Organization ID executing this workflow.")] = None
    user_id: Annotated[str | None, Field(description="User ID initiating this workflow.")] = None

    # Inputs (Read-only for agents)
    inputs: Annotated[InputData, Field(description="Immutable input data.")]

    # Dynamic Step Results (Replaces hardcoded step fields)
    step_results: Annotated[
        dict[str, Any],
        Field(default_factory=dict, description="Dynamic container for agent outputs keyed by step ID."),
    ]

    # Formatted output
    xai_report_formatted: Annotated[str | None, Field(description="Final markdown report cache.")] = None

    step_xai: Annotated[XAIReport | None, Field(description="XAI Reporter output.")] = None

    # Dynamic Evaluation Results (New Multi-Matrix System)
    # Key = Step ID (e.g. "step_judge_cognitive")
    # Value = EvaluationResult object
    audit_results: Annotated[
        dict[str, EvaluationResult],
        Field(default_factory=dict, description="Dynamic container for matrix-based evaluations."),
    ]

    # Reasoning Context (Stateless Blob Storage for Gemini 3 / GPT-5.1)
    # Key = Step ID
    # Value = { "token": "...", "model": "gemini-1.5-pro", "provider": "google" }
    reasoning_context: Annotated[
        dict[str, dict[str, str]],
        Field(default_factory=dict, description="Storage for encrypted reasoning blobs with metadata."),
    ]

    # Transient Reasoning Trace (The "Hot Potato" token for next step)
    last_reasoning_trace: Annotated[
        str | None,
        Field(default=None, description="The encrypted reasoning token from the immediately preceding step."),
    ]

    # Auxiliary Data
    aux_data: Annotated[
        dict[str, Any], Field(default_factory=dict, description="Temporary storage for hooks and side-effects.")
    ]

    # Usage Metrics (Cost Tracking)
    usage: Annotated[
        dict[str, dict[str, float | int | str]],
        Field(default_factory=dict, description="Accumulated usage stats per step (cost, tokens)."),
    ]

    model_config = ConfigDict(validate_assignment=True)

    def get_previous_outputs_summary(self) -> str:
        """Generates a text summary of all previous agent outputs.

        Used to provide context to subsequent agents.

        Returns:
            str: Concatenated JSON dumps of visited steps.

        """
        summary = []
        
        # Display names for known steps (preserving Finnish localization)
        step_display_names = {
            "step_guard": "Vartija",
            "step_analyst": "Analyytikko",
            "step_profiler": "Profiloija",
            "step_logician": "Loogikko",
            "step_falsifier": "Falsifioija",
            "step_overseer": "Valvoja",
            "step_causal": "Kausaalinen",
            "step_detector": "Tunnistaja",
            "step_judge": "Tuomari",
            "step_archivist": "Arkistonhoitaja",
            "step_coach": "Valmentaja",
            "step_interaction": "Vuorovaikutusanalysaattori",
            "step_panel": "Paneeli",
            "step_xai": "XAI Raportoija",
        }

        # Iterate through the mapping to maintain order, but check step_results
        for step_id, display_name in step_display_names.items():
            if step_id in self.step_results:
                data = self.step_results[step_id]
                # Use model_dump_json() for Pydantic v2 or json() for v1
                # formatting for readability
                try:
                    content = data.model_dump_json(indent=2)
                except AttributeError:
                    content = str(data)
                summary.append(f"--- {display_name} ---\n{content}\n")
        
        # Handle any other steps that might be in step_results but not in the standard mapping?
        # For now, sticking to the preservation of existing behavior logic.

        if not summary:
            return "(Ei aiempia tuloksia)"

        return "\n".join(summary)

    def get_latest_reasoning_metadata(self) -> dict[str, str] | None:
        """Retrieves the reasoning metadata (token + model) from the most recently executed relevant step."""
        priority_steps = ["step_xai", "step_panel", "step_coach", "step_judge", "step_judge_cognitive", "step_analyst"]
        for step_id in priority_steps:
            if step_id in self.reasoning_context:
                return self.reasoning_context[step_id]
        return None

    def __getattr__(self, name: str) -> Any:
        """Fallback to step_results for legacy 'step_X' access."""
        # Avoid infinite recursion for Pydantic internal lookups if any (usually not an issue with __getattr__)
        if name.startswith("step_") and name in self.step_results:
            return self.step_results[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
