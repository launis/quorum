
"""Verify Report Generation Script.

This script mocks a full WorkflowState with rich data for all agents,
including the updated ReasoningTrace structures and the new Judge/EvaluationResult schema.
It then runs the PdfReportService to generate a preview PDF.
"""

import asyncio
import logging
from datetime import datetime
from uuid import uuid4

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import Domain Models
# Mock Repository (Minimal Implementation)
from backend.database.repository import AbstractWorkflowRepository
from backend.models.domain.analyst import AnalystOutput, Hypothesis
from backend.models.domain.causal import CausalAnalysis, CausalOutput, CounterfactualTest
from backend.models.domain.coach import CoachingPlan
from backend.models.domain.evaluation import DimensionResultItem, EvaluationResult
from backend.models.domain.falsifier import FalsifierData, FalsifierOutput, WaltonStressTest
from backend.models.domain.logician import CognitiveLevel, LogicianData, LogicianOutput, ToulminComponent, WaltonScheme
from backend.models.domain.overseer import OverseerData, OverseerOutput
from backend.models.domain.xai import XAIOutput
from backend.models.enums import AbductiveConclusion, BloomLevel, FidelityLevel, PlausibilityLevel, StrategicDepth
from backend.models.state import WorkflowState

# Import Service
from backend.services.pdf_generator import PdfReportService


class MockWorkflowRepository(AbstractWorkflowRepository):
    def __init__(self, state: WorkflowState | None = None):
        self._state = state

    async def get_execution(self, execution_id: str):
        if self._state and self._state.workflow_id == execution_id:
            return self._state
        return self._state  # Return the state anyway for simplicity in this script

    async def get_execution_status(self, execution_id: str):
        return "completed"

    async def save_execution(self, state: WorkflowState): pass
    async def get_component_by_id(self, component_id: str):
        # Return a mock matrix config if requested
        if component_id == "matrix_standard_v1":
             return {
                 "id": "matrix_standard_v1",
                 "content": {
                     "criteria": [
                         {"id": "analysis", "label": "Analysis"},
                         {"id": "evaluation", "label": "Evaluation"},
                         {"id": "synthesis", "label": "Synthesis"}
                     ]
                 }
             }
        return None
    async def get_prompt_by_id(self, prompt_id: str): return None
    async def create_execution(self, execution_data): return "mock_id"
    async def update_execution(self, execution_id, updates): return True
    async def delete_execution(self, execution_id): return True
    async def get_all_executions(self, organization_id=None, user_id=None): return []
    async def get_workflow_definition(self, workflow_id): return None
    async def log_audit_event(self, event_data): pass
    async def get_audit_logs(self, **kwargs): return []
    async def get_all_workflows(self, **kwargs): return []
    async def get_workflow_by_id(self, workflow_id): return None
    async def create_workflow(self, workflow_data): return "mock_wf_id"
    async def update_workflow(self, workflow_id, updates): return True
    async def delete_workflow(self, workflow_id): return True
    async def get_all_steps(self): return []
    async def get_step_by_id(self, step_id): return None
    async def create_step(self, step_data): return "mock_step_id"
    async def update_step(self, step_id, updates): return True
    async def delete_step(self, step_id): return True
    async def get_all_components(self, **kwargs): return []
    async def get_component_by_name(self, name): return None
    async def update_component_metadata(self, *args): return True
    async def register_component(self, component_data): return "mock_comp_id"
    async def get_banned_phrases(self): return []
    async def add_banned_phrase(self, *args): pass
    async def delete_banned_phrase(self, *args): return True
    async def count_workflows(self): return 0
    async def get_prompt_template(self, template_id): return None
    async def get_knowledge_base_items(self): return []
    async def get_model_registry(self): return {}
    async def update_model_registry(self, registry_data): return True
    async def count_executions_by_matrix(self, matrix_id): return 0
    async def get_components_using_dimension(self, dimension_id): return []
    async def log_usage(self, record): pass
    async def list_organizations(self): return []
    async def get_organization(self, org_id): return None
    async def create_organization(self, org_data): return "mock_org_id"
    async def update_organization(self, org_id, updates): return True
    async def delete_organization(self, org_id): return True
    async def list_users(self, org_id=None): return []
    async def delete_org_data(self, org_id): pass
    async def get_org_usage_total(self, org_id, since=None): return 0.0

    async def get_workflow_state(self, workflow_id: str):
        return None
    async def save_workflow_state(self, state):
        pass
    async def get_component_by_id(self, component_id: str):
        # Return a mock matrix component if needed
        return {"content": {"scale": {"min": 0, "max": 5}}}
    async def list_workflows(self):
         return []

async def main():
    logger.info("Starting Report Verification...")

    # 1. Create Agent Outputs First

    # Context & Analyst
    step_analyst = AnalystOutput(
        reasoning_trace="Analyzing the input text for grounding...",
        hypotheses=[
            Hypothesis(
                id="HYP-1",
                description="User wants to improve prompting skills.",
                confidence=0.9,
                claim_text="help me",
                evidence_found=True,
                search_query="prompting skills"
            ),
            Hypothesis(
                id="HYP-2",
                description="User is currently a passenger.",
                confidence=0.8,
                claim_text="I am lost",
                evidence_found=True,
                search_query="passenger psychology"
            )
        ],
        rag_evidence=["Found mention of 'help me' in input."],
        evidence_found=True
    )

    # ... (omitted for brevity, will be in the file)

    # Logician
    step_logician = LogicianOutput(
        reasoning_trace="Evaluating logical structure...",
        logician_data=LogicianData(
            toulmin_analysis=[
                ToulminComponent(id="T-1", claim="I want to code better.", data="Input text.", warrant="Coding requires strict logic.")
            ],
            cognitive_level=CognitiveLevel(
                bloom_level=BloomLevel.ANALYZING,
                strategic_depth=StrategicDepth.MEDIUM,
                bloom_score=4.0,
                strategic_score=2.0
            ),
            walton_scheme=WaltonScheme(
                identified_scheme="Argument from Expert Opinion",
                critical_questions=["Is the expert credible?"]
            ),
            toulmin_score=3.5
        )
    )

    # Falsifier
    step_falsifier = FalsifierOutput(
        reasoning_trace="Checking for critical loops...",
        falsifier_data=FalsifierData(
            stress_test_findings=[
                WaltonStressTest(question="Why did you say that?", observation="User corrected output.", evidence_held=True)
            ],
            fidelity_audit={
                "fidelity_score": FidelityLevel.HIGH,
                "fidelity_numeric": 3.0,
                "justification": "Good fidelity."
            }
        )
    )


    # Causal
    step_causal = CausalOutput(
        reasoning_trace="Analyzing causality...",
        causal_analysis=CausalAnalysis(
            abductive_conclusion=AbductiveConclusion.GENUINE,
            abductive_score=0.9,
            counterfactual_test=CounterfactualTest(
                plausibility_score=PlausibilityLevel.HIGH,
                plausibility_numeric=3.0,
                confidence_score=0.95,
                actual_scenario="User asked for help.",
                simulation_result="Outcome unchanged."
            ),
            abductive_reasoning={
                "verdict": "GENUINE",
                "confidence_score": 0.9
            },
            observation="Observed strict adherence.",
            hypothesis="User is truthful."
        )
    )

    # Overseer
    step_overseer = OverseerOutput(
        reasoning_trace="Checking facts...",
        overseer_data=OverseerData(
            fact_checks=[
                 {"claim": "Sky is blue.", "verification_result": "Verified", "source_or_reasoning": "Nature"},
                 {"claim": "Earth is flat.", "verification_result": "Debunked", "source_or_reasoning": "Reality", "correction": "It is round."}
            ],
            hallucination_detected=False,
            ethical_issues=[]
        )
    )

    # Judge
    step_judge = EvaluationResult(
        reasoning_trace="Based on the lack of imperative commands, the user is a Passenger.",
        matrix_id="matrix_standard_v1",
        timestamp=datetime.now(),
        total_score=1.5,
        final_verdict="PASSENGER (Matkustaja)",
        dimensions=[
            DimensionResultItem(dimension_id="analysis", dimension_label="Analysis", score=1.0, reasoning="Weak."),
            DimensionResultItem(dimension_id="evaluation", dimension_label="Evaluation", score=2.0, reasoning="Okay."),
            DimensionResultItem(dimension_id="synthesis", dimension_label="Synthesis", score=1.5, reasoning="Poor.")
        ],
        scale_min=1.0, # Update to match matrix standard
        scale_max=4.0
    )

    # Coach
    step_coach = CoachingPlan(
        reasoning_trace="User needs to be more active.",
        actionable_steps=["Use more imperative verbs.", "Define context clearly."],
        bibliography=[{"source_id": "Kahneman2011", "title": "Thinking, Fast and Slow"}],
        focus_areas=["Agency", "Clarity"]
    )

    # XAI
    step_xai = XAIOutput(
         reasoning_trace="Summarizing the verdict.",
         executive_summary="User failed the driver's license test.",
         final_verdict="PASSENGER",
         confidence_score=0.95,
         analysis_strengths="Honesty",
         analysis_weaknesses="Passivity",
         analysis_opportunities="Learn prompting strategies.",
         analysis_recommendations="Follow the coaching plan.",
         xai_report_formatted="# Executive Summary\nUser failed.\n# Detailed Analysis\n..."
    )

    # 2. Create WorkflowState with all data
    state = WorkflowState(
        workflow_id=str(uuid4()),
        user_id="test_user",
        session_id="test_session",
        step_analyst=step_analyst,
        step_logician=step_logician,
        step_falsifier=step_falsifier,
        step_causal=step_causal,
        step_overseer=step_overseer,
        step_judge=step_judge,
        step_coach=step_coach,
        step_xai=step_xai
    )


    # 3. Generate Report
    # Pass the state to the repository so it can be fetched by ID
    repo = MockWorkflowRepository(state)
    service = PdfReportService(repository=repo)

    try:
        # Use the ID from the state
        pdf_bytes = await service.generate_execution_pdf(state.workflow_id)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backend/preview_report_{timestamp}.pdf"
        with open(filename, "wb") as f:
            f.write(pdf_bytes)

        logger.info(f"SUCCESS: Report saved to {filename}")
        print(f"Report generated: {filename}")

    except Exception as e:
        logger.error(f"FAILURE: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:
        import traceback
        with open("error_log.txt", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        print("Error logged to error_log.txt")
        exit(1)
