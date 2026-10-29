"""Unit tests for input DTOs in backend_v2.models.dtos.inputs."""

from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from backend_v2.models.dtos.inputs import (
    Base64Attachment,
    GuidedReflectionInputDTO,
    IngressInputValue,
    ProcessedChatDTO,
    QuestionAnswerPair,
)


def test_question_answer_pair_strictness() -> None:
    """Test QuestionAnswerPair strictness, type enforcement, and immutability."""
    pair = QuestionAnswerPair(question="What?", answer="Yes.")
    assert pair.question == "What?"
    assert pair.answer == "Yes."

    with pytest.raises(ValidationError, match="Instance is frozen"):
        pair.__setattr__("question", "Why?")

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        QuestionAnswerPair.model_validate_json('{"question": "What?", "answer": "Yes.", "extra": "not allowed"}')

    with pytest.raises(ValidationError, match="Input should be a valid string"):
        QuestionAnswerPair.model_validate_json('{"question": 123, "answer": "Yes."}')


def test_guided_reflection_input_dto_strictness() -> None:
    """Test GuidedReflectionInputDTO strictness and min_length constraints."""
    pair = QuestionAnswerPair(question="Q1", answer="A1")

    dto = GuidedReflectionInputDTO(pairs=[pair], metadata={"topic": "Test"})
    assert len(dto.pairs) == 1
    assert dto.metadata["topic"] == "Test"

    with pytest.raises(ValidationError, match="List should have at least 1 item after validation, not 0"):
        GuidedReflectionInputDTO(pairs=[], metadata={})

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        GuidedReflectionInputDTO.model_validate_json(
            '{"pairs": [{"question": "Q1", "answer": "A1"}], "metadata": {}, "invalid_field": "boom"}'
        )


def test_guided_reflection_to_markdown() -> None:
    """Test deterministic Markdown serialization with and without metadata."""
    dto = GuidedReflectionInputDTO(
        pairs=[
            QuestionAnswerPair(question="First Q", answer="First A"),
            QuestionAnswerPair(question="Second Q", answer="Second A"),
        ],
        metadata={"b-key!": "b_value", "a_key": "a_value"},
    )

    md_output = dto.to_markdown(title="My Form")

    expected = (
        '<questionnaire title="My Form">\n'
        "  <metadata>\n"
        "    <a_key>a_value</a_key>\n"
        "    <b_key>b_value</b_key>\n"
        "  </metadata>\n"
        "  <qa_pair>\n"
        "    <question>First Q</question>\n"
        "    <answer>First A</answer>\n"
        "  </qa_pair>\n"
        "  <qa_pair>\n"
        "    <question>Second Q</question>\n"
        "    <answer>Second A</answer>\n"
        "  </qa_pair>\n"
        "</questionnaire>"
    )

    assert md_output == expected

    dto_no_meta = GuidedReflectionInputDTO(
        pairs=[QuestionAnswerPair(question="Only Q", answer="Only A")],
        metadata={},
    )
    assert "<metadata>" not in dto_no_meta.to_markdown()


def test_processed_chat_dto_strictness() -> None:
    """Test ProcessedChatDTO positive instantiation and negative validation boundaries."""
    chat = ProcessedChatDTO(
        combined="<turn>User: Hi</turn>",
        user_only="Hi",
        ai_only="Hello",
    )
    assert chat.combined == "<turn>User: Hi</turn>"
    assert chat.user_only == "Hi"
    assert chat.ai_only == "Hello"

    with pytest.raises(ValidationError, match="Instance is frozen"):
        chat.__setattr__("user_only", "Mutated")

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ProcessedChatDTO.model_validate_json('{"combined": "a", "user_only": "b", "ai_only": "c", "extra": "x"}')

    with pytest.raises(ValidationError, match="Field required"):
        ProcessedChatDTO.model_validate_json('{"combined": "a", "user_only": "b"}')


def test_base64_attachment_strictness() -> None:
    """Test Base64Attachment positive instantiation and negative validation boundaries."""
    att = Base64Attachment(filename="doc.pdf", content_base64="YWJj", content_type="application/pdf")
    assert att.filename == "doc.pdf"
    assert att.content_base64 == "YWJj"
    assert att.content_type == "application/pdf"

    att_default = Base64Attachment(filename="notes.txt", content_base64="ZGVm")
    assert att_default.content_type is None

    with pytest.raises(ValidationError, match="Instance is frozen"):
        att.__setattr__("filename", "other.pdf")

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        Base64Attachment.model_validate_json('{"filename": "a.txt", "content_base64": "YWJj", "unknown": "1"}')

    with pytest.raises(ValidationError, match="Input should be a valid string"):
        Base64Attachment.model_validate_json('{"filename": 999, "content_base64": "YWJj"}')


def test_ingress_input_value_union() -> None:
    """Test IngressInputValue closed union type adapter validation."""
    adapter: TypeAdapter[IngressInputValue] = TypeAdapter(IngressInputValue)

    assert adapter.validate_python("text") == "text"
    assert adapter.validate_python(42) == 42
    assert adapter.validate_python(["a", "b"]) == ["a", "b"]

    with pytest.raises(ValidationError):
        adapter.validate_python({"unrecognized_dict": "invalid"})
