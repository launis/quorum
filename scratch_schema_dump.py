from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.models.enums import BlockDataType
from backend_v2.models.v2_core import PromptBlock

compiler = PromptCompiler()

mock_block = {
    "id": "blk_1234567890abcdef",
    "slug": "eval_test",
    "category_id": "task_definition",
    "type": BlockDataType.STRING,
    "description": {"default_locale": "en", "translations": {"en": "Desc", "fi": "Desc"}},
    "label": {"default_locale": "en", "translations": {"en": "Eval Score", "fi": "Eval Score"}},
    "ai_description": "Test Desc",
}

DynamicSchema = compiler.build_dynamic_schema(
    schema_name="TestSchema", criteria=[PromptBlock.model_validate(mock_block)], strictness_level=50
)

import json
print(json.dumps(DynamicSchema.model_json_schema(), indent=2))
