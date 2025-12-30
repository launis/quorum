import json
import os
import re
from typing import List, Dict, Set

def parse_bibliography(file_path: str) -> List[str]:
    """Reads bibliography.txt and returns a list of reference strings."""
    if not os.path.exists(file_path):
        print(f"Warning: {file_path} not found.")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        # Assume one reference per line (or separated by newlines)
        # We clean empty lines
        lines = [line.strip() for line in f.readlines() if line.strip()]
    return sorted(list(set(lines))) # Deduplicate and sort

def parse_concepts_from_text(file_paths: List[str]) -> Dict[str, str]:
    """
    Heuristic:
    1. Read text.
    2. Split into sentences.
    3. Identify sentences with Citations (parentheses + year).
    4. For each such sentence, identify potential 'Concepts' (Capitalized terms) in the SAME sentence.
    5. Map Concept -> Sentence (Definition).
    """
    concepts = {}
    citation_pattern = re.compile(r'\((?:vrt\.\s*)?(?:[A-Za-zÅÄÖåäö&,-]+\s+)+(?:et\s+al\.|ym\.)?\s*,?\s*\d{4}[a-z]?\)')
    
    # Simple simplistic tokenizer for potential concepts (Capitalized words, length > 3, not standard filler)
    # Exclude common sentence starters if we can (hard in Finnish without NLP)
    # We will assume if a term appears multiple times, it's a concept.
    
    ignore_terms = {"The", "This", "That", "There", "When", "What", "Tämä", "Se", "Kun", "Jos", "Mutta", "Vaikka", "Luku", "Kuva", "Table", "Taulukko"}
    
    for path in file_paths:
        if not os.path.exists(path):
            continue
            
        text = ""
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                with open(path, 'r', encoding=encoding) as f:
                    text = f.read()
                print(f"Successfully read {path} with encoding {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if not text:
            print(f"Failed to read {path} with any supported encoding.")
            continue
            
        # Split into sentences (naive)
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
        
        for sent in sentences:
            sent = sent.strip()
            # 1. Check for citation
            if citation_pattern.search(sent) or "19" in sent or "20" in sent: # Loose check for year if regex fails
                 if not citation_pattern.search(sent): continue # Strict regex check

                 # 2. Extract potential keys (Capitalized words)
                 words = re.findall(r'\b[A-ZÅÄÖ][a-zåäö]+\b', sent)
                 
                 for w in words:
                     if w in ignore_terms: continue
                     if len(w) < 4: continue
                     
                     # 3. Store match
                     # If concept exists, maybe append? Or overwrite? 
                     # Let's keep the LONGEST definition or First?
                     # Let's keep the one with the most citations?
                     
                     if w not in concepts:
                         concepts[w] = sent
                     else:
                         # Heuristic: Prefer definition that starts with the term?
                         if sent.startswith(w):
                             concepts[w] = sent
                             
    return concepts

def rebuild_kb():
    print("Starting Knowledge Base rebuild...")
    
    # 1. Parse Bibliography
    bib_path = os.path.join("data", "bibliography.txt")
    bibliography = parse_bibliography(bib_path)
    print(f"Loaded {len(bibliography)} references from {bib_path}")

    # 2. Parse Concepts from Source Texts
    source_files = [
        os.path.join("data", "Holistinen Mestaruus.txt"),
        os.path.join("data", "chapter2_source.txt")
    ]
    concepts = parse_concepts_from_text(source_files)
    print(f"Extracted {len(concepts)} concepts from source texts.")
    
    # Merge with manual overrides (optional or keep purely automatic?)
    # User said "concepts should be significantly larger", so automation is key.
    # We can keep the manual ones as high-quality seed.
    manual_concepts = {
         "Bloom": "Standardoidut testit ovat usein psykometrisesti luotettavia mutta sisällöllisesti kapea-alaisia (Wiggins 1998). Laadulliset menetelmät ovat puolestaan valideja, mutta kärsivät usein heikosta reliabiliteetista ja subjektiivisuudesta (Koretz ym. 1994). Tässä artikkelissa esitellään hybridirubriikki, uusi kaksitasoinen teoreettinen viitekehys, joka on suunniteltu hallitsemaan tätä jännitettä.",
        "Toulmin": "Tämä vaiheittainen malli on tietoinen arkkitehtuurivalinta, joka priorisoi maksimaalista auditoitavuutta ja jäljitettävyyttä tehokkuuden kustannuksella. Analyytikko-agentti ankkuroi väitteet, Loogikko-agentti purkaa argumentin Toulminin mallilla (Väite, Perusteet, Oikeutus), ja Kriitikkoryhmä falsifioi sen.",
        "BARS": "Tämä metodologinen valinta sisältää kuitenkin tietoisesti hyväksyttyjä rajoitteita. BARS-menetelmiä (Behaviorally Anchored Rating Scales) on perinteisesti kehitetty parantamaan luotettavuutta ankkuroimalla arviointitasot konkreettisiin kuvauksiin (Smith & Kendall 1963). Kognitiivinen Arviointimatriisi on 4-portainen BARS-asteikko.",
        "Hybrid Rubric": "Hybridirubriikki on uusi arviointiviitekehys, joka hallitsee reliabiliteetin ja validiteetin paradoksia (Borsboom ym. 2004) kaksitasoisella arkkitehtuurilla. Analyyttinen taso (BARS) maksimoi reliabiliteetin, ja holistinen taso (Kognitiivinen Kvoorum) maksimoi pätevyyden tunnistamalla sääntöjä ylittävän mestaruuden.",
        "Performative Reflection": "Perustavanlaatuinen uhka on Goodhartin laki (Strathern 1997), jonka mukaisesti käyttäjät voivat oppia manipuloimaan järjestelmää. Tämä ilmenee ’performatiivisena reflektiona’, jossa käyttäjä tuottaa vakuuttavan mutta epäaidon narratiivin (vrt. Goffman 1959; Cullen 2020)."
    }
    
    # Merge: Manual overwrites automatic
    concepts.update(manual_concepts)

    # 3. Construct Final JSON
    data = {
        "concepts": concepts,
        "references": {
            "bibliography": bibliography
        }
    }

    # 4. Save
    output_path = os.path.join("data", "coach_resources.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Successfully rebuilt {output_path} with {len(concepts)} concepts and {len(bibliography)} references.")

if __name__ == "__main__":
    rebuild_kb()
