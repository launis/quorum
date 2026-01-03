
import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.append("c:/Users/risto/OneDrive/quorum")

from backend.models.state import WorkflowState, InputData
from backend.models.domain import EvaluationResult, DimensionResultItem, XAIReport
from backend.hooks.reporting import generate_report

def test_reporting():
    print("Initializing Mock State...")
    state = WorkflowState(
        execution_id="test-exec-1",
        workflow_id="wf-test",
        inputs=InputData(history_text="foo", product_text="bar", reflection_text="baz")
    )
    
    # Mock Metadata
    meta = {
        "luontiaika": datetime.now().isoformat(),
        "agentti": "Tester",
        "vaihe": 1,
        "versio": "2.0"
    }

    base_json_defaults = {
        "metadata": meta,
        "metodologinen_loki": "Log",
        "edellisen_vaiheen_validointi": "Valid",
        "semanttinen_tarkistussumma": "Hash"
    }
    
    # Simulate Judge 1 (Standard)
    res1 = EvaluationResult(
        matrix_id="matrix_standard_v1",
        total_score=3,
        scale_min=1,
        scale_max=5,
        dimensions=[
            DimensionResultItem(dimension_id="analysis", score=3, reasoning="Good analysis"),
            DimensionResultItem(dimension_id="evaluation", score=2, reasoning="OK eval")
        ],
        **base_json_defaults
    )
    
    # Simulate Judge 2 (Cognitive)
    res2 = EvaluationResult(
        matrix_id="matrix_cognitive_v2",
        total_score=4,
        scale_min=1,
        scale_max=5,
        dimensions=[
            DimensionResultItem(dimension_id="analysis", score=4, reasoning="Better analysis"),
            DimensionResultItem(dimension_id="evaluation", score=4, reasoning="Great eval")
        ],
        **base_json_defaults
    )
    
    # Populate audit_results (Side Channel)
    state.audit_results['step_judge'] = res1
    state.audit_results['step_judge_cognitive'] = res2
    
    # Initialize reporter state
    state.step_reporter = XAIReport(
        executive_summary="Test Summary",
        analysis_strengths="S",
        analysis_weaknesses="W",
        analysis_opportunities="O",
        analysis_recommendations="R",
        final_verdict="Pass",
        confidence_score=0.9,
        **base_json_defaults
    )
    
    print("Running generate_report hook...")
    updated_state = generate_report(state)
    
    print("Checking results...")
    xai = updated_state.step_reporter
    
    # Check comparison_data (Dynamic Field potentially)
    comp_data = getattr(xai, 'comparison_data', None)
    
    if comp_data:
        print("SUCCESS: comparison_data found!")
        print(json.dumps(comp_data, indent=2))
        
        # Verify rows
        rows = comp_data.get('rows', [])
        print(f"Rows count: {len(rows)}")
        if len(rows) > 0:
            print("Row 1 Delta:", rows[0].get('delta'))
    else:
        print("FAILURE: comparison_data is None or Missing.")
        
    if updated_state.step_reporter.xai_report_formatted:
        print("SUCCESS: Report Markdown generated.")
        print(updated_state.step_reporter.xai_report_formatted[:100] + "...")
    else:
        print("FAILURE: Report Markdown missing.")

if __name__ == "__main__":
    test_reporting()
