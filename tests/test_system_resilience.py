import pytest
import os
from fastapi import HTTPException
from unittest.mock import MagicMock, patch
from backend.api.builder_router import create_workflow, WorkflowCreateRequest
from backend.hooks.reporting import generate_report
from backend.models.state import WorkflowState, InputData
from backend.models.domain import XAIReport, Metadata, EvaluationResult, Pisteet, PisteetKriteeri

import unittest

class TestSystemResilienceAsync(unittest.IsolatedAsyncioTestCase):
    async def test_create_workflow_db_failure(self):
        """
        Test that DB failures during workflow creation result in a clean 500 error,
        not an unhandled traceback leaking internal info.
        """
        mock_engine = MagicMock()
        # Simulate DB insert crash
        mock_engine.repository.db.table.return_value.insert.side_effect = Exception("Simulated DB Crash")
        
        req = WorkflowCreateRequest(name="Fail Workflow", steps=[])
        
        # Mock User
        mock_user = MagicMock()
        mock_user.uid = "test_user"
        
        with self.assertRaises(HTTPException) as cm:
            await create_workflow(req, mock_engine, current_user=mock_user)
        
        exc = cm.exception
        assert exc.status_code == 500
        assert "Simulated DB Crash" in exc.detail

def test_reporting_hook_catches_exceptions():
    """
    Test that the Reporting Hook catches internal errors (e.g., Template Missing) 
    and writes a user-friendly error message to the report variable,
    ensuring the UI has something to show.
    """
    # Setup state with a reporter slot ready
    meta = Metadata(luontiaika="now", agentti="test", vaihe=1)
    
    # Required InputData stub
    inputs_stub = InputData(history_text="", product_text="", reflection_text="")

    state = WorkflowState(
        execution_id="test-exec-1",
        inputs=inputs_stub,
        step_reporter=XAIReport(
            metadata=meta,
            executive_summary="", analysis_strengths="", analysis_weaknesses="",
            analysis_opportunities="", analysis_recommendations="", final_verdict="", confidence_score=0.0,
            metodologinen_loki="", edellisen_vaiheen_validointi="", semanttinen_tarkistussumma=""
        )
    )
    
    # Force an exception during execution (e.g. at the start of generate_report)
    # We patch 'os.path.dirname' to throw an error, which happens early.
    with patch('os.path.dirname', side_effect=Exception("Chaos Monkey Attack")):
        new_state = generate_report(state)
        
    # Validation
    assert new_state is not None
    rep_text = new_state.step_reporter.xai_report_formatted
    assert rep_text is not None
    assert "# Virhe Raportoinnissa" in rep_text
    assert "Chaos Monkey Attack" in rep_text

def test_reporting_hook_handles_mixed_data_types():
    """
    Testaa, että reporting hook osaa käsitellä Pisteet-objektin riippumatta siitä,
    onko se Pydantic-malli vai dict (esim. model_dump() konversion jälkeen).
    Varmistaa, ettei 'AttributeError: dict object has no attribute' tapahdu.
    """
    
    # Init base types
    from backend.models.domain import TuomioJaPisteet
    meta = Metadata(luontiaika="now", agentti="test", vaihe=1)
    
    # 1. Test with POJO (Plain Old Python Object / Pydantic)
    pisteet_obj = Pisteet(
        analyysi=PisteetKriteeri(arvosana=4, perustelu="Good job"),
        synteesi=PisteetKriteeri(arvosana=3, perustelu="Okay")
    )

    # Mock Step Judge (TuomioJaPisteet to match WorkflowState schema)
    # Must provide ALL required fields from BaseJSON and TuomioJaPisteet
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
        
        # Extra fields (legacy or simulated)
        tuomio="Test Verdict", 
        confidence=0.8
    )

    # State Setup
    inputs_stub = InputData(history_text="", product_text="", reflection_text="")
    
    state = WorkflowState(
        execution_id="test-exec-mixed-types",
        inputs=inputs_stub,
        step_reporter=XAIReport(
            metadata=meta,
            executive_summary="Summary", analysis_strengths="", analysis_weaknesses="",
            analysis_opportunities="", analysis_recommendations="", final_verdict="", confidence_score=0.0,
            metodologinen_loki="", edellisen_vaiheen_validointi="", semanttinen_tarkistussumma=""
        )
    )
    state.step_judge = step_judge

    # --- Run 1: Normal Pydantic Object ---
    # Patch Environment imported in reporting.py
    # Also patch os.path.exists to ensure template dir check passes in test env
    with patch('backend.hooks.reporting.Environment') as MockEnv, \
         patch('backend.hooks.reporting.os.path.exists', return_value=True):
        
        mock_env_instance = MockEnv.return_value
        mock_template = MagicMock()
        mock_env_instance.get_template.return_value = mock_template
        
        # Mock render to return a dummy string
        mock_render = MagicMock(return_value="Valid Report")
        mock_template.render = mock_render
        
        generate_report(state)
        
        # Verify call happened
        mock_render.assert_called_once()
        
        # Verify scores were passed to template
        call_args = mock_render.call_args
        report_content = call_args.kwargs.get('report_content')
        
        assert report_content is not None, "report_content was not passed to render"
        assert "scores" in report_content
        assert report_content["scores"]["analyysi"]["score"] == 4, "Should handle Pydantic object"

    # --- Run 2: Dict Input (Simulation of Serialization issue) ---
    # Convert pisteet to dict to simulate the 'model_dump' scenario or JSON loading
    step_judge.pisteet = pisteet_obj.model_dump() 
    
    with patch('backend.hooks.reporting.Environment') as MockEnv, \
         patch('backend.hooks.reporting.os.path.exists', return_value=True):
        
        mock_env_instance = MockEnv.return_value
        mock_template = MagicMock()
        mock_env_instance.get_template.return_value = mock_template
        
        mock_render = MagicMock(return_value="Valid Report Dict")
        mock_template.render = mock_render
        
        generate_report(state)
        
        # Verify call happened
        mock_render.assert_called_once()
        
        # Verify scores worked despite input being dict
        call_args = mock_render.call_args
        report_content = call_args.kwargs.get('report_content')
        
        assert "scores" in report_content
        assert report_content["scores"]["analyysi"]["score"] == 4, "Should handle Dict object"
