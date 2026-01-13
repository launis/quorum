"""Workflow State Management.

This module defines the `WorkflowState` and `InputData` models, which serve as the
"blackboard" or shared memory for the entire execution pipeline. It handles
the persistence of agent outputs and the continuity of the reasoning process.
"""

from datetime import datetime
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field

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
        step_guard (Optional[TaintedData]): Agent 1 - Security & PII checks.
        step_analyst (Optional[TodistusKartta]): Agent 2 - Research & Evidence.
        step_profiler (Optional[ProfilerAnalysis]): Agent 2.5 - Psych/Text Analysis.
        step_logician (Optional[ArgumentaatioAnalyysi]): Agent 3 - Logical Structure Analysis.
        step_falsifier (Optional[LogiikkaAuditointi]): Agent 4 - Stress Testing & Falsification.
        step_overseer (Optional[EtiikkaJaFakta]): Agent 5 - Ethics & Fact Checking.
        step_causal (Optional[KausaalinenAuditointi]): Agent 6 - Causal & Counterfactual Analysis.
        step_detector (Optional[PerformatiivisuusAuditointi]): Agent 7 - Performativity & Authenticity.
        step_judge (Optional[TuomioJaPisteet]): Agent 9 - Scoring & Verdict.
        step_judge_cognitive (Optional[TuomioJaPisteet]): Agent 9b - Cognitive BARS Scoring.
        step_archivist (Optional[CaseLawContext]): Agent 8a - Historical alignment.
        step_coach (Optional[CoachingPlan]): Agent 8c - Feedback & Action Plan.
        step_interaction (Optional[InteractionAnalysis]): Agent 2.2 - Interaction Dynamics.
        step_panel (Optional[PanelAudit]): Agent 5 (Parallel) - Consolidated Audit.
        step_reporter (Optional[XAIReport]): Agent 10 - Final Executive Report.
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
    start_time: Annotated[datetime, Field(default_factory=datetime.now, description="Execution start timestamp.")]
    current_step_name: Annotated[str, Field(description="Name of the currently executing step/agent.")] = "init"
    version: Annotated[int, Field(default=1, description="Optimistic locking version.")] = 1

    # Identity Context (New Jan 2026)
    organization_id: Annotated[str | None, Field(description="Organization ID executing this workflow.")] = None
    user_id: Annotated[str | None, Field(description="User ID initiating this workflow.")] = None

    # Inputs (Read-only for agents)
    inputs: Annotated[InputData, Field(description="Immutable input data.")]

    # Agent Outputs (Initially None, populated during execution)
    step_guard: Annotated[TaintedData | None, Field(description="Agent 1: Security & PII checks.")] = None
    step_analyst: Annotated[TodistusKartta | None, Field(description="Agent 2: Research & Evidence.")] = None
    step_profiler: Annotated[ProfilerAnalysis | None, Field(description="Agent 2.5: Psych/Text Analysis.")] = None
    step_logician: Annotated[
        ArgumentaatioAnalyysi | None,
        Field(description="Agent 3: Logical Structure Analysis."),
    ] = None
    step_falsifier: Annotated[
        LogiikkaAuditointi | None,
        Field(description="Agent 4: Stress Testing & Falsification."),
    ] = None
    step_overseer: Annotated[EtiikkaJaFakta | None, Field(description="Agent 5: Ethics & Fact Checking.")] = None
    step_causal: Annotated[
        KausaalinenAuditointi | None,
        Field(description="Agent 6: Causal & Counterfactual Analysis."),
    ] = None
    step_detector: Annotated[
        PerformatiivisuusAuditointi | None,
        Field(description="Agent 7: Performativity & Authenticity."),
    ] = None
    step_judge: Annotated[TuomioJaPisteet | None, Field(description="Agent 9: Scoring & Verdict.")] = None
    step_judge_cognitive: Annotated[TuomioJaPisteet | None, Field(description="Agent 9b: Cognitive BARS Scoring.")] = (
        None
    )
    step_archivist: Annotated[CaseLawContext | None, Field(description="Agent 8a: Historical alignment.")] = None
    step_coach: Annotated[CoachingPlan | None, Field(description="Agent 8c: Feedback & Action Plan.")] = None
    step_interaction: Annotated[
        InteractionAnalysis | None,
        Field(description="Agent 2.2: Interaction Dynamics."),
    ] = None
    step_panel: Annotated[PanelAudit | None, Field(description="Agent 5 (Parallel): Consolidated Audit.")] = None
    step_reporter: Annotated[XAIReport | None, Field(description="Agent 10: Final Executive Report.")] = None

    # Formatted output
    xai_report_formatted: Annotated[str | None, Field(description="Final markdown report cache.")] = None

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

    def get_latest_reasoning_metadata(self) -> dict[str, str] | None:
        """Retrieves the reasoning metadata (token + model) from the most recently executed relevant step."""
        priority_steps = ["step_panel", "step_coach", "step_judge", "step_judge_cognitive", "step_analyst"]
        for step_id in priority_steps:
            if step_id in self.reasoning_context:
                return self.reasoning_context[step_id]
        return None
