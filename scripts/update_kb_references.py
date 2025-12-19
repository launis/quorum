
import json
import re
import difflib
import sys

seed_path = r'c:\Users\risto\OneDrive\quorum\backend\database\seed_data.json'
refs_path = r'c:\Users\risto\OneDrive\quorum\data\parsed_references.json'

def normalize(s):
    return s.lower().replace('&', '').replace(',', '').replace('.', '')

try:
    with open(seed_path, 'r', encoding='utf-8') as f:
        seed = json.load(f)
    
    with open(refs_path, 'r', encoding='utf-8') as f:
        new_refs = json.load(f)

    # 1. Update references
    # Keep "Holistinen Mestaruus" if not in list, as a fallback for document-specific concepts
    holistinen_ref = {
        "citation": "Holistinen Mestaruus. (2025). Lähdeaineisto. Quorum.",
        "short_citation": "Holistinen Mestaruus 2025",
        "link": ""
    }
    # Check if it's already there? Unlikely.
    new_refs.append(holistinen_ref)

    # Find knowledge_base in system_config
    if 'system_config' in seed:
        kb_config = None
        for item in seed['system_config']:
            if item.get('id') == 'knowledge_base':
                kb_config = item
                break
        
        if not kb_config:
            print("Error: 'knowledge_base' item not found in 'system_config'")
            sys.exit(1)
            
        kb_config['references'] = new_refs
        
        # Access concepts from the found config
        concepts = kb_config.get('concepts', {})
    else:
        # Fallback for old structure or error
        print(f"Error: 'system_config' not found. Keys: {list(seed.keys())}")
        sys.exit(1)

    # Map short citations for lookup
    ref_map = {r['short_citation']: r for r in new_refs}
    # Also create a lookup by author names for fuzzy matching
    author_map = {}
    for r in new_refs:
        short = r['short_citation']
        parts = short.split()
        if parts and parts[-1].isdigit():
            author_key = " ".join(parts[:-1])
        else:
            author_key = short
        
        norm_key = normalize(author_key)
        author_map[norm_key] = short
        first_word = normalize(parts[0])
        if first_word not in author_map: 
             author_map[first_word] = short

    # 2. Update Concepts
    updated_concepts = {}
    
    for term, definition in concepts.items():
        # Extract current marker (vrt. X)
        match = re.search(r'\(vrt\. ([^)]+)\)', definition)
        new_def = definition
        
        if match:
            current_cit = match.group(1).strip()
            # Try exact match
            if current_cit in ref_map:
                final_cit = current_cit
            else:
                # Fuzzy match / Heuristic
                norm_cit = normalize(current_cit.split('19')[0].split('20')[0].strip()) # remove year
                
                if norm_cit in author_map:
                    final_cit = author_map[norm_cit]
                else:
                    matches = difflib.get_close_matches(norm_cit, author_map.keys(), n=1, cutoff=0.6)
                    if matches:
                        final_cit = author_map[matches[0]]
                    else:
                        if "Holistinen" in current_cit:
                             final_cit = "Holistinen Mestaruus 2025"
                        elif "OWASP" in current_cit:
                             found_owasp = None
                             for sc in ref_map.keys():
                                 if "OWASP" in sc:
                                     llm_code_match = re.search(r'LLM\d+', sc)
                                     current_llm_code_match = re.search(r'LLM\d+', current_cit)
                                     if llm_code_match and current_llm_code_match:
                                         if llm_code_match.group(0) == current_llm_code_match.group(0):
                                             found_owasp = sc
                                             break
                             
                             if found_owasp:
                                 final_cit = found_owasp
                             else:
                                 final_cit = "Holistinen Mestaruus 2025"
                        else:
                             print(f"Warning: Could not map '{current_cit}' for concept '{term}'. Defaulting to Holistinen.")
                             final_cit = "Holistinen Mestaruus 2025"
            
            # Replace in definition
            base_def = re.sub(r'\s*\(vrt\. [^)]+\)', '', definition).strip()
            new_def = f"{base_def} (vrt. {final_cit})"
            
        else:
            new_def = f"{definition.strip()} (vrt. Holistinen Mestaruus 2025)"
            
        updated_concepts[term] = new_def

    kb_config['concepts'] = updated_concepts

    with open(seed_path, 'w', encoding='utf-8') as f:
        json.dump(seed, f, indent=4, ensure_ascii=False)
        
    print("Successfully updated seed_data.json with strict references.")

except Exception as e:
    print(f"Error: {e}")
