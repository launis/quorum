
from pydantic import BaseModel

def test_mock_state():
    data = {"history_text": "Success"}
    
    # Logic from registry.py
    class MockState:
        def __init__(self, data):
            self._data = data
            # Creates class with attributes from data, then instantiates
            self.inputs = type("Inputs", (), data)()
            
        def __getattr__(self, name):
            return self._data.get(name)

    state = MockState(data)
    print(f"Direct Access: {state.inputs.history_text}")
    print(f"Has Attr: {hasattr(state.inputs, 'history_text')}")
    
    # Verify getattr fallback
    print(f"GetAttr on inputs: {getattr(state.inputs, 'history_text', 'Fail')}")

if __name__ == "__main__":
    test_mock_state()
