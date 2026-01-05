import logging
import os
from contextlib import asynccontextmanager

from arq import create_pool
from arq.connections import RedisSettings
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.admin_router import router as admin_router
from backend.api.agents_router import router as agents_router
from backend.api.auth_router import router as auth_router
from backend.api.builder_router import router as builder_router
from backend.api.config_router import router as config_router
from backend.api.execution_router import router as execution_router
from backend.api.llm_router import router as llm_router
from backend.api.organization_router import router as organization_router

# Routers
from backend.api.tools_router import router as tools_router

# Dependencies
from backend.dependencies import CurrentUserDep, DatabaseDep, EngineDep
from backend.exceptions import AppException
from backend.settings import get_settings

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def _print_startup_banner():
    settings = get_settings()
    print("\n" + "=" * 60)
    print(" 🧠  COGNITIVE QUORUM v2.2 - SYSTEM STATUS")
    print("=" * 60)

    # 1. Database Mode
    db_mode = "☁️  FIRESTORE (Cloud)" if settings.storage_backend == "FIRESTORE" else "📂  TINYDB (Local JSON)"
    print(f" 💾  DATABASE:    {db_mode}")

    # 2. LLM Configuration
    llm_mode = "🤖  REAL AI (Live APIs)" if not settings.use_mock_llm else "🎭  MOCK LLM (Simulation)"
    print(f" 🧠  INTELLIGENCE: {llm_mode}")

    # 3. Environment
    env = "🚀  PRODUCTION" if settings.storage_backend == "FIRESTORE" else "🛠️  DEVELOPMENT"
    print(f" 🌍  ENVIRONMENT:  {env}")

    print("-" * 60)
    # 4. Data Source info
    data_source = "Mock DB (db_mock.json)" if settings.use_mock_db else "Prod DB (db.json)"
    if settings.storage_backend == "FIRESTORE":
        data_source = "Firestore (Cloud)"
    print(f" 📂  DATA SOURCE:  {data_source}")
    print("=" * 60 + "\n")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Cognitive Quorum Backend...")
    _print_startup_banner()

    # Ensure Auth Root User Exists
    try:
        # Manual Bootstrap to avoid Depends() issues outside of request context
        from backend.dependencies import get_db_client_dep, get_settings_dep
        from backend.services.auth import AuthService

        db_client = get_db_client_dep()
        settings = get_settings_dep()

        use_firebase = settings.storage_backend.upper() == "FIRESTORE" and not settings.use_mock_db

        logger.info("[Bootstrap] Verifying Root User...")
        auth_service = AuthService(db_client, use_firebase=use_firebase)
        auth_service.ensure_root_user()  # This now also seeds DEMO users

        logger.info("[Bootstrap] Auth System ready.")
    except Exception as e:
        logger.error(f"Auth System Bootstrap Failed: {e}")

    # Initialize Arq (Background Tasks)
    try:
        # 1. Attempt Real Redis
        redis_settings = RedisSettings(host=settings.redis_host, port=settings.redis_port)
        redis_pool = await create_pool(redis_settings)
        app.state.arq_pool = redis_pool
        logger.info(f"Arq Redis connection established at {settings.redis_host}:{settings.redis_port}")

    except (OSError, ConnectionError, TimeoutError, Exception) as e:
        # 2. Fallback to In-Memory Redis (fakeredis)
        logger.warning(f"Real Redis connection failed ({type(e).__name__}: {e}). Switching to In-Memory Mode.")

        try:
            from arq.connections import ArqRedis
            from arq.worker import Worker
            from fakeredis.aioredis import FakeRedis

            from backend.worker import WorkerSettings

            # Initialize FakeRedis
            # Arq expects a pool-like object, FakeRedis works as one, but needs 'connection_kwargs' for Arq logging
            fake_redis = FakeRedis()
            fake_redis.connection_kwargs = {"host": "localhost", "port": 6379}  # Mock for Arq compatibility

            # PATCH: Arq 0.26+ calls .get_connection() on the pool, which FakeRedis lacks
            if not hasattr(fake_redis, "get_connection"):

                async def _get_conn():
                    return fake_redis

                fake_redis.get_connection = _get_conn

            # PATCH: Arq also calls .release(conn)
            if not hasattr(fake_redis, "release"):

                async def _release(conn):
                    pass

                fake_redis.release = _release

            # PATCH: Arq calls .disconnect() on the pool? No, on connection. FakeRedis has close() but Arq might call something else.
            # But the specific error is AttributeError: 'FakeRedis' object has no attribute 'retry' in await conn.retry.call_with_retry
            # Wait, 'conn' IS 'fake_redis' because _get_conn returns self.
            # So fake_redis needs a .retry attribute which has a .call_with_retry method.

            class MockRetry:
                async def call_with_retry(self, func, on_error):
                    return await func()

            if not hasattr(fake_redis, "retry"):
                fake_redis.retry = MockRetry()

            # PATCH: Arq tries to log Redis info on startup, which crashes on FakeRedis
            # We patch the logging function itself to be a no-op
            import arq.connections

            async def _no_op_log(*args, **kwargs):
                pass

            arq.connections.log_redis_info = _no_op_log
            
            # PATCH: We must also patch the reference in arq.worker, as it likely imported the function already
            import arq.worker
            arq.worker.log_redis_info = _no_op_log

            # PATCH: Arq 0.26+ uses connection.pack_commands(cmds) for pipelining optimization
            if not hasattr(fake_redis, "pack_commands"):

                def _pack(cmds):
                    return cmds  # Pass through for fake redis

                fake_redis.pack_commands = _pack

            if not hasattr(fake_redis, "send_packed_command"):

                async def _send_packed(cmds):
                    pass

                fake_redis.send_packed_command = _send_packed

            # PATCH: Arq 0.26+ uses send_command(*args)
            if not hasattr(fake_redis, "send_command"):

                async def _send_command(*args, **kwargs):
                    pass

                fake_redis.send_command = _send_command

            # ArqRedis wrapper needed for Arq features
            arq_redis = ArqRedis(fake_redis)

            app.state.arq_pool = arq_redis
            logger.info("In-Memory Redis pool initialized.")

            # Start Embedded Worker
            # We must override the redis_pool in settings to use our shared fake instance
            class EmbeddedWorkerSettings(WorkerSettings):
                redis_pool = arq_redis
                # Disable signal handling since we run in thread/task
                handle_signals = False

            if os.environ.get("TESTING", "").lower() != "true":
                worker = Worker(
                    functions=WorkerSettings.functions,
                    redis_pool=arq_redis,
                    on_startup=WorkerSettings.on_startup,
                    on_shutdown=WorkerSettings.on_shutdown,
                )

                # Run worker in background task
                import asyncio

                worker_task = asyncio.create_task(worker.async_run())
                app.state.worker_task = worker_task
                logger.info("Embedded Arq Worker started in background task.")
            else:
                logger.info("Embedded Arq Worker SKIPPED (TESTING mode).")

        except ImportError:
            logger.error("Failed to start In-Memory Redis: 'fakeredis' not installed.")
            logger.warning("Background tasks will be unavailable.")
        except Exception as ex:
            logger.error(f"In-Memory Worker startup failed: {ex}")

    # Note: Engine is lazy-loaded on first request to avoid complex manual DI here.
    yield
    # Shutdown
    logger.info("Shutting down...")

    if hasattr(app.state, "worker_task"):
        logger.info("Stopping embedded worker...")
        app.state.worker_task.cancel()
        try:
            await app.state.worker_task
        except asyncio.CancelledError:
            pass

    if hasattr(app.state, "arq_pool"):
        pool = app.state.arq_pool
        # Check if it's a real pool or fake
        if hasattr(pool, "close"):
            await pool.close()
        logger.info("Arq Redis connection closed.")


app = FastAPI(
    title="Cognitive Quorum API",
    description="Backend for Cognitive Quorum application.",
    version="2.1.0",
    lifespan=lifespan,
)

import logfire  # noqa: E402

from backend.logging_config import configure_logfire  # noqa: E402

configure_logfire()
if os.getenv("DISABLE_LOGFIRE", "").lower() != "true":
    try:
        logfire.instrument_fastapi(app)
    except Exception as e:
        logger.warning(f"Failed to instrument FastAPI with Logfire: {e}")


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code, content={"error": exc.message, "details": exc.details, "status": "error"}
    )


# --- CORS Configuration ---
# Allows frontend (Flutter/Streamlit) on different domains to talk to this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tools_router)
app.include_router(execution_router)
app.include_router(agents_router)
app.include_router(admin_router)
app.include_router(config_router)
app.include_router(auth_router)
app.include_router(llm_router, prefix="/llm", tags=["LLM"])
app.include_router(builder_router)
app.include_router(organization_router)


@app.middleware("http")
async def add_no_cache_header(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.on_event("startup")
async def startup_event():
    from backend.bootstrap import bootstrap_application

    await bootstrap_application()


# Database setup
settings = get_settings()
# print(f"DEBUG: ACTIVE DATABASE PATH: {os.path.abspath(settings.start_db_path)}")

# Ensure data dirs exist
os.makedirs(settings.data_dir, exist_ok=True)
os.makedirs(os.path.dirname(settings.start_db_path), exist_ok=True)
UPLOAD_DIR = os.path.join(settings.data_dir, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# --- Root / DB Endpoints ---


# ... imports ...


@app.get(
    "/db/seed_data",
    summary="Get Seed Data",
    response_description="Returns the full components, steps, and workflows from the database.",
)
async def get_seed_data(engine: EngineDep, current_user: CurrentUserDep):
    """Retrieves the raw seed data configuration (components, steps, workflows).
    Now scoped by User Role (Root sees all).

    Args:
        engine (EngineDep): Dependency.
        current_user (CurrentUserDep): Authenticated User.

    Returns:
        dict: Object containing lists of components, steps, and workflows.

    """
    try:
        components = await engine.repository.get_all_components()
        steps = await engine.repository.get_all_steps()

        # Pass Role/Org for filtering
        workflows = await engine.repository.get_all_workflows(
            organization_id=current_user.organization_id, role=current_user.role
        )

        return {"components": components, "steps": steps, "workflows": workflows}
    except Exception as e:
        print(f"DEBUG: Error reading seed data from DB: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/db/workflows", summary="List Workflows (DB)", response_description="A list of all workflow definitions.")
async def get_workflows(engine: EngineDep, current_user: CurrentUserDep):
    """Retrieves all workflow definitions from the repository.
    Scoped by User Role.

    Args:
        engine (EngineDep): Dependency.
        current_user (CurrentUserDep): Authenticated User.

    Returns:
        List[dict]: List of workflow objects.

    """
    try:
        workflows = await engine.repository.get_all_workflows(
            organization_id=current_user.organization_id, role=current_user.role
        )
        return workflows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/db/reset", deprecated=True)
def reset_db_legacy(db: DatabaseDep):
    """Legacy stub, functionality moved to Admin Router."""
    return {"message": "Use /admin/database/reset/* endpoints."}


@app.get(
    "/db/preview_prompt/{step_id}",
    summary="Preview Step Prompt",
    response_description="The constructed prompt segments for a specific step.",
)
async def preview_prompt(engine: EngineDep, step_id: str = Path(..., description="The ID of the step to preview.")):
    """Previews the prompt that would be generated for a specific step identifier.

    Args:
        step_id (str): Step Identifier.
        engine (WorkflowEngine): Dependency.

    Returns:
        dict: Prompt structure (user, system, parts).

    Raises:
        HTTPException: If prompt generation fails.

    """
    try:
        preview = await engine.preview_step_prompt(step_id)
        if "error" in preview:
            raise HTTPException(status_code=400, detail=preview["error"])
        return preview
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/db/preview_full_chain/{workflow_id}",
    summary="Preview Full Chain",
    response_description="The concatenated full prompt chain for deep auditing.",
)
async def preview_full_chain(engine: EngineDep, workflow_id: str = Path(..., description="The ID of the workflow.")):
    """Generates a full textual preview of the entire sequential audit chain.

    Args:
        workflow_id (str): Workflow Identifier.
        engine (WorkflowEngine): Dependency.

    Returns:
        dict: Object containing 'full_chain_text'.

    """
    try:
        preview_text = await engine.preview_full_chain_prompts(workflow_id)
        if preview_text.startswith("Error"):
            raise HTTPException(status_code=404, detail=preview_text)
        return {"full_chain_text": preview_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/config/introspection",
    summary="Introspect Codebase",
    response_description="Lists available schemas, hooks, and agents found in code.",
)
def introspect_codebase():
    """Performs runtime introspection of the backend codebase to discover available resources.

    Returns:
        dict: Lists of schemas, hooks, and agents.

    """
    import inspect

    from backend.models import domain

    # 1. Inspect Schemas
    available_schemas = []
    for name, obj in inspect.getmembers(domain):
        if inspect.isclass(obj) and issubclass(obj, domain.BaseModel) and obj is not domain.BaseModel:
            available_schemas.append(name)

    # 2. Inspect Hooks (Legacy - Deprecated/Removed)
    available_hooks = []

    # 3. Inspect Agents
    available_agents = []
    from backend.agents import analyst, base, critics, guard, judge, logician, panel, xai

    agent_modules = [base, guard, analyst, logician, critics, judge, panel, xai]

    for module in agent_modules:
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and name.endswith("Agent") and name != "BaseAgent":
                available_agents.append(name)

    return {"schemas": sorted(available_schemas), "hooks": [], "agents": sorted(list(set(available_agents)))}


@app.get("/health", summary="Health Check", response_description="Simple status indicator.")
def health_check():
    """Basic liveness probe.
    """
    return {"status": "ok"}
