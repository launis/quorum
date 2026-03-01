from enum import Enum
from pydantic import BaseModel, ConfigDict, Field

class ChatRole(str, Enum):
    USER = "User"
    AI = "AI"

class ChatMessageDTO(BaseModel):
    model_config = ConfigDict(strict=True, extra="ignore")
    order: int = Field(..., description="Viestin järjestysnumero (1-n)")
    role: ChatRole = Field(..., description="Viestin lähettäjä: User tai AI")
    text: str = Field(..., description="Viestin sisältö")

class ChatHistoryDTO(BaseModel):
    model_config = ConfigDict(strict=True, extra="ignore")
    conversation: list[ChatMessageDTO] = Field(..., description="Lista keskustelun viesteistä aikajärjestyksessä")
