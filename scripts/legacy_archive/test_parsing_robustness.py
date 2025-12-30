import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.components.hooks.parsing import _clean_and_parse_json

def test_parsing():
    test_cases = [
        # 1. Standard JSON
        ('{"key": "value"}', {"key": "value"}),
        
        # 2. JSON with markdown
        ('```json\n{"key": "value"}\n```', {"key": "value"}),
        
        # 3. JSON with extra text
        ('Here is the JSON:\n{"key": "value"}\nHope this helps!', {"key": "value"}),
        
        # 4. JSON with nested braces
        ('{"key": {"nested": "value"}}', {"key": {"nested": "value"}}),
        
        # 5. Malformed JSON (should return raw output dict)
        ('{"key": "value"', {"raw_output": '{"key": "value"'}),
    ]
    
    print("Running parsing tests...")
    for i, (input_text, expected) in enumerate(test_cases):
        result = _clean_and_parse_json(input_text)
        if result == expected:
            print(f"Test {i+1}: PASS")
        else:
            print(f"Test {i+1}: FAIL")
            print(f"  Input: {input_text}")
            print(f"  Expected: {expected}")
            print(f"  Got: {result}")

if __name__ == "__main__":
    test_parsing()
