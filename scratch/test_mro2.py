from pydantic import BaseModel, Field

class BaseA(BaseModel):
    field_a: str = Field(...)

class BaseB(BaseModel):
    field_b: str = Field(...)

class Merged(BaseB, BaseA):
    pass

print(list(Merged.model_fields.keys()))
