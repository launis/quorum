"""SDUI presentation rules DTOs.

Defines immutable Pydantic V2 schemas for presentation rules,
visual intents, and aesthetic metadata used by SDUI adapters.
"""

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.enums import VisualIntent


class SourceDisplayNameDTO(V2CoreBase):
    """Localized display names for a data source or gateway.

    Attributes:
        display_name_fi: Finnish display name.
        display_name_en: English display name.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    display_name_fi: Annotated[str, Field(description="Finnish display name")]
    display_name_en: Annotated[str, Field(description="English display name")]

    def get_display_name(self, locale: str) -> str:
        """Resolve display name by locale with English fallback.

        Args:
            locale: Two-letter ISO language code (e.g. 'fi', 'en').

        Returns:
            Localized display name string.
        """
        return self.display_name_fi if locale == "fi" else self.display_name_en


class TheoryEvidenceItemDTO(V2CoreBase):
    """Localized explanation for theoretical framework grounding.

    Attributes:
        fi: Finnish explanation.
        en: English explanation.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    fi: Annotated[str, Field(description="Finnish explanation")]
    en: Annotated[str, Field(description="English explanation")]

    def get_text(self, locale: str) -> str:
        """Resolve theoretical explanation text by locale with English fallback.

        Args:
            locale: Two-letter ISO language code (e.g. 'fi', 'en').

        Returns:
            Localized framework description text.
        """
        return self.fi if locale == "fi" else self.en


class PrintableSourcesRulesDTO(V2CoreBase):
    """Aesthetic rules configuration for PrintableSourcesAdapter.

    Attributes:
        literature_source: Scientific literature source display name.
        theory_evidence_map: Mapping of framework tokens to localized explanations.
        default_tool: Default gateway tool display name.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    literature_source: Annotated[SourceDisplayNameDTO, Field(description="Scientific literature source display name")]
    theory_evidence_map: Annotated[
        dict[str, TheoryEvidenceItemDTO], Field(description="Mapping of framework tokens to localized explanations")
    ]
    default_tool: Annotated[SourceDisplayNameDTO, Field(description="Default gateway tool display name")]


class XaiAestheticsItemDTO(V2CoreBase):
    """Visual styling rules for an XAI highlight extension item.

    Attributes:
        severity: Visual severity intent for badge/card styling.
        icon_name: Material icon identifier string.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    severity: Annotated[VisualIntent, Field(description="Visual severity intent for badge/card styling")]
    icon_name: Annotated[str, Field(description="Material icon identifier string")]


class XaiAestheticsRulesDTO(V2CoreBase):
    """Aesthetic styling configuration for XaiHighlightsAdapter.

    Attributes:
        rules: Mapping from extension type to visual styling.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    rules: Annotated[
        dict[str, XaiAestheticsItemDTO], Field(description="Mapping from extension type to visual styling")
    ]

    def __getitem__(self, key: str) -> XaiAestheticsItemDTO:
        """Retrieve visual styling item by key.

        Args:
            key: Extension type identifier string.

        Returns:
            Matched XaiAestheticsItemDTO.
        """
        return self.rules[key]

    def __contains__(self, key: str) -> bool:
        """Check if styling key exists.

        Args:
            key: Extension type identifier string.

        Returns:
            True if key is defined, False otherwise.
        """
        return key in self.rules


class PenaltyRuleItemDTO(V2CoreBase):
    """Visual styling rules for an applied penalty.

    Attributes:
        severity: Visual intent indicator.
        title_key: Localization key for penalty title.
        desc_key: Localization key for penalty description.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    severity: Annotated[VisualIntent, Field(description="Visual intent indicator")]
    title_key: Annotated[str, Field(description="Localization key for penalty title")]
    desc_key: Annotated[str, Field(description="Localization key for penalty description")]


class PenaltiesRulesDTO(V2CoreBase):
    """Aesthetic styling configuration for PenaltiesAdapter.

    Attributes:
        rules: Mapping of penalty tokens to styling rules.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    rules: Annotated[dict[str, PenaltyRuleItemDTO], Field(description="Mapping of penalty tokens to styling rules")]

    def __getitem__(self, token: str) -> PenaltyRuleItemDTO:
        """Retrieve penalty styling rules by token.

        Args:
            token: Penalty token identifier string.

        Returns:
            Matched PenaltyRuleItemDTO.
        """
        return self.rules[token]

    def __contains__(self, token: str) -> bool:
        """Check if penalty token exists.

        Args:
            token: Penalty token identifier string.

        Returns:
            True if token is defined, False otherwise.
        """
        return token in self.rules


class VarianceRuleItemDTO(V2CoreBase):
    """Visual styling rules for variance alignment levels.

    Attributes:
        severity: Visual intent indicator.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    severity: Annotated[VisualIntent, Field(description="Visual intent indicator")]


class VarianceRulesDTO(V2CoreBase):
    """Aesthetic styling configuration for VarianceAdapter.

    Attributes:
        rules: Mapping of variance level keys to visual styling.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    rules: Annotated[
        dict[str, VarianceRuleItemDTO], Field(description="Mapping of variance level keys to visual styling")
    ]

    def __getitem__(self, key: str) -> VarianceRuleItemDTO:
        """Retrieve variance styling rules by level key.

        Args:
            key: Variance level identifier string.

        Returns:
            Matched VarianceRuleItemDTO.
        """
        return self.rules[key]

    def __contains__(self, key: str) -> bool:
        """Check if variance level key exists.

        Args:
            key: Variance level identifier string.

        Returns:
            True if key is defined, False otherwise.
        """
        return key in self.rules
