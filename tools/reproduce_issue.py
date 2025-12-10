import json

raw_output = """{
  "metadata": {
    "timestamp": "2024-02-29T10:45:00Z",
    "agent": "VARTIJA-AGENTTI",
    "phase": 1,
    "version": "1.0"
  },
  "metodologinen_loki": "test"
}"""

print(f"Testing JSON parsing...")
try:
    data = json.loads(raw_output, strict=False)
    print("Success!")
    print(data)
except json.JSONDecodeError as e:
    print(f"Error: {e}")
    print(f"Error at line {e.lineno}, column {e.colno}, char {e.pos}")

print("-" * 20)
print("Testing with trailing comma inside metadata...")
raw_output_trailing = """{
  "metadata": {
    "timestamp": "2024-02-29T10:45:00Z",
    "agent": "VARTIJA-AGENTTI",
    "phase": 1,
    "version": "1.0",
  },
  "metodologinen_loki": "test"
}"""
try:
    data = json.loads(raw_output_trailing, strict=False)
    print("Success with trailing comma!")
except json.JSONDecodeError as e:
    print(f"Error with trailing comma: {e}")
