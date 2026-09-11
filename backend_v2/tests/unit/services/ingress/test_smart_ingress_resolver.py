"""Unit tests for SmartIngressResolver.

Validates 2-tier lexical matching, Anti-Collision Firewall, fail-fast required input validation,
empty input rejection, and unconstrained dynamic input preservation.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.inputs import Base64Attachment, WorkflowInputsIngress
from backend_v2.models.dtos.ingress import ResolvedIngressDTO
from backend_v2.models.v2_core import ExpectedInput
from backend_v2.services.ingress.smart_ingress_resolver import SmartIngressResolver


def _create_sample_expected_inputs() -> list[ExpectedInput]:
    """Provide standard sample expected inputs matching Holistic Audit workflow."""
    return [
        ExpectedInput(
            input_key="chat_log",
            label=I18nText(
                translations={
                    "fi": "Keskusteluhistoria (Chat)",
                    "en": "Conversation History (Chat)",
                }
            ),
            required=True,
            is_chat_history=True,
            input_modes=["file", "paste"],
            description=I18nText(translations={"en": "Chat history", "fi": "Keskusteluhistoria"}),
        ),
        ExpectedInput(
            input_key="product_text",
            label=I18nText(
                translations={
                    "fi": "Lopputuote",
                    "en": "Product",
                }
            ),
            required=False,
            is_chat_history=False,
            input_modes=["file", "paste"],
            description=I18nText(translations={"en": "Final product", "fi": "Lopputuote"}),
        ),
        ExpectedInput(
            input_key="reflection_text",
            label=I18nText(
                translations={
                    "fi": "Reflektiodokumentti",
                    "en": "Reflection",
                }
            ),
            required=False,
            is_chat_history=False,
            input_modes=["file", "paste"],
            description=I18nText(translations={"en": "Reflection document", "fi": "Reflektiodokumentti"}),
        ),
    ]


class TestSmartIngressResolver:
    """Test suite for SmartIngressResolver."""

    def setup_method(self) -> None:
        """Initialize resolver and sample expected inputs."""
        self.resolver = SmartIngressResolver()
        self.expected_inputs = _create_sample_expected_inputs()

    def test_exact_key_match_success(self) -> None:
        """Partition 1: Exact input_key match success (Tier 1)."""
        raw_inputs = WorkflowInputsIngress(
            dynamic_inputs={
                "chat_log": "User: Hello\nAI: Hi there",
                "product_text": "Final strategic roadmap report",
            }
        )

        resolved = self.resolver.resolve(raw_inputs, self.expected_inputs, target_locale="fi")

        assert isinstance(resolved, ResolvedIngressDTO)
        assert "chat_log" in resolved.resolved_inputs
        assert resolved.resolved_inputs["chat_log"] == "User: Hello\nAI: Hi there"
        assert resolved.resolved_inputs["product_text"] == "Final strategic roadmap report"
        assert resolved.source_identity_manifest["chat_log"] == "chat_log"
        assert resolved.source_identity_manifest["product_text"] == "product_text"
        assert resolved.source_identity_manifest["reflection_text"] == "Reflektiodokumentti"

    def test_localized_label_match_success(self) -> None:
        """Partition 2: Localized label and stem matching success (Tier 2)."""
        raw_inputs = WorkflowInputsIngress(
            dynamic_inputs={
                "keskusteluhistoria": "User: Strategy prompt\nAI: Response",
                "lopputuote": "Delivered executive slides",
                "reflektio": "Learnings and retrospectives",
            }
        )

        resolved = self.resolver.resolve(raw_inputs, self.expected_inputs, target_locale="en")

        assert resolved.resolved_inputs["chat_log"] == "User: Strategy prompt\nAI: Response"
        assert resolved.resolved_inputs["product_text"] == "Delivered executive slides"
        assert resolved.resolved_inputs["reflection_text"] == "Learnings and retrospectives"
        assert resolved.source_identity_manifest["chat_log"] == "keskusteluhistoria"
        assert resolved.source_identity_manifest["product_text"] == "lopputuote"
        assert resolved.source_identity_manifest["reflection_text"] == "reflektio"

    def test_collision_firewall_triggers_fail_fast(self) -> None:
        """Partition 3: Collision on slot chat_log raises 400 VALIDATION_FAILED."""
        raw_inputs = WorkflowInputsIngress(
            dynamic_inputs={
                "keskusteluhistoria": {
                    "filename": "keskusteluhistoria.pdf",
                    "content_base64": "SGVsbG8=",
                },
                "keskusteluhistoria_user_only": {
                    "filename": "keskusteluhistoria_user_only.md",
                    "content_base64": "V29ybGQ=",
                },
            }
        )

        with pytest.raises(AppException) as excinfo:
            self.resolver.resolve(raw_inputs, self.expected_inputs, target_locale="fi")

        app_exc = excinfo.value
        assert app_exc.status_code == 400
        assert app_exc.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
        assert "collision" in app_exc.details
        assert app_exc.details["collision"]["slot"] == "chat_log"
        assert "keskusteluhistoria.pdf" in app_exc.details["collision"]["sources"]
        assert "keskusteluhistoria_user_only.md" in app_exc.details["collision"]["sources"]

    def test_missing_required_input_fails_fast(self) -> None:
        """Partition 4: Missing required input raises 400 VALIDATION_FAILED."""
        raw_inputs = WorkflowInputsIngress(
            dynamic_inputs={
                "product_text": "Only product supplied, chat_log omitted",
            }
        )

        with pytest.raises(AppException) as excinfo:
            self.resolver.resolve(raw_inputs, self.expected_inputs, target_locale="en")

        app_exc = excinfo.value
        assert app_exc.status_code == 400
        assert app_exc.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
        assert app_exc.details["missing_fields"] == ["chat_log"]

    @pytest.mark.parametrize(
        "empty_value",
        [
            "",
            "   \n  \t ",
            None,
            [],
            {},
        ],
    )
    def test_empty_required_inputs_fail_fast(self, empty_value: object) -> None:
        """Partition 5: Empty required inputs fail fast with missing_fields."""
        raw_inputs = WorkflowInputsIngress(
            dynamic_inputs={
                "chat_log": empty_value,
            }
        )

        with pytest.raises(AppException) as excinfo:
            self.resolver.resolve(raw_inputs, self.expected_inputs, target_locale="fi")

        assert excinfo.value.status_code == 400
        assert excinfo.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
        assert "chat_log" in excinfo.value.details["missing_fields"]

    def test_unconstrained_dynamic_inputs_preserved(self) -> None:
        """Partition 6: Extra dynamic inputs not in expected_inputs are preserved."""
        raw_inputs = WorkflowInputsIngress(
            dynamic_inputs={
                "chat_log": "User: Discussion text\nAI: Analysis",
                "custom_metadata_tag": "v2_release_candidate",
                "document_timestamp": 1741700000,
            }
        )

        resolved = self.resolver.resolve(raw_inputs, self.expected_inputs, target_locale="fi")

        assert resolved.resolved_inputs["chat_log"] == "User: Discussion text\nAI: Analysis"
        assert resolved.resolved_inputs["custom_metadata_tag"] == "v2_release_candidate"
        assert resolved.resolved_inputs["document_timestamp"] == 1741700000
        assert resolved.source_identity_manifest["custom_metadata_tag"] == "custom_metadata_tag"

    def test_base64_attachment_object_resolution(self) -> None:
        """Boundary: Strongly typed Base64Attachment instance extraction."""
        attachment = Base64Attachment(
            filename="keskusteluhistoria.pdf",
            content_base64="ZXhhbXBsZQ==",
        )
        raw_inputs = WorkflowInputsIngress(
            dynamic_inputs={
                "file_slot_1": attachment,
            }
        )

        resolved = self.resolver.resolve(raw_inputs, self.expected_inputs, target_locale="fi")

        assert resolved.resolved_inputs["chat_log"] == attachment
        assert resolved.source_identity_manifest["chat_log"] == "keskusteluhistoria.pdf"

    def test_resolved_ingress_dto_strictness(self) -> None:
        """Boundary: ResolvedIngressDTO enforces extra='forbid' and frozen=True."""
        dto = ResolvedIngressDTO(
            resolved_inputs={"chat_log": "valid"},
            source_identity_manifest={"chat_log": "sample.pdf"},
        )

        with pytest.raises(ValidationError):
            ResolvedIngressDTO(
                resolved_inputs={"chat_log": "valid"},
                source_identity_manifest={"chat_log": "sample.pdf"},
                hallucinated_extra_key="forbidden",  # type: ignore[call-arg]
            )

        with pytest.raises(ValidationError):
            dto.resolved_inputs = {"mutated": True}  # type: ignore[misc]

    def test_ambiguous_match_fails_fast(self) -> None:
        """Negative: Candidate resolving to multiple distinct slots raises 400 VALIDATION_FAILED."""
        attachment = Base64Attachment(
            filename="keskusteluhistoria.pdf",
            content_base64="ZXhhbXBsZQ==",
        )
        raw_inputs = WorkflowInputsIngress(
            dynamic_inputs={
                "product_text": attachment,
            }
        )

        with pytest.raises(AppException) as excinfo:
            self.resolver.resolve(raw_inputs, self.expected_inputs, target_locale="fi")

        assert excinfo.value.status_code == 400
        assert excinfo.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
        assert "ambiguous_match" in excinfo.value.details
        assert "chat_log" in excinfo.value.details["ambiguous_match"]["slots"]
        assert "product_text" in excinfo.value.details["ambiguous_match"]["slots"]

    def test_raw_inputs_none_fails_fast_on_missing_required(self) -> None:
        """Negative: None raw_inputs fails fast on required inputs."""
        with pytest.raises(AppException) as excinfo:
            self.resolver.resolve(None, self.expected_inputs, target_locale="en")

        assert excinfo.value.status_code == 400
        assert excinfo.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
        assert "chat_log" in excinfo.value.details["missing_fields"]
