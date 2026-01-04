import logging
from datetime import datetime
from typing import TYPE_CHECKING, Annotated, Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)

from backend.models.domain import (
    ArgumentaatioAnalyysi,
    CaseLawContext,
    CoachingPlan,
    EtiikkaJaFakta,
    EvaluationResult,
    InteractionAnalysis,
    KausaalinenAuditointi,
    LogiikkaAuditointi,
    PanelAudit,
    PerformatiivisuusAuditointi,
    ProfilerAnalysis,
    TaintedData,
    TodistusKartta,
    TuomioJaPisteet,
    XAIReport,
)


class InputData(BaseModel):
    """Raw input data received from the user/API."""

    history_text: Annotated[str, Field(description="Historical context (chat logs, previous events).")]
    product_text: Annotated[str, Field(description="The primary artifact or text to be analyzed.")]
    reflection_text: Annotated[str, Field(description="Self-reflection or meta-commentary provided by the user.")]

    # Optional bibliography context
    bibliography_context: Annotated[Optional[List[str]], Field(description="Optional list of reference citations.")] = (
        None
    )

    model_config = ConfigDict(validate_assignment=True)


class WorkflowState(BaseModel):
    """
    Represents the central "Blackboard" state for a workflow execution.

    This state object persists in memory throughout the lifecycle of an execution,
    serving as the shared data repository for all agents. It contains input data,
    metadata, and the cumulative outputs of all executed steps.

    Attributes:
        execution_id (str): Unique UUID for this execution instance.
        workflow_id (Optional[str]): ID of the workflow definition being executed.
        workflow_name (Optional[str]): Human-readable name of the workflow.
        start_time (datetime): Timestamp when the execution began.
        current_step_name (str): The identifier of the currently active step/agent.
        inputs (InputData): Immutable input data provided at initialization.
    """

    # Metadata
    execution_id: Annotated[str, Field(description="Unique UUID for this execution instance.")]
    workflow_id: Annotated[Optional[str], Field(description="ID of the workflow being executed.")] = None
    workflow_name: Annotated[Optional[str], Field(description="Name of the workflow being executed.")] = None
    start_time: Annotated[datetime, Field(default_factory=datetime.now, description="Execution start timestamp.")]
    current_step_name: Annotated[str, Field(description="Name of the currently executing step/agent.")] = "init"
    version: Annotated[int, Field(default=1, description="Optimistic locking version.")] = 1

    # Identity Context (New Jan 2026)
    organization_id: Annotated[Optional[str], Field(description="Organization ID executing this workflow.")] = None
    user_id: Annotated[Optional[str], Field(description="User ID initiating this workflow.")] = None

    # Inputs (Read-only for agents)
    inputs: Annotated[InputData, Field(description="Immutable input data.")]

    # Agent Outputs (Initially None, populated during execution)
    step_guard: Annotated[
        Optional[TaintedData], Field(description="Agent 1: Security & PII checks.")
    ] = None
    step_analyst: Annotated[
        Optional[TodistusKartta], Field(description="Agent 2: Research & Evidence.")
    ] = None
    step_profiler: Annotated[
        Optional[ProfilerAnalysis], Field(description="Agent 2.5: Psych/Text Analysis.")
    ] = None
    step_logician: Annotated[
        Optional[ArgumentaatioAnalyysi],
        Field(description="Agent 3: Logical Structure Analysis."),
    ] = None
    step_falsifier: Annotated[
        Optional[LogiikkaAuditointi],
        Field(description="Agent 4: Stress Testing & Falsification."),
    ] = None
    step_overseer: Annotated[
        Optional[EtiikkaJaFakta], Field(description="Agent 5: Ethics & Fact Checking.")
    ] = None
    step_causal: Annotated[
        Optional[KausaalinenAuditointi],
        Field(description="Agent 6: Causal & Counterfactual Analysis."),
    ] = None
    step_detector: Annotated[
        Optional[PerformatiivisuusAuditointi],
        Field(description="Agent 7: Performativity & Authenticity."),
    ] = None
    step_judge: Annotated[
        Optional[TuomioJaPisteet], Field(description="Agent 9: Scoring & Verdict.")
    ] = None
    step_judge_cognitive: Annotated[
        Optional[TuomioJaPisteet], Field(description="Agent 9b: Cognitive BARS Scoring.")
    ] = None
    step_archivist: Annotated[
        Optional[CaseLawContext], Field(description="Agent 8a: Historical alignment.")
    ] = None
    step_coach: Annotated[
        Optional[CoachingPlan], Field(description="Agent 8c: Feedback & Action Plan.")
    ] = None
    step_interaction: Annotated[
        Optional[InteractionAnalysis],
        Field(description="Agent 2.2: Interaction Dynamics."),
    ] = None
    step_panel: Annotated[
        Optional[PanelAudit], Field(description="Agent 5 (Parallel): Consolidated Audit.")
    ] = None
    step_reporter: Annotated[
        Optional[XAIReport], Field(description="Agent 10: Final Executive Report.")
    ] = None

    # Formatted output
    xai_report_formatted: Annotated[Optional[str], Field(description="Final markdown report cache.")] = None

    # Dynamic Evaluation Results (New Multi-Matrix System)
    # Key = Step ID (e.g. "step_judge_cognitive")
    # Value = EvaluationResult object
    audit_results: Annotated[
        Dict[str, EvaluationResult],
        Field(default_factory=dict, description="Dynamic container for matrix-based evaluations."),
    ]

    # Reasoning Context (Stateless Blob Storage for Gemini 3 / GPT-5.1)
    # Key = Step ID
    # Value = { "token": "...", "model": "gemini-1.5-pro", "provider": "google" }
    reasoning_context: Annotated[
        Dict[str, Dict[str, str]],
        Field(default_factory=dict, description="Storage for encrypted reasoning blobs with metadata."),
    ]

    # Transient Reasoning Trace (The "Hot Potato" token for next step)
    last_reasoning_trace: Annotated[
        Optional[str],
        Field(default=None, description="The encrypted reasoning token from the immediately preceding step."),
    ]

    # Auxiliary Data
    aux_data: Annotated[
        Dict[str, Any], Field(default_factory=dict, description="Temporary storage for hooks and side-effects.")
    ]

    model_config = ConfigDict(validate_assignment=True)

    def get_previous_outputs_summary(self) -> str:
        """
        Generates a text summary of all previous agent outputs.
        Used to provide context to subsequent agents.

        Returns:
            str: Concatenated JSON dumps of visited steps.
        """
        summary = []
        steps = [
            ("Vartija", self.step_guard),
            ("Analyytikko", self.step_analyst),
            ("Profiloija", self.step_profiler),
            ("Loogikko", self.step_logician),
            ("Falsifioija", self.step_falsifier),
            ("Valvoja", self.step_overseer),
            ("Kausaalinen", self.step_causal),
            ("Tunnistaja", self.step_detector),
            ("Tuomari", self.step_judge),
            ("Arkistonhoitaja", self.step_archivist),
            ("Valmentaja", self.step_coach),
            ("Vuorovaikutusanalysaattori", self.step_interaction),
            ("Paneeli", self.step_panel),
        ]

        for name, data in steps:
            if data:
                # Use model_dump_json() for Pydantic v2 or json() for v1
                # formatting for readability
                try:
                    content = data.model_dump_json(indent=2)
                except AttributeError:
                    content = str(data)
                summary.append(f"--- {name} ---\n{content}\n")

        if not summary:
            return "(Ei aiempia tuloksia)"

        return "\n".join(summary)

    def get_latest_reasoning_metadata(self) -> Optional[Dict[str, str]]:
        """
        Retrieves the reasoning metadata (token + model) from the most recently executed relevant step.
        """
        priority_steps = ["step_panel", "step_coach", "step_judge", "step_judge_cognitive", "step_analyst"]
        for step_id in priority_steps:
            if step_id in self.reasoning_context:
                return self.reasoning_context[step_id]
        return None
