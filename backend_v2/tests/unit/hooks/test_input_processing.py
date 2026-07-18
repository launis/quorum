from unittest.mock import patch

import pytest

from backend_v2.hooks.input_processing import _process_chat_history
from backend_v2.models.v2_core import ChatHistoryDTO, ChatMessageDTO


@pytest.mark.asyncio
@patch("backend_v2.hooks.input_processing.ChatParserService.parse_pasted_chat")
async def test_process_chat_history_separates_speakers(mock_parse):
    mock_parse.return_value = ChatHistoryDTO(
        conversation=[
            ChatMessageDTO(role="user", content="Hello AI!"),
            ChatMessageDTO(role="ai", content="Hello User!"),
            ChatMessageDTO(role="user", content="What is 2+2?"),
        ]
    )

    with patch("backend_v2.hooks.input_processing.get_pii_service") as mock_pii:
        result = await _process_chat_history(
            resolved_text="some text",
            key="chat_log",
            system_repo=None,
            enable_semantic_smoothing=False,
            enable_eager_anonymization=False,
            language="en"
        )

    assert result["combined"] == "<user_payload>\nHello AI!\n</user_payload>\n\n<ai_draft_context>\nHello User!\n</ai_draft_context>\n\n<user_payload>\nWhat is 2+2?\n</user_payload>"
    assert result["user_only"] == "Hello AI!\n\nWhat is 2+2?"
    assert result["ai_only"] == "Hello User!"

@pytest.mark.asyncio
async def test_process_chat_history_bypasses_nlp_for_json():
    json_input = '''
    {
        "conversation": [
            {"role": "user", "content": "Hello"}
        ]
    }
    '''
    with patch("backend_v2.hooks.input_processing.ChatParserService.parse_pasted_chat") as mock_parse:
        with patch("backend_v2.hooks.input_processing.get_pii_service") as mock_get_pii:
            result = await _process_chat_history(
                resolved_text=json_input,
                key="chat_log",
                system_repo=None,
                enable_semantic_smoothing=True,
                enable_eager_anonymization=True,
                language="en",
            )
            
            mock_get_pii.assert_not_called()
            mock_parse.assert_not_called()
            
            assert result["combined"] == "<user_payload>\nHello\n</user_payload>"
            assert result["user_only"] == "Hello"


@pytest.mark.asyncio
async def test_process_inputs_missing_context():
    from unittest.mock import MagicMock

    from backend_v2.core.hook_registry import HookState
    from backend_v2.exceptions import AppException
    from backend_v2.hooks.input_processing import process_inputs

    state = HookState(workflow_id="", execution_id="", inputs={}, global_context_vars={}, metadata={})
    deps = MagicMock()

    with pytest.raises(AppException) as exc:
        await process_inputs(state, deps)

    assert exc.value.details["error_code"] == "MISSING_EXECUTION_CONTEXT"


@pytest.mark.asyncio
async def test_process_inputs_missing_language():
    from unittest.mock import AsyncMock, MagicMock

    from backend_v2.core.hook_registry import HookState
    from backend_v2.exceptions import AppException
    from backend_v2.hooks.input_processing import process_inputs

    state = HookState(workflow_id="w1", execution_id="e1", inputs={}, global_context_vars={}, metadata={})

    mock_workflow_repo = MagicMock()
    mock_workflow_repo.get_workflow_by_id = AsyncMock(
        return_value={
            "id": "wor_1234567890123456",
            "slug": "test_workflow",
            "name": "Test Workflow",
            "description": "desc",
            "status": "draft",
            "version": 1,
            "default_profile_id": "out_1234567890123456",
            "expected_inputs": [],
        }
    )

    deps = MagicMock()
    deps.workflow_repo = mock_workflow_repo

    with pytest.raises(AppException) as exc:
        await process_inputs(state, deps)

    assert exc.value.details["error_code"] == "CONFIGURATION_ERROR"
