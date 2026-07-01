from pydantic import BaseModel, Field, ConfigDict
from backend_v2.llm.ingress_pipeline import UniversalIngress

class MyModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    real_name: str = Field(..., alias="eval_1")
    other: str

raw_llm_output = {
    "eval_1": "Hello",
    "other": "World"
}

cleaned = UniversalIngress.clean_dict_against_model(raw_llm_output, MyModel)
print("Cleaned:", cleaned)
try:
    MyModel.model_validate(cleaned)
    print("Success")
except Exception as e:
    print("Error:", e)
