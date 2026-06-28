from fastapi.testclient import TestClient
from backend_v2.main import app
from backend_v2.models.v2_core import PromptBlock
from backend_v2.models.dtos.api import CurrentUserDTO

client = TestClient(app)

def run():
    # 1. Fetch blocks
    # Wait, the endpoint requires current_user.
    # To bypass, we can just call StudioService.
    import asyncio
    from backend_v2.services.studio import StudioService
    from backend_v2.models.v2_core import MatrixScale, MatrixClaim, TDAAssertion
    from backend_v2.models.i18n import I18nText
    
    async def _test():
        user = CurrentUserDTO(id="usr_test", email="test@test.com", role="superadmin", organization_id="org_test")
        svc = StudioService()
        
        blocks = await svc.list_prompt_blocks(user)
        if not blocks:
            print("No blocks found")
            return
            
        block = blocks[0]
        
        tda = TDAAssertion(
            tda_id="tda_12345678901234561234567890123456",
            concept_description="test",
            inverse_evidence=False,
            aggregation_mode="EXISTS",
            allow_contextual_override=True,
            evaluation_track="COGNITIVE_JUDGEMENT"
        )
        
        claim = MatrixClaim(
            label=I18nText(default_locale="en", translations={"en": "test"}),
            ai_description="test",
            tda_assertions=[tda]
        )
        
        scale = MatrixScale(
            score=5,
            ai_label="TEST",
            claims=[claim]
        )
        
        block.scales = [scale]
        
        # Save
        updated = await svc.save_prompt_block(user, block.id, block)
        print("Updated override:", updated.scales[0].claims[0].tda_assertions[0].allow_contextual_override)
        
        # Fetch again
        fetched = await svc.get_prompt_block(user, block.id)
        print("Fetched override:", fetched.scales[0].claims[0].tda_assertions[0].allow_contextual_override)
        
    asyncio.run(_test())

if __name__ == "__main__":
    run()
