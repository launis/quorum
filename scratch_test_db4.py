import asyncio
from backend_v2.settings import get_settings
from backend_v2.database.factory import get_driver
from backend_v2.database.repositories.workflow import WorkflowRepositoryImpl
from backend_v2.database.repositories.component import ComponentRepositoryImpl
from backend_v2.database.repositories.knowledge import KnowledgeRepositoryImpl
from backend_v2.database.repositories.system import SystemRepositoryImpl
from backend_v2.services.studio import StudioService
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.v2_core import PromptBlock, MatrixScale, MatrixClaim, TDAAssertion

async def run():
    settings = get_settings()
    driver = await get_driver(settings)
    
    workflow_repo = WorkflowRepositoryImpl(driver)
    component_repo = ComponentRepositoryImpl(driver)
    knowledge_repo = KnowledgeRepositoryImpl(driver)
    system_repo = SystemRepositoryImpl(driver)
    
    svc = StudioService(
        workflow_repo=workflow_repo,
        component_repo=component_repo,
        knowledge_repo=knowledge_repo,
        system_repo=system_repo
    )
    
    user = TokenData(
        id="usr_test",
        email="test@test.com",
        role=UserRole.ROOT,
        organization_id="system"
    )
    
    blocks = await svc.list_prompt_blocks(user)
    
    for block in blocks:
        if block.scales and block.scales[0].claims and block.scales[0].claims[0].tda_assertions:
            print(f"Testing on block {block.id}")
            
            tda = block.scales[0].claims[0].tda_assertions[0]
            tda = tda.model_copy(update={"allow_contextual_override": True})
            
            claim = block.scales[0].claims[0].model_copy(update={"tda_assertions": [tda]})
            scale = block.scales[0].model_copy(update={"claims": [claim]})
            block = block.model_copy(update={"scales": [scale]})
            
            saved = await svc.save_prompt_block(user, block.id, block)
            print("After save, override is:", saved.scales[0].claims[0].tda_assertions[0].allow_contextual_override)
            
            fetched = await svc.get_prompt_block(user, block.id)
            print("After fetch, override is:", fetched.scales[0].claims[0].tda_assertions[0].allow_contextual_override)
            return
            
    print("No TDAs found anywhere.")

if __name__ == "__main__":
    asyncio.run(run())
