from backend_v2.models.v2_core import PromptBlock
import json

data = {
    "id": "blk_1234567890123456",
    "slug": "test",
    "label": {"default_locale": "en", "translations": {"en": "Test"}},
    "description": {"default_locale": "en", "translations": {"en": "Test"}},
    "category_id": "system_rule",
    "type": "string",
    "scales": [
        {
            "score": 5,
            "ai_label": "EXCELLENT",
            "claims": [
                {
                    "label": {"default_locale": "en", "translations": {"en": "Test"}},
                    "ai_description": "test",
                    "tda_assertions": [
                        {
                            "tda_id": "tda_12345678901234561234567890123456",
                            "concept_description": "test",
                            "inverse_evidence": False,
                            "aggregation_mode": "EXISTS",
                            "evaluation_track": "COGNITIVE_JUDGEMENT",
                            "allow_contextual_override": True,
                            "bounding_box_scope": "paragraph"
                        }
                    ]
                }
            ]
        }
    ]
}

try:
    block = PromptBlock.model_validate(data)
    tda = block.scales[0].claims[0].tda_assertions[0]
    print("Parsed allow_contextual_override:", tda.allow_contextual_override)
    dumped = block.model_dump(mode="json")
    print("Dumped allow_contextual_override:", dumped["scales"][0]["claims"][0]["tda_assertions"][0].get("allow_contextual_override"))
except Exception as e:
    import traceback
    traceback.print_exc()
