
import sys
import os
from datetime import datetime
from typing import Any, Dict

# Add project root to path
sys.path.insert(0, os.getcwd())

from backend.models.domain import ReportContext
try:
    from backend.hooks.reporting import generate_report
    # We can't easily run the hook without a full State object, 
    # but we can test the ReportContext model directly.
except ImportError:
    pass

def test_report_context():
    print("Testing ReportContext instantiation...")
    
    # Simulate the dictionary constructed in hooks/reporting.py
    ctx_args = {
        "summary": "Test Summary",
        "critical_findings": ["Finding 1", "Finding 2"],
        "pre_mortem_signals": [],
        "hitl_required": False,
        "ethical_issues": [],
        "audit_questions": [],
        "uncertainty": {},
        # This is the critical structure: Dict[str, Dict]
        "scores": {
            "logic": {"arvosana": 4.0, "perustelu": "Good logic"},
            "coherence": {"arvosana": 5.0, "perustelu": "Excellent"}
        },
        "average_score": 4.5,
        "timestamp": "10.02.2026",
        "coaching_plan": {"steps": ["Step 1"]},
        "penalties_applied": [],
        "score_summary": "Great job",
        "input_control_ratio": 0.8,
        "structural_warnings": [],
        "archivist_precedents": None,
        "google_search_results": []
    }
    
    try:
        # Attempt to create the model
        context = ReportContext(**ctx_args)
        print("✅ ReportContext instantiation successful")
        print(f"   Scores: {context.scores}")
        
    except Exception as e:
        print(f"❌ ReportContext instantiation FAILED: {e}")

if __name__ == "__main__":
    test_report_context()
