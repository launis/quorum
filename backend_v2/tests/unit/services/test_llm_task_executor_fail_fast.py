from unittest.mock import AsyncMock

import pytest
from pydantic import BaseModel

from backend_v2.exceptions import AppException
from backend_v2.services.llm_task_executor import LLMTaskExecutor


class DummySchema(BaseModel):
    pass


@pytest.mark.asyncio
async def test_llm_executor_fails_fast_on_empty_payload() -> None:
    """Tier 4 Bug Hunting: RED STATE
    Varmistetaan, että LLMTaskExecutor kaatuu välittömästi (Fail-Fast),
    jos sille syötettävä viestiketju ei sisällä lainkaan analysoitavaa lähdetekstiä.
    """
    executor = LLMTaskExecutor(prompt_compiler=AsyncMock())
    mock_client = AsyncMock()

    # Simuloidaan tilanne, jossa ContextBuilder on vahingossa
    # filtteröinyt kaiken tekstin pois (esim. target_blocks takia)
    empty_messages = [
        {"role": "system", "content": "You are an AI auditor. Analyze the following text."},
        {
            "role": "user",
            "content": "<context_data>\n\n</context_data>",
        },  # Tyhjä konteksti!
    ]

    with pytest.raises(AppException) as exc_info:
        await executor.execute_structured_task(
            client=mock_client,
            messages=empty_messages,
            response_model=DummySchema,
        )

    assert exc_info.value.status_code == 400
    assert "payload is empty" in exc_info.value.message.lower()
