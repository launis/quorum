from typing import Type
from pydantic import BaseModel
from src.models.interfaces import (
    BaseJSON, TaintedData, TodistusKartta, ArgumentaatioAnalyysi,
    LogiikkaAuditointi, KausaalinenAuditointi, PerformatiivisuusAuditointi,
    EtiikkaJaFakta, TuomioJaPisteet, XAIReport
)
from pydantic import BaseModel

# Define RawInput locally or import if added to interfaces
class RawInput(BaseModel):
    history_text: str
    product_text: str
    reflection_text: str

class SchemaRegistry:
    _registry = {
        "RawInput": RawInput,
        "TaintedData": TaintedData,
        "TodistusKartta": TodistusKartta,
        "ArgumentaatioAnalyysi": ArgumentaatioAnalyysi,
        "LogiikkaAuditointi": LogiikkaAuditointi,
        "KausaalinenAuditointi": KausaalinenAuditointi,
        "PerformatiivisuusAuditointi": PerformatiivisuusAuditointi,
        "EtiikkaJaFakta": EtiikkaJaFakta,
        "TuomioJaPisteet": TuomioJaPisteet,
        "XAIReport": XAIReport
    }

    @classmethod
    def get_schema(cls, schema_name: str) -> Type[BaseModel]:
        schema = cls._registry.get(schema_name)
        if not schema:
            raise ValueError(f"Schema '{schema_name}' not found in registry.")
        return schema
