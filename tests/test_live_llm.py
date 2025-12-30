import pytest
import os
import logging
import json
import unittest
from typing import Type
from pydantic import BaseModel
from backend.llm.provider import LLMFactory
from backend.models import domain

# Config
logger = logging.getLogger(__name__)

# Helper to check API Key presence
def has_google_key():
    return bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.path.exists("service-account.json"))

@pytest.mark.live
@pytest.mark.skipif(not has_google_key(), reason="GOOGLE_API_KEY or service-account.json not found")
class TestLiveLLM(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        # Ensure env var is set if file exists, for Google Auth library
        if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS") and os.path.exists("service-account.json"):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath("service-account.json")

    async def test_live_gemini_connectivity(self):
        """
        LIVE INTEGRATION TEST: Basic Connectivity
        """
        logger.info("Running LIVE Gemini Connectivity Test...")
        model_name = "gemini-1.5-flash"
        
        try:
            provider = LLMFactory.create_provider("gemini", model_name)
            response = await provider.generate(
                prompt="Reply with exactly one word: Hello",
                temperature=0.0,
                max_tokens=10
            )
            self.assertIsNotNone(response.content)
            # Log response for debugging if assert fails
            if "Hello" not in response.content and "hello" not in response.content:
                print(f"DEBUG GEMINI RESPONSE: '{response.content}'")
                logger.error(f"Gemini replied unexpectedly: '{response.content}'")
            
            # Allow case-insensitive or partial match
            content_lower = response.content.lower()
            self.assertTrue("hello" in content_lower or "hi" in content_lower)
        except Exception as e:
            pytest.fail(f"Live API Call to Gemini Failed: {str(e)}")

    async def test_live_critical_schemas_validity(self):
        """
        LIVE TEST: Schema Validation
        
        Iterates through critical domain models (XAIReport, TuomioJaPisteet, etc.)
        and requests a mock generation from Gemini.
        
        This detects 'BadRequestError' caused by invalid JSON Schemas 
        (e.g., empty properties for OBJECT type, recursive definitions).
        """
        logger.info("Running LIVE Schema Validation...")
        
        # List of schemas that MUST work with Gemini
        schemas: list[Type[BaseModel]] = [
            domain.TaintedData,
            domain.TodistusKartta,
            domain.ArgumentaatioAnalyysi,
            domain.LogiikkaAuditointi,
            domain.EtiikkaJaFakta,
            domain.KausaalinenAuditointi,
            domain.PerformatiivisuusAuditointi,
            domain.TuomioJaPisteet,
            domain.CoachingPlan,
            domain.XAIReport, 
            domain.InteractionAnalysis,
            domain.ProfilerAnalysis
        ]
        
        model_name = "gemini-1.5-flash" # Use flash for speed
        provider = LLMFactory.create_provider("gemini", model_name)
        
        for schema_cls in schemas:
            schema_name = schema_cls.__name__
            logger.info(f"Validating schema: {schema_name}")
            
            try:
                # We ask for a minimal valid instance
                await provider.generate(
                    prompt=f"Generate a valid JSON object for the schema provided. Fill with dummy data.",
                    response_schema=schema_cls,
                    temperature=0.0,
                    max_tokens=1024
                )
                print(f"✅ Schema {schema_name} passed.")
                
            except Exception as e:
                # Log full error for debugging
                logger.error(f"❌ Schema {schema_name} FAILED: {e}")
                pytest.fail(f"Schema {schema_name} represents an invalid structure for Gemini: {e}")
