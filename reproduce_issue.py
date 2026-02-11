try:
    from backend.models.domain import ReasoningFidelity
    from backend.models.enums import FidelityLevel
    print("Import successful")
    
    data = {
        "fidelity_score": FidelityLevel.HIGH,
        "fidelity_numeric": 3.0,
        "justification": "Test",
        "quote": "Quote"
    }
    obj = ReasoningFidelity.model_validate(data)
    print("Validation successful")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
