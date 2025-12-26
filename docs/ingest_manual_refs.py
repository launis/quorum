from tinydb import TinyDB, Query
import uuid
import re

def extract_short_citation(full_entry):
    # Matches "Author, A. & Author, B. 2023:" or "Author. 2023:"
    # Pattern: Authors + Year + Colon/Dot
    match = re.match(r'^(.+?)\.\s*(\d{4}[a-z]?)[.:]', full_entry)
    if match:
        authors_part = match.group(1)
        year = match.group(2)
        
        # Cleanup "(toim.)"
        authors_part = re.sub(r'\s*\(.*?\)', '', authors_part)
        
        authors = []
        # Split by &
        parts = authors_part.split('&')
        for part in parts:
            # Split by comma or semicolon
            names = re.split(r'[,;]', part)
            surname = names[0].strip()
            if surname:
                authors.append(surname)
        
        # Take max 3 authors for short citation? Or just join all with &
        # Convention: "Author & Author 2023" or "Author et al. 2023" if many?
        # For simplicity, stick to "Author & Author 2023"
        
        short_authors = " & ".join(authors)
        if len(authors) > 2:
             short_authors = f"{authors[0]} ym."
             
        return f"{short_authors} {year}"
    
    # Fallback for organization names like "OWASP Foundation. 2025:"
    match_org = re.match(r'^(.+?)\.\s*(\d{4}[a-z]?)[.:]', full_entry)
    if match_org:
         return f"{match_org.group(1)} {match_org.group(2)}"
         
    return None

def ingest_manual_refs():
    p_source = r'c:\Users\risto\OneDrive\quorum\docs\manual_refs.txt'
    p_db = r'c:\Users\risto\OneDrive\quorum\data\db.json'
    
    with open(p_source, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    db = TinyDB(p_db)
    kb = db.table('knowledge_base')
    
    count = 0
    skipped = 0
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 10:
            continue
            
        # Basic check if it looks like a ref
        if not re.search(r'\d{4}', line):
            continue

        short_cit = extract_short_citation(line)
        
        # DOI
        doi_link = None
        doi_match = re.search(r'(10\.\d{4,9}/[-._;()/:A-Z0-9]+)', line, re.IGNORECASE)
        if doi_match:
            doi_link = f"https://doi.org/{doi_match.group(1)}"
            
        # Store
        # Check duplicate by citation text? or short citation?
        # Let's check duplicate by full text roughly
        existing = kb.search(Query().citation == line)
        if not existing:
             entry = {
                "id": str(uuid.uuid4()),
                "type": "reference",
                "citation": line,
                "short_citation": short_cit,
                "doi_link": doi_link,
                "metadata": {"source": "manual_paste_step1222"}
             }
             kb.insert(entry)
             count += 1
        else:
             skipped += 1
             
    print(f"Ingested {count} new references. Skipped {skipped} existing.")

if __name__ == "__main__":
    ingest_manual_refs()
