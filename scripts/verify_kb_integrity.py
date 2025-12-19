
import json
import re

def verify_kb():
    try:
        with open(r'c:\Users\risto\OneDrive\quorum\backend\database\seed_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        kb = None
        for item in data.get('system_config', []):
            if item.get('id') == 'knowledge_base':
                kb = item
                break
        
        if not kb:
            print("Knowledge Base not found in seed_data.")
            return

        concepts = kb.get('concepts', {})
        references = kb.get('references', [])
        
        ref_map = {r['short_citation']: r for r in references}
        
        missing_links = []
        linked_count = 0
        total_concepts = len(concepts)
        
        print(f"Checking {total_concepts} concepts against {len(ref_map)} references...\n")
        
        for term, definition in concepts.items():
            # Extract content inside (vrt. ...) or just (...)
            # Pattern: (vrt. Citation Year) or (vrt. Name et al. Year)
            # Regex: \(vrt\. ([^)]+)\)
            match = re.search(r'\(vrt\. ([^)]+)\)', definition)
            if match:
                citation_key = match.group(1).strip()
                # Sometimes citation might be "Smith & Kendall 1963"
                # Check if this key exists in ref_map
                
                # Loose matching: try exact match first
                if citation_key in ref_map:
                    linked_count += 1
                else:
                    # Check if multiple citations? "vrt. A; B"
                    sub_keys = [k.strip() for k in citation_key.split(';')]
                    all_found = True
                    for sk in sub_keys:
                        if sk not in ref_map:
                            all_found = False
                            missing_links.append(f"Concept '{term}' points to '{sk}' which is missing.")
                    if all_found:
                        linked_count += 1
            else:
                 # Check if it has NO citation
                 missing_links.append(f"Concept '{term}' has no '(vrt. ...)' citation marker.")

        print(f"Linked: {linked_count}/{total_concepts}")
        if missing_links:
            print("\nIssues Found:")
            for issue in missing_links:
                print(f"- {issue}")
        else:
            print("\nAll concepts are successfully linked!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_kb()
