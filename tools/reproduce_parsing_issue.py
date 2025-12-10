import json
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

try:
    from src.components.hooks.parsing import _clean_and_parse_json
except ImportError:
    # Fallback if running from root without src in path
    sys.path.append(os.getcwd())
    from src.components.hooks.parsing import _clean_and_parse_json

def test_parsing():
    # Simulate the problematic output:
    # 1. Contains a valid inner JSON (metadata)
    # 2. Contains a malformed outer JSON due to invalid escape
    
    # This string mimics the structure seen in logs:
    # A large JSON where one field has a bad escape like \uXXXX where XXXX is invalid or just a lone \u
    # The parser fails on the outer object, then continues scanning and finds the inner "metadata" object which is valid.
    
    malformed_json = r"""
    {
      "metadata": {
        "luontiaika": "2024-07-30T12:00:00Z",
        "agentti": "VARTIJA-AGENTTI",
        "vaihe": 1
      },
      "data": {
        "text": "Here is some text with a bad escape sequence: \u00"
      }
    }
    """
    
    print("--- Testing Malformed JSON (Bad Escape) ---")
    try:
        result = _clean_and_parse_json(malformed_json)
        print(f"DEBUG: Result keys: {list(result.keys())}")
        if "metadata" in result:
            print("SUCCESS: Parsed object with metadata.")
        else:
            print("FAILURE: Did not find metadata.")
            if "raw_output" in result:
                print(f"DEBUG: Raw output start: {result['raw_output'][:50]}...")
    except Exception as e:
        print(f"ERROR: {e}")

    # Test Case 2: Unescaped Newlines in String
    # Python triple-quoted string preserves newlines. 
    # If we pass this directly to json.loads, it fails.
    json_with_newlines = """
    {
      "metadata": {"id": 2},
      "text": "Line 1
Line 2"
    }
    """
    print("\n--- Testing JSON with Unescaped Newlines ---")
    try:
        result = _clean_and_parse_json(json_with_newlines)
        if "metadata" in result:
            print("SUCCESS: Parsed object with metadata.")
        else:
            print("FAILURE: Did not find metadata.")
    except Exception as e:
        print(f"ERROR: {e}")

    # Test Case 3: Truncated JSON
    truncated_json = """
    {
      "metadata": {"id": 3},
      "data": "Some long content that gets cu
    """
    print("\n--- Testing Truncated JSON ---")
    try:
        result = _clean_and_parse_json(truncated_json)
        if "metadata" in result:
            print("SUCCESS: Parsed object with metadata.")
        else:
            print("FAILURE: Did not find metadata.")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_parsing()
