import logging

from fastapi import APIRouter, status

from backend.exceptions import AppException
from backend.llm.client import LLMClient
from backend.logging_config import log_error
from backend.models.dtos.builder import PlaygroundRequest, PlaygroundResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/playground", tags=["Playground"])

# Note: PlaygroundRequest is imported from dtos.builder


@router.post("/run", response_model=PlaygroundResponse)
async def run_prompt(request: PlaygroundRequest) -> PlaygroundResponse:
    """Executes a prompt template with variables against the LLM."""
    # FAIL FAST: Empty inputs
    if not request.system_instruction and not request.user_message:
        raise AppException(
            message="Both system_instruction and user_message cannot be empty.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": "EMPTY_PROMPT_INPUT"},
        )

    # 1. Inject Variables
    try:
        if request.variables:
            system_content = request.system_instruction.format(**request.variables)
        else:
            system_content = request.system_instruction
    except KeyError as e:
        error_code = "PROMPT_VARIABLE_MISSING"
        logger.warning(f"Playground Variable Error: {e}")
        raise AppException(
            message=f"Missing variable in template: {e}",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": error_code},
        ) from e
    except ValueError as e:
        error_code = "PROMPT_FORMATTING_FAILED"
        logger.error(f"Playground Formatting Error: {e}")
        raise AppException(
            message=f"Prompt formatting failed: {e}",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": error_code},
        ) from e

    # 2. Initialize Client
    client = LLMClient()

    # 3. Construct Messages
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": request.user_message},
    ]

    # 4. Execute
    try:
        response_text = await client.run_chat(messages=messages, **request.model_params)
        # TODO: LLMClient needs update to return usage stats. For now, empty usage.
        return PlaygroundResponse(content=response_text, usage=None)

    except Exception as e:
        error_code = "LLM_EXECUTION_FAILED"
        log_error(logger, e)
        raise AppException(
            message=f"LLM execution failed: {str(e)}",
            status_code=status.HTTP_502_BAD_GATEWAY,  # Upstream error
            details={"error_code": error_code},
        ) from e
