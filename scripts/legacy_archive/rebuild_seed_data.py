import json
import re
import os
from typing import List, Dict, Any

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CHAPTER2_FILE = os.path.join(DATA_DIR, 'chapter2_source.txt')
BIBLIOGRAPHY_FILE = os.path.join(DATA_DIR, 'bibliography_source.txt')
OUTPUT_FILE = os.path.join(DATA_DIR, 'seed_data.json')

def load_text(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def parse_bibliography(text: str) -> Dict[str, str]:
    """Parses bibliography text into a dictionary of {short_citation: full_entry}."""
    refs = {}
    # Split by newline, assuming each entry starts on a new line
    # This is a simplification; robust parsing might need regex for "Author. Year:" pattern
    lines = text.strip().split('\n')
    current_entry = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line starts with a likely author pattern (Name, I. or Name, I. & Name, I.)
        # and contains a year like "2023:" or "2023."
        if re.match(r'^[A-Z][a-zA-Z\-]+,', line) and re.search(r'\d{4}[a-z]?[.:]', line):
            if current_entry:
                # Process previous entry to extract short citation
                short_cit = extract_short_citation(current_entry)
                if short_cit:
                    refs[short_cit] = current_entry
            current_entry = line
        else:
            # Continuation of previous entry
            current_entry += " " + line
            
    # Process last entry
    if current_entry:
        short_cit = extract_short_citation(current_entry)
        if short_cit:
            refs[short_cit] = current_entry
            
    return refs

def extract_short_citation(full_entry: str) -> str:
    """Extracts 'Author Year' or 'Author & Author Year' from full entry."""
    # Pattern: Start of string, capture names until year
    # Example: "Acemoglu, Daron & Restrepo, Pascual. 2018:" -> "Acemoglu & Restrepo 2018"
    # Example: "AERA, APA & NCME. 2014:" -> "AERA, APA & NCME 2014"
    
    match = re.match(r'^(.+?)\.\s*(\d{4}[a-z]?)[.:]', full_entry)
    if match:
        authors_part = match.group(1)
        year = match.group(2)
        
        # Simplify authors
        # "Acemoglu, Daron & Restrepo, Pascual" -> "Acemoglu & Restrepo"
        # "Anderson, Lorin W. & Krathwohl, David R. (toim.)" -> "Anderson & Krathwohl"
        
        # Remove (toim.) etc
        authors_part = re.sub(r'\s*\(.*?\)', '', authors_part)
        
        authors = []
        # Split by & first
        parts = authors_part.split('&')
        for part in parts:
            # Split by comma to get surname
            names = part.strip().split(',')
            surname = names[0].strip()
            authors.append(surname)
            
        short_authors = " & ".join(authors)
        return f"{short_authors} {year}"
    return None

def find_citation_in_text(text: str, bibliography: Dict[str, str]) -> Dict[str, str]:
    """Finds a citation in the text and returns {short: full}."""
    # This is a heuristic. We look for (Author Year) patterns in the text
    # and try to match them with bibliography keys.
    
    # Normalize text citations: (Smith 2020) -> Smith 2020
    # Also handle: (Smith 2020; Jones 2021)
    
    found_citations = {}
    
    # Regex for (Name... Year)
    # Matches: (Smith 2020), (Smith & Jones 2020), (Smith ym. 2020)
    citation_matches = re.findall(r'\(([^)]+\d{4}[a-z]?)\)', text)
    
    for match in citation_matches:
        # Split multiple citations separated by ;
        sub_citations = match.split(';')
        for sub in sub_citations:
            sub = sub.strip()
            # Try to match with bibliography keys
            # Exact match?
            if sub in bibliography:
                return {'citation': sub, 'citation_full': bibliography[sub]}
            
            # Fuzzy match?
            # "Smith ym. 2020" vs "Smith, John ym. 2020" in bib key?
            # Or "Smith et al. 2020"
            
            # Let's try to find the best matching key in bibliography
            # Key format in bib: "Surname & Surname 2020"
            # Text format: "Surname ym. 2020"
            
            # Extract year
            year_match = re.search(r'\d{4}[a-z]?', sub)
            if not year_match:
                continue
            year = year_match.group(0)
            
            # Extract first surname
            surname = sub.split()[0].replace(',', '')
            
            for bib_key, bib_full in bibliography.items():
                if year in bib_key and surname in bib_key:
                    return {'citation': bib_key, 'citation_full': bib_full}
                    
    return {'citation': "", 'citation_full': ""}

def clean_content(content: str) -> str:
    """Remove internal document references like (ks. Luku X.X)."""
    # Patterns: (ks. Luku X.X), (ks. Luku X), (vrt. Luku X.X)
    return re.sub(r'\s*\((?:ks\.|vrt\.)\s*Luku\s*[\d\.]+\)', '', content).strip()


def parse_components(text: str, bibliography: Dict[str, str]) -> List[Dict[str, Any]]:
    components = []
    
    # Define patterns for component types
    # Format in text: "Mandaatti 1 (Nimi): Kuvaus..." or just "Mandaatti 1: Kuvaus..."
    # We need to capture the type, number, name (optional), and content.
    
    # Map Finnish types to English IDs
    type_map = {
        'Menetelmä': 'method',
        'Sääntö': 'rule',
        'Heuristiikka': 'heuristic',
        'Protokolla': 'protocol',
        'Mandaatti': 'mandate',
        'Periaate': 'principle',
        'Vaatimus': 'requirement'
    }
    
    # Regex to find these blocks. 
    # We assume they start with the Keyword and are followed by a number or name, then content.
    # They end at the next component or section header.
    
    # Strategy: Split text by these keywords to find chunks, then parse each chunk.
    # But keywords appear in normal text too. We look for "Keyword X" or "Keyword X (Name)" at start of lines or sentences.
    
    # Let's iterate through the text looking for specific patterns
    
    lines = text.split('\n')
    current_component = None
    buffer = []
    
    # Regex for component start: e.g., "Mandaatti 1 (Erimielisyyden...):"
    # Relaxed pattern: Allow start of line OR preceded by newline/space
    # Also handle cases where there is no number, or name is different format
    start_pattern = re.compile(r'(?:^|\n)\s*(Menetelmä|Sääntö|Heuristiikka|Protokolla|Mandaatti|Periaate|Vaatimus)\s+(\d+)?\s*(?:\(([^)]+)\))?[:.]\s*(.*)')
    
    # Also handle "Sääntö 1: ..." without parens
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        match = start_pattern.match(line)
        if match:
            print(f"DEBUG: Found match: {match.groups()}")
            # Save previous component if exists
            if current_component:
                raw_content = " ".join(buffer)
                current_component['content'] = clean_content(raw_content)
                # Find citation in content
                cit = find_citation_in_text(current_component['content'], bibliography)
                current_component.update(cit)
                components.append(current_component)
                buffer = []
                current_component = None
            
            # Start new component
            c_type_fi = match.group(1)
            c_num = match.group(2) or "1" # Default to 1 if not numbered (e.g. Periaate 1)
            c_name = match.group(3) or ""
            c_content_start = match.group(4)
            
            c_id = f"{type_map[c_type_fi]}_{c_num}"
            print(f"DEBUG: Creating component {c_id}")
            
            # If name is empty, try to extract from content start if it looks like a title
            # But usually "Sääntö 1: Luottamuksen Kehä" -> Name is Luottamuksen Kehä
            if not c_name and c_content_start:
                # Check if content start is short and looks like a title
                # e.g. "Luottamuksen Kehä, vain vartijan..."
                # Split by comma or dot
                parts = re.split(r'[,.]', c_content_start, 1)
                if len(parts) > 1 and len(parts[0]) < 50:
                     c_name = parts[0].strip()
            
            current_component = {
                "id": c_id,
                "type": type_map[c_type_fi],
                "name": c_name if c_name else f"{c_type_fi} {c_num}",
                "description": f"{c_type_fi} {c_num} extracted from Chapter 2",
            }
            buffer.append(c_content_start)
        else:
            # print(f"DEBUG: No match for line: {line[:20]}...")
            if current_component:
                # Check if line is a new section header (e.g. "2.4.3 ...")
                if re.match(r'^\d+\.\d+', line):
                     # End current component
                    raw_content = " ".join(buffer)
                    current_component['content'] = clean_content(raw_content)
                    cit = find_citation_in_text(current_component['content'], bibliography)
                    current_component.update(cit)
                    components.append(current_component)
                    buffer = []
                    current_component = None
                else:
                    buffer.append(line)
                    
    # Save last component
    if current_component:
        raw_content = " ".join(buffer)
        current_component['content'] = clean_content(raw_content)
        cit = find_citation_in_text(current_component['content'], bibliography)
        current_component.update(cit)
        components.append(current_component)

    # Add Headers
    headers = []
    for fi_type, en_type in type_map.items():
        headers.append({
            "id": f"HEADER_{en_type}s", # Plural ID
            "type": "header",
            "name": f"HEADER_{en_type.upper()}S",
            "content": f"Seuraavat ovat {fi_type.lower()}t, joita sinun tulee noudattaa tarkasti.",
            "description": f"Header for {en_type}s",
            "citation": "",
            "citation_full": ""
        })
    
    return headers + components

def create_steps(bibliography: Dict[str, str]) -> List[Dict[str, Any]]:
    # Define steps based on Chapter 2.3
    # We manually construct these to ensure high quality and correct mapping
    
    steps = [
        {
            "id": "step_1",
            "name": "Vartija (Guard)",
            "description": "Esikäsittely ja Turvaportti. Rakenteellinen puhdistus, normalisointi, anonymisointi ja uhkien luokittelu.",
            "citation": "OWASP Foundation 2025f", # Example
            "citation_full": bibliography.get("OWASP Foundation 2025f", ""),
            "component": "GuardAgent",
            "execution_config": {
                "llm_prompts": ["HEADER_rules", "rule_1", "HEADER_protocols", "protocol_1", "protocol_2"],
                "pre_hooks": ["sanitize_and_anonymize_input"]
            },
            "output_schema": "TaintedData"
        },
        {
            "id": "step_2",
            "name": "Analyytikko (Analyst)",
            "description": "Todistepohjainen Ankkurointi. Luo todistuskartan ja ankkuroi analyysin todistusaineistoon.",
            "citation": "Lewis ym. 2020",
            "citation_full": bibliography.get("Lewis ym. 2020", ""),
            "component": "AnalystAgent",
            "execution_config": {
                "llm_prompts": ["HEADER_rules", "rule_1", "rule_3", "HEADER_mandates", "mandate_2", "mandate_3"]
            },
            "output_schema": "TodistusKartta"
        },
        {
            "id": "step_3",
            "name": "Loogikko (Logician)",
            "description": "Argumentaation Rakentaminen. Muodostaa hypoteesin osaamistasosta (Bloom) ja jäsentää argumentin (Toulmin).",
            "citation": "Toulmin 2003",
            "citation_full": bibliography.get("Toulmin 2003", ""),
            "component": "LogicianAgent",
            "execution_config": {
                "llm_prompts": ["HEADER_rules", "rule_1", "rule_3", "HEADER_mandates", "mandate_2", "mandate_3"]
            },
            "output_schema": "ArgumentaatioAnalyysi"
        },
        {
            "id": "step_4",
            "name": "Looginen Falsifioija (Logical Falsifier)",
            "description": "Argumentaation Auditoija. Iskee argumentaation rakenteeseen ja ylläpitää erimielisyyttä.",
            "citation": "Popper 1934",
            "citation_full": bibliography.get("Popper 1934", ""),
            "component": "LogicalFalsifierAgent",
            "execution_config": {
                "llm_prompts": ["HEADER_principles", "principle_1", "HEADER_mandates", "mandate_1", "HEADER_rules", "rule_1"]
            },
            "output_schema": "LogiikkaAuditointi"
        },
        {
            "id": "step_5",
            "name": "Faktuaalinen ja Eettinen Valvoja (Factual Overseer)",
            "description": "Todisteiden Valvoja. Varmistaa väitteiden faktuaalisuuden ja eettisyyden (RFI-protokolla).",
            "citation": "Weidinger ym. 2021",
            "citation_full": bibliography.get("Weidinger ym. 2021", ""),
            "component": "FactualOverseerAgent",
            "execution_config": {
                "llm_prompts": ["HEADER_protocols", "protocol_3", "HEADER_requirements", "requirement_1", "HEADER_rules", "rule_1"],
                "pre_hooks": ["execute_google_search"]
            },
            "output_schema": "EtiikkaJaFakta"
        },
        {
            "id": "step_6",
            "name": "Kausaalinen Analyytikko (Causal Analyst)",
            "description": "Temporaalinen Auditoija. Auditoi kausaalista uskottavuutta ja aikajanaa.",
            "citation": "Pearl 2009",
            "citation_full": bibliography.get("Pearl 2009", ""),
            "component": "CausalAnalystAgent",
            "execution_config": {
                "llm_prompts": ["HEADER_heuristics", "heuristic_1", "heuristic_2", "heuristic_3", "HEADER_rules", "rule_1"]
            },
            "output_schema": "KausaalinenAuditointi"
        },
        {
            "id": "step_7",
            "name": "Performatiivisuuden Tunnistaja (Performativity Detector)",
            "description": "Käyttäytymisanalyytikko. Tunnistaa manipulointia ja performatiivisia narratiiveja.",
            "citation": "Stumborg ym. 2022",
            "citation_full": bibliography.get("Stumborg ym. 2022", ""),
            "component": "PerformativityDetectorAgent",
            "execution_config": {
                "llm_prompts": ["HEADER_mandates", "mandate_4", "HEADER_rules", "rule_4", "HEADER_rules", "rule_1"],
                "pre_hooks": ["detect_performative_patterns"]
            },
            "output_schema": "PerformatiivisuusAuditointi"
        },
        {
            "id": "step_8",
            "name": "Tuomari (Judge)",
            "description": "Synteesi ja Konfliktinratkaisu. Kokoaa tulokset ja ratkaisee konfliktit hierarkkisesti.",
            "citation": "Wynn, Satija & Hadfield 2025",
            "citation_full": bibliography.get("Wynn, Satija & Hadfield 2025", ""),
            "component": "JudgeAgent",
            "execution_config": {
                "llm_prompts": ["HEADER_rules", "rule_6", "HEADER_mandates", "mandate_1", "HEADER_rules", "rule_1"],
                "post_hooks": ["calculate_final_scores"]
            },
            "output_schema": "TuomioJaPisteet"
        },
        {
            "id": "step_9",
            "name": "XAI-Raportoija (XAI Reporter)",
            "description": "Raportointi. Laatii XAI-raportin ja tuo esiin epävarmuudet.",
            "citation": "Adadi & Berrada 2018",
            "citation_full": bibliography.get("Adadi & Berrada 2018", ""),
            "component": "XAIReporterAgent",
            "execution_config": {
                "llm_prompts": ["HEADER_methods", "method_3", "HEADER_rules", "rule_5", "HEADER_protocols", "protocol_4", "HEADER_rules", "rule_1"],
                "post_hooks": ["generate_jinja2_report"]
            },
            "output_schema": "XAIReport"
        }
    ]
    return steps

def main():
    print("Reading source files...")
    chapter2_text = load_text(CHAPTER2_FILE)
    bibliography_text = load_text(BIBLIOGRAPHY_FILE)
    
    print("Parsing bibliography...")
    bibliography = parse_bibliography(bibliography_text)
    print(f"Parsed {len(bibliography)} references.")
    
    print("Parsing components from Chapter 2...")
    components = parse_components(chapter2_text, bibliography)
    print(f"Parsed {len(components)} components.")
    
    print("Creating code components...")
    code_components = create_code_components()
    components.extend(code_components)
    
    print("Creating workflow steps...")
    steps = create_steps(bibliography)
    
    # Create Workflow definition
    workflow = {
        "id": "sequential_audit_chain",
        "name": "Sequential Audit Chain",
        "description": "9-step audit chain based on Chapter 2.3",
        "steps": [s['id'] for s in steps]
    }
    
    # Assemble final data
    seed_data = {
        "components": components,
        "steps": steps,
        "workflows": [workflow]
    }
    
    print(f"Writing to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(seed_data, f, indent=2, ensure_ascii=False)
        
    print("Done.")

def create_code_components() -> List[Dict[str, Any]]:
    return [
        {"name": "GuardAgent", "module": "backend.agents.guard", "class": "GuardAgent", "type": "agent"},
        {"name": "AnalystAgent", "module": "backend.agents.analyst", "class": "AnalystAgent", "type": "agent"},
        {"name": "LogicianAgent", "module": "backend.agents.logician", "class": "LogicianAgent", "type": "agent"},
        {"name": "LogicalFalsifierAgent", "module": "backend.agents.critics", "class": "LogicalFalsifierAgent", "type": "agent"},
        {"name": "FactualOverseerAgent", "module": "backend.agents.critics", "class": "FactualOverseerAgent", "type": "agent"},
        {"name": "CausalAnalystAgent", "module": "backend.agents.critics", "class": "CausalAnalystAgent", "type": "agent"},
        {"name": "PerformativityDetectorAgent", "module": "backend.agents.critics", "class": "PerformativityDetectorAgent", "type": "agent"},
        {"name": "JudgeAgent", "module": "backend.agents.judge", "class": "JudgeAgent", "type": "agent"},
        {"name": "XAIReporterAgent", "module": "backend.agents.judge", "class": "XAIReporterAgent", "type": "agent"}
    ]

if __name__ == "__main__":
    main()
