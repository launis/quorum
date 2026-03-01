"""Bootstrap logic for the backend application."""

import json
import logging
import os
from datetime import datetime

from backend.dependencies import (
    get_agent_registry_dep,
    get_async_repository,
    get_db_client_dep,
    get_document_service_dep,
    get_engine,
    get_prompt_builder_dep,
    get_storage_service_dep,
)
from backend.exceptions import AppException, ErrorCodes, FatalInterruption
from backend.logging_config import setup_logging
from backend.settings import get_settings


async def bootstrap_application():
    """Centralized initialization logic for the backend.

    Handles logging, configuration checks, and Engine warmup.
    """
    # 1. Initialize Logging
    setup_logging(log_level=logging.DEBUG)
    logger = logging.getLogger("backend.bootstrap")

    settings = get_settings()

    logger.info("=" * 50)
    logger.info("   Cognitive Quorum Backend v0.2.0")
    logger.info(f"   Startup Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 50)

    # 2. Log Configuration
    # Safe check using computed property
    if settings.active_backend == "FIRESTORE" and not settings.use_mock_db:
        logger.info("   [CONFIG] Database Mode: FIRESTORE (Cloud Defaults)")
    else:
        logger.info(f"   [CONFIG] Database Path: {os.path.abspath(settings.start_db_path)}")
    logger.info("   [CONFIG] Model Strategy: Database Controlled")

    if settings.use_mock_llm:
        logger.warning("!" * 50)
        logger.warning("   [INFO] OPERATING IN MOCK LLM MODE")
        logger.warning("   [INFO] No external API calls will be made.")
        logger.warning("!" * 50)
    else:
        logger.info("=" * 50)
        logger.info("   [INFO] OPERATING IN REAL LLM MODE")
        logger.info("   [INFO] External API calls WILL be made.")
        logger.info("=" * 50)

    # 3. Google Search Check
    search_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    search_cx = os.getenv("GOOGLE_SEARCH_CX")
    if search_key and search_cx:
        logger.info(f"   [CONFIG] Google Search: ENABLED (Key: ...{search_key[-4:]})")
    else:
        logger.info("   [CONFIG] Google Search: DISABLED (Missing Key or CX)")

    logger.info("=" * 50)

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

    # 5. Warmup Engine Singleton & Dependencies
    try:
        logger.info("   [INFO] Warming up Engine Singleton...")

        # Manually resolve dependencies to avoid FastAPI Depends() leakage
        get_db_client_dep()

        # In Async-First, we get the repo directly via factory
        repo = await get_async_repository()

        # Registry and PromptBuilder use the repo
        registry = await get_agent_registry_dep(repo)
        pb = await get_prompt_builder_dep(repo, registry)

        storage_service = get_storage_service_dep()
        document_service = get_document_service_dep(storage_service)

        # Initialize Engine
        engine = await get_engine()
        logger.info("   [INFO] Engine Ready.")

        # 6. Recovery: Auto-Resume Interrupted Jobs
        logger.info("   [INFO] Checking for interrupted jobs... (DEPRECATED: Engine redesign handles state externally)")
        # await engine.recover_interrupted_jobs()

        return engine

    except FatalInterruption as fi:
        logger.critical("!" * 60)
        logger.critical(f"   [CRITICAL STARTUP FAILURE] {fi.step_name}")
        logger.critical(f"   Reason: {fi.reason}")
        logger.critical(f"   Details: {json.dumps(fi.details, indent=2)}")
        logger.critical("!" * 60)
        raise fi

    except Exception as e:
        logger.error(f"   [CRITICAL] Engine Warmup Failed: {e}", exc_info=True)
        raise AppException(
            message=f"Startup Failed: {e}",
            status_code=500,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR, "original_error": str(e)},
        ) from e
