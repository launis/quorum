
import logging
import sys

# Add project root to sys.path
sys.path.append("c:\\src\\quorum")


from backend.agents.base import BaseAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Test")

class TestAgent(BaseAgent):
    pass

def test_injection():
    # Pass model=None to avoid Factory validation
    agent = TestAgent(model=None)

    # CASE 1: Empty Dict
    data = {}
    logger.info("Testing Empty Dict...")
    agent._apply_python_authority(data)

    # Assertions
    assert "metadata" in data, "Metadata block missing"
    assert "luontiaika" in data["metadata"], "Timestmap missing"
    assert "agentti" in data["metadata"], "Agent name missing"
    assert "semanttinen_tarkistussumma" in data, "Checksum missing"
    assert data["metadata"]["agentti"] == "TestAgent", "Wrong agent name"

    print(f"Case 1 Pass. Time: {data['metadata']['luontiaika']}")

    # CASE 2: Existing Partial Data (Simulation of Hallucination)
    data2 = {
        "metadata": {
            "luontiaika": "2024-05-21T10:00:00Z", # OLD TIME
            "agentti": "FakeAgent"
        },
        "content": "some content"
    }
    logger.info("Testing Override...")
    agent._apply_python_authority(data2)

    # Assertions
    assert data2["metadata"]["luontiaika"] != "2024-05-21T10:00:00Z", "Timestamp NOT overridden!"
    assert data2["metadata"]["agentti"] == "TestAgent", "Agent name NOT overridden!"
    assert "semanttinen_tarkistussumma" in data2, "Checksum missing"

    print(f"Case 2 Pass. Time: {data2['metadata']['luontiaika']} (Overridden)")

    # Verify Checksum
    chk = data2["semanttinen_tarkistussumma"]
    print(f"Checksum: {chk}")

    # CASE 3: Pydantic Model Injection
    logger.info("Testing Pydantic Model...")
    from pydantic import BaseModel

    class MockMeta(BaseModel):
        luontiaika: str = "old"
        agentti: str = "old"
        vaihe: int = 1
        versio: str = "1.0"
        suoritus_ymparisto: str = "old"

    class MockModel(BaseModel):
        metadata: MockMeta
        semanttinen_tarkistussumma: str = "old_hash"
        content: str = "stuff"

    model_inst = MockModel(metadata=MockMeta())
    agent._apply_python_authority(model_inst)

    assert model_inst.metadata.luontiaika != "old", "Model Timestamp NOT overridden"
    assert model_inst.metadata.agentti == "TestAgent", "Model Agent NOT overridden"
    assert model_inst.semanttinen_tarkistussumma != "old_hash", "Model Checksum NOT updated"

    print(f"Case 3 Pass (Model). Time: {model_inst.metadata.luontiaika}")

if __name__ == "__main__":
    try:
        test_injection()
        print("\nSUCCESS: Logic is sound.")
    except Exception as e:
        print(f"\nFAILURE: {e}")
        exit(1)
