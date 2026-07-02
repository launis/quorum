import importlib

import pytest
from pydantic import BaseModel, Field

import backend_v2.utils.pydantic_utils

importlib.reload(backend_v2.utils.pydantic_utils)
from backend_v2.exceptions import AppException
from backend_v2.utils.pydantic_utils import inflate


class MockModel(BaseModel):
    name: str
    age: int = Field(ge=0)


def test_inflate_none() -> None:
    assert inflate(None, MockModel) is None


def test_inflate_dict() -> None:
    data = {"name": "Test", "age": 25}
    model = inflate(data, MockModel)
    assert model is not None
    assert model.name == "Test"


def test_inflate_invalid_dict() -> None:
    data = {"name": "Test", "age": -5}
    with pytest.raises(AppException):
        inflate(data, MockModel)


def test_inflate_model_instance() -> None:
    model = MockModel(name="Test", age=25)
    assert inflate(model, MockModel) is model


def test_inflate_unrecognized() -> None:
    with pytest.raises(AppException):
        inflate("not a dict or model", MockModel)
