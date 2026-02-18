import asyncio
import logging
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Adjust path to find backend
sys.path.append(".")

from backend.agents.guard import GuardAgent
from backend.agents.retrieval import RetrievalAgent
from backend.exceptions import AgentExecutionError, ErrorCodes, AppException
from backend.models.domain import GuardOutput, SecurityCheck, TaintedDataContent, ContextData, Metadata
from backend.models.enums import RiskLevel, SimulationType

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestVerifier")

class TestRefactorV2(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        # Patch LLMFactory to prevent real provider creation
        self.patcher = patch("backend.llm.provider.LLMFactory.create_provider")
        self.mock_create_provider = self.patcher.start()
        self.mock_create_provider.return_value = MagicMock()
        
    def tearDown(self):
        self.patcher.stop()

    async def test_guard_fail_fast_no_org_id(self):
        """Test that GuardAgent fails fast if organization_id is missing."""
        logger.info("TEST 1: GuardAgent Fail Fast (Missing Org ID)")
        agent = GuardAgent(model="mock-model", provider="openai")
        
        inputs = {
            "history_text": "history",
            "product_text": "product",
            "reflection_text": "reflection"
            # Missing organization_id
        }

        with self.assertRaises(AgentExecutionError) as cm:
            await agent.execute(inputs, system_instruction="dummy")
        
        self.assertEqual(cm.exception.details.get("error_code"), ErrorCodes.EMPTY_INPUT)
        logger.info("PASS: GuardAgent failed with EMPTY_INPUT as expected.")

    async def test_guard_metadata_enrichment(self):
        """Test that GuardAgent enriches metadata with org_id and workflow."""
        logger.info("TEST 2: GuardAgent Metadata Enrichment")
        
        # Mock LLM Provider to return valid GuardOutput
        mock_provider = MagicMock()
        mock_response = MagicMock()
        
        # Mock Response Content
        guard_output = GuardOutput(
            security_check=SecurityCheck(
                threat_detected=False,
                risk_level=RiskLevel.LOW,
                risk_score=1.0,
                simulation_score=1.0,
                anonymized=False
            ),
            tainted_data=TaintedDataContent(
                 chat_history="h", product_text="p", reflection_text="r", safe_data="s"
            ),
            thought_process="thinking",
            conclusion="ok",
            confidence_score=1.0
        )
        mock_response.content = guard_output.model_dump_json()
        mock_response.parsed_content = None
        mock_response.metrics = {}
        mock_response.token_usage = {}
        mock_provider.generate = AsyncMock(return_value=mock_response)

        agent = GuardAgent(model="mock-model", provider="openai")
        agent.llm_provider = mock_provider
        
        # Inputs with context
        inputs = {
            "history_text": "history",
            "product_text": "product",
            "reflection_text": "reflection",
            "organization_id": "org-123"
        }
        
        # Execution Context
        context = {
            "organization_id": "org-123",
            "workflow_name": "test-workflow"
        }
        
        try:
            # Execute
            result = await agent.execute(inputs, execution_context=context, system_instruction="dummy")
        except Exception as e:
            logger.error(f"Test 2 Failed with: {e}")
            if hasattr(e, "details"):
                logger.error(f"Details: {e.details}")
            raise e
        
        # Verify Metadata
        self.assertIsInstance(result, GuardOutput)
        self.assertIsNotNone(result.metadata)
        self.assertEqual(result.metadata.organization_id, "org-123")
        self.assertEqual(result.metadata.workflow, "test-workflow")
        self.assertEqual(result.metadata.agentti, "GuardAgent")
        
        logger.info("PASS: GuardAgent enriched metadata correctly.")

    @patch("backend.agents.retrieval.get_repository")
    @patch("backend.agents.retrieval.get_settings")
    @patch("backend.agents.retrieval.get_db_client")
    async def test_retrieval_success_no_dummy_meta(self, mock_db_client, mock_settings, mock_get_repo):
        """Test RetrievalAgent runs without dummy metadata and warns on missing org_id."""
        logger.info("TEST 3: RetrievalAgent Success (No Dummy Meta)")
        
        # Mock Settings
        settings = MagicMock()
        settings.max_precedent_scan_depth = 5
        settings.max_precedent_return_count = 3
        mock_settings.return_value = settings
        
        # Mock Repo
        repo = AsyncMock()
        repo.get_all_executions.return_value = [] # Return empty list for simplicity
        mock_get_repo.return_value = repo

        agent = RetrievalAgent(model="mock-model", provider="openai")
        
        inputs = {
            "organization_id": "org-123"
        }
        
        # Execute
        # Should raise KNOWLEDGE_NOT_INGESTED because repo returns empty (Fail Fast in Retrieval)
        # But we want to verify it doesn't crash on Metadata or ContextData creation BEFORE that.
        # Actually validation happens at end.
        
        try:
            await agent.execute(inputs, system_instruction="dummy")
        except AgentExecutionError as e:
            # We expect KNOWLEDGE_NOT_INGESTED (if strict) or it returns empty?
            # Code says: if not selected_precedents and not kb_items: raise KNOWLEDGE_NOT_INGESTED
            if e.details.get("error_code") == ErrorCodes.KNOWLEDGE_NOT_INGESTED:
                logger.info("PASS: RetrievalAgent reached completion check (KNOWLEDGE_NOT_INGESTED).")
            else:
                logger.error(f"FAIL: RetrievalAgent failed with unexpected error: {e}")
                raise e
        except Exception as e:
             logger.error(f"FAIL: Unexpected exception: {e}")
             raise e

    @patch("backend.agents.retrieval.get_repository")
    @patch("backend.agents.retrieval.get_settings")
    @patch("backend.agents.retrieval.get_db_client")
    async def test_retrieval_missing_org_id_warning(self, mock_db_client, mock_settings, mock_get_repo):
        """Test RetrievalAgent warns but proceeds if org_id is missing (Guard responsibility)."""
        logger.info("TEST 4: RetrievalAgent Missing inputs (Warning Only)")
        
        # Mock Settings
        settings = MagicMock()
        settings.max_precedent_scan_depth = 5
        settings.max_precedent_return_count = 3
        mock_settings.return_value = settings
        
        repo = AsyncMock()
        repo.get_all_executions.return_value = []
        mock_get_repo.return_value = repo

        agent = RetrievalAgent(model="mock-model", provider="openai")
        
        inputs = {} # Missing org_id
        
        # Should NOT raise EMPTY_INPUT (as validation was removed)
        # Should fail later at KNOWLEDGE_NOT_INGESTED or similar
        try:
            await agent.execute(inputs, system_instruction="dummy")
        except AgentExecutionError as e:
            if e.details.get("error_code") == ErrorCodes.KNOWLEDGE_NOT_INGESTED:
                 logger.info("PASS: RetrievalAgent proceeded past input check.")
            else:
                 raise e

if __name__ == "__main__":
    unittest.main(verbosity=2)
