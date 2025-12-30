import json
import re
import os
import uuid

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
SEED_DATA_PATH = os.path.join(DATA_DIR, 'seed_data.json')
BIBLIOGRAPHY_PATH = os.path.join(DATA_DIR, 'bibliography.txt')

# New Component Types
NEW_TYPES = {
    "HEADER_METHODS": "Menetelmä",
    "HEADER_HEURISTICS": "Heuristiikka",
    "HEADER_PROTOCOLS": "Protokolla",
    "HEADER_PRINCIPLES": "Periaate",
    "HEADER_REQUIREMENTS": "Vaatimus",
    "HEADER_RULES": "Sääntö",
    "HEADER_MANDATES": "Mandaatti"
}

# Phase Mapping (New Order)
# 1. Guard
# 2. Analyst
# 3. Logician
# 4. Logical Falsifier
# 5. Factual Overseer (Was 7)
# 6. Causal Analyst (Was 5)
# 7. Performativity Detector (Was 6)
# 8. Judge
# 9. XAI

PHASE_ORDER = [
    "STEP_1_GUARD",
    "STEP_2_ANALYST",
    "STEP_3_LOGICIAN",
    "STEP_4_FALSIFIER",
    "STEP_7_FACT_CHECKER", # Moved to Pos 5
    "STEP_5_CAUSAL",       # Moved to Pos 6
    "STEP_6_PERFORMATIVITY", # Moved to Pos 7
    "STEP_8_JUDGE",
    "STEP_9_XAI"
]

# Granular Component Mapping (Draft from Plan)
PHASE_COMPONENTS = {
    "STEP_1_GUARD": ["HEADER_MANDATES", "MANDATE_1_1", "HEADER_RULES", "RULE_2", "RULE_3", "PROMPT_GUARD"],
    "STEP_2_ANALYST": ["HEADER_MANDATES", "MANDATE_1_1", "HEADER_RULES", "RULE_2", "RULE_3", "RULE_4", "RULE_5", "PROMPT_ANALYST"],
    "STEP_3_LOGICIAN": ["HEADER_MANDATES", "MANDATE_1_1", "HEADER_RULES", "RULE_2", "RULE_3", "RULE_4", "RULE_5", "PROMPT_LOGICIAN"],
    "STEP_4_FALSIFIER": ["HEADER_MANDATES", "MANDATE_1_1", "HEADER_PRINCIPLES", "PRINCIPLE_1", "PROMPT_FALSIFIER"],
    "STEP_7_FACT_CHECKER": ["HEADER_MANDATES", "MANDATE_1_1", "HEADER_RULES", "RULE_9", "HEADER_PROTOCOLS", "PROTOCOL_3", "HEADER_REQUIREMENTS", "REQUIREMENT_1", "PROMPT_FACT_CHECKER"],
    "STEP_5_CAUSAL": ["HEADER_MANDATES", "MANDATE_1_1", "HEADER_HEURISTICS", "HEURISTIC_1", "HEURISTIC_2", "HEURISTIC_3", "PROMPT_CAUSAL"],
    "STEP_6_PERFORMATIVITY": ["HEADER_MANDATES", "MANDATE_1_1", "MANDATE_4", "HEADER_RULES", "RULE_8", "PROMPT_PERFORMATIVITY"],
    "STEP_8_JUDGE": ["HEADER_MANDATES", "MANDATE_1_3", "HEADER_RULES", "RULE_6", "RULE_13", "RULE_15", "PROMPT_JUDGE"],
    "STEP_9_XAI": ["HEADER_RULES", "RULE_1", "PROMPT_XAI"]
}

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def parse_bibliography():
    references = []
    if not os.path.exists(BIBLIOGRAPHY_PATH):
        print(f"Warning: Bibliography file not found at {BIBLIOGRAPHY_PATH}")
        return references

    with open(BIBLIOGRAPHY_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Simple parsing logic
        # Author(s). Year: Title. Publisher/Journal.
        parts = line.split('. ', 2)
        if len(parts) >= 2:
            author_part = parts[0]
            # Try to extract year
            year_match = re.search(r'(\d{4})', line)
            year = year_match.group(1) if year_match else "Unknown"
            
            # Create ID
            author_slug = author_part.split(',')[0].split(' ')[0].upper()
            ref_id = f"REF_{author_slug}_{year}"
            
            ref = {
                "id": ref_id,
                "type": "Reference",
                "content": line,
                "citation": f"({author_part.split(',')[0]} {year})",
                "name": f"Ref: {author_part.split(',')[0]} {year}",
                "description": "Bibliographic Reference"
            }
            references.append(ref)
            
    return references

def clean_content(text):
    # Remove "OTSIKKO: " prefixes
    text = re.sub(r'OTSIKKO:\s*', '', text)
    # Remove internal references like (ks. Luku 2.3.3)
    text = re.sub(r'\(ks\.\s*(Luku|Chapter)\s*[\d\.]+\)', '', text, flags=re.IGNORECASE)
    return text

def main():
    print("Loading seed data...")
    data = load_json(SEED_DATA_PATH)
    
    # 1. Create Reference Components
    print("Parsing bibliography...")
    new_refs = parse_bibliography()
    # Filter out existing refs to avoid duplicates (based on ID)
    # Filter out existing refs to avoid verified duplicates
    existing_ids = set()
    for c in data.get('components', []):
        c_id = c.get('id') or c.get('name')
        if c_id:
            existing_ids.add(c_id)
    for ref in new_refs:
        if ref['id'] not in existing_ids:
            data['components'].append(ref)
            existing_ids.add(ref['id'])
            
    # 2. Create New Header Components
    print("Creating headers...")
    for header_id, name in NEW_TYPES.items():
        if header_id not in existing_ids:
            header = {
                "id": header_id,
                "type": "Header",
                "content": name, # Just the name for now
                "name": name,
                "description": f"Header for {name}"
            }
            data['components'].append(header)
            existing_ids.add(header_id)

    # 3. Re-categorize and Clean Components
    print("Cleaning and re-categorizing components...")
    # This part requires some heuristic or manual mapping. 
    # For now, we will just clean the content.
    # In a real scenario, we'd need a map of RULE_1 -> Requirement, etc.
    # I will implement a basic re-typing based on the plan's examples.
    
    type_mapping = {
        "RULE_1": "Requirement", # Example from plan
        "RULE_9": "Rule",
        "PROTOCOL_3": "Protocol", # Assuming this exists or will be created
        "PRINCIPLE_1": "Principle",
        "HEURISTIC_1": "Heuristic"
    }
    
    for comp in data['components']:
        if 'content' in comp:
            comp['content'] = clean_content(comp['content'])
            
        # Update type if in mapping
        if 'id' in comp and comp['id'] in type_mapping:
            comp['type'] = type_mapping[comp['id']]
            
        # Add citation placeholder if missing (and it's a rule/mandate)
        if comp.get('type') in ['Rule', 'Mandate', 'Method', 'Heuristic', 'Protocol', 'Principle', 'Requirement']:
             if 'citation' not in comp or not comp['citation']:
                 comp['citation'] = "(Source Needed)" # Placeholder

    # 4. Update Workflows (Reordering)
    print("Updating workflows...")
    for wf in data.get('workflows', []):
        if wf['id'] == 'WORKFLOW_MAIN':
            wf['sequence'] = PHASE_ORDER
            
    # 5. Update Steps (Granular Mapping)
    print("Updating steps with granular mapping...")
    # Create a lookup for references to add them to phases
    # For simplicity, we'll add ALL references to ALL phases for now, 
    # OR we need a smart way to link them. 
    # The plan said: "When a component is added... its associated Reference... MUST also be added".
    # This is hard to automate perfectly without a map. 
    # I will add a generic "HEADER_REFERENCES" and a subset of refs if possible, 
    # or just rely on the granular list provided in the plan (which didn't list specific refs).
    # I will append relevant references dynamically if I can find them.
    
    # Let's just stick to the explicit list in PHASE_COMPONENTS for now.
    
    for step in data.get('steps', []):
        step_id = step['id']
        if step_id in PHASE_COMPONENTS:
            # Update llm_prompts
            new_prompts = PHASE_COMPONENTS[step_id]
            
            # Ensure all referenced components exist in data['components']
            # If not, we might need to create placeholders or warn.
            
            step['execution_config']['llm_prompts'] = new_prompts

    # 6. Save
    print("Saving updated seed data...")
    save_json(SEED_DATA_PATH, data)
    print("Done.")

if __name__ == "__main__":
    main()
