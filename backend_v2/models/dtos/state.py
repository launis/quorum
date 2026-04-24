from pydantic import BaseModel, ConfigDict


class HookStateMetadata(BaseModel):
    """Strictly typed metadata for hook execution."""

    model_config = ConfigDict(frozen=True, extra="ignore", strict=True)

    target_locale: str


class I18nStatePayload(BaseModel):
    """Strictly typed payload for I18n state inputs."""

    model_config = ConfigDict(frozen=True, extra="ignore", strict=True)

    language: str
