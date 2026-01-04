import logging
from typing import Any

from arq.connections import RedisSettings

from backend.logging_config import configure_logfire, setup_logging
from backend.settings import get_settings

# Initialize settings
settings = get_settings()

# --- Worker Job Tasks ---

async def execute_workflow_task(ctx: Any, execution_id: str, workflow_id: str, inputs: dict) -> None:
    """
    Background job to execute a workflow.
    """
    logging.info(f"[Job] executing workflow {workflow_id} (Execution ID: {execution_id})")
    
    # Retrieve pre-initialized services from worker context
    repository = ctx["repository"]
    registry = ctx["registry"]
    prompt_builder = ctx["prompt_builder"]

    # Initialize Runner
    from backend.core.runner import PipelineRunner
    runner = PipelineRunner(repository, registry, prompt_builder)
    
    # Run
    # Note: We need to reconstruct the state or fetch it. 
    # Usually the API creates the initial state. 
    # For now, let's assume we initialize it here or fetch.
    # Actually, the runner needs 'initialize_state'.
    
    # We await the runner execution.
    # But wait, runner.execute_loop takes 'state' and 'pipeline_steps'.
    # We need to resolve the workflow steps first.
    
    try:
        # 1. Fetch Workflow
        workflow = await repository.get_workflow(workflow_id)
        if not workflow:
            logging.error(f"[Job] Workflow {workflow_id} not found.")
            return

        # 2. Initialize State
        state = await runner.initialize_state(
            execution_id=execution_id,
            raw_inputs=inputs,
            workflow_id=workflow_id,
            workflow_name=workflow.get("name")
        )

        # 3. Resolve Steps (Agents)
        steps_config = workflow.get("steps", [])
        pipeline_steps = []
        for step_conf in steps_config:
            agent_instance = registry.get_agent_for_step(step_conf)
            pipeline_steps.append((agent_instance, step_conf))

        # 4. Execute
        # Tracker: We need a tracker. For background tasks, we might log or update DB directly.
        # Let's use a simple logger tracker or similar.
        # Ideally, we should inject a DbTracker.
        from backend.services.tracker import ProgressTracker
        tracker = ProgressTracker(repository, execution_id)
        
        await runner.execute_loop(state, pipeline_steps, tracker, execution_id)
        logging.info(f"[Job] Workflow execution {execution_id} completed.")

    except Exception as e:
        logging.error(f"[Job] Workflow execution failed: {e}", exc_info=True)


async def startup(ctx: Any) -> None:
    """
    Called when the worker starts.
    We initialize logging and Logfire here to ensure worker logs are captured.
    """
    setup_logging()
    configure_logfire()
    logging.info("Arq Worker started successfully.")
    
    # Initialize Services (DB, Registry)
    from backend.dependencies import get_async_repository, get_db_client_dep
    from backend.services.agent_registry import AgentRegistry
    from backend.services.prompt_builder import PromptBuilder

    db_client = get_db_client_dep()
    repository = get_async_repository(db_client)
    
    registry = AgentRegistry(repository)
    registry.discover_and_register_agents()
    
    prompt_builder = PromptBuilder(repository, registry)
    
    # Store in context for jobs
    ctx["repository"] = repository
    ctx["registry"] = registry
    ctx["prompt_builder"] = prompt_builder
    logging.info("Worker services initialized.")

async def shutdown(ctx: Any) -> None:
    """
    Called when the worker shuts down.
    """
    logging.info("Arq Worker shutting down.")

async def health_check(ctx: Any) -> str:
    """
    Simple health check task.
    """
    return "OK"

class WorkerSettings:
    """
    Configuration for the Arq worker.
    """
    functions = [health_check, execute_workflow_task]  # Registered tasks
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings(
        host=settings.redis_host,
        port=settings.redis_port,
    )
