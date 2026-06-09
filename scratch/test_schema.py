from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.models.v2_core import PromptBlock
from backend_v2.models.enums import BlockDataType

mock_matrix_block = {
    "id": "blk_1234567890abcdef",
    "slug": "test_matrix",
    "category_id": "matrix",
    "description": {"default_locale": "en", "translations": {"en": "Desc"}},
    "type": BlockDataType.FLOAT,
    "allow_decimals": True,
    "scale_min": 1,
    "scale_max": 5,
    "label": {"default_locale": "en", "translations": {"en": "Critical Distance Score"}},
    "ai_description": "ROLE: ADVERSARIAL AUDITOR... Evaluate the user's intellectual effort...",
    "scales": [
        {
            "score": 1,
            "ai_label": "UNCRITICAL ACCEPTANCE",
            "claims": [
                {
                    "label": {
                        "default_locale": "en",
                        "translations": {
                            "en": "The user is a 'Yes-man'. Blindly accepted the AI's first response."
                        },
                    },
                    "ai_description": "CRITICAL EVALUATION DIRECTIVE: Total failure of critical faculty.",
                    "tda_assertions": [
                        {
                            "tda_id": "tda_11111111111111111111111111111111",
                            "ai_rule_description": "Total failure of critical faculty...",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY",
                        }
                    ],
                }
            ],
        }
    ]
}

compiler = PromptCompiler()
dynamic_schema = compiler.build_dynamic_schema(
    schema_name="Step_Test_Response",
    criteria=[PromptBlock.model_validate(mock_matrix_block)],
    has_search_result=False,
    has_shuffled_atoms=True,
    target_locale="en"
)

schema_json = dynamic_schema.model_json_schema()
defs = schema_json.get("$defs", {})
atom_response_schema = None
for def_name, def_schema in defs.items():
    if "AtomResponse" in def_name:
        atom_response_schema = def_schema
        break

print(list(atom_response_schema["properties"].keys()))
