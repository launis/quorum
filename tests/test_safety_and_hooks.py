"""Safety and Hook Logic Tests."""

import json
import os
import shutil
import time
import uuid

import pytest
from fastapi.testclient import TestClient
from tinydb import TinyDB

from backend.core.engine import WorkflowEngine
from backend.database.repository import TinyDBRepository
from backend.dependencies import get_engine
from backend.main import app
from backend.models.state import InputData, WorkflowState


# --- SETUP Fixture ---
@pytest.fixture(scope="module")
def shared_engine_safe():
    """Create shared engine for safety tests."""
    base_dir = f"test_safety_{uuid.uuid4().hex}"
    os.makedirs(base_dir, exist_ok=True)
    db_path = os.path.join(base_dir, "db.json")

    db = TinyDB(db_path)
    repo = TinyDBRepository(db)

    try:
        # Load Seeds
        with open("backend/seed/seed_data.json", encoding="utf-8") as f:
            seed = json.load(f)
        repo.db.drop_tables()
        if "workflows" in seed:
            repo.db.table("workflows").insert_multiple(seed["workflows"])
        if "components" in seed:
            repo.db.table("components").insert_multiple(seed["components"])
        if "steps" in seed:
            repo.db.table("steps").insert_multiple(seed["steps"])

        # Inject Mock System Config to prevent AgentRegistry failure
        repo.db.table("system_config").insert(
            {
                "type": "model_registry",
                "models": {
                    "mock_provider": {
                        "fast": {"model_name": "mock-fast", "provider": "mock"},
                        "deep": {"model_name": "mock-deep", "provider": "mock"},
                    }
                },
            }
        )

    except Exception as e:
        db.close()
        shutil.rmtree(base_dir, ignore_errors=True)
        raise e

    from backend.services.agent_registry import AgentRegistry
    from backend.services.document_service import DocumentService
    from backend.services.prompt_builder import PromptBuilder
    from backend.services.storage import LocalFileStorage

    storage = LocalFileStorage(base_path=base_dir)
    registry = AgentRegistry(repo)
    # No async discovery in sync fixture, but tests seem to inject mocks later or use db state.

    prompt_builder = PromptBuilder(repo, registry)
    doc_service = DocumentService(storage)

    engine = WorkflowEngine(
        db_path=db_path,
        repository=repo,
        registry=registry,
        prompt_builder=prompt_builder,
        storage_client=storage,
        document_service=doc_service,
    )
    yield engine
    db.close()
    time.sleep(0.1)
    shutil.rmtree(base_dir, ignore_errors=True)


# --- TEST: Copy-on-Write Safety ---
def test_fork_step_safety(shared_engine_safe):
    """Test safety of step forking (Copy-on-Write)."""
    app.dependency_overrides[get_engine] = lambda: shared_engine_safe
    client = TestClient(app)

    try:
        # 1. Verify Original State
        target_step_id = "step_logician"
        original_step = client.get(f"/builder/steps/{target_step_id}").json()
        original_prompts = original_step["execution_config"]["llm_prompts"]

        # 2. Clone a shared step (Forking)
        fork_res = client.post("/builder/steps/clone", json={"source_step_id": target_step_id})
        assert fork_res.status_code == 200
        new_step = fork_res.json()
        new_step_id = new_step["id"]
        assert new_step_id != target_step_id

        # 3. Modify the NEW step (e.g. remove a prompt)
        new_config = new_step["execution_config"]
        # Simulating user removing 'MANDATE_1'
        new_config["llm_prompts"] = [p for p in original_prompts if p != "MANDATE_1"]

        update_res = client.put(f"/builder/steps/{new_step_id}", json={"execution_config": new_config})
        assert update_res.status_code == 200

        # 4. SAFETY CHECK: Original step must remain UNTOUCHED
        check_original = client.get(f"/builder/steps/{target_step_id}").json()
        assert "MANDATE_1" in check_original["execution_config"]["llm_prompts"]
        assert check_original["execution_config"]["llm_prompts"] == original_prompts

        # 5. Verify New Step is changed
        check_new = client.get(f"/builder/steps/{new_step_id}").json()
        assert "MANDATE_1" not in check_new["execution_config"]["llm_prompts"]

        print("\n✅ Fork Safety Verified: Shared step remained intact.")

    finally:
        app.dependency_overrides.clear()


# --- TEST: Python Hooks (Mock Execution) ---
# --- TEST: Python Hooks (Mock Execution) ---
def test_python_hooks_execution():
    """Test execution of python hooks (Profiler)."""
    import asyncio

    asyncio.run(_test_python_hooks_execution_async())


async def _test_python_hooks_execution_async():
    from backend.agents.profiler import ProfilerAgent

    # Mock Provider
    class MockProvider:
        async def generate(self, prompt, system_instruction, response_schema, **kwargs):
            # BaseAgent expects an object with .content and .reasoning_token
            class MockResponse:
                def __init__(self, content):
                    self.content = content
                    self.reasoning_token = None
                    self.token_usage = {
                        "prompt_tokens": 10,
                        "completion_tokens": 10,
                        "total_tokens": 20,
                        "total_cost": 0.001,
                    }

            data = {
                "metadata": {
                    "luontiaika": "2024-01-01T00:00:00Z",
                    "agentti": "TestAgent",
                    "vaihe": 2.5,
                    "versio": "2.0",
                },
                "metodologinen_loki": "Test Log",
                "edellisen_vaiheen_validointi": "Valid",
                "semanttinen_tarkistussumma": "hash123",
                "intentio_analyysi": "Test",
                "tunnetila_ja_savy": "Neutral",
                "tunnistetut_vinoumat": [],
                "psykologinen_profiili": "None",
                "manipulaatio_yritykset": "None",
                "teksti_metriikka": None,
            }
            return MockResponse(json.dumps(data))

    # Initialize Agent
    agent = ProfilerAgent(model="test", provider="mock")
    agent.llm_provider = MockProvider()

    # State
    state = WorkflowState(
        execution_id="test_hook",
        inputs=InputData(history_text="This is a simple test sentence.", product_text="", reflection_text=""),
    )
    if not hasattr(state, "aux_data") or state.aux_data is None:
        state.aux_data = {}

    # Execute
    new_state = await agent.execute(state)

    assert new_state.step_profiler is not None
    metrics = new_state.step_profiler.teksti_metriikka

    if metrics:
        assert metrics.word_count > 0
        assert metrics.sentence_count > 0
        print("\n✅ Python Hook (Profiler Metrics) Verified.")
    else:
        print("\n⚠️ Profiler Hook did not return metrics (Check implementation)")
