from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatRole(str, Enum):
    USER = "User"
    AI = "AI"

class ChatMessageDTO(BaseModel):
    model_config = ConfigDict(strict=True, extra="ignore")
    order: int = Field(..., description="Sequential message order (1-n)")
    role: ChatRole = Field(..., description="Sender of the message: User or AI")
    text: str = Field(..., description="Content of the message")

    @field_validator("role", mode="before")
    @classmethod
    def parse_role(cls, v: Any) -> ChatRole:
        if isinstance(v, str):
            for member in ChatRole:
                if member.value.lower() == v.lower():
                    return member
            return ChatRole(v)
        return v

class ChatHistoryDTO(BaseModel):
    model_config = ConfigDict(strict=True, extra="ignore")
    conversation: list[ChatMessageDTO] = Field(..., description="List of messages in chronological order")
