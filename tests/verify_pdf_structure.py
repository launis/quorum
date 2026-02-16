
import sys
from unittest.mock import MagicMock

# AGGRESSIVE MOCKING
sys.modules["numpy"] = MagicMock()
sys.modules["matplotlib"] = MagicMock()
sys.modules["matplotlib.pyplot"] = MagicMock()
sys.modules["weasyprint"] = MagicMock()

import asyncio

from backend.models.view import SectionType
from backend.services.pdf_generator import PdfReportService


# Mock Repository
class MockRepository:
    async def get_execution(self, _id):
        return {
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
                                "dimensions": [
                                    {"id": "d1", "label": "Dimension 1", "score": 3, "reasoning": "Ok"}
                                ]
                            },
                            {
                                "agent_name": "Judge (matrix_cognitive_v2)",
                                "total_score": 42,
                                "scale_min": 10,
                                "scale_max": 50,
                                "final_verdict": "Excellent",
                                "dimensions": [
                                    {"id": "c1", "label": "Cognitive 1", "score": 40, "reasoning": "Smart"}
                                ]
                            }
                        ]
                    }
                }
            }
        }

    async def get_component_by_id(self, _id):
        return None

async def test_pdf_generation_structure():
    print("Dependencies mocked aggressively.")

    repo = MockRepository()
    service = PdfReportService(repository=repo)

    try:
        # Check logic via Transformer directly
        execution = await repo.get_execution("id")
        view = service.transformer.transform(execution)

        print(f"BFF Transformer generated {len(view.sections)} sections.")
        score_cards = [s for s in view.sections if s.type == SectionType.SCORE_CARD]
        print(f"Found {len(score_cards)} Score Cards.")

        for sc in score_cards:
            print(f" - {sc.title}: Score {sc.data['total_score']} (Max {sc.data['max_score']})")

        if len(score_cards) == 2:
            print("SUCCESS: Dual scores detected.")
        else:
            print("FAILURE: Dual scores NOT detected.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pdf_generation_structure())
