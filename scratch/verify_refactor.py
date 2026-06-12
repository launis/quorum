import json
import textwrap

try:
    with open(r'c:\src\quorum\backend_v2\seed\seed_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    all_descriptions = []
    
    def gather_descriptions(d):
        if isinstance(d, dict):
            if 'concept_description' in d and isinstance(d['concept_description'], str):
                all_descriptions.append({
                    'desc': d['concept_description'],
                    'anti_patterns': d.get('anti_patterns', [])
                })
            for k, v in d.items():
                gather_descriptions(v)
        elif isinstance(d, list):
            for item in d:
                gather_descriptions(item)
                
    gather_descriptions(data)
    
    issues = []
    for i, item in enumerate(all_descriptions):
        desc = item['desc']
        if '<disambiguation>' in desc or '</disambiguation>' in desc:
            issues.append(f"Issue in index {i}: <disambiguation> tag still present!")
        if '<syntactic_constraint>' in desc or '</syntactic_constraint>' in desc:
            issues.append(f"Issue in index {i}: <syntactic_constraint> tag still present!")
            
    print(f"Total concept_descriptions checked: {len(all_descriptions)}")
    print(f"Total legacy tag issues found: {len(issues)}")
    
    for issue in issues:
        print(issue)
        
    print("\n--- SANITY CHECK: Last 3 refactored items ---")
    # Find ones with anti_patterns we added
    refactored = [i for i in all_descriptions if any('rejection criteria' in ap.get('pattern', '') or 'stylistic reframing' in ap.get('pattern', '') for ap in i['anti_patterns'])]
    
    for i, item in enumerate(refactored[-3:]): # last 3 from the end
        print(f"\nExample {i+1}:")
        print("DESC:", textwrap.shorten(item['desc'], width=150))
        print("ANTI_PATTERNS:", json.dumps(item['anti_patterns'], indent=2))

except Exception as e:
    print(f"Error: {e}")
