from pydantic import BaseModel, Field, model_validator, ConfigDict

class BaseA(BaseModel):
    field_a: str = Field(...)
    
    @model_validator(mode="after")
    def val_a(self):
        if self.field_a == "invalid":
            raise ValueError("bad a")
        return self

class BaseB(BaseModel):
    field_b: str = Field(...)

class Merged(BaseA, BaseB):
    pass

print("Merged(BaseA, BaseB):", list(Merged.model_fields.keys()))

class Merged2(BaseB, BaseA):
    pass

print("Merged2(BaseB, BaseA):", list(Merged2.model_fields.keys()))

# test instantiation and validation
m = Merged2(field_b="b", field_a="a")
print(m)
try:
    Merged2(field_b="b", field_a="invalid")
except ValueError as e:
    print("Caught validation error:", e)
