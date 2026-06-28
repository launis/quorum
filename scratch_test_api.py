from fastapi.testclient import TestClient
from backend_v2.main import app

client = TestClient(app)

def run():
    # Bypass auth using dependency override
    from backend_v2.api.dependencies import get_current_user
    from backend_v2.models.dtos.iam import UserResponseDTO
    
    def override_get_current_user():
        return UserResponseDTO(id="usr_test", email="test@test.com", role="superadmin", organization_id="org_test")
        
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    # 1. Fetch blocks
    response = client.get("/api/v2/admin/prompt-blocks")
    if response.status_code != 200:
        print("Failed to get blocks:", response.text)
        return
        
    blocks = response.json()
    if not blocks:
        print("No blocks found")
        return
        
    block = blocks[0]
    print(f"Original block ID: {block['id']}")
    
    # 2. Modify block to add allow_contextual_override
    tda = {
        "tda_id": "tda_12345678901234561234567890123456",
        "concept_description": "test",
        "inverse_evidence": False,
        "aggregation_mode": "EXISTS",
        "allow_contextual_override": True,
        "evaluation_track": "COGNITIVE_JUDGEMENT"
    }
    
    claim = {
        "label": {"default_locale": "en", "translations": {"en": "test"}},
        "ai_description": "test",
        "tda_assertions": [tda]
    }
    
    scale = {
        "score": 5,
        "ai_label": "TEST",
        "claims": [claim]
    }
    
    block["scales"] = [scale]
    
    # 3. Save block
    put_response = client.put(f"/api/v2/admin/prompt-blocks/{block['id']}", json=block)
    if put_response.status_code != 200:
        print("Failed to save block:", put_response.text)
        return
        
    updated = put_response.json()
    print("Updated override:", updated["scales"][0]["claims"][0]["tda_assertions"][0].get("allow_contextual_override"))
    
    # 4. Fetch again
    get_response = client.get(f"/api/v2/admin/prompt-blocks/{block['id']}")
    fetched = get_response.json()
    print("Fetched override:", fetched["scales"][0]["claims"][0]["tda_assertions"][0].get("allow_contextual_override"))

if __name__ == "__main__":
    run()
