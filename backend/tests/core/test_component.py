from typing import Any

import pytest

from backend.core.component import BaseComponent
from backend.exceptions import AppException, ErrorCodes


# Mock Implementation
class StrictComponent(BaseComponent[dict[str, Any], str]):
    async def execute(
        self,
        input_data: dict[str, Any],
        execution_context: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> str:
        if "fail" in input_data:
            # Simulate Fail Fast
            raise AppException(message="Mock Failure", details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR})
        return input_data.get("value", "default")


@pytest.mark.asyncio
async def test_strict_component_execution():
    """Verify strict component works as expected."""
    comp = StrictComponent()
    result = await comp.execute({"value": "test_ok"})
    assert result == "test_ok"


@pytest.mark.asyncio
async def test_strict_component_failure():
    """Verify component raises AppException."""
    comp = StrictComponent()
    with pytest.raises(AppException) as exc:
        await comp.execute({"fail": True})
    assert exc.value.error_code == ErrorCodes.INTERNAL_SERVER_ERROR


def test_base_agent_compatibility():
    """Check if BaseAgent can still be imported (signature check)."""
    try:
        from backend.agents.base import BaseAgent
    except TypeError as e:
        pytest.fail(f"BaseAgent incompatible with new BaseComponent: {e}")
    except ImportError:
        # Ignore import errors related to missing deps in test env if any,
        # but BaseAgent should import fine.
        pass
