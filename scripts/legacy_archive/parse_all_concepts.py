
import re
import json

file_path = r'c:\Users\risto\OneDrive\quorum\data\Holistinen Mestaruus.txt'
output_path = r'c:\Users\risto\OneDrive\quorum\data\extracted_concepts.json'

def extract_concepts(text):
    concepts = {}
    references = []
    
    # 1. Look for patterns like "Concept: Definition (Ref)"
    # Regex to capture "Term: Definition" or similar bullet points
    # Assuming concepts are often capitalized or at start of lines
    
    # Strategy: Look for lines that look like definitions
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Pattern 1: Bold concept in markdown or simple "Term:"
        # "Toulmin: ..." or "**Toulmin**: ..."
        match = re.match(r'^[\*-]?\s*(\*{0,2})([A-ZÅÄÖ][a-zA-ZÅÄÖ\s\-\(\)]+)(\*{0,2})[:–-]\s*(.+)', line)
        if match:
            term = match.group(2).strip()
            definition = match.group(4).strip()
            
            # heuristic to avoid random list items being treated as concepts
            if len(term) < 50 and len(definition) > 10: 
                concepts[term] = definition

    return concepts

try:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    extracted = extract_concepts(content)
    
    print(f"Found {len(extracted)} potential concepts.")
    
    # Save to file for inspection
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extracted, f, indent=4, ensure_ascii=False)
        
    # Print first 20 names to verify
    print("First 20 concepts found:")
    for k in list(extracted.keys())[:20]:
        print(f"- {k}")

except Exception as e:
    print(f"Error: {e}")
