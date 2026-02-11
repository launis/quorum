
import asyncio
from backend.api.bff_transformer import ReportTransformer
from backend.models.view import SectionType

def test_transformer_dual_score_generation():
    # Mock Data (Dual Run)
    raw_data = {
        "id": "exec_dual_pdf",
        "workflow_id": "fused_audit_chain_dual",
        "results": {
            "step_results": {
                "step_judge": {
                    "score_cards": [
                        {
                            "agent_name": "Judge (matrix_standard_v1)",
                            "total_score": 3.5,
                            "scale_min": 1,
                            "scale_max": 4,
                            "final_verdict": "Good",
                            "dimensions": []
                        },
                        {
                            "agent_name": "Judge (matrix_cognitive_v2)",
                            "total_score": 42,
                            "scale_min": 10,
                            "scale_max": 50,
                            "final_verdict": "Excellent",
                            "dimensions": []
                        }
                    ]
                }
            }
        }
    }

    transformer = ReportTransformer()
    view = transformer.transform(raw_data)
    
    print(f"Transformers generated {len(view.sections)} sections.")
    score_cards = [s for s in view.sections if s.type == SectionType.SCORE_CARD]
    print(f"Found {len(score_cards)} Score Cards.")
    
    for sc in score_cards:
        print(f" - {sc.title}: Score {sc.data['total_score']} (Max {sc.data['max_score']})")
    
    if len(score_cards) == 2:
        print("SUCCESS: Dual scores detected.")
    else:
        print("FAILURE: Dual scores NOT detected.")

if __name__ == "__main__":
    test_transformer_dual_score_generation()
