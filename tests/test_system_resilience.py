import unittest
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from backend.api.builder_router import WorkflowCreateRequest, create_workflow
from backend.hooks.reporting import generate_report
from backend.models.domain import Metadata, Pisteet, PisteetKriteeri, XAIReport
from backend.models.state import InputData, WorkflowState


class TestSystemResilienceAsync(unittest.IsolatedAsyncioTestCase):
    async def test_create_workflow_db_failure(self):
        """Test that DB failures during workflow creation result in a clean 500 error,
        not an unhandled traceback leaking internal info.
        """
        mock_engine = MagicMock()
        from unittest.mock import AsyncMock

        mock_engine.repository = MagicMock()
        mock_engine.repository.create_workflow = AsyncMock(side_effect=Exception("Simulated DB Crash"))

        req = WorkflowCreateRequest(name="Fail Workflow", steps=[])

        from backend.models.auth import TokenData, UserRole

        mock_user = TokenData(uid="test_user", role=UserRole.ROOT, email="test@example.com", organization_id="system")

        with self.assertRaises(HTTPException) as cm:
            await create_workflow(req, mock_engine, current_user=mock_user)

        exc = cm.exception
        # Check for 403 (Auth) or 500 (DB)
        assert exc.status_code == 403 or exc.status_code == 500
        assert "Simulated DB Crash" in exc.detail


def test_reporting_hook_catches_exceptions():
    """Test that the Reporting Hook catches internal errors."""
    meta = Metadata(luontiaika="now", agentti="test", vaihe=1)
    inputs_stub = InputData(history_text="", product_text="", reflection_text="")

    state = WorkflowState(
        execution_id="test-exec-1",
        inputs=inputs_stub,
        step_reporter=XAIReport(
            metadata=meta,
            executive_summary="",
            analysis_strengths="",
            analysis_weaknesses="",
            analysis_opportunities="",
            analysis_recommendations="",
            final_verdict="",
            confidence_score=0.0,
            metodologinen_loki="",
            edellisen_vaiheen_validointi="",
            semanttinen_tarkistussumma="",
        ),
    )

    with patch("os.path.dirname", side_effect=Exception("Chaos Monkey Attack")):
        new_state = generate_report(state)

    assert new_state is not None
    rep_text = new_state.step_reporter.xai_report_formatted
    assert rep_text is not None
    assert "# Virhe Raportoinnissa" in rep_text
    assert "Chaos Monkey Attack" in rep_text


def test_reporting_hook_handles_mixed_data_types():
    """Test mixed Pydantic/Dict data types in Reporting Hook."""
    from backend.models.domain import TuomioJaPisteet

    meta = Metadata(luontiaika="now", agentti="test", vaihe=1)

    pisteet_obj = Pisteet(
        analyysi=PisteetKriteeri(arvosana=4, perustelu="Good job"),
        synteesi=PisteetKriteeri(arvosana=3, perustelu="Okay"),
    )

    step_judge = TuomioJaPisteet(
        metadata=meta,
        metodologinen_loki="log",
        edellisen_vaiheen_validointi="valid",
        semanttinen_tarkistussumma="hash",
        konfliktin_ratkaisut=[],
        mestaruus_poikkeama={"tunnistettu": False, "perustelu": "None"},
        aitous_epaily={"automaattinen_lippu": False, "viesti_hitl:lle": "None"},
        pisteet=pisteet_obj,
        kriittiset_havainnot_yhteenveto=[],
        tuomio="Test Verdict",
        confidence=0.8,
    )

    inputs_stub = InputData(history_text="", product_text="", reflection_text="")

    state = WorkflowState(
        execution_id="test-exec-mixed-types",
        inputs=inputs_stub,
        step_reporter=XAIReport(
            metadata=meta,
            executive_summary="Summary",
            analysis_strengths="",
            analysis_weaknesses="",
            analysis_opportunities="",
            analysis_recommendations="",
            final_verdict="",
            confidence_score=0.0,
            metodologinen_loki="",
            edellisen_vaiheen_validointi="",
            semanttinen_tarkistussumma="",
        ),
    )
    state.step_judge = step_judge

    # Run 1
    with (
        patch("backend.hooks.reporting.Environment") as MockEnv,
        patch("backend.hooks.reporting.os.path.exists", return_value=True),
    ):
        mock_env_instance = MockEnv.return_value
        mock_template = MagicMock()
        mock_env_instance.get_template.return_value = mock_template
        mock_render = MagicMock(return_value="Valid Report")
        mock_template.render = mock_render

        generate_report(state)

        call_args = mock_render.call_args
        report_content = call_args.kwargs.get("report_content")
        assert report_content["scores"]["analyysi"]["score"] == 4

    # Run 2
    step_judge.pisteet = pisteet_obj.model_dump()

    with (
        patch("backend.hooks.reporting.Environment") as MockEnv,
        patch("backend.hooks.reporting.os.path.exists", return_value=True),
    ):
        mock_env_instance = MockEnv.return_value
        mock_template = MagicMock()
        mock_env_instance.get_template.return_value = mock_template
        mock_render = MagicMock(return_value="Valid Report Dict")
        mock_template.render = mock_render

        generate_report(state)

        call_args = mock_render.call_args
        report_content = call_args.kwargs.get("report_content")
        assert report_content["scores"]["analyysi"]["score"] == 4
