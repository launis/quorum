from pydantic import BaseModel, Field
from typing import Literal
class Test(BaseModel):
    x: Literal['N/A', 'doc0', 'a1'] = Field(..., json_schema_extra={'pattern': r'^(N/A|doc\d+|a\d+)$'})

print(Test.model_json_schema())
