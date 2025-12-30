import os
import json
import logging
from datetime import datetime
from backend.settings import get_settings
from backend.logging_config import setup_logging
from backend.exceptions import FatalInterruption
from backend.dependencies import (
    get_db_client_dep,
    get_repository_dep,
    get_agent_registry_dep,
    get_prompt_builder_dep,
    get_engine
)

async def bootstrap_application():
    """
    Centralized initialization logic for the backend.
    Handles logging, configuration checks, and Engine warmup.
    """
    # 1. Initialize Logging
    setup_logging(log_level=logging.DEBUG)
    logger = logging.getLogger("backend.bootstrap")
    
    settings = get_settings()
    
    logger.info("="*50)
    logger.info(f"   Cognitive Quorum Backend v0.2.0")
    logger.info(f"   Startup Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*50)
    
    # 2. Log Configuration
    if settings.storage_backend.upper() == "FIRESTORE" and not settings.use_mock_db:
        logger.info(f"   [CONFIG] Database Mode: FIRESTORE (Cloud Defaults)")
    else:
        logger.info(f"   [CONFIG] Database Path: {os.path.abspath(settings.start_db_path)}")
    logger.info(f"   [CONFIG] Model Strategy: Database Controlled")
    
    if settings.use_mock_llm:
        logger.warning("!"*50)
        logger.warning("   [INFO] OPERATING IN MOCK LLM MODE")
        logger.warning("   [INFO] No external API calls will be made.")
        logger.warning("!"*50)
    else:
        logger.info("="*50)
        logger.info("   [INFO] OPERATING IN REAL LLM MODE")
        logger.info("   [INFO] External API calls WILL be made.")
        logger.info("="*50)
    
    # 3. Google Search Check
    search_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    search_cx = os.getenv("GOOGLE_SEARCH_CX")
    if search_key and search_cx:
        logger.info(f"   [CONFIG] Google Search: ENABLED (Key: ...{search_key[-4:]})")
    else:
        logger.info(f"   [CONFIG] Google Search: DISABLED (Missing Key or CX)")
        
    logger.info("="*50)
    
    # 4. Initialize available models cache
    # Note: Using generic provider access if possible
    # from backend.llm.provider import GoogleGeminiProvider
    
    if not settings.use_mock_llm:
        logger.info("   [INFO] Fetching available models from API is deferred to lazy access.")
        # try:
        #     models = GoogleGeminiProvider.fetch_available_models()
        #     logger.info(f"   [INFO] Models Cached: {models}")
        # except Exception as e:
        #     logger.warning(f"   [WARNING] Failed to fetch models on startup (will verify lazily): {e}")
    else:
         logger.info("   [INFO] Using Mock Models list.")
         # Mock provider doesn't have fetch_availble_models, but we can set the cache manually if we access `backend.llm.provider`
         # Or we can just let UI use fallback.
         # Ideally we inject.
         # For now, let's just log. The MockProvider is not GoogleAIProvider.
         pass

    # 5. Warmup Engine Singleton & Dependencies
    try:
        logger.info("   [INFO] Warming up Engine Singleton...")
        
        # Manually resolve dependencies to avoid FastAPI Depends() leakage
        db = get_db_client_dep()
        repo = get_repository_dep(db)
        registry = get_agent_registry_dep(repo)
        pb = get_prompt_builder_dep(repo, registry)
        
        # Initialize Engine
        engine = get_engine(repository=repo, registry=registry, prompt_builder=pb)
        logger.info("   [INFO] Engine Ready.")

        # 6. Recovery: Auto-Resume Interrupted Jobs
        logger.info("   [INFO] Checking for interrupted jobs...")
        await engine.recover_interrupted_jobs()

        return engine
        
    except FatalInterruption as fi:
        logger.critical("!"*60)
        logger.critical(f"   [CRITICAL STARTUP FAILURE] {fi.step_name}")
        logger.critical(f"   Reason: {fi.reason}")
        logger.critical(f"   Details: {json.dumps(fi.details, indent=2)}")
        logger.critical("!"*60)
        raise fi
        
    except Exception as e:
        logger.error(f"   [CRITICAL] Engine Warmup Failed: {e}", exc_info=True)
        raise RuntimeError(f"Startup Failed: {e}")
