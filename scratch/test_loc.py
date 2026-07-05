import json
from typing import Annotated, Literal
from pydantic import BaseModel, Field, ConfigDict, ValidationError

class BulletListItem(BaseModel):
    text: str

class BulletListBlock(BaseModel):
    model_config = ConfigDict(title="bullet_list")
    block_type: Literal["bullet_list"] = "bullet_list"
    items: list[BulletListItem]

class ParagraphBlock(BaseModel):
    model_config = ConfigDict(title="paragraph")
    block_type: Literal["paragraph"] = "paragraph"
    text: str

AnyBlock = Annotated[ParagraphBlock | BulletListBlock, Field(discriminator="block_type")]

class Container(BaseModel):
    blocks: list[AnyBlock]

# Test 1: Proper discriminator, but wrong items
try:
    c = Container.model_validate({"blocks": [{"block_type": "bullet_list", "items": ["string"]}]})
except ValidationError as e:
    print("Test 1 (Correct structure, wrong items):")
    print(e.json())

# Test 2: Wrapped object (LiteLLM bug?)
try:
    c = Container.model_validate({"blocks": [{"bullet_list": {"items": ["string"]}}]})
except ValidationError as e:
    print("\nTest 2 (Wrapped object):")
    print(e.json())
