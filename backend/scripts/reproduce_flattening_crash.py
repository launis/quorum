
import asyncio
import logging
import os
import sys

# Ensure backend is in path
sys.path.append(os.getcwd())

from pydantic import ValidationError

from backend.agents.critics import PerformativityDetectorAgent
from backend.llm.provider import LLMResponse, MockProvider

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FlatteningMockProvider(MockProvider):
    """Mocks a flattened response that violates the nested schema."""
    async def generate(self, *args, **kwargs):
        # FLATTENED JSON (Missing 'performativity_analysis' wrapper)
        flattened_content = """
        {
            "reasoning_trace": "Simulated reasoning...",
            "performativity_heuristics": "Analysis here...",
            "pre_mortem_analysis": "Prediction here...",
            "authenticity_assessment": "Assessment here...",
            "metadata": {}
        }
        """

        # In the REAL provider, Instructor would try to parse this against PerformativityOutput
        # and RAISE ValidationError because 'performativity_analysis' is missing.
        # We simulate that behavior here if response_schema is passed.

        response_schema = kwargs.get("response_schema")
        if response_schema:
            try:
                # Simulate Instructor Validation
                response_schema.model_validate_json(flattened_content)
            except ValidationError as e:
                logger.info("MockProvider: Simulating Instructor Validation Failure...")
                raise e # This matches current LiteLLMProvider behavior

        return LLMResponse(
            content=flattened_content,
            parsed_content=None,
            token_usage={},
            provider_metadata={},
            tool_calls=[],
            messages=[]
        )

async def main():
    logger.info("--- Reproducing Flattened JSON Crash ---")

    agent = PerformativityDetectorAgent()

    # Inject our malicious mock provider
    agent.llm_provider = FlatteningMockProvider(model_name="mock-flattening")

    try:
        # Execute should fail with AgentExecutionError wrapping ValidationError
        # UNLESS our fix works (which logic says it won't yet)
        result = await agent.execute(input_data={"test": "data"})
        print("SUCCESS! Result:", result)
        # If we get here with current code, my analysis is wrong.

    except Exception as e:
        logger.error(f"Caught Expected Error: {type(e).__name__}: {e}")
        # Identify if it's the schema validation error
        if "Field required" in str(e) or "validation error" in str(e).lower():
            logger.info("CONFIRMED: Provider blocked execution before Healing could run.")
        else:
            logger.info("Different error occurred.")

if __name__ == "__main__":
    asyncio.run(main())
