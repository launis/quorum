"""Regression test for SDUI schema discriminator omission in Structured Outputs.

Reproduces the bug where Pydantic fails with:
    ValidationError: Unable to extract tag using discriminator 'block_type'
when an LLM outputs content blocks without explicit 'block_type' or when
the schema generator omits 'block_type' from 'required'.
"""

from typing import Annotated, Any, Literal
import pytest
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from backend_v2.llm.adapters.base_adapter import BaseLLMAdapter
from backend_v2.llm.ingress_pipeline import UniversalIngress
from backend_v2.models.dtos.synthesis import MatrixSectionSynthesesResult
from backend_v2.models.view.sdui import AlertBlock, BulletListBlock, ParagraphBlock


class DummyAdapter(BaseLLMAdapter):
    """Minimal adapter subclass for testing _strip_unsupported_constraints."""

    def prepare_structured_output(self, response_model: type[BaseModel]) -> dict[str, Any] | type[BaseModel]:
        json_schema = response_model.model_json_schema()
        self._strip_unsupported_constraints(json_schema)
        return json_schema

    def prepare_caching_payload(self, messages: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        return messages, {}

    def prepare_provider_kwargs(self, model: str, temperature: float | None = None) -> dict[str, Any]:
        return {}

    def calculate_cost(self, usage: Any) -> float:
        return 0.0

    async def teardown_cache(self, cache_id: str) -> None:
        pass


def test_schema_generator_requires_discriminator_properties():
    """Partition 1: Verify that _strip_unsupported_constraints forces 'block_type' to be required in schema."""
    adapter = DummyAdapter()
    schema = adapter.prepare_structured_output(MatrixSectionSynthesesResult)
    assert isinstance(schema, dict)
    defs = schema.get("$defs", {})

    # In strict mode, discriminator fields like block_type MUST be listed in required
    assert "ParagraphBlock" in defs
    assert "block_type" in defs["ParagraphBlock"].get("required", []), (
        "ParagraphBlock schema must require 'block_type' so LLM outputs the discriminator"
    )

    assert "AlertBlock" in defs
    assert "block_type" in defs["AlertBlock"].get("required", []), (
        "AlertBlock schema must require 'block_type' so LLM outputs the discriminator"
    )


def test_ingress_pipeline_handles_missing_discriminator_in_discriminated_union():
    """Partition 2: Verify that UniversalIngress.clean_dict_against_model correctly handles discriminated
    unions where the LLM omitted the explicit discriminator tag ('block_type') for AlertBlock.
    """
    raw_llm_payload = {
        "sections": [
            {
                "layout_id": "layout_2_2d_compare",
                "content_blocks": [
                    {
                        "text": "Arviointi korostaa kriittistä läpinäkyvyyden puutetta...",
                        "citations": [0, 2, 3],
                        "exact_quotes": ["Logiikka on täysin piilotettu."],
                        "id": "layout_2_2d_compare_paragraph_1",
                        "severity": "critical_override",
                    }
                ],
            }
        ]
    }

    # ACL cleans the dict against the root response model
    cleaned = UniversalIngress.clean_dict_against_model(raw_llm_payload, MatrixSectionSynthesesResult)

    # Validation must succeed and produce an AlertBlock (since severity is present)
    result = MatrixSectionSynthesesResult.model_validate(cleaned)
    assert len(result.sections) == 1
    assert len(result.sections[0].content_blocks) == 1
    block = result.sections[0].content_blocks[0]
    assert isinstance(block, AlertBlock)
    assert block.block_type == "alert_box"
    assert block.severity == "critical_override"


def test_ingress_pipeline_handles_missing_discriminator_for_paragraph_and_bullet_list():
    """Partition 3: Verify that UniversalIngress resolves ParagraphBlock and BulletListBlock
    when block_type is omitted by the LLM.
    """
    raw_llm_payload = {
        "sections": [
            {
                "layout_id": "layout_1_radar",
                "content_blocks": [
                    {
                        "text": "Yleinen yhteenveto johtamistavasta ja tuloksista.",
                        "citations": [1],
                        "exact_quotes": ["Johtamistapa on osallistava."],
                        "id": "paragraph_1",
                    },
                    {
                        "items": [
                            {"text": "Kohta 1: Strateginen selkeys", "citations": [], "exact_quotes": []},
                            {"text": "Kohta 2: Viestinnän avoimuus", "citations": [], "exact_quotes": []},
                        ],
                        "id": "list_1",
                    },
                ],
            }
        ]
    }

    cleaned = UniversalIngress.clean_dict_against_model(raw_llm_payload, MatrixSectionSynthesesResult)
    result = MatrixSectionSynthesesResult.model_validate(cleaned)

    assert len(result.sections) == 1
    assert len(result.sections[0].content_blocks) == 2

    p_block = result.sections[0].content_blocks[0]
    assert isinstance(p_block, ParagraphBlock)
    assert p_block.block_type == "paragraph"
    assert p_block.text == "Yleinen yhteenveto johtamistavasta ja tuloksista."

    b_block = result.sections[0].content_blocks[1]
    assert isinstance(b_block, BulletListBlock)
    assert b_block.block_type == "bullet_list"
    assert len(b_block.items) == 2


def test_strip_unsupported_constraints_preserves_custom_discriminator_names():
    """Partition 4: Verify that _strip_unsupported_constraints forces arbitrary discriminator
    properties into required for custom discriminated unions.
    """
    class VariantA(BaseModel):
        model_config = ConfigDict(strict=True, extra="forbid")
        extension_type: Literal["type_a"] = "type_a"
        data_a: str

    class VariantB(BaseModel):
        model_config = ConfigDict(strict=True, extra="forbid")
        extension_type: Literal["type_b"] = "type_b"
        data_b: int

    CustomUnion = Annotated[VariantA | VariantB, Field(discriminator="extension_type")]

    class CustomContainer(BaseModel):
        model_config = ConfigDict(strict=True, extra="forbid")
        items: list[CustomUnion]

    adapter = DummyAdapter()
    schema = adapter.prepare_structured_output(CustomContainer)
    defs = schema.get("$defs", {})

    assert "VariantA" in defs
    assert "extension_type" in defs["VariantA"].get("required", [])
    assert "VariantB" in defs
    assert "extension_type" in defs["VariantB"].get("required", [])


def test_ingress_pipeline_rejects_completely_invalid_union_dict():
    """Partition 5: Verify that truly invalid union payloads still fail Pydantic validation (Fail-Fast)."""
    raw_llm_payload = {
        "sections": [
            {
                "layout_id": "layout_invalid",
                "content_blocks": [
                    {
                        "completely_unknown_key": 12345,
                    }
                ],
            }
        ]
    }

    cleaned = UniversalIngress.clean_dict_against_model(raw_llm_payload, MatrixSectionSynthesesResult)
    with pytest.raises(ValidationError):
        MatrixSectionSynthesesResult.model_validate(cleaned)
