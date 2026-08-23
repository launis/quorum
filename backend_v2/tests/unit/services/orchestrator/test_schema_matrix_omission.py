from backend_v2.models.v2_core import I18nText, MatrixClaim, MatrixScale, PromptBlock, TDAAssertion
from backend_v2.services.orchestrator.schema_factory import SchemaFactory


def dummy_resolve_i18n(text: str, locale: str) -> str:
    return text


def test_build_dynamic_schema_omits_zero_evidence_matrix() -> None:
    factory = SchemaFactory(resolve_i18n_fn=dummy_resolve_i18n)

    # Create a Matrix PromptBlock
    tda = TDAAssertion(
        tda_id="tda_1234567890abcdef1234567890abcdef",
        concept_description="Test concept description valid",
        aggregation_mode="ALL_MUST_COMPLY",
        inverse_evidence=False,
    )
    claim = MatrixClaim(
        label=I18nText(default_locale="en", translations={"en": "test"}),
        tda_assertions=[tda],
    )
    scale = MatrixScale(
        score=1,
        name=I18nText(default_locale="en", translations={"en": "test_scale"}),
        ai_label="Test Scale",
        claims=[claim],
    )
    matrix = PromptBlock(
        id="blk_0123456789abcdef",
        slug="test-matrix-1",
        description=I18nText(default_locale="en", translations={"en": "test matrix block"}),
        category_id="matrix",
        scales=[scale],
        type="instruction",
        label=I18nText(default_locale="en", translations={"en": "Test Matrix"}),
    )

    # 1. No dag_results -> Matrix is included
    schema_no_dag = factory.build_dynamic_schema(
        "TestSchemaNoDag", criteria=[matrix], strictness_level=50, expected_sdui_type="grid"
    )
    assert "global_matrices" in schema_no_dag.model_fields
    assert "blk_0123456789abcdef" in schema_no_dag.model_fields["global_matrices"].annotation.model_fields

    # 2. dag_results with PASSED -> Matrix is included
    dag_passed = {"tda_1234567890abcdef1234567890abcdef": {"status": "PASSED"}}
    schema_passed = factory.build_dynamic_schema(
        "TestSchemaPassed", criteria=[matrix], strictness_level=50, dag_results=dag_passed, expected_sdui_type="grid"
    )
    assert "global_matrices" in schema_passed.model_fields
    assert "blk_0123456789abcdef" in schema_passed.model_fields["global_matrices"].annotation.model_fields

    # 4. dag_results with FAILED -> Matrix is OMITTED
    dag_failed = {"tda_1234567890abcdef1234567890abcdef": {"status": "FAILED"}}
    schema_failed = factory.build_dynamic_schema(
        "TestSchemaFailed", criteria=[matrix], strictness_level=50, dag_results=dag_failed, expected_sdui_type="grid"
    )
    assert "global_matrices" not in schema_failed.model_fields
