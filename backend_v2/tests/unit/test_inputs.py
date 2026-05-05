import pytest
from pydantic import ValidationError

from backend_v2.models.domain.inputs import Base64Attachment, WorkflowInputs
from backend_v2.models.dtos.inputs import GuidedReflectionInputDTO, QuestionAnswerPair


def test_base64_attachment_strictness() -> None:
    """Test that Base64Attachment forbids extra fields and requires mandatory fields."""
    # Valid
    attachment = Base64Attachment(filename="test.txt", content_base64="dGVzdA==")
    assert attachment.filename == "test.txt"
    assert attachment.content_base64 == "dGVzdA=="

    # Extra fields should fail
    with pytest.raises(ValidationError):
        Base64Attachment(
            filename="test.txt",
            content_base64="dGVzdA==",
            extra_field="should_fail",  # type: ignore
        )

    # Missing mandatory
    with pytest.raises(ValidationError):
        Base64Attachment(filename="test.txt")  # type: ignore


def test_workflow_inputs_valid() -> None:
    """Test valid creation of WorkflowInputs with dynamic inputs."""
    inputs = WorkflowInputs(
        organization_id="org_123",
        user_id="usr_123",
        language="fi",
        simulation_mode=True,
        dynamic_inputs={"product_text": "Some text here", "nested": {"key": "value"}},
    )
    assert inputs.organization_id == "org_123"
    assert inputs.language == "fi"
    assert inputs.simulation_mode is True
    assert inputs.dynamic_inputs["product_text"] == "Some text here"


def test_workflow_inputs_empty_strings() -> None:
    """Test that min_length=1 catches empty strings."""
    with pytest.raises(ValidationError) as exc:
        WorkflowInputs(organization_id="")
    assert "String should have at least 1 character" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        WorkflowInputs(language="")
    assert "String should have at least 1 character" in str(exc.value)

    with pytest.raises(ValidationError):
        WorkflowInputs(user_id="")


def test_workflow_inputs_extra_fields() -> None:
    """Test that top-level extra fields are strictly forbidden."""
    with pytest.raises(ValidationError) as exc:
        WorkflowInputs(
            organization_id="org_123",
            invalid_duck_typing="should_fail",  # type: ignore
        )
    assert "Extra inputs are not permitted" in str(exc.value)


def test_workflow_inputs_base64_pollution_root() -> None:
    """Test that prevent_base64_pollution stops base64 payloads at the root level."""
    with pytest.raises(ValidationError) as exc:
        WorkflowInputs.model_validate(
            {
                "organization_id": "org_123",
                "some_file": {"filename": "test.txt", "content_base64": "dGVzdA=="},
            }
        )
    assert "Binary 'content_base64' payload detected" in str(exc.value)


def test_workflow_inputs_base64_pollution_dynamic() -> None:
    """Test that prevent_base64_pollution stops base64 payloads inside dynamic_inputs."""
    with pytest.raises(ValidationError) as exc:
        WorkflowInputs.model_validate(
            {
                "organization_id": "org_123",
                "dynamic_inputs": {"attachment": {"filename": "test.txt", "content_base64": "dGVzdA=="}},
            }
        )
    assert "Binary 'content_base64' payload detected" in str(exc.value)


def test_workflow_inputs_prevent_base64_not_dict() -> None:
    """Test prevent_base64_pollution ignores non-dict data."""

    # Since model_validator(mode="before") is called with the raw input,
    # if we pass a non-dict (like an object, though pydantic might reject it later),
    # the validator should just return it.
    class DummyObj:
        pass

    # This will fail Pydantic's core validation since WorkflowInputs expects a dict,
    # but our custom validator should not crash.
    with pytest.raises(ValidationError):
        WorkflowInputs.model_validate(DummyObj())


def test_question_answer_pair_strictness() -> None:
    """Test QuestionAnswerPair enforces strict Pydantic V2 requirements."""
    pair = QuestionAnswerPair(question="Q1", answer="A1")
    assert pair.question == "Q1"
    assert pair.answer == "A1"

    # Extra fields forbidden
    with pytest.raises(ValidationError) as exc:
        QuestionAnswerPair(question="Q1", answer="A1", extra="bad")  # type: ignore
    assert "Extra inputs are not permitted" in str(exc.value)

    # Mutation forbidden
    with pytest.raises(ValidationError):
        pair.question = "Q2"  # type: ignore


def test_guided_reflection_input_dto_strictness() -> None:
    """Test GuidedReflectionInputDTO enforces Fail-Fast constraints."""
    # Valid
    dto = GuidedReflectionInputDTO(pairs=[QuestionAnswerPair(question="Q", answer="A")], metadata={"user_id": "123"})
    assert len(dto.pairs) == 1
    assert dto.metadata["user_id"] == "123"

    # min_length=1 violation
    with pytest.raises(ValidationError) as exc:
        GuidedReflectionInputDTO(pairs=[])
    assert "List should have at least 1 item" in str(exc.value)

    # Extra fields forbidden
    with pytest.raises(ValidationError) as exc:
        GuidedReflectionInputDTO(
            pairs=[QuestionAnswerPair(question="Q", answer="A")],
            invalid_duck_typing="should_fail",  # type: ignore
        )
    assert "Extra inputs are not permitted" in str(exc.value)


def test_guided_reflection_to_markdown() -> None:
    """Test deterministically ordered Markdown serialization."""
    dto = GuidedReflectionInputDTO(
        pairs=[QuestionAnswerPair(question="Q1", answer="A1"), QuestionAnswerPair(question="Q2", answer="A2")],
        metadata={"b": "2", "a": "1"},
    )

    md = dto.to_markdown(title="Test Reflection")

    # Metadata should be sorted alphabetically by key
    assert "# Test Reflection\n" in md
    assert "**a:** 1\n" in md
    assert "**b:** 2\n" in md

    # Pairs should be serialized in order
    assert "### Q: Q1" in md
    assert "> **A:** A1\n" in md
    assert "### Q: Q2" in md
    assert "> **A:** A2" in md
