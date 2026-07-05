from unittest.mock import MagicMock, patch

from backend_v2.utils.llm_debug_logger import write_debug_prompt_log


@patch("backend_v2.utils.llm_debug_logger.get_settings")
def test_write_debug_prompt_log_not_dev(mock_get_settings):
    mock_settings = MagicMock()
    mock_settings.environment = "production"
    mock_get_settings.return_value = mock_settings

    write_debug_prompt_log(
        execution_id="123",
        step_id="step_1",
        role_block=None,
        protocol_block=None,
        criteria_blocks=[],
        base_system_prompt="system",
        user_payload="user",
    )
    # The file system logic should not run


@patch("backend_v2.utils.llm_debug_logger.Path")
@patch("backend_v2.utils.llm_debug_logger.open", create=True)
@patch("backend_v2.utils.llm_debug_logger.get_settings")
def test_write_debug_prompt_log_in_dev(mock_get_settings, mock_open, mock_path):
    mock_settings = MagicMock()
    mock_settings.environment = "development"
    mock_get_settings.return_value = mock_settings

    mock_dir = MagicMock()
    mock_dir.exists.return_value = True

    mock_file = MagicMock()
    mock_dir.__truediv__.return_value = mock_file

    # Setup Path chain: Path("data") / "files" / "executions" / execution_id
    mock_path.return_value.__truediv__.return_value.__truediv__.return_value.__truediv__.return_value = mock_dir

    write_debug_prompt_log(
        execution_id="123",
        step_id="step_1",
        role_block=None,
        protocol_block=None,
        criteria_blocks=[],
        base_system_prompt="system",
        user_payload="user",
    )
    mock_open.assert_called_once()
