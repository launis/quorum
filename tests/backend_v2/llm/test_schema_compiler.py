
from pydantic import BaseModel

from backend_v2.llm.schema_builder import SchemaCompilerService
from backend_v2.models.enums import BlockDataType
from backend_v2.models.v2_core import PromptBlock


def _create_mock_blocks() -> list[PromptBlock]:
    return [
        PromptBlock.model_validate({
            "id": "blk_11111111",
            "slug": "score_x",
            "category_id": "test",
            "label": {"default_locale": "en", "translations": {"en": "Score X"}},
            "description": {"default_locale": "en", "translations": {"en": "Score X desc"}},
            "type": BlockDataType.FLOAT,
            "require_justification": True
        }),
        PromptBlock.model_validate({
            "id": "blk_22222222",
            "slug": "summary",
            "category_id": "test",
            "label": {"default_locale": "en", "translations": {"en": "Summary"}},
            "description": {"default_locale": "en", "translations": {"en": "Summary desc"}},
            "type": BlockDataType.STRING,
            "require_justification": False
        })
    ]

def test_schema_compiler_generates_correct_fields() -> None:
    blocks = _create_mock_blocks()
    DynamicModel = SchemaCompilerService.compile(blocks)

    # Assert it creates a subclass of BaseModel
    assert issubclass(DynamicModel, BaseModel)

    # Assert fields are correctly coerced and mapped
    fields = DynamicModel.model_fields
    assert "score_x" in fields
    assert fields["score_x"].annotation is float

    assert "score_x_justification" in fields
    assert fields["score_x_justification"].annotation is str

    assert "score_x_citation" in fields
    assert fields["score_x_citation"].annotation is str

    assert "summary" in fields
    assert fields["summary"].annotation is str

    # require_justification was False for summary
    assert "summary_justification" not in fields

def test_schema_compiler_prevents_memory_leaks_via_cache() -> None:
    blocks = _create_mock_blocks()

    # Compile the first instance
    FirstModel = SchemaCompilerService.compile(blocks)

    # Iterate exactly 10,000 times, mimicking a high-traffic LLM worker loop
    for _ in range(10000):
        IteratedModel = SchemaCompilerService.compile(blocks)

        # The exact memory address (id) and class definition MUST be identical.
        # This proves `create_model` was NOT called 10,000 times.
        assert id(FirstModel) == id(IteratedModel)
        assert FirstModel is IteratedModel

    # Verify model cache info
    cache_info = SchemaCompilerService._get_or_create_model.cache_info()
    assert cache_info.hits >= 10000
    assert cache_info.misses >= 1 # At least the first one missed
