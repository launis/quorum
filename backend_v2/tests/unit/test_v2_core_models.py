import pytest
from pydantic import ValidationError

from backend_v2.models.domain.prompt_blocks import SystemRulePromptBlock
from backend_v2.models.enums import DisplayScale
from backend_v2.models.state import WorkflowState  # noqa: F401 (Ensures ExecutionRecord is rebuilt)
from backend_v2.models.v2_core import ExecutionRecord, MCPAuditTrace, OutputProfile


def test_prompt_block_fail_fast_on_corrupt_type() -> None:
    data = {
        "id": "blk_1111111111111111",
        "slug": "pb_1",
        "label": {"translations": {"en": "T", "fi": "T"}},
        "description": {"translations": {"en": "D", "fi": "D"}},
        "category_id": "system_rule",
        "type": "INVALID_TYPE",
    }
    with pytest.raises(ValidationError) as exc_info:
        SystemRulePromptBlock.model_validate(data)
    assert "INVALID_TYPE" in str(exc_info.value)


def test_mcp_audit_trace_fail_fast_on_corrupt_timestamp() -> None:
    data = {"tool_id": "t1", "step_name": "s1", "query": "q", "timestamp": "not-a-date"}
    with pytest.raises(ValidationError) as exc_info:
        MCPAuditTrace.model_validate(data)
    assert "valid datetime" in str(exc_info.value)


def test_execution_record_fail_fast_on_corrupt_status() -> None:
    data = {"id": "exe_eeeeeeeeeeeeeeee", "workflow_id": "wf_1", "status": "INVALID_STATUS", "raw_inputs": {}}
    with pytest.raises(ValidationError) as exc_info:
        ExecutionRecord.model_validate(data)
    # Phase 1: status is now LaxExecutionStatus (enum) inherited from ExecutionCoreFields
    assert "INVALID_STATUS" in str(exc_info.value)


from typing import Any


def test_embedded_output_profile_description_parsing() -> None:
    # 1. Success case with valid I18nText
    valid_data: dict[str, Any] = {
        "id": "prf_1234567890123456",
        "slug": "test-profile",
        "workflow_id": "wf_9d68c573802341db",
        "name": {"translations": {"en": "My Profile", "fi": "My Profile"}},
        "description": {
            "translations": {"en": "A valid description", "fi": "A valid description"},
        },
        "display_scale": DisplayScale.ORIGINAL,
        "target_block_order": ["metadata_block", "executive_summary_block"],
        "matrix_synthesis_groups": [],
    }
    profile_success = OutputProfile.model_validate(valid_data)
    assert profile_success.description is not None
    assert profile_success.description.get("en") == "A valid description"

    # 2. Fail-fast case with invalid description
    invalid_data: dict[str, Any] = {
        "id": "prf_1234567890123456",
        "slug": "test-profile",
        "workflow_id": "wf_9d68c573802341db",
        "name": {"translations": {"en": "My Profile", "fi": "My Profile"}},
        "description": "This is a simple string instead of I18nText dict",
        "display_scale": DisplayScale.ORIGINAL,
    }
    with pytest.raises(ValidationError) as exc_info:
        OutputProfile.model_validate(invalid_data)
    assert "Input should be a valid dictionary" in str(exc_info.value)


def test_execution_record_has_context_variables() -> None:
    data = {
        "id": "exe_1234567890123456",
        "workflow_id": "wf_1234567890",
        "output_profile_id": "prof_1234567890123456",
        "status": "PENDING",
        "target_locale": "fi",
        "metadata": {},
        "raw_inputs": {},
        "context_variables": {"report_context": {"output_extensions": []}},
    }

    record = ExecutionRecord.model_validate(data, strict=False)
    assert record.context_variables == {"report_context": {"output_extensions": []}}


def test_execution_core_fields_inheritance_on_execution_record() -> None:
    """Phase 1: Verify ExecutionRecord correctly inherits ExecutionCoreFields SSOT."""
    from backend_v2.models.execution_core import ExecutionCoreFields

    # 1. Verify inheritance chain
    assert issubclass(ExecutionRecord, ExecutionCoreFields), "ExecutionRecord must inherit from ExecutionCoreFields"

    # 2. Verify ExecutionCoreFields enforces V2CoreBase config
    config = ExecutionCoreFields.model_config
    assert config.get("frozen") is True, "ExecutionCoreFields must be frozen"
    assert config.get("strict") is True, "ExecutionCoreFields must be strict"
    assert config.get("extra") == "forbid", "ExecutionCoreFields must forbid extra fields"

    # 3. Verify all core fields are accessible on ExecutionRecord instances
    core_field_names = {
        "status",
        "target_locale",
        "execution_trace",
        "execution_trace_storage_path",
        "context_variables",
        "context_variables_storage_path",
        "progress",
        "status_message",
    }
    record_fields = set(ExecutionRecord.model_fields.keys())
    missing = core_field_names - record_fields
    assert not missing, f"ExecutionRecord missing inherited core fields: {missing}"

    # 4. Verify core fields on ExecutionCoreFields itself
    ecf_fields = set(ExecutionCoreFields.model_fields.keys())
    assert core_field_names == ecf_fields, (
        f"ExecutionCoreFields must define exactly the SSOT fields. Expected: {core_field_names}, Got: {ecf_fields}"
    )


def test_strict_schema_parity_for_core_execution_fields() -> None:
    """Meta-test: Enforce that child classes inherit and do NOT redefine core fields.

    Uses __annotations__ (not model_fields) because model_fields includes
    BOTH inherited AND own fields, making it impossible to detect redefinitions.
    __annotations__ contains ONLY the fields explicitly defined at that class level.

    The 'status' field is whitelisted as a legitimate override because
    ExecutionRecord uses LaxExecutionStatus (broader type) while
    ExecutionCoreFields uses Literal (strict domain type).
    """
    from backend_v2.models.execution_core import ExecutionCoreFields
    from backend_v2.models.v2_core import ExecutionRecord

    core_field_names = set(ExecutionCoreFields.model_fields.keys())
    assert len(core_field_names) >= 5, "ExecutionCoreFields must define at least 5 shared fields"

    # Fields that child classes are explicitly allowed to override
    # (e.g., ExecutionRecord overrides 'status' with LaxExecutionStatus)
    allowed_overrides = {"status"}

    for child_cls in [WorkflowState, ExecutionRecord]:
        # 1. Verify inheritance
        assert issubclass(child_cls, ExecutionCoreFields), f"{child_cls.__name__} must inherit from ExecutionCoreFields"

        # 2. Verify NO redefinition of core fields using __annotations__
        own_annotations = child_cls.__annotations__  # Only THIS class level
        redefined = (core_field_names - allowed_overrides) & set(own_annotations.keys())
        assert not redefined, (
            f"{child_cls.__name__} illegally redefines inherited core fields: {redefined}. "
            f"These must be defined ONLY in ExecutionCoreFields."
        )

        # 3. Verify all core fields are accessible on the child
        child_all_fields = set(child_cls.model_fields.keys())
        missing = core_field_names - child_all_fields
        assert not missing, f"{child_cls.__name__} is missing inherited core fields: {missing}"


def test_output_profile_rejects_purged_synthesis_field() -> None:
    """Negative test: OutputProfile rejects purged synthesis field with ValidationError under extra='forbid'."""
    from backend_v2.models.core_base import I18nText
    from backend_v2.models.v2_core import OutputProfile

    payload = {
        "id": "prf_1234567890abcdef",
        "slug": "test-profile",
        "workflow_id": "wf_1234567890abcdef",
        "name": I18nText(translations={"en": "Test Profile"}),
        "synthesis": {},
    }
    with pytest.raises(ValidationError) as exc_info:
        OutputProfile.model_validate(payload)
    assert "Extra inputs are not permitted" in str(exc_info.value)


def test_output_profile_computed_properties() -> None:
    """Test computed properties on OutputProfile."""
    from backend_v2.models.core_base import I18nText
    from backend_v2.models.enums import TargetBlockType
    from backend_v2.models.v2_core import MatrixSynthesisGroup, OutputProfile

    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test-profile",
        workflow_id="wf_1234567890abcdef",
        name=I18nText(translations={"en": "Test Profile"}),
        target_block_order=[
            TargetBlockType.METADATA_BLOCK,
            TargetBlockType.EXECUTIVE_SUMMARY_BLOCK,
            TargetBlockType.MATRIX_GRAPHS_BLOCK,
        ],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_1111111111111111",
                title=I18nText(translations={"en": "Group 1"}),
                target_blocks=["blk_1"],
            )
        ],
        matrix_visible_columns=["label", "row_explanation"],
        synthesis_length_constraint=500,
        max_quotes_per_matrix=5,
        max_unmet_criteria=3,
    )
    assert profile.requires_executive_synthesis is True
    assert profile.requires_group_synthesis is True
    assert profile.requires_row_explanations is True
    assert profile.is_synthesis_expected is True
    assert profile.synthesis_length_constraint == 500
    assert profile.max_quotes_per_matrix == 5
    assert profile.max_unmet_criteria == 3


def test_matrix_synthesis_group_validation() -> None:
    """Test MatrixSynthesisGroup strict validation and fields."""
    from backend_v2.models.core_base import I18nText
    from backend_v2.models.v2_core import MatrixSynthesisGroup

    # Valid group with 16-hex Opaque ID
    group = MatrixSynthesisGroup(
        id="grp_1111111111111111",
        title=I18nText(translations={"en": "Group 1", "fi": "Ryhmä 1"}),
        target_blocks=["blk_1", "blk_2"],
        view_type="2d_compare",
    )
    assert group.id == "grp_1111111111111111"
    assert group.target_blocks == ["blk_1", "blk_2"]
    assert group.view_type == "2d_compare"

    # Invalid id pattern: spaces
    with pytest.raises(ValidationError):
        MatrixSynthesisGroup(
            id="invalid id with spaces!",
            title=I18nText(translations={"en": "Group 1", "fi": "Ryhmä 1"}),
            target_blocks=["blk_1"],
        )

    # Invalid id pattern: semantic slug
    with pytest.raises(ValidationError):
        MatrixSynthesisGroup(
            id="grp_critical_thinking",
            title=I18nText(translations={"en": "Group 1", "fi": "Ryhmä 1"}),
            target_blocks=["blk_1"],
        )

    # Empty target_blocks
    with pytest.raises(ValidationError):
        MatrixSynthesisGroup(
            id="grp_1111111111111111",
            title=I18nText(translations={"en": "Group 1", "fi": "Ryhmä 1"}),
            target_blocks=[],
        )


def test_output_profile_validate_matrix_graphs_coherence() -> None:
    """Test OutputProfile cross-field validation for MATRIX_GRAPHS_BLOCK and matrix_synthesis_groups."""
    from backend_v2.models.core_base import I18nText
    from backend_v2.models.enums import TargetBlockType
    from backend_v2.models.v2_core import MatrixSynthesisGroup, OutputProfile

    group = MatrixSynthesisGroup(
        id="grp_1111111111111111",
        title=I18nText(translations={"en": "Grp", "fi": "Ryhmä"}),
        target_blocks=["blk_1"],
    )

    # Valid: matrix_graphs_block with at least 1 synthesis group
    profile = OutputProfile(
        id="prf_1234567890123456",
        slug="test-profile",
        workflow_id="wf_1234567890123456",
        name=I18nText(translations={"en": "Name", "fi": "Nimi"}),
        target_block_order=[TargetBlockType.MATRIX_GRAPHS_BLOCK],
        matrix_synthesis_groups=[group],
    )
    assert len(profile.matrix_synthesis_groups) == 1

    # Invalid: matrix_graphs_block with empty matrix_synthesis_groups raises ValueError
    with pytest.raises(ValidationError) as exc_info:
        OutputProfile(
            id="prf_1234567890123456",
            slug="test-profile",
            workflow_id="wf_1234567890123456",
            name=I18nText(translations={"en": "Name", "fi": "Nimi"}),
            target_block_order=[TargetBlockType.MATRIX_GRAPHS_BLOCK],
            matrix_synthesis_groups=[],
        )
    assert "MATRIX_GRAPHS_BLOCK is present in target_block_order but matrix_synthesis_groups is empty" in str(
        exc_info.value
    )


@pytest.mark.parametrize(
    "purged_field",
    [
        "layouts",
        "metric_mappings",
        "user_role_mappings",
        "extension_labels",
    ],
)
def test_output_profile_rejects_purged_legacy_fields(purged_field: str) -> None:
    """Negative test: OutputProfile rejects purged legacy fields under extra='forbid'."""
    from backend_v2.models.v2_core import OutputProfile

    payload = {
        "id": "prf_1234567890123456",
        "slug": "test-profile",
        "workflow_id": "wf_1234567890123456",
        "name": {"translations": {"en": "Name", "fi": "Nimi"}},
        "target_block_order": ["metadata_block"],
        purged_field: [],
    }
    with pytest.raises(ValidationError) as exc_info:
        OutputProfile.model_validate(payload)
    assert "Extra inputs are not permitted" in str(exc_info.value)


def test_matrix_synthesis_group_cardinality_validation() -> None:
    """Verify strict dimensional cardinality coupling on MatrixSynthesisGroup."""
    from backend_v2.models.enums import PresetView
    from backend_v2.models.v2_core import I18nText, MatrixSynthesisGroup

    title = I18nText(translations={"en": "Title", "fi": "Otsikko"})

    # 1D metrics: exactly 1 block
    MatrixSynthesisGroup(id="grp_1111111111111111", title=title, target_blocks=["b1"], view_type=PresetView.METRICS_1D)
    with pytest.raises(ValidationError) as exc:
        MatrixSynthesisGroup(id="grp_1111111111111111", title=title, target_blocks=["b1", "b2"], view_type=PresetView.METRICS_1D)
    assert "view_type '1d_metrics' requires exactly 1 target block" in str(exc.value)

    # 2D compare: exactly 2 blocks
    MatrixSynthesisGroup(id="grp_2222222222222222", title=title, target_blocks=["b1", "b2"], view_type=PresetView.COMPARE_2D)
    with pytest.raises(ValidationError) as exc:
        MatrixSynthesisGroup(id="grp_2222222222222222", title=title, target_blocks=["b1"], view_type=PresetView.COMPARE_2D)
    assert "view_type '2d_compare' requires exactly 2 target blocks" in str(exc.value)

    # 3D radar: exactly 3 blocks
    MatrixSynthesisGroup(id="grp_3333333333333333", title=title, target_blocks=["b1", "b2", "b3"], view_type=PresetView.MATRIX_3D)
    with pytest.raises(ValidationError) as exc:
        MatrixSynthesisGroup(id="grp_3333333333333333", title=title, target_blocks=["b1", "b2"], view_type=PresetView.MATRIX_3D)
    assert "view_type '3d_matrix' requires exactly 3 target blocks" in str(exc.value)

    # Text only: at least 1 block
    MatrixSynthesisGroup(id="grp_4444444444444444", title=title, target_blocks=["b1"], view_type=PresetView.TEXT_ONLY)
    MatrixSynthesisGroup(id="grp_4444444444444444", title=title, target_blocks=["b1", "b2"], view_type=PresetView.TEXT_ONLY)
    with pytest.raises(ValidationError) as exc:
        MatrixSynthesisGroup(id="grp_4444444444444444", title=title, target_blocks=[], view_type=PresetView.TEXT_ONLY)
    assert "List should have at least 1 item after validation" in str(exc.value)


def test_output_profile_unique_group_ids_validation() -> None:
    """Verify OutputProfile enforces unique MatrixSynthesisGroup IDs."""
    from backend_v2.models.enums import PresetView, TargetBlockType
    from backend_v2.models.v2_core import I18nText, MatrixSynthesisGroup, OutputProfile

    title = I18nText(translations={"en": "Title", "fi": "Otsikko"})
    grp1 = MatrixSynthesisGroup(id="grp_1111111111111111", title=title, target_blocks=["b1"], view_type=PresetView.METRICS_1D)
    grp2 = MatrixSynthesisGroup(id="grp_1111111111111111", title=title, target_blocks=["b2"], view_type=PresetView.METRICS_1D)

    with pytest.raises(ValidationError) as exc:
        OutputProfile(
            id="prf_1234567890123456",
            slug="test-profile",
            workflow_id="wf_1234567890123456",
            name=title,
            target_block_order=[TargetBlockType.MATRIX_GRAPHS_BLOCK],
            matrix_synthesis_groups=[grp1, grp2],
        )
    assert "Duplicate synthesis group IDs detected in matrix_synthesis_groups" in str(exc.value)


def test_output_profile_plain_string_directives_and_length_constraints() -> None:
    """Verify OutputProfile accepts English plain strings for all 9 prompt directives and length constraints."""
    from backend_v2.models.enums import TargetBlockType
    from backend_v2.models.v2_core import I18nText, OutputProfile

    title = I18nText(translations={"en": "Title", "fi": "Otsikko"})
    profile = OutputProfile(
        id="prf_1234567890123456",
        slug="test-profile",
        workflow_id="wf_1234567890123456",
        name=title,
        target_block_order=[TargetBlockType.METADATA_BLOCK],
        tone_instruction="Act as a Senior Executive Coach.",
        executive_summary_directive="EXECUTIVE SUMMARY MANDATE",
        matrix_1d_synthesis_directive="1D MANDATE",
        matrix_2d_synthesis_directive="2D MANDATE",
        matrix_3d_synthesis_directive="3D MANDATE",
        matrix_text_synthesis_directive="TEXT MANDATE",
        row_explanation_directive="ROW MANDATE",
        xai_synthesis_directive="XAI MANDATE",
        variance_synthesis_directive="VARIANCE MANDATE",
        synthesis_length_constraint=1000,
        row_explanation_length_constraint=250,
        xai_length_constraint=300,
        variance_length_constraint=500,
    )

    assert profile.tone_instruction == "Act as a Senior Executive Coach."
    assert profile.executive_summary_directive == "EXECUTIVE SUMMARY MANDATE"
    assert profile.synthesis_length_constraint == 1000
    assert profile.row_explanation_length_constraint == 250
    assert profile.xai_length_constraint == 300
    assert profile.variance_length_constraint == 500
    assert profile.matrix_graph_length_constraint is None


def test_output_profile_matrix_graph_length_constraint_validation() -> None:
    """Verify matrix_graph_length_constraint valid partition [50-2000] and boundary rejection."""
    from backend_v2.models.enums import TargetBlockType
    from backend_v2.models.v2_core import I18nText, OutputProfile

    title = I18nText(translations={"en": "Title", "fi": "Otsikko"})
    base_kwargs = {
        "id": "prf_1234567890123456",
        "slug": "test-profile",
        "workflow_id": "wf_1234567890123456",
        "name": title,
        "target_block_order": [TargetBlockType.METADATA_BLOCK],
    }

    # Valid partitions
    p_valid_50 = OutputProfile(**base_kwargs, matrix_graph_length_constraint=50)
    assert p_valid_50.matrix_graph_length_constraint == 50

    p_valid_400 = OutputProfile(**base_kwargs, matrix_graph_length_constraint=400)
    assert p_valid_400.matrix_graph_length_constraint == 400

    p_valid_2000 = OutputProfile(**base_kwargs, matrix_graph_length_constraint=2000)
    assert p_valid_2000.matrix_graph_length_constraint == 2000

    # Negative: < 50
    with pytest.raises(ValidationError) as exc_low:
        OutputProfile(**base_kwargs, matrix_graph_length_constraint=49)
    assert "Input should be greater than or equal to 50" in str(exc_low.value)

    # Negative: > 2000
    with pytest.raises(ValidationError) as exc_high:
        OutputProfile(**base_kwargs, matrix_graph_length_constraint=2001)
    assert "Input should be less than or equal to 2000" in str(exc_high.value)

