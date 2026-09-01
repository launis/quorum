"""Centralized Polyfactory model factories for strict Pydantic V2 models."""

import uuid
from typing import Any, Literal

from polyfactory.factories.pydantic_factory import ModelFactory

from backend_v2.models.domain.prompt_blocks import SystemRulePromptBlock
from backend_v2.models.enums import (
    BlockDataType,
    DisplayScale,
    PromptBlockCategory,
    TargetBlockType,
)
from backend_v2.models.v2_core import (
    I18nText,
    MatrixSynthesisGroup,
    OutputProfile,
    Workflow,
)


class I18nTextFactory(ModelFactory[I18nText]):
    """Polyfactory model factory for I18nText localization containers."""

    __model__ = I18nText
    __set_as_default_factory_for_type__ = True

    @classmethod
    def translations(cls) -> dict[str, str]:
        """Generates standard English and Finnish test translations."""
        return {"en": "English test text", "fi": "Finnish test text"}


class WorkflowFactory(ModelFactory[Workflow]):
    """Polyfactory model factory for DAG Workflow orchestrator models."""

    __model__ = Workflow
    __set_as_default_factory_for_type__ = True

    status: str = "draft"
    version: int = 1
    is_public: bool = False
    organization_id: str | None = "org_testorg123"
    allowed_exports: list[Literal["pdf", "docx", "raw_json", "xlsx"]] = ["pdf"]
    historical_context_mode: Literal["DISABLED"] = "DISABLED"
    expected_inputs: list[Any] = []
    steps: list[Any] = []

    @classmethod
    def id(cls) -> str:
        """Generates a valid Opaque Stripe ID with 'wf_' prefix."""
        return f"wf_{uuid.uuid4().hex[:16]}"

    @classmethod
    def slug(cls) -> str:
        """Generates a unique test slug."""
        return f"wf_slug_{uuid.uuid4().hex[:8]}"

    @classmethod
    def name(cls) -> I18nText:
        """Generates a localized name."""
        return I18nText(translations={"en": "Test Workflow", "fi": "Testi Työnkulku"})

    @classmethod
    def description(cls) -> I18nText:
        """Generates a localized description."""
        return I18nText(translations={"en": "Test Workflow Description", "fi": "Testi Työnkulun Kuvaus"})

    @classmethod
    def default_profile_id(cls) -> str:
        """Generates a valid default profile Opaque Stripe ID."""
        return f"prof_{uuid.uuid4().hex[:16]}"


class SystemRulePromptBlockFactory(ModelFactory[SystemRulePromptBlock]):
    """Polyfactory model factory for SystemRulePromptBlock domain models."""

    __model__ = SystemRulePromptBlock
    __set_as_default_factory_for_type__ = True

    category_id: PromptBlockCategory = PromptBlockCategory.SYSTEM_RULE
    type: BlockDataType = BlockDataType.INSTRUCTION
    is_evaluative: bool = False
    allow_decimals: bool = False
    is_lightweight_protocol: bool = False
    organization_id: str | None = "org_testorg123"
    output_extensions: list[str] = []
    instruction_text: str | None = "System instruction text for test execution."

    @classmethod
    def id(cls) -> str:
        """Generates a valid Opaque Stripe ID with 'blk_' prefix."""
        return f"blk_{uuid.uuid4().hex[:16]}"

    @classmethod
    def slug(cls) -> str:
        """Generates a unique block slug."""
        return f"blk_slug_{uuid.uuid4().hex[:8]}"

    @classmethod
    def label(cls) -> I18nText:
        """Generates a localized label."""
        return I18nText(translations={"en": "Test Block Label", "fi": "Testilohkon Nimike"})

    @classmethod
    def description(cls) -> I18nText:
        """Generates a localized description."""
        return I18nText(translations={"en": "Test Block Description", "fi": "Testilohkon Kuvaus"})


class OutputProfileFactory(ModelFactory[OutputProfile]):
    """Polyfactory model factory for OutputProfile presentation configuration models."""

    __model__ = OutputProfile
    __set_as_default_factory_for_type__ = True

    organization_id: str | None = "org_testorg123"
    display_scale: DisplayScale = DisplayScale.ORIGINAL
    target_block_order: list[TargetBlockType] = [
        TargetBlockType.METADATA_BLOCK,
        TargetBlockType.EXECUTIVE_SUMMARY_BLOCK,
        TargetBlockType.SYNTHESIS_TEXT_BLOCK,
    ]
    matrix_synthesis_groups: list[MatrixSynthesisGroup] = []

    @classmethod
    def id(cls) -> str:
        """Generates a valid Opaque Stripe ID with 'prof_' prefix."""
        return f"prof_{uuid.uuid4().hex[:16]}"

    @classmethod
    def slug(cls) -> str:
        """Generates a unique profile slug."""
        return f"prof_slug_{uuid.uuid4().hex[:8]}"

    @classmethod
    def workflow_id(cls) -> str:
        """Generates an associated workflow Opaque Stripe ID."""
        return f"wf_{uuid.uuid4().hex[:16]}"

    @classmethod
    def name(cls) -> I18nText:
        """Generates a localized name."""
        return I18nText(translations={"en": "Executive Summary Profile", "fi": "Johdon Tiivistelmä"})

    @classmethod
    def description(cls) -> I18nText:
        """Generates a localized description."""
        return I18nText(translations={"en": "Profile Description", "fi": "Profiilin Kuvaus"})
