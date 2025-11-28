import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

from src.components.hooks.reporting import generate_jinja2_report

def test_print():
    mock_data = {
        "summary": "Tämä on testiyhteenveto.",
        "critical_findings": ["Havainto 1", "Havainto 2"],
        "hitl_required": False,
        "ethical_issues": [],
        "audit_questions": [],
        "uncertainty": {
            "aleatoric": "Matala",
            "systemic": [],
            "epistemic": "Matala"
        },
        "pisteet": {
            "analyysi_ja_prosessi": {"arvosana": 3, "perustelu": "Hyvä"},
            "arviointi_ja_argumentaatio": {"arvosana": 4, "perustelu": "Erinomainen"},
            "synteesi_ja_luovuus": {"arvosana": 3, "perustelu": "Luova"}
        }
    }
    
    print("--- CALLING HOOK ---")
    result = generate_jinja2_report(mock_data)
    print("--- HOOK FINISHED ---")
    
    # print("Result keys:", result.keys())
    # print("Report content type:", type(result['report_content']))

if __name__ == "__main__":
    test_print()
