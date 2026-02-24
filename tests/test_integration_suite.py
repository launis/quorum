
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone
import uuid
from typing import Any, Dict, List

from pydantic import BaseModel, Field

# Backend Imports
from backend.core.engine import GraphEngine
from backend.models.workflow import WorkflowDefinition, WorkflowStep
from backend.models.state import WorkflowState, TraceEvent
from backend.models.domain.inputs import WorkflowInputs
from backend.exceptions import AppException, ErrorCodes, WorkflowExecutionError

# Domain Models for Reporting Hook
from backend.hooks.reporting import generate_report
from backend.models.domain.xai import XAIOutput, ReportContext
from backend.models.domain.judge import JudgeOutput, JudgeScoreCard, DimensionResultItem
from backend.models.domain.evaluation import EvaluationResult
from backend.models.domain.overseer import OverseerOutput, OverseerData, EthicalObservation, FactCheckRFI
from backend.models.domain.logician import LogicianOutput, LogicianData, WaltonScheme, ToulminComponent, CognitiveLevel
from backend.models.domain.performativity import PerformativityOutput, PerformativityAnalysis, PreMortemAnalysis, PerformativityHeuristic
from backend.models.enums import AuthenticityLevel, BloomLevel, StrategicDepth, FidelityLevel, AbductiveConclusion, PlausibilityLevel
from backend.models.domain.coach import BibliographyResult, BibliographyItem

# --- Test Data Fixtures ---

@pytest.fixture
def simple_workflow_def():
    return WorkflowDefinition(
        id="test_flow",
        name="Test Workflow",
        description="A simple mock workflow",
        steps=[
            WorkflowStep(
                id="step_1",
                name="Step 1",
                task_key="mock_task_1",
                inputs={"data": "$inputs.history_text"}
            ),
            WorkflowStep(
                id="step_2",
                name="Step 2",
                task_key="mock_task_2",
                inputs={"prev_result": "$step_1.result"}
            )
        ]
    )

@pytest.fixture
def engine():
    return GraphEngine()

# --- Mock Models for Typed retrieval ---
class MockInputModel(BaseModel):
    field_a: str
    field_b: int

class MockOutputModel(BaseModel):
    result: str
    score: float

class TestWorkflowEngine:
    """
    Comprehensive tests for the GraphEngine (Orchestrator).
    Select with: pytest -k TestWorkflowEngine
    """

    @pytest.mark.asyncio
    async def test_01_initial_state_inflation(self, engine, simple_workflow_def):
        """Verify state initialization and input inflation."""
        
        valid_payload = {
            "inputs": {
                "history_text": "History",
                "organization_id": "org-123"
            },
            "extra_context": "foo"
        }

        with patch("backend.core.registry.TaskRegistry.get") as mock_get:
            mock_task = MagicMock()
            mock_task.input_schema = MockInputModel 
            mock_task.handler = AsyncMock(return_value={"result": "pass"})
            mock_get.return_value = mock_task

            def_copy = simple_workflow_def.model_copy(update={
                "steps": [
                        WorkflowStep(
                            id="step_1",
                            name="Step 1",
                            task_key="mock_task_1",
                            inputs={"field_a": "A", "field_b": "1"}
                        )
                ]
            })

            result = await engine.execute_workflow(def_copy, valid_payload)
            
            assert result["status"] == "completed"
            assert result["workflow_id"] == "test_flow"
            ctx = result["context_variables"]
            assert isinstance(ctx["inputs"], dict)
            assert ctx["inputs"]["history_text"] == "User: History"
            assert ctx["inputs"]["organization_id"] == "org-123"
            assert ctx["extra_context"] == "foo"

    @pytest.mark.asyncio
    async def test_02_input_inflation_failure(self, engine, simple_workflow_def):
        """Verify that invalid input structure raises 400."""
        invalid_payload = {
            "inputs": ["not", "a", "dict"] 
        }

        with pytest.raises(AppException) as excinfo:
            await engine.execute_workflow(simple_workflow_def, invalid_payload)
        
        assert excinfo.value.status_code == 400
        assert excinfo.value.error_code == ErrorCodes.INVALID_JSON_PAYLOAD

    def test_resolve_inputs_strict(self, engine):
        """Test _resolve_inputs logic strictly."""
        state = WorkflowState(
            workflow_id="test",
            context_variables={
                "inputs": WorkflowInputs(history_text="Official History"),
                "step_1": {"nested": {"val": 42}},
                "step_typed": MockOutputModel(result="Success", score=0.9)
            }
        )

        # 1. Simple Mapping
        mapping = {"text": "$inputs.history_text"}
        res = engine._resolve_inputs(mapping, state)
        assert res["text"] == "Official History"

        # 2. Nested Dict Mapping
        mapping = {"num": "$step_1.nested.val"}
        res = engine._resolve_inputs(mapping, state)
        assert res["num"] == 42

        # 3. Model Attribute Mapping
        mapping = {"sc": "$step_typed.score"}
        res = engine._resolve_inputs(mapping, state)
        assert res["sc"] == 0.9

        # 4. Strict Typed Retrieval (Whole Object)
        class ConsumerModel(BaseModel):
            source: MockOutputModel

        mapping = {"source": "$step_typed"}
        res = engine._resolve_inputs(mapping, state, input_schema=ConsumerModel)
        assert isinstance(res["source"], MockOutputModel)
        assert res["source"].result == "Success"

    @pytest.mark.asyncio
    async def test_03_execute_workflow_success(self, engine, simple_workflow_def):
        """Full execution of a 2-step workflow."""
        with patch("backend.core.registry.TaskRegistry.get") as mock_get:
            task1 = MagicMock()
            class Input1(BaseModel):
                data: str
            task1.input_schema = Input1
            task1.handler = AsyncMock(return_value={"result": "step1_data", "reasoning": "thought1"})
            
            task2 = MagicMock()
            class Input2(BaseModel):
                prev_result: str
            task2.input_schema = Input2
            task2.handler = AsyncMock(return_value={"final": "done", "reasoning": "thought2"})

            def get_task(key):
                if key == "mock_task_1": return task1
                if key == "mock_task_2": return task2
                return None
            mock_get.side_effect = get_task

            payload = {"inputs": {"history_text": "Start"}}
            final_state_dump = await engine.execute_workflow(simple_workflow_def, payload)
            
            assert final_state_dump["status"] == "completed"
            trace = final_state_dump["execution_trace"]
            assert len(trace) == 2
            
            assert trace[0]["step_name"] == "step_1"
            assert trace[0]["content"] == {"result": "step1_data"}
            
            assert trace[1]["step_name"] == "step_2"
            assert trace[1]["content"] == {"final": "done"}

    @pytest.mark.asyncio
    async def test_04_execute_fail_fast_validation(self, engine, simple_workflow_def):
        """Verify execution stops if input validation fails."""
        with patch("backend.core.registry.TaskRegistry.get") as mock_get:
            task1 = MagicMock()
            class IntInput(BaseModel):
                idx: int
            task1.input_schema = IntInput
            mock_get.return_value = task1

            bad_def = simple_workflow_def.model_copy(update={
                "steps": [
                     WorkflowStep(
                        id="step_1",
                        name="Step 1",
                        task_key="mock_task_1", 
                        inputs={"idx": "NOT_AN_INT"}
                    )
                ]
            })

            with pytest.raises(AppException) as exc:
                await engine.execute_workflow(bad_def, {"inputs": {}})
            
            assert exc.value.status_code == 400
            assert exc.value.error_code == ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED

    @pytest.mark.asyncio
    async def test_05_execute_task_not_found(self, engine, simple_workflow_def):
        """Verify 404 if task key missing from registry."""
        with patch("backend.core.registry.TaskRegistry.get", return_value=None):
            with pytest.raises(AppException) as exc:
                await engine.execute_workflow(simple_workflow_def, {"inputs": {}})
            
            assert exc.value.status_code == 404
            assert exc.value.error_code == ErrorCodes.TASK_NOT_FOUND

    @pytest.mark.asyncio
    async def test_06_halting_signal(self, engine, simple_workflow_def):
        """Verify execution stops when finding stop_execution=True."""
        with patch("backend.core.registry.TaskRegistry.get") as mock_get:
            task1 = MagicMock()
            task1.input_schema = MockInputModel
            task1.handler = AsyncMock(return_value={"stop_execution": True, "reason": "guard triggered"})
            mock_get.return_value = task1

            def_halt = simple_workflow_def.model_copy(update={
                 "steps": [
                    WorkflowStep(
                        id="step_1",
                        name="Step 1",
                        task_key="mock_task_1", 
                        inputs={"field_a": "x", "field_b": "1"}
                    ),
                    WorkflowStep(
                        id="step_2",
                        name="Step 2",
                        task_key="mock_task_2",
                        inputs={}
                    )
                ]
            })

            final_state = await engine.execute_workflow(def_halt, {"inputs": {}})
            
            assert final_state["status"] == "stopped"
            trace = final_state["execution_trace"]
            assert len(trace) == 1
            assert trace[0]["content"]["stop_execution"] is True

    @pytest.mark.asyncio
    async def test_07_hook_execution(self, engine):
        """Verify hooks are mapped and executed."""
        wf = WorkflowDefinition(
            id="hook_test",
            name="Hook Test",
            description="Testing hooks",
            steps=[
                WorkflowStep(
                    id="step_h",
                    name="Step H",
                    task_key="mock_task",
                    config={"pre_hooks": ["mock_hook"]}
                )
            ]
        )

        with patch.dict("backend.core.engine.HOOK_MAPPING", {"mock_hook": ("tests.test_integration_suite", "mock_hook_func")}):
            with patch("backend.core.registry.TaskRegistry.get") as mock_get:
                task = MagicMock()
                class MockSchema(BaseModel):
                    pass
                task.input_schema = MockSchema
                task.handler = AsyncMock(return_value={"ok": True})
                mock_get.return_value = task

                mock_module = MagicMock()
                mock_hook_fn = MagicMock(return_value=WorkflowState(workflow_id="hooked", context_variables={"hook_ran": True}))
                mock_module.mock_hook_func = mock_hook_fn

                with patch("importlib.import_module", return_value=mock_module):
                    result = await engine.execute_workflow(wf, {"inputs": {}})
                    assert result["context_variables"].get("hook_ran") is True


class TestReportingHook:
    """
    Business Logic tests for Reporting Hook (Data Aggregation).
    Select with: pytest -k TestReportingHook
    """

    def test_generate_report_success(self):
        # 1. Mock Inputs
        inputs = WorkflowInputs(
            history_text="User: Hello\nAI: Hi there.",
            organization_id="org-123"
        )

        # 2. Mock Agent Outputs
        score_card = JudgeScoreCard(
            agent_name="Standard Judge",
            total_score=4.5,
            max_score=5,
            verdict="Good",
            dimensions=[
                DimensionResultItem(dimension_id="dim1", dimension_label="Dim 1", score=4.5, reasoning="Good stuff")
            ],
            scale_min=1.0,
            scale_max=5.0
        )
        
        xai_out = XAIOutput(
            thought_process="Thinking...",
            conclusion="Done.",
            executive_summary="Executive Summary Text",
            analysis_strengths="Strengths",
            analysis_weaknesses="Weaknesses",
            analysis_opportunities="Opportunities",
            analysis_recommendations="Recommendations",
            final_verdict="Verdict",
            confidence_score=0.9,
            score_cards=[score_card]
        )

        judge_out = JudgeOutput(
            thought_process="Judging...",
            conclusion="Judged.",
            confidence_score=0.9,
            matrix_id="matrix-1",
            score_card=score_card,
            scale_min=1.0,
            scale_max=5.0,
            critical_findings=["Finding 1", "Finding 2"]
        )

        overseer_out = OverseerOutput(
            thought_process="Overseeing...",
            conclusion="Overseen.",
            confidence_score=0.9,
            overseer_data=OverseerData(
                fact_checks=[],
                ethical_issues=[
                    EthicalObservation(issue_type="Bias", severity="Warning", description="Minor bias detected")
                ]
            )
        )

        perf_out = PerformativityOutput(
            thought_process="Detecting...",
            conclusion="Detected.",
            confidence_score=0.8,
            performativity_analysis=PerformativityAnalysis(
                performativity_heuristics=[
                    PerformativityHeuristic(heuristic_name="H1", flag_raised=False, description="OK")
                ],
                pre_mortem_analysis=PreMortemAnalysis(
                    performed=True,
                    weak_signals=["Signal 1", "Signal 2"]
                ),
                authenticity_assessment=AuthenticityLevel.ORGANIC,
                authenticity_score=3.0
            )
        )

        log_out = LogicianOutput(
            thought_process="Reasoning...",
            conclusion="Reasoned.",
            confidence_score=0.95,
            logician_data=LogicianData(
                toulmin_analysis=[ToulminComponent(id="t1", claim="c", data="d", warrant="w")],
                cognitive_level=CognitiveLevel(
                    bloom_level=BloomLevel.ANALYZING,
                    strategic_depth=StrategicDepth.HIGH,
                    bloom_score=4.0,
                    strategic_score=3.0
                ),
                walton_scheme=WaltonScheme(
                    identified_scheme="Scheme A",
                    critical_questions=["Q1", "Q2"]
                ),
                toulmin_score=3.0
            )
        )

        bib_res = BibliographyResult(
            references=[
                BibliographyItem(source_id="s1", title="Source 1")
            ]
        )

        # 3. Construct WorkflowState
        state = WorkflowState(
            workflow_id="test-flow",
            context_variables={
                "inputs": inputs,
                "step_xai": xai_out,
                "step_judge": judge_out,
                "step_overseer": overseer_out,
                "step_detector": perf_out,
                "step_logician": log_out,
                "bibliography_result": bib_res
            }
        )

        # 4. Run Hook
        new_state = generate_report(state)

        # 5. Assertions
        ctx = new_state.context_variables.get("report_context")
        assert ctx is not None
        assert isinstance(ctx, dict)
        
        assert ctx["summary"] == "Executive Summary Text"
        assert ctx["critical_findings"] == ["Finding 1", "Finding 2"]
        assert ctx["pre_mortem_signals"] == ["Signal 1", "Signal 2"]
        assert len(ctx["ethical_issues"]) == 1
        assert ctx["ethical_issues"][0]["issue_type"] == "Bias"
        assert len(ctx["audit_questions"]) == 2
        assert ctx["audit_questions"][0]["question"] == "Q1"
        assert "dim1" in ctx["scores"]
        assert ctx["scores"]["dim1"]["arvosana"] == 4.5
        assert ctx["average_score"] == 4.5
        assert len(ctx["bibliography"]) == 1
        assert ctx["bibliography"][0]["source_id"] == "s1"

    def test_generate_report_fail_fast_missing_inputs(self):
        state = WorkflowState(workflow_id="test-fail", context_variables={})
        with pytest.raises(Exception) as exc:
            generate_report(state)
        assert "Missing 'inputs'" in str(exc.value)

    def test_generate_report_fallback_minimal(self):
        inputs = WorkflowInputs(history_text="...", organization_id="1")
        state = WorkflowState(workflow_id="test-fallback", context_variables={"inputs": inputs})
        
        new_state = generate_report(state)
        ctx = new_state.context_variables.get("report_context")
        
        assert ctx["summary"] == "No Executive Summary available (XAI Agent did not run or failed)."
        assert ctx["critical_findings"] == []
        assert ctx["scores"] == {}
        assert ctx["average_score"] == 0.0
        assert ctx["bibliography"] == []
