import asyncio
from unittest.mock import MagicMock, patch

import pytest

from backend_v2.utils.llm_debug_logger import write_debug_prompt_log, write_llm_telemetry_log


@pytest.mark.asyncio
@patch("backend_v2.utils.llm_debug_logger.get_settings")
async def test_write_debug_prompt_log_not_dev(mock_get_settings: MagicMock) -> None:
    mock_settings = MagicMock()
    mock_settings.environment = "production"
    mock_get_settings.return_value = mock_settings

    await write_debug_prompt_log(
        execution_id="123",
        step_id="step_1",
        role_block=None,
        protocol_block=None,
        criteria_blocks=[],
        base_system_prompt="system",
        user_payload="user",
    )
    # The file system logic should not run


@pytest.mark.asyncio
@patch("backend_v2.utils.llm_debug_logger.Path")
@patch("backend_v2.utils.llm_debug_logger.open", create=True)
@patch("backend_v2.utils.llm_debug_logger.get_settings")
async def test_write_debug_prompt_log_in_dev(
    mock_get_settings: MagicMock, mock_open: MagicMock, mock_path: MagicMock
) -> None:
    mock_settings = MagicMock()
    mock_settings.environment = "development"
    mock_get_settings.return_value = mock_settings

    mock_dir = MagicMock()
    mock_dir.exists.return_value = True

    mock_file = MagicMock()
    mock_dir.__truediv__.return_value = mock_file

    # Setup Path chain: Path("data") / "files" / "executions" / execution_id
    mock_path.return_value.__truediv__.return_value.__truediv__.return_value.__truediv__.return_value = mock_dir

    mock_role = MagicMock(id="blk_role", category_id="persona")
    mock_proto = MagicMock(id="blk_proto", category_id="protocol")
    mock_crit = MagicMock(id="blk_crit", category_id="matrix")

    await write_debug_prompt_log(
        execution_id="123",
        step_id="step_1",
        role_block=mock_role,
        protocol_block=mock_proto,
        criteria_blocks=[mock_crit],
        base_system_prompt="system",
        user_payload="user",
        task_blueprint="bp_test",
        expected_schema_name="TestSchema",
    )
    mock_open.assert_called_once()


@pytest.mark.asyncio
@patch("backend_v2.utils.llm_debug_logger.Path")
@patch("backend_v2.utils.llm_debug_logger.open", create=True)
@patch("backend_v2.utils.llm_debug_logger.get_settings")
async def test_write_debug_prompt_log_concurrent_under_lock(
    mock_get_settings: MagicMock, mock_open: MagicMock, mock_path: MagicMock
) -> None:
    mock_settings = MagicMock()
    mock_settings.environment = "development"
    mock_get_settings.return_value = mock_settings

    mock_dir = MagicMock()
    mock_file = MagicMock()
    mock_dir.__truediv__.return_value = mock_file
    mock_path.return_value.__truediv__.return_value.__truediv__.return_value.__truediv__.return_value = mock_dir

    async with asyncio.TaskGroup() as tg:
        for i in range(10):
            tg.create_task(
                write_debug_prompt_log(
                    execution_id=f"exec_{i}",
                    step_id=f"step_{i}",
                    role_block=None,
                    protocol_block=None,
                    criteria_blocks=[],
                    base_system_prompt="system",
                    user_payload="user",
                )
            )

    assert mock_open.call_count == 10


@pytest.mark.asyncio
@patch("backend_v2.utils.llm_debug_logger.get_settings")
async def test_write_llm_telemetry_log_not_dev(mock_get_settings: MagicMock) -> None:
    mock_settings = MagicMock()
    mock_settings.environment = "production"
    mock_get_settings.return_value = mock_settings

    await write_llm_telemetry_log(
        execution_id="exec_123",
        step_id="step_1",
        duration_ms=150,
        cache_hit=True,
        tokens=42,
        trigger_reason="initial",
    )


@pytest.mark.asyncio
@patch("backend_v2.utils.llm_debug_logger.Path")
@patch("backend_v2.utils.llm_debug_logger.open", create=True)
@patch("backend_v2.utils.llm_debug_logger.get_settings")
async def test_write_llm_telemetry_log_in_dev(
    mock_get_settings: MagicMock, mock_open: MagicMock, mock_path: MagicMock
) -> None:
    mock_settings = MagicMock()
    mock_settings.environment = "development"
    mock_get_settings.return_value = mock_settings

    mock_dir = MagicMock()
    mock_dir.exists.return_value = True

    mock_file = MagicMock()
    mock_dir.__truediv__.return_value = mock_file

    mock_path.return_value.__truediv__.return_value.__truediv__.return_value.__truediv__.return_value = mock_dir

    await write_llm_telemetry_log(
        execution_id="exec_123",
        step_id="step_1",
        duration_ms=150,
        cache_hit=False,
        tokens=100,
        trigger_reason="retry",
    )
    mock_open.assert_called_once()


