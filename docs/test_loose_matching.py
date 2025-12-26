import json
from tinydb import TinyDB, Query
import re

# 1. Simulate the Final Product Text (from User's Dump step_coach/step_analyst)
# "Ekologinen resilienssikriisi", "Geoteknologinen valtaistelu", "Supermegatrendit", "Sitra"
SIMULATED_TEXT = """
Kriittinen Analyysi Sitran Megatrendien Evoluutiosta (2017 - 2023): Supermegatrendit Postnormaalissa Ajassa.
Raportti sisältää analyysin Ekologisesta resilienssikriisistä, Geoteknologisesta valtaistelusta 
ja Epävarmuuden sosiaalisesta polarisaatiosta sekä strategiset toimenpide-ehdotukset.
Kaupallinen johtoryhmä. Strategia. Prompt engineering.
"""

def analyze_loose_matches():
    db_path = r'c:\Users\risto\OneDrive\quorum\data\db.json'
    db = TinyDB(db_path)
    kb = db.table('knowledge_base')
    items = kb.all()
    
    concepts = {i['term'].lower(): i for i in items if i.get('type') == 'concept'}
    references = {i['term'].lower(): i for i in items if i.get('type') == 'reference'} # term is matching key usually

    print(f"Loaded {len(concepts)} concepts and {len(references)} references.")
    print("-" * 40)

    # 1. Search for Concepts in Text
    found_concepts = []
    print("Scanning text for KONCEPTS (Content Match)...")
    for term, item in concepts.items():
        # Concept term matching (len > 3 to avoid noise)
        if len(term) > 3 and term in SIMULATED_TEXT.lower():
            definition = item.get('definition', '')
            # Extract citations from definition if possible
            citations = extract_citations_from_def(definition)
            found_concepts.append({
                "term": item['term'],
                "match_in_text": term,
                "linked_citations": citations
            })

    # 2. Results
    if found_concepts:
        print(f"\n[SUCCESS] Found {len(found_concepts)} semantic matches via Concepts:")
        for fc in found_concepts:
            print(f"  - Concept: '{fc['term']}' found in text.")
            if fc['linked_citations']:
                print(f"    -> POTENTIAL SOURCE LINK: {fc['linked_citations']}")
            else:
                print(f"    -> (No direct citation in concept definition, but concept matches)")
    else:
        print("\n[FAIL] No existing Concepts found in text.")

    # 3. Check specific keywords based on user session
    keywords = ["resilienssi", "strategia", "sitra", "megatrendit"]
    print("\nChecking specifically for keywords in DB:")
    for kw in keywords:
        in_text = kw in SIMULATED_TEXT.lower()
        in_db_concept = kw in concepts
        print(f"  - '{kw}': In Text? {in_text} | In DB? {in_db_concept}")

def extract_citations_from_def(text):
    # Simple regex for (Author Year)
    import re
    # Matches (Name 2020)
    return re.findall(r'\([A-Za-z\s]+ \d{4}\)', text)

if __name__ == "__main__":
    analyze_loose_matches()
