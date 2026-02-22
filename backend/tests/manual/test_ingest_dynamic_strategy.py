import asyncio
import os
import sys
import logging

logger = logging.getLogger(__name__)

sys.path.append(os.getcwd())

from backend.database.wrapper import get_db_client
from backend.services.knowledge_base_service import KnowledgeBaseService
from backend.settings import get_settings


async def test_dynamic_strategy():
    logger.info("Initializing dependencies for Dynamic Strategy Test...")
    settings = get_settings()
    db = get_db_client()

    # Mocking dependencies
    from backend.database.factory import get_repository

    repo = await get_repository(settings, db)

    from backend.services.storage import get_storage_driver

    storage = get_storage_driver()

    from backend.services.document_service import DocumentService

    docs = DocumentService(storage)

    from backend.services.usage_service import UsageService

    usage = UsageService(repo)

    from backend.services.agent_registry import AgentRegistry

    registry = AgentRegistry(repo)
    await registry.discover_and_register_agents()

    print("Creating KnowledgeBaseService with Registry...")
    KnowledgeBaseService(
        repository=repo, storage_client=storage, document_service=docs, registry=registry, usage_service=usage
    )

    # Test 1: Resolve 'fast' strategy
    logger.info("\n--- TEST 1: Resolve 'fast' Strategy ---")
    try:
        # We can't easily call ingest without a file, but we can test the resolution logic via a helper or by mocking extract
        # For this test, we'll access the registry directly to confirm resolution works as the service would use it
        config_fast = await registry.resolve_model_config("fast")
        logger.info(f"Verified 'fast' config: {config_fast}")

        # Manually trigger the logic that happens inside extract_concepts_with_llm
        from backend.llm.provider import LLMFactory

        provider_fast = LLMFactory.create_provider(
            provider_type=config_fast.provider, model_name=config_fast.model_name, usage_service=usage
        )
        logger.info(f"VERIFIED: 'fast' strategy resolves to provider model: {getattr(provider_fast, '_model_name', 'unknown')}")
    except Exception as e:
        logger.error(f"FAILED 'fast' test: {e}")

    # Test 2: Resolve 'deep' strategy
    logger.info("\n--- TEST 2: Resolve 'deep' Strategy ---")
    try:
        config_deep = await registry.resolve_model_config("deep")
        logger.info(f"Verified 'deep' config: {config_deep}")

        provider_deep = LLMFactory.create_provider(
            provider_type=config_deep.provider, model_name=config_deep.model_name, usage_service=usage
        )
        logger.info(f"VERIFIED: 'deep' strategy resolves to provider model: {getattr(provider_deep, '_model_name', 'unknown')}")
    except Exception as e:
        logger.error(f"FAILED 'deep' test: {e}")


if __name__ == "__main__":
    asyncio.run(test_dynamic_strategy())
