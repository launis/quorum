
import pytest
import shutil
import os
import uuid
import json
import time
from fastapi.testclient import TestClient
from tinydb import TinyDB

from backend.main import app
# Import from builder_router to ensure we override the exact dependency used there
from backend.api.builder_router import get_engine 

from backend.core.engine import WorkflowEngine
from backend.models.state import WorkflowState, InputData
from backend.agents.panel import PanelAgent
from backend.database.repository import TinyDBRepository

# Mock Output simulating a Panel response
MOCK_PANEL_OUTPUT = {
    "logiikka_auditointi": {
        "metadata": {"luontiaika": "2024-12-25T12:00:00", "agentti": "Panel", "vaihe": 5.0, "versio": "2.0", "edellisen_vaiheen_validointi": "OK", "metodologinen_loki": "Log", "semanttinen_tarkistussumma": "123"},
        "walton_stressitesti_loydokset": [{"kysymys": "Q1", "kestiko_todistusaineisto": True, "havainto": "Test"}],
        "paattelyketjun_uskollisuus_auditointi": {"onko_post_hoc_rationalisointia": False, "perustelu": "None", "uskollisuus_score": "KORKEA"}
    },
    "etiikka_ja_fakta": {
        "metadata": {"luontiaika": "2024-12-25T12:00:00", "agentti": "Panel", "vaihe": 9.0, "versio": "2.0", "edellisen_vaiheen_validointi": "OK", "metodologinen_loki": "Log", "semanttinen_tarkistussumma": "123"},
        "faktantarkistus_rfi": [],
        "eettiset_havainnot": []
    },
    "kausaalinen_auditointi": {
        "metadata": {"luontiaika": "2024-12-25T12:00:00", "agentti": "Panel", "vaihe": 7.0, "versio": "2.0", "edellisen_vaiheen_validointi": "OK", "metodologinen_loki": "Log", "semanttinen_tarkistussumma": "123"},
        "kausaalinen_auditointi": {"aikajana_validi": True, "havainnot": "Obs"},
        "kontrafaktuaalinen_testi": {"skenaario_A_toteutunut": "A", "skenaario_B_simulaatio": "B", "uskottavuus_arvio": "Valid"},
        "abduktiivinen_paatelma": "Aito Oivallus"
    }
}

@pytest.fixture(scope="module")
def shared_engine():
    # Use unique dir to avoid lock issues
    base_dir = f"test_fusion_{uuid.uuid4().hex}"
    os.makedirs(base_dir, exist_ok=True)
    db_path = os.path.join(base_dir, "db.json")
    
    # 1. Setup DB
    db = TinyDB(db_path)
    repo = TinyDBRepository(db)
    
    # 2. Seed Data
    try:
        # Assuming run from root
        with open("backend/database/seed_data.json", "r", encoding="utf-8") as f:
            seed = json.load(f)
        
        repo.db.drop_tables()
        if 'workflows' in seed:
            repo.db.table('workflows').insert_multiple(seed['workflows'])
        if 'components' in seed:
            repo.db.table('components').insert_multiple(seed['components'])
        if 'steps' in seed:
            repo.db.table('steps').insert_multiple(seed['steps'])
    except Exception as e:
        print(f"Seeding failed: {e}")
        db.close()
        shutil.rmtree(base_dir, ignore_errors=True)
        raise e
        
    # 3. Create Engine
    engine = WorkflowEngine(db_path, repository=repo)
    
    yield engine
    
    # Teardown
    db.close()
    # Wait for file handle release
    time.sleep(1.0)
    
    max_retries = 3
    for i in range(max_retries):
        try:
            shutil.rmtree(base_dir, ignore_errors=False)
            break
        except OSError:
            if i < max_retries - 1:
                time.sleep(1.0)
            else:
                print(f"[Warning] Could not remove temp dir {base_dir} after retries.")
                # Final attempt mostly to suppress error
                shutil.rmtree(base_dir, ignore_errors=True)

def test_compile_fusion_flow(shared_engine):
    # Override the dependency to use our shared_engine
    app.dependency_overrides[get_engine] = lambda: shared_engine
    
    try:
        client = TestClient(app)
        
        # 1. List Workflows to find seed
        wfs_res = client.get("/builder/workflows")
        assert wfs_res.status_code == 200
        wfs = wfs_res.json()
        
        target = next((w for w in wfs if w['id'] == 'sequential_audit_chain'), None)
        assert target is not None, "Seed workflow 'sequential_audit_chain' missing"
        
        # 2. Copy
        copy_res = client.post(f"/builder/workflows/{target['id']}/copy", json={"new_name": "Fusion Test WF"})
        assert copy_res.status_code == 200
        new_id = copy_res.json()['id']
        
        # 3. Fuse
        # We fuse the 5 middle steps
        payload = {
            "workflow_id": new_id,
            "steps": ["step_logician", "step_falsifier", "step_causal", "step_detector", "step_overseer"]
        }
        fuse_res = client.post("/builder/compile", json=payload)
        
        if fuse_res.status_code != 200:
             print(f"Fusion Error: {fuse_res.text}")
             
        assert fuse_res.status_code == 200
        data = fuse_res.json()
        
        # Verify structure
        new_steps_list = data['new_steps']
        assert "step_panel" in new_steps_list
        assert "step_logician" not in new_steps_list
        
        # Verify Panel Position (Should be around index 4, after guard, analyst, interaction, profiler)
        assert new_steps_list.index("step_panel") == 4
        
        # 4. Verify DB persistence
        wf_res = client.get(f"/builder/workflows/{new_id}")
        assert "step_panel" in wf_res.json()['steps']
        
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_panel_agent_fan_out():
    # Mock Provider
    class MockProvider:
        async def generate(self, prompt, system_instruction, response_schema, **kwargs):
            return MOCK_PANEL_OUTPUT
            
    # Create Agent
    agent = PanelAgent(model_config={"model_name": "test"}, llm_provider=MockProvider())
    
    # State setup (using InputData for validation)
    state = WorkflowState(inputs=InputData(history_text="H", product_text="P", reflection_text="R"))
    
    # Ensure aux_data dict exists (in case not auto-init)
    if not hasattr(state, 'aux_data') or state.aux_data is None:
        state.aux_data = {}

    # Execute
    new_state = await agent.execute(state)
    
    # Check Fan-Out
    # 1. Logician/Falsifier output
    assert new_state.step_falsifier is not None
    assert new_state.step_falsifier.paattelyketjun_uskollisuus_auditointi.uskollisuus_score == "KORKEA"
    assert new_state.step_falsifier.metadata.agentti == "Panel"
    
    # 2. Causal output
    assert new_state.step_causal is not None
    assert new_state.step_causal.abduktiivinen_paatelma == "Aito Oivallus"
    
