from typing import cast
from unittest.mock import AsyncMock

import pytest

from backend_v2.api.routers.studio.prompt_blocks import get_prompt_blocks
from backend_v2.models.auth import TokenData, UserRole


@pytest.fixture
def mock_current_user() -> TokenData:
    return TokenData(id="usr_123", role=UserRole.ADMIN)


@pytest.fixture
def mock_studio_service() -> AsyncMock:
    return AsyncMock()


@pytest.mark.asyncio
async def test_get_prompt_blocks(mock_current_user: TokenData, mock_studio_service: AsyncMock) -> None:
    mock_studio_service.list_prompt_blocks.return_value = []
    res = await get_prompt_blocks(current_user=mock_current_user, studio_service=mock_studio_service)
    assert res == []


@pytest.mark.asyncio
async def test_studio_service_crashes_on_legacy_execution_persona() -> None:
    from typing import Any

    from backend_v2.services.studio import StudioService

    class MockDB:
        async def get_all_prompt_blocks(self) -> list[dict[str, Any]]:
            return [
                {
                    "id": "blk_1234567890abcdef",
                    "category_id": "matrix",
                    "type": "instruction",
                    "execution_persona": "DETERMINISTIC_PARSER",
                }
            ]

    service = StudioService(
        workflow_repo=cast(Any, None),
        component_repo=cast(Any, None),
        prompt_block_repo=cast(Any, MockDB()),
        output_profile_repo=cast(Any, None),
        knowledge_repo=cast(Any, None),
        system_repo=cast(Any, None),
    )
    user = TokenData(id="usr_123", role=UserRole.ADMIN)

    # This should now throw AppException (STATE_INTEGRITY_ERROR) due to our Fail-Fast fix
    from backend_v2.exceptions import AppException

    with pytest.raises(AppException) as exc_info:
        await service.list_prompt_blocks(user)

    assert exc_info.value.details.get("error_code") == "STATE_INTEGRITY_ERROR"
