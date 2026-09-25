"""State Data Transfer Objects (DTOs) for Phase 9 Cognitive Quorum V2.

This module encapsulates the structures required for handling hook states and
localization payload parameters within the state pipeline.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import ConfigDict, Field, JsonValue

from backend_v2.models.core_base import V2CoreBase


class HookStateMetadata(V2CoreBase):
    """Strictly typed metadata for hook execution.

    Attributes:
        target_locale: The designated target localization code (e.g., 'fi', 'en').
        fields_to_translate: Collection of specific dictionary keys or attributes targeted for translation.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    target_locale: Annotated[str, Field(description="Target locale code")]
    fields_to_translate: Annotated[
        list[str],
        Field(default_factory=list, description="Targeted translation fields"),
    ]


class I18nStatePayload(V2CoreBase):
    """Strictly typed payload for I18n state inputs.

    Attributes:
        language: The targeted language identification code representing state localization targets.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    language: str


class TranslationResponseDTO(V2CoreBase):
    """Strictly typed response payload for the dynamic LLM translation hook.

    Attributes:
        translated_data: Fully translated dictionary representing localized dynamic key-value pairs.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    translated_data: Annotated[
        dict[str, JsonValue],
        Field(description="Fully translated dictionary representing localized dynamic key-value pairs."),
    ]
