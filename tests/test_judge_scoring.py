import pytest
from unittest.mock import MagicMock, patch
from backend.agents.judge import JudgeAgent
from backend.schemas import TuomioJaPisteet

def test_judge_scoring_calculation():
    agent = JudgeAgent()
    
    # Mock LLM response with raw scores
    mock_response = {
        "pisteet": {
            "analyysi_ja_prosessi": {"arvosana": 3, "perustelu": "ok"},
            "arviointi_ja_argumentaatio": {"arvosana": 4, "perustelu": "good"},
            "synteesi_ja_luovuus": {"arvosana": 2, "perustelu": "fair"}
        },
        # Other required fields for schema validation (mocked)
        "konfliktin_ratkaisut": [],
        "mestaruus_poikkeama": {"tunnistettu": False, "perustelu": ""},
        "aitous_epaily": {"automaattinen_lippu": False, "viesti_hitl:lle": ""},
        "kriittiset_havainnot_yhteenveto": []
    }
    
    # Mock get_json_response to return the mock_response directly
    # (We bypass actual validation here to test the calculation logic)
    with patch.object(agent, 'get_json_response', return_value=mock_response):
        result = agent._process(validation_schema=None) # Schema not needed for this mock
        
    # Assertions
    assert result['lasketut_yhteispisteet'] == 9 # 3 + 4 + 2
    assert result['lasketut_keskiarvo'] == 3.0 # 9 / 3

def test_judge_scoring_calculation_decimals():
    agent = JudgeAgent()
    
    mock_response = {
        "pisteet": {
            "analyysi_ja_prosessi": {"arvosana": 4, "perustelu": ""},
            "arviointi_ja_argumentaatio": {"arvosana": 4, "perustelu": ""},
            "synteesi_ja_luovuus": {"arvosana": 3, "perustelu": ""}
        }
    }
    
    with patch.object(agent, 'get_json_response', return_value=mock_response):
        result = agent._process()
        
    assert result['lasketut_yhteispisteet'] == 11
    assert result['lasketut_keskiarvo'] == 3.67 # 11 / 3 rounded to 2 decimals
