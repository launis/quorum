import sys
import asyncio
from typing import Any

async def run_debug():
    from backend_v2.models.dtos.lightweight_matrix import AtomEvaluationItemDTO
    from pydantic import ValidationError
    
    ev_dict = {
        "atom_id": "test_atom",
        "used_source_aliases": [],
        "used_evidence_ids": [],
        "extracted_facts": {},
        "exact_quotes": [],
        "internal_logic_en": {
            "step_1_identify_premise": "a",
            "step_2_scan_source": "b",
            "step_3_evaluate_anti_patterns": "c",
            "step_4_final_conclusion": "d"
        },
        "status": "FAIL",
        "chart_display_label": "lbl",
        "visual_intent": "default",
        "counter_quote": None,
        "semantic_reasoning": "reasoning",
        "contextual_override": False,
        "structural_location": "N/A",
        "extensions": {"coaching": "This is a coaching tip."}
    }
    
    try:
        dto = AtomEvaluationItemDTO.model_validate(ev_dict)
        print("AtomEvaluationItemDTO valid:", dto.extensions)
    except ValidationError as e:
        print("AtomEvaluationItemDTO ValidationError:", e)

if __name__ == "__main__":
    asyncio.run(run_debug())
