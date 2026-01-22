import asyncio
import logging
from backend.database.factory import get_repository
from backend.settings import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_repo")

async def verify_repo():
    settings = get_settings()
    logger.info(f"Settings DB Path: {settings.prod_db_path}")
    
    # 1. Initialize Repository (Same logic as Factory)
    repo = None
    try:
        from backend.database.wrapper import TinyDBClient
        from backend.database.repository import TinyDBRepository
        
        client = TinyDBClient(settings.prod_db_path)
        repo = TinyDBRepository(client)
        logger.info("Repository initialized manually.")
    except Exception as e:
        logger.error(f"Failed to init repo manually: {e}")
        return

    # 2. Call get_model_registry
    logger.info("Calling get_model_registry()...")
    try:
        registry = await repo.get_model_registry()
        logger.info(f"Result: {registry}")
        
        if "models" in registry:
            models = registry["models"]
            # Flexible check: check any provider (google, vertex_ai, etc)
            found = False
            for provider, strategies in models.items():
                if "GuardAgent" in strategies:
                    logger.info(f"SUCCESS: GuardAgent found in provider '{provider}' with value: {strategies['GuardAgent']}")
                    found = True
                    break
            
            if not found:
                 logger.error(f"FAILURE: GuardAgent not found in any provider. Providers: {list(models.keys())}")
        else:
            logger.error("FAILURE: 'models' key missing from registry.")

    except Exception as e:
        logger.error(f"Exception during get_model_registry: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_repo())
