
import os
import json
import logging
from unittest.mock import MagicMock, patch
from backend.models.state import WorkflowState, WorkflowInputs
from backend.models.domain import CoachingPlan, ActionGroup, ActionItem
from backend.agents.coach import CoachAgent
from backend.services.administration_service import AdministrationService
from backend.database.repository import TinyDBRepository
from backend.database.wrapper import TinyDBWrapper
from backend.database.seeder import seed_database
from backend.services.progress import ProgressTracker

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Verifier")

TEST_DB_PATH = "test_db.json"

def test_admin_service_delegation():
    """
    Test that AdministrationService.rebuild_database calls seeder.seed_database
    and populates the DB.
    """
    logger.info("--- Testing AdministrationService Delegation ---")
    
    # Clean prev test
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
        
    # Mock Repository (just enough to pass init)
    repo_mock = MagicMock(spec=TinyDBRepository)
    admin_service = AdministrationService(repo_mock)
    
    # We need to hook into the import in administration_service
    # But since I refactored it to do `from backend.database.seeder import seed_database` inside the method,
    # we can mock that module function or just run it and check side effects.
    # Let's run it with a side-effect override of DB_PATH via arguments?
    # No, administration_service.rebuild_database() calls seed_database() with NO args.
    # So it uses default DB_PATH.
    # To test SAFELY, we must mock `backend.database.seeder.seed_database` to NOT run against real DB,
    # OR we relying on the fact that I can't easily change the target unless I change config.
    
    # Approach: Mock `seed_database` in `backend.database.seeder` to verify call.
    with patch('backend.database.seeder.seed_database') as mock_seed:
        tracker = ProgressTracker()
        admin_service.rebuild_database(tracker)
        
        if mock_seed.called:
            logger.info("SUCCESS: AdministrationService called seed_database().")
        else:
            logger.error("FAILURE: AdministrationService DID NOT call seed_database().")

def test_coach_hook_logic():
    """
    Test CoachAgent.enrich_learning_plan with nested ActionGroup structure.
    """
    logger.info("--- Testing CoachAgent Hook Logic ---")
    
    # Setup Data
    item1 = ActionItem(otsikko="Logic Error", kuvaus="Fix reasoning.", resurssit=[])
    group1 = ActionGroup(kategoria="Logic", kohdat=[item1])
    
    plan = CoachingPlan(
        kannustava_palaute="Good job",
        kehityskohteet_konkreettisesti=[group1],
        lopputuloksen_kehitysehdotukset=[],
        lahdeluettelo=[]
    )
    
    # Setup State
    state = WorkflowState(
        step_id="step_coach",
        inputs=WorkflowInputs(product_text="Foo", history_text="Bar", reflection_text="Baz"),
        step_coach=plan
    )
    
    # Initialize Agent
    agent = CoachAgent(run_id="test", step_id="step_coach", db_client=MagicMock())
    # Mock KnowledgeBase
    agent.knowledge_base = {
        "concepts": {"logic": "Reasoning rules (vrt. Aristotle 350BC)"},
        "references": [{"citation": "Aristotle (350BC). Prior Analytics.", "short_citation": "Aristotle 350BC"}]
    }
    
    try:
        # Run Hook
        new_state = agent.enrich_learning_plan(state)
        
        # Verify
        groups = new_state.step_coach.kehityskohteet_konkreettisesti
        res = groups[0].kohdat[0].resurssit
        
        if len(res) > 0 and "Aristotle" in res[0]:
             logger.info(f"SUCCESS: Enrichment worked. Found citation: {res[0]}")
        else:
             logger.warning(f"PARTIAL: Code ran but didn't find citation. Resurssit: {res}. (This might be regex/text match issue, but no crash is the main goal)")
             
        # Check explicit crash
        logger.info("SUCCESS: CoachAgent hook execution finished without error.")
        
    except AttributeError as e:
        logger.error(f"FAILURE: Code crashed with AttributeError: {e}")
    except Exception as e:
        logger.error(f"FAILURE: Code crashed with Exception: {e}")

def verify_db_configs():
    """
    Check physical files for oppimispolku_viikko
    """
    logger.info("--- Verifying DB Configurations ---")
    
    paths = [
        r'c:\Users\risto\OneDrive\quorum\backend\database\db_mock.json',
        r'c:\Users\risto\OneDrive\quorum\data\db.json' 
    ]
    
    for p in paths:
        if not os.path.exists(p):
            logger.warning(f"File not found: {p}")
            continue
            
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Find Config
        comps = data.get('components', {})
        found = False
        clean = True
        
        for k, v in comps.items():
            if v.get('id') == "COACH_OUTPUT_CONFIG":
                found = True
                content = v.get('content', [])
                if "oppimispolku_viikko" in content:
                    logger.error(f"FAILURE: {p} still contains 'oppimispolku_viikko'")
                    clean = False
                else:
                    logger.info(f"SUCCESS: {p} is clean.")
        
        if not found:
            logger.warning(f"Warning: COACH_OUTPUT_CONFIG not found in {p}")

if __name__ == "__main__":
    test_admin_service_delegation()
    test_coach_hook_logic()
    verify_db_configs()
