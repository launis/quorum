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
from backend.models.domain.coach import CoachingPlan, BibliographyItem
from backend.models.domain.evaluation import DimensionResultItem
from backend.models.domain.falsifier import FalsifierData, FalsifierOutput, WaltonStressTest, ReasoningFidelity
from backend.models.domain.judge import JudgeOutput, JudgeScoreCard
from backend.models.domain.logician import CognitiveLevel, LogicianData, LogicianOutput, ToulminComponent, WaltonScheme
from backend.models.domain.overseer import OverseerData, OverseerOutput, FactCheckRFI
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

    async def save_execution(self, state: WorkflowState):
        pass

    async def get_component_by_id(self, component_id: str):
        # Return a mock matrix config if requested
        if component_id == "matrix_standard_v1":
            return {
                "id": "matrix_standard_v1",
                "content": {
                    "criteria": [
                        {"id": "analysis", "label": "Analysis"},
                        {"id": "evaluation", "label": "Evaluation"},
                        {"id": "synthesis", "label": "Synthesis"},
                    ]
                },
            }
        return None

    async def get_prompt_by_id(self, prompt_id: str):
        return None

    async def create_execution(self, execution_data):
        return "mock_id"

    async def update_execution(self, execution_id, updates):
        return True

    async def delete_execution(self, execution_id):
        return True

    async def get_all_executions(self, organization_id=None, user_id=None):
        return []

    async def get_workflow_definition(self, workflow_id):
        return None

    async def log_audit_event(self, event_data):
        pass

    async def get_audit_logs(self, organization_id=None, actor_uid=None, action=None, limit=100, **kwargs):
        from typing import Any
        return []

    async def get_all_workflows(self, organization_id=None, role=None, **kwargs):
        from typing import Any
        return []

    async def get_workflow_by_id(self, workflow_id):
        return None

    async def create_workflow(self, workflow_data):
        return "mock_wf_id"

    async def update_workflow(self, workflow_id, updates):
        return True

    async def delete_workflow(self, workflow_id):
        return True

    async def get_all_steps(self):
        return []

    async def get_step_by_id(self, step_id):
        return None

    async def create_step(self, step_data):
        return "mock_step_id"

    async def update_step(self, step_id, updates):
        return True

    async def delete_step(self, step_id):
        return True

    async def get_all_components(self, type=None, exclude_types=None, **kwargs):
        from typing import Any
        return []

    async def get_component_by_name(self, name):
        return None

    async def update_component_metadata(self, *args):
        return True

    async def register_component(self, component_data):
        return "mock_comp_id"

    async def create_component(self, component_data):
        return "mock_comp_id"

    async def delete_component(self, component_id):
        return True

    async def get_system_settings(self, organization_id=None, force_refresh=False):
        return {}

    async def update_component(self, component_id, updates):
        return True

    async def update_system_settings(self, updates, organization_id=None):
        return True

    async def get_banned_phrases(self):
        return []

    async def add_banned_phrase(self, *args):
        pass

    async def delete_banned_phrase(self, *args):
        return True

    async def count_workflows(self):
        return 0

    async def get_prompt_template(self, template_id):
        return None

    async def get_concepts(self):
        return []

    async def get_references(self):
        return []

    async def get_claims(self):
        return []

    async def clear_knowledge_base(self):
        pass

    async def add_concept(self, item):
        return "mock_id"

    async def add_reference(self, item):
        return "mock_id"

    async def add_claim(self, item):
        return "mock_id"

    async def get_model_registry(self):
        return {}

    async def update_model_registry(self, registry_data):
        return True

    async def count_executions_by_matrix(self, matrix_id):
        return 0

    async def get_components_using_dimension(self, dimension_id):
        return []

    async def log_usage(self, record):
        pass

    async def list_organizations(self):
        return []

    async def get_organization(self, org_id):
        return None

    async def create_organization(self, org_data):
        return "mock_org_id"

    async def update_organization(self, org_id, updates):
        return True

    async def delete_organization(self, org_id):
        return True

    async def list_users(self, org_id=None):
        return []

    async def delete_org_data(self, org_id):
        pass

    async def get_org_usage_total(self, org_id, since=None):
        return 0.0

    async def get_workflow_state(self, workflow_id: str):
        return None

    async def save_workflow_state(self, state):
        pass

    async def list_workflows(self):
        return []


async def main():
    logger.info("Starting Report Verification...")

    # 1. Create Agent Outputs First

    # Context & Analyst
    step_analyst = AnalystOutput(
        hypotheses=[
            Hypothesis(
                id="HYP-1",
                claim_text="help me",
                evidence_found=True,
                search_query="prompting skills",
                quotes=["user: help me"],
            ),
            Hypothesis(
                id="HYP-2",
                claim_text="I am lost",
                evidence_found=True,
                search_query="passenger psychology",
                quotes=["user: I am lost"],
            ),
        ],
        rag_evidence=["Found mention of 'help me' in input."],
        thought_process="User input indicates a need for guidance.",
        conclusion="User requires coaching.",
        confidence_score=0.9,
    )

    # ... (omitted for brevity, will be in the file)

    # Logician
    step_logician = LogicianOutput(
        thought_process="Logical structure is weak.",
        conclusion="Argument is fallacious.",
        confidence_score=0.8,
        logician_data=LogicianData(
            toulmin_analysis=[
                ToulminComponent(
                    id="T-1",
                    claim="I want to code better.",
                    data="Input text.",
                    warrant="Coding requires strict logic.",
                )
            ],
            cognitive_level=CognitiveLevel(
                bloom_level=BloomLevel.ANALYZING,
                strategic_depth=StrategicDepth.MEDIUM,
                bloom_score=4.0,
                strategic_score=2.0,
            ),
            walton_scheme=WaltonScheme(
                identified_scheme="Argument from Expert Opinion", critical_questions=["Is the expert credible?"]
            ),
            toulmin_score=3.5,
        ),
    )

    # Falsifier
    step_falsifier = FalsifierOutput(
        thought_process="No critical loops found.",
        conclusion="Stable.",
        confidence_score=0.9,
        falsifier_data=FalsifierData(
            stress_test_findings=[
                WaltonStressTest(
                    question="Why did you say that?", observation="User corrected output.", evidence_held=True
                )
            ],
            fidelity_audit=ReasoningFidelity(
                fidelity_score=FidelityLevel.HIGH,
                fidelity_numeric=3.0,
                justification="Good fidelity.",
            ),
        ),
    )

    # Causal
    step_causal = CausalOutput(
        thought_process="Causal links are tenuous.",
        conclusion="Mere correlation.",
        confidence_score=0.7,
        causal_analysis=CausalAnalysis(
            abductive_conclusion=AbductiveConclusion.GENUINE,
            abductive_score=0.9,
            counterfactual_test=CounterfactualTest(
                plausibility_score=PlausibilityLevel.HIGH,
                plausibility_numeric=3.0,
                actual_scenario="User asked for help.",
                simulation_result="Outcome unchanged.",
            ),
            observation="Observed strict adherence.",
            hypothesis="User is truthful.",
        ),
    )

    # Overseer
    step_overseer = OverseerOutput(
        thought_process="Fact check complete.",
        conclusion="Facts verified.",
        confidence_score=0.95,
        overseer_data=OverseerData(
            fact_checks=[
                FactCheckRFI(claim="Sky is blue.", verification_result="Verified", source_or_reasoning="Nature"),
                FactCheckRFI(
                    claim="Earth is flat.",
                    verification_result="Debunked",
                    source_or_reasoning="Reality",
                ),
            ],
            ethical_issues=[],
        ),
    )

    # Judge
    # Judge

    score_card = JudgeScoreCard(
        agent_name="Standard Judge",
        total_score=1.5,
        max_score=4,
        verdict="PASSENGER (Matkustaja)",
        dimensions=[
            DimensionResultItem(dimension_id="analysis", dimension_label="Analysis", score=1.0, reasoning="Weak."),
            DimensionResultItem(dimension_id="evaluation", dimension_label="Evaluation", score=2.0, reasoning="Okay."),
            DimensionResultItem(dimension_id="synthesis", dimension_label="Synthesis", score=1.5, reasoning="Poor."),
        ],
        scale_min=1.0,
        scale_max=4.0,
    )

    step_judge = JudgeOutput(
        matrix_id="matrix_standard_v1",
        score_card=score_card,
        scale_min=1.0,
        scale_max=4.0,
        confidence_score=0.9,
        thought_process="Scoring based on criteria.",
        conclusion="Low score assigned.",
    )

    # Coach
    step_coach = CoachingPlan(
        thought_process="User is passive.",
        conclusion="Action required.",
        confidence_score=0.9,
        actionable_steps=["Use more imperative verbs.", "Define context clearly."],
        bibliography=[BibliographyItem(source_id="Kahneman2011", title="Thinking, Fast and Slow")],
        focus_areas=["Agency", "Clarity"],
    )

    # XAI
    step_xai = XAIOutput(
        thought_process="Synthesizing report.",
        conclusion="Report generated.",
        confidence_score=0.95,
        executive_summary="User failed the driver's license test.",
        final_verdict="PASSENGER",
        analysis_strengths="Honesty",
        analysis_weaknesses="Passivity",
        analysis_opportunities="Learn prompting strategies.",
        analysis_recommendations="Follow the coaching plan.",
        xai_report_formatted="# Executive Summary\nUser failed.\n# Detailed Analysis\n...",
    )

    # 2. Create WorkflowState with all data
    state = WorkflowState(
        workflow_id=str(uuid4()),
        context_variables={
            "user_id": "test_user",
            "session_id": "test_session",
            "step_analyst": step_analyst.model_dump(),
            "step_logician": step_logician.model_dump(),
            "step_falsifier": step_falsifier.model_dump(),
            "step_causal": step_causal.model_dump(),
            "step_overseer": step_overseer.model_dump(),
            "step_judge": step_judge.model_dump(),
            "step_coach": step_coach.model_dump(),
            "step_xai": step_xai.model_dump(),
        }
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
