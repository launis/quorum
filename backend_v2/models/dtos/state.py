from typing import Any

from backend_v2.models.core_base import V2CoreBase


class HookStateMetadata(V2CoreBase):
    """Strictly typed metadata for hook execution."""

    target_locale: str
    fields_to_translate: list[str] = []


class I18nStatePayload(V2CoreBase):
    """Strictly typed payload for I18n state inputs."""

    language: str


class TranslationResponseDTO(V2CoreBase):
    """Strictly typed response payload for the dynamic LLM translation hook."""

    translated_data: dict[str, Any]
