
import sys
import os
from datetime import datetime
import json

# Add project root to path
sys.path.insert(0, os.getcwd())

from backend.api.schemas import ExecutionResponse

def test_dto_with_report_data():
    print("Testing ExecutionResponse DTO with FULL Report Data...")
    
    # Simulate Complex XAI Output (JSON structure from DB)
    report_data = {
        "execution_id": "exec_report_test",
        "started_at": "2026-02-10T14:00:00",
        "status": "completed",
        "result": {
             # XAIOutput fields flattened into result by Agent logic usually
             "final_verdict": "Pass",
             "total_score": 4.0,
             "executive_summary": "Excellent adherence to mandates.",
             "analysis_strengths": "Strong logic.",
             "analysis_weaknesses": "None.",
             "score_cards": [
                 {
                     "agent_name": "Judge (Standard)",
                     "total_score": 4.0,
                     "max_score": 5,
                     "verdict": "Pass",
                     "dimensions": [
                         {"dimension_id": "logic", "score": 5, "reasoning": "Perfect."}
                     ]
                 }
             ],
             "coaching_plan": {
                 "steps": ["Keep it up"]
             }
        },
        "audit_results": {
            "step_judge": {"score": 4, "details": "..."},
            "step_analyst": {"hypotheses": ["H1", "H2"]},
            "step_xai": {
                # Raw agent output
                "executive_summary": "Excellent adherence..."
            }
        }
    }
    
    try:
        # Validate
        dto = ExecutionResponse.model_validate(report_data)
        print("✅ Validation Successful")
        
        # Serialize
        json_output = dto.model_dump_json(by_alias=True)
        data = json.loads(json_output)
        
        # Verify Deep Fields
        result = data.get("result", {})
        
        if result.get("executive_summary") == "Excellent adherence to mandates.":
             print("✅ 'executive_summary' preserved in result")
        else:
             print("❌ 'executive_summary' MISSING or CORRUPT")

        if result.get("score_cards") and len(result["score_cards"]) > 0:
             print("✅ 'score_cards' preserved")
             print(f"   - Judge: {result['score_cards'][0]['agent_name']}")
        else:
             print("❌ 'score_cards' MISSING")

        audit = data.get("audit_results", {})
        if audit.get("step_analyst"):
             print("✅ 'audit_results.step_analyst' preserved")
        else:
             print("❌ 'audit_results' MISSING")

    except Exception as e:
        print(f"❌ Validation Failed: {e}")

if __name__ == "__main__":
    test_dto_with_report_data()
