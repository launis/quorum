
import sys
import os
from datetime import datetime

# Setup path
sys.path.append(os.getcwd())

from backend.engine import WorkflowEngine
from backend.config import DB_PATH

def test_date_injection():
    print(f"Testing Prompt Date Injection...")
    engine = WorkflowEngine(DB_PATH)
    
    # 1. Inspect Step 1 Prompt
    step_id = "step_1"
    prompt = engine._construct_prompt_for_step(step_id)
    
    # 2. Get Today's Date with Format Specifier
    today_date = datetime.now().strftime("%d.%m.%Y")
    expected_str = f"SYSTEM TIME: {today_date} (DD.MM.YYYY)"
    
    print(f"Expected String: {expected_str}")
    
    if expected_str in prompt:
        print("SUCCESS: Today's date with format specifier found!")
        print(f"Snippet: {prompt[:200]}...")
        sys.exit(0)
    else:
        print("FAILURE: Date not found.")
        print(f"Prompt Start: {prompt[:200]}")
        sys.exit(1)

if __name__ == "__main__":
    test_date_injection()
