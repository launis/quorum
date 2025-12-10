
import json

filename = 'data/seed_data.json'

try:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
        
    print(f"Total length: {len(content)}")
    
    # The error was around char 70565
    start = max(0, 70565 - 100)
    end = min(len(content), 70565 + 100)
    
    print(f"Content around 70565 ({start}-{end}):")
    print(repr(content[start:end]))
    
    # Try to parse
    json.loads(content)
    print("JSON is valid")
except json.JSONDecodeError as e:
    print(f"JSON Error: {e}")
    print(f"Error at line {e.lineno} column {e.colno} (char {e.pos})")
    
    # Print lines around the error
    lines = content.splitlines()
    if 0 <= e.lineno - 1 < len(lines):
        print(f"Line {e.lineno}: {repr(lines[e.lineno - 1])}")
except Exception as e:
    print(f"Error: {e}")
