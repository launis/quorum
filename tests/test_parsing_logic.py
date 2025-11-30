import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

try:
    from src.components.hooks.parsing import _clean_and_parse_json, _repair_json_string
except ImportError:
    # Fallback if running from root without src in path
    sys.path.append(os.getcwd())
    from src.components.hooks.parsing import _clean_and_parse_json, _repair_json_string

class TestParsingRobustness(unittest.TestCase):

    def test_repair_json_string(self):
        # Test 1: Valid JSON should be unchanged
        self.assertEqual(_repair_json_string('{"key": "value"}'), '{"key": "value"}')
        
        # Test 2: Invalid \u escape
        # Note: raw strings in python still interpret backslashes if they escape the quote, but here we want literal backslashes
        self.assertEqual(_repair_json_string(r'{"key": "val\u00ue"}'), r'{"key": "val\\u00ue"}')
        
        # Test 3: Unescaped backslash
        self.assertEqual(_repair_json_string(r'{"key": "val\ue"}'), r'{"key": "val\\ue"}') # \u without 4 digits
        self.assertEqual(_repair_json_string(r'{"path": "C:\Users"}'), r'{"path": "C:\\Users"}')
        
        # Test 4: Valid escapes should remain valid
        self.assertEqual(_repair_json_string(r'{"key": "line\nbreak"}'), r'{"key": "line\nbreak"}')
        self.assertEqual(_repair_json_string(r'{"key": "tab\t"}'), r'{"key": "tab\t"}')
        self.assertEqual(_repair_json_string(r'{"key": "\u1234"}'), r'{"key": "\u1234"}')

    def test_parse_simple_json(self):
        text = '{"key": "value"}'
        result = _clean_and_parse_json(text)
        self.assertEqual(result, {"key": "value"})

    def test_parse_json_with_markdown(self):
        text = 'Here is the JSON:\n```json\n{"key": "value"}\n```'
        result = _clean_and_parse_json(text)
        self.assertEqual(result, {"key": "value"})

    def test_parse_malformed_json_escape(self):
        # This mimics the failure case
        text = r'''
        {
          "metadata": {"id": 1},
          "data": "Invalid escape \u00 here"
        }
        '''
        result = _clean_and_parse_json(text)
        # With repair, this should parse the outer object
        self.assertIn("metadata", result)
        self.assertIn("data", result)
        self.assertEqual(result["metadata"]["id"], 1)
        # The data string might have the backslash escaped
        self.assertIn("Invalid escape", result["data"])

    def test_parse_nested_json(self):
        text = '{"outer": {"inner": "value"}}'
        result = _clean_and_parse_json(text)
        self.assertEqual(result, {"outer": {"inner": "value"}})

    def test_parse_multiple_candidates_selects_metadata(self):
        # If there are multiple JSONs, it should pick the one with 'metadata'
        text = r'''
        Some thought process:
        {
           "thought": "I should do this"
        }
        
        Final answer:
        {
           "metadata": {"agent": "test"},
           "result": "success"
        }
        '''
        result = _clean_and_parse_json(text)
        self.assertIn("metadata", result)
        self.assertEqual(result["metadata"]["agent"], "test")

    def test_parse_json_with_unescaped_newlines(self):
        text = """
        {
            "metadata": {"id": 1},
            "text": "Line 1
Line 2"
        }
        """
        result = _clean_and_parse_json(text)
        self.assertIn("metadata", result)
        # The repair replaces literal newline with \n, which json.loads parses as a newline char
        self.assertEqual(result["text"], "Line 1\nLine 2")

    def test_parse_truncated_json(self):
        text = '{"metadata": {"id": 1}, "data": "truncated'
        result = _clean_and_parse_json(text)
        self.assertIn("metadata", result)
        self.assertEqual(result["metadata"]["id"], 1)
        # The data field might be closed with a quote and brace
        self.assertTrue(result["data"].startswith("truncated"))

if __name__ == '__main__':
    unittest.main()
