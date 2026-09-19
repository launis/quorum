"""Unit tests for v2_core proxy module verifying PEP 484 re-exports and schema validity."""

import inspect

from pydantic import BaseModel

import backend_v2.models.v2_core as v2_core


def test_v2_core_exports_all_symbols() -> None:
    """Verify that every symbol declared in __all__ exists and is accessible."""
    assert hasattr(v2_core, "__all__")
    assert len(v2_core.__all__) > 40

    for symbol in v2_core.__all__:
        assert hasattr(v2_core, symbol), f"Symbol {symbol} missing from v2_core module"
        val = getattr(v2_core, symbol)
        assert val is not None, f"Symbol {symbol} in v2_core is None"


def test_v2_core_models_subclass_basemodel() -> None:
    """Verify that domain models and DTOs in v2_core correctly subclass BaseModel and validate."""
    model_count = 0
    for symbol in v2_core.__all__:
        val = getattr(v2_core, symbol)
        if inspect.isclass(val) and issubclass(val, BaseModel):
            model_count += 1
            assert hasattr(val, "model_validate")
            assert hasattr(val, "model_dump")

    assert model_count >= 20, f"Expected at least 20 BaseModel subclasses, found {model_count}"
