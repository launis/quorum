import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import json
from pydantic import BaseModel, Field
from tenacity import RetryError
import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set low retry delay for tests to run fast
os.environ["LLM_RETRY_DELAY"] = "0.01" 
os.environ["LLM_MAX_RETRIES"] = "2"
os.environ["GOOGLE_API_KEY"] = "fake_key"
os.environ["OPENAI_API_KEY"] = "fake_key"

from backend.llm_provider import GoogleGeminiProvider, OpenAIProvider

class TestSchema(BaseModel):
    field: str
    score: int = Field(ge=1, le=10) # Includes minimum/maximum checks
    
    class Config:
        json_schema_extra = {
            "examples": [{"field": "example_value"}]
        }

class TestLLMResilience(unittest.IsolatedAsyncioTestCase):

    @patch("google.generativeai.GenerativeModel")
    @patch("google.generativeai.configure")
    async def test_gemini_structured_output_config(self, mock_configure, mock_model_cls):
        """Verify Gemini provider sets strict JSON mode and cleans schema."""
        mock_instance = mock_model_cls.return_value
        mock_response = MagicMock()
        mock_response.parts = [MagicMock()]
        mock_response.text = '{"field": "value"}'
        
        # CHANGED: generate_content_async and awaitable return
        mock_instance.generate_content_async = AsyncMock(return_value=mock_response)

        provider = GoogleGeminiProvider()
        result = await provider.generate("prompt", response_schema=TestSchema)

        # Check that generation_config had the schema and mime_type
        call_kwargs = mock_model_cls.call_args[1]
        gen_config = call_kwargs['generation_config']
        
        self.assertEqual(gen_config['response_mime_type'], 'application/json')
        
        # Verify schema was cleaned (should be a dict, not class)
        self.assertIsInstance(gen_config['response_schema'], dict)
        self.assertNotIn('examples', gen_config['response_schema']) 
        self.assertIn('properties', gen_config['response_schema'])
        
        # Verify min/max removal
        props = gen_config['response_schema']['properties']
        self.assertNotIn('maximum', props.get('score', {}))
        self.assertNotIn('minimum', props.get('score', {}))

    @patch("google.generativeai.GenerativeModel")
    @patch("google.generativeai.configure")
    async def test_gemini_retry(self, mock_configure, mock_model_cls):
        """Verify Gemini provider retries on exception."""
        mock_instance = mock_model_cls.return_value
        
        # CHANGED: generate_content_async
        mock_instance.generate_content_async = AsyncMock(side_effect=[Exception("Transient Error"), MagicMock(parts=[MagicMock()], text="success")])

        provider = GoogleGeminiProvider()
        result = await provider.generate("prompt")

        self.assertEqual(result, "success")
        self.assertEqual(mock_instance.generate_content_async.call_count, 2)

    @patch("openai.AsyncOpenAI")
    async def test_openai_structured_output_config(self, mock_client_cls):
        """Verify OpenAI provider uses parse method when schema is provided."""
        mock_client = mock_client_cls.return_value
        mock_parsed = MagicMock()
        mock_parsed.model_dump.return_value = {"field": "value"}
        
        # CHANGED: async parse
        mock_client.beta.chat.completions.parse = AsyncMock()
        mock_client.beta.chat.completions.parse.return_value.choices[0].message.parsed = mock_parsed

        provider = OpenAIProvider()
        result = await provider.generate("prompt", response_schema=TestSchema)

        mock_client.beta.chat.completions.parse.assert_called_once()
        self.assertEqual(result['field'], 'value')

    @patch("openai.AsyncOpenAI")
    async def test_openai_retry(self, mock_client_cls):
        """Verify OpenAI provider retries on exception."""
        mock_client = mock_client_cls.return_value
        
        # CHANGED: async create side effect
        mock_client.chat.completions.create = AsyncMock(side_effect=[Exception("API Timeout"), MagicMock(choices=[MagicMock(message=MagicMock(content="success"))])])

        provider = OpenAIProvider()
        result = await provider.generate("prompt")

        self.assertEqual(result, "success")
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR) # Suppress expected logs
    unittest.main()
