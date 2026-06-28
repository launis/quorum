import pytest
import asyncio
from backend_v2.services.studio import StudioService
from backend_v2.models.dtos.api import CurrentUserDTO
from backend_v2.models.v2_core import MatrixScale, MatrixClaim, TDAAssertion
from backend_v2.models.i18n import I18nText

async def run():
    user = CurrentUserDTO(id="usr_test", email="test@test.com", role="superadmin", organization_id="org_test")
    svc = StudioService()
    
    # 1. Fetch first block
    blocks = await svc.list_prompt_blocks(user)
    if not blocks:
        print("No blocks found")
        return
        
    block = blocks[0]
    print(f"Original block ID: {block.id}")
    
    # 2. Add a mock MatrixScale with allow_contextual_override=True
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
    
    # 3. Save
    updated = await svc.save_prompt_block(user, block.id, block)
    print("Updated override:", updated.scales[0].claims[0].tda_assertions[0].allow_contextual_override)
    
    # 4. Fetch again to verify persistence
    fetched = await svc.get_prompt_block(user, block.id)
    print("Fetched override:", fetched.scales[0].claims[0].tda_assertions[0].allow_contextual_override)
    
if __name__ == "__main__":
    asyncio.run(run())
