from typing import Any
from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel, ValidationError

from backend_v2.core.registry import (
    GridSchemaStrategy,
    HeroInsightSchemaStrategy,
    MarkdownSchemaStrategy,
    TaskDefinition,
    TaskMetadataDTO,
    TaskRegistry,
    _coerce_bool,
    get_schema_strategy,
    register_sdui_schema,
)
from backend_v2.exceptions import AppException, ConfigurationError
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.enums import BlockDataType, PromptBlockCategory
from backend_v2.models.v2_core import I18nText, MatrixClaim, MatrixScale, TDAAssertion
from backend_v2.models.view.sdui import HeroInsightBlock, MarkdownBlock


class DummyInput(BaseModel):
    val: str


class DummyOutput(BaseModel):
    res: str


def test_task_registry_registration() -> None:
    registry = TaskRegistry()
    registry._tasks.clear()

    metadata = TaskMetadataDTO(category="test_category", description="Test task meta", timeout_seconds=30)

    @registry.register_task(
        name="test_task",
        input_schema=DummyInput,
        output_schema=DummyOutput,
        metadata=metadata,
    )
    def dummy_handler(data: DummyInput) -> DummyOutput:
        """Test handler docstring."""
        return DummyOutput(res=data.val)

    task = registry.get("test_task")
    assert task.name == "test_task"
    assert task.input_schema == DummyInput
    assert task.description == "Test handler docstring."
    assert task.metadata == metadata

    with pytest.raises(AppException) as exc:
        registry.get("unknown_task")
    assert exc.value.status_code == 404

    # Test duplicate
    with pytest.raises(AppException) as exc:

        @registry.register_task(name="test_task", input_schema=DummyInput, output_schema=DummyOutput)
        def duplicate_handler(data: DummyInput) -> DummyOutput:
            return DummyOutput(res="dup")

    assert exc.value.status_code == 500


def test_task_definition_strictness() -> None:
    def handler() -> None:
        pass

    meta = TaskMetadataDTO(category="computation", tags=["fast", "core"])
    td = TaskDefinition(
        name="test",
        handler=handler,
        input_schema=DummyInput,
        output_schema=DummyOutput,
        metadata=meta,
    )
    assert td.name == "test"
    assert td.metadata == meta

    with pytest.raises(ValidationError):
        TaskDefinition(
            name="test",
            handler=handler,
            input_schema=DummyInput,
            output_schema=DummyOutput,
            extra="fail",  # type: ignore[call-arg]
        )


def test_task_metadata_dto_extra_field_forbidden() -> None:
    """ISTQB Negative Test: Extra fields on TaskMetadataDTO must raise ValidationError."""
    with pytest.raises(ValidationError):
        TaskMetadataDTO(category="test", extra_key="invalid")  # type: ignore[call-arg]


def test_get_schema_strategy_resolves_correctly() -> None:
    assert get_schema_strategy("markdown") == MarkdownSchemaStrategy
    assert get_schema_strategy("hero_insight") == HeroInsightSchemaStrategy
    assert get_schema_strategy("grid") == GridSchemaStrategy


def test_get_schema_strategy_unknown_raises_error() -> None:
    with pytest.raises(AppException) as exc:
        get_schema_strategy("unknown_type")
    assert exc.value.status_code == 500
    assert "Unknown expected_sdui_type" in exc.value.message


def test_register_sdui_schema_duplicate_raises_error() -> None:
    with pytest.raises(AppException) as exc:

        @register_sdui_schema("grid")
        class DuplicateGridSchemaStrategy(GridSchemaStrategy):
            pass

    assert exc.value.status_code == 500
    assert "is already registered" in exc.value.message


def test_coerce_bool() -> None:
    assert _coerce_bool("true") is True
    assert _coerce_bool("1") is True
    assert _coerce_bool("yes") is True
    assert _coerce_bool("false") is False
    assert _coerce_bool("0") is False
    assert _coerce_bool("no") is False
    assert _coerce_bool(True) is True
    assert _coerce_bool(False) is False
    assert _coerce_bool("other") == "other"


def test_markdown_and_hero_insight_schema_strategy() -> None:
    resolve_i18n = MagicMock(return_value="resolved")
    md_strat = MarkdownSchemaStrategy(resolve_i18n)
    assert md_strat.build_schema("TestSchema", [], strictness_level=100) == MarkdownBlock

    hero_strat = HeroInsightSchemaStrategy(resolve_i18n)
    assert hero_strat.build_schema("TestSchema", [], strictness_level=100) == HeroInsightBlock


def _mock_resolve_i18n(i18n: Any, locale: str = "en") -> str:
    if isinstance(i18n, I18nText):
        return i18n.resolve(locale)
    return str(i18n)


def test_grid_schema_strategy_shuffled_atoms() -> None:
    strat = GridSchemaStrategy(_mock_resolve_i18n)

    # Shuffled atoms with strictness >= 100
    schema_cls = strat.build_schema(
        "DynamicStrictGrid",
        criteria=[],
        has_shuffled_atoms=True,
        strictness_level=100,
        source_document_ids=["doc_1"],
        allowed_atom_ids=["atom_1"],
        allowed_dynamic_keys=["k1"],
    )
    assert issubclass(schema_cls, BaseModel)
    fields = schema_cls.model_fields
    assert "evaluations" in fields
    assert "evaluation_notes" in fields
    assert "reasoning_trace" in fields

    # Shuffled atoms with semantic strictness < 100
    schema_cls_sem = strat.build_schema(
        "DynamicSemanticGrid",
        criteria=[],
        has_shuffled_atoms=True,
        strictness_level=80,
    )
    assert "evaluations" in schema_cls_sem.model_fields


def test_grid_schema_strategy_matrix_and_criteria() -> None:
    strat = GridSchemaStrategy(_mock_resolve_i18n)

    matrix_block = MatrixPromptBlock(
        id="pb_1234567890abcdef",
        slug="matrix-1",
        label=I18nText(translations={"en": "Matrix 1"}),
        description=I18nText(translations={"en": "Matrix description"}),
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        ai_description="Matrix AI description",
        output_extensions=["confidence", "risk_flag", "custom_text", "justification"],
        scales=[
            MatrixScale(
                score=1,
                ai_label="POOR",
                claims=[
                    MatrixClaim(
                        label=I18nText(translations={"en": "Claim 1"}),
                        tda_assertions=[
                            TDAAssertion(
                                tda_id="tda_12345678901234567890123456789012",
                                inverse_evidence=False,
                                aggregation_mode="EXISTS",
                                concept_description="Concept description for testing assertion rules",
                                depends_on=(),
                            )
                        ],
                    )
                ],
            )
        ],
    )

    crit_instruction = SystemRulePromptBlock(
        id="pb_2234567890abcdef",
        slug="instruction-1",
        label=I18nText(translations={"en": "Instruction 1"}),
        description=I18nText(translations={"en": "Instruction desc"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
        type=BlockDataType.INSTRUCTION,
    )

    crit_eval = SystemRulePromptBlock(
        id="pb_3234567890abcdef",
        slug="eval-1",
        label=I18nText(translations={"en": "Eval Criterion"}),
        description=I18nText(translations={"en": "Eval desc"}),
        category_id=PromptBlockCategory.RUNTIME_VARIABLES,
        type=BlockDataType.CRITERIA,
        output_extensions=["confidence", "risk_flag", "notes"],
    )

    dag_results = {"tda_12345678901234567890123456789012": {"status": "PASSED"}}

    schema = strat.build_schema(
        "MatrixGridSchema",
        criteria=[matrix_block, crit_instruction, crit_eval],
        has_shuffled_atoms=False,
        strictness_level=100,
        dag_results=dag_results,
    )

    fields = schema.model_fields
    assert "global_matrices" in fields
    assert "pb_2234567890abcdef" in fields
    assert "pb_3234567890abcdef" in fields


def test_grid_schema_strategy_matrix_zero_evidence_omitted() -> None:
    strat = GridSchemaStrategy(_mock_resolve_i18n)

    matrix_block = MatrixPromptBlock(
        id="pb_4234567890abcdef",
        slug="no-ev-matrix",
        label=I18nText(translations={"en": "No Evidence Matrix"}),
        description=I18nText(translations={"en": "No ev desc"}),
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        scales=[
            MatrixScale(
                score=1,
                ai_label="POOR",
                claims=[
                    MatrixClaim(
                        label=I18nText(translations={"en": "Claim 1"}),
                        tda_assertions=[
                            TDAAssertion(
                                tda_id="tda_abcdef0123456789abcdef0123456789",
                                inverse_evidence=False,
                                aggregation_mode="EXISTS",
                                concept_description="Missing concept description for testing assertion rules",
                                depends_on=(),
                            )
                        ],
                    )
                ],
            )
        ],
    )

    schema = strat.build_schema(
        "NoEvidenceSchema",
        criteria=[matrix_block],
        has_shuffled_atoms=False,
        strictness_level=100,
        dag_results={},  # tda_missing not in dag_results
    )
    assert "global_matrices" not in schema.model_fields


def test_grid_schema_strategy_missing_label_raises_configuration_error() -> None:
    strat = GridSchemaStrategy(_mock_resolve_i18n)

    invalid_block = SystemRulePromptBlock.model_construct(
        id="pb_5234567890abcdef",
        slug="invalid-block",
        label=None,  # type: ignore[arg-type]
        description=I18nText(translations={"en": "Desc"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
        type=BlockDataType.CRITERIA,
    )

    with pytest.raises(ConfigurationError):
        strat.build_schema(
            "InvalidBlockSchema",
            criteria=[invalid_block],
            has_shuffled_atoms=False,
            strictness_level=100,
        )
