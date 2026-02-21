
import asyncio
import os
import sys

sys.path.append(os.getcwd())

from backend.database.wrapper import get_db_client
from backend.services.knowledge_base_service import KnowledgeBaseService
from backend.settings import get_settings

os.environ["GEMINI_API_KEY"] = "mock_key_for_test"
os.environ["OPENAI_API_KEY"] = "mock_key_for_test"

async def test_kb_service_init():
    print("Initializing dependencies...")
    settings = get_settings()
    db = get_db_client()

    # Mocking dependencies for manual test without full FastAPI context
    # In a real app, Depends() handles this. Here we manually call them.
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
    await registry.discover_and_register_agents() # critical for resolving strategies

    # Manually resolving the provider using the 'deep' strategy
    # effectively simulating: llm_provider = await get_llm_provider("deep", registry, usage)
    from backend.llm.provider import LLMFactory
    deep_config = await registry.resolve_model_config("deep")
    print(f"Resolved 'deep' strategy config: {deep_config}")

    llm_provider = LLMFactory.create_provider(
        provider_type=deep_config.provider,
        model_name=deep_config.model_name,
        usage_service=usage,
        limits={"tpm": 500000, "rpm": 300}
    )

    print("Creating KnowledgeBaseService...")
    service = KnowledgeBaseService(
        repository=repo,
        storage_client=storage,
        document_service=docs,
        registry=registry,
        usage_service=usage
    )

    print("Service created successfully.")
    print("VERIFIED: Smart Ingestion test reached end successfully.")

if __name__ == "__main__":
    asyncio.run(test_kb_service_init())
