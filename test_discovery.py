
import sys
import os

# Mock setup
class BaseAgent:
    def __init__(self, model): pass

class GuardAgent(BaseAgent): pass
class AnalystAgent(BaseAgent): pass
class OtherClass: pass

INITIAL_MODEL = "test-model"

def test_discovery():
    agents_map = {}
    # Simulate globals()
    g = globals().copy()
    
    for name, obj in g.items():
        if isinstance(obj, type) and issubclass(obj, BaseAgent) and obj is not BaseAgent:
            print(f"Discovered: {name}")
            agents_map[name] = obj(model=INITIAL_MODEL)
            
    expected = ["GuardAgent", "AnalystAgent"]
    for e in expected:
        if e not in agents_map:
            print(f"FAILED: {e} not found")
            sys.exit(1)
            
    if "OtherClass" in agents_map:
        print("FAILED: OtherClass incorrectly discovered")
        sys.exit(1)
        
    print("SUCCESS: Dynamic discovery works.")

if __name__ == "__main__":
    test_discovery()
