
import json
import re

file_path = r'c:\Users\risto\OneDrive\quorum\data\Holistinen Mestaruus.txt'
try:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Try to find start of bibliography
    markers = ["Lähdeluettelo", "Lähteet", "References"]
    bib_text = ""
    for m in markers:
        if m in content:
            bib_text = content.split(m)[-1] # Take the last split just in case
            break
            
    if not bib_text:
        # Fallback: take last 200 lines
        lines = content.split('\n')
        bib_text = '\n'.join(lines[-200:])

    # Regex to parse entries
    # Assumes format: Author(s). (Year). Title. ...
    # And tries to catch URLs
    
    entries = []
    # Split by double newlines or lines that look like start of a citation (Word, Word... (Year))
    # A simple line-by-line heuristic might be better if they are single spaced
    
    raw_lines = [l.strip() for l in bib_text.split('\n') if l.strip()]
    
    current_entry = ""
    parsed_entries = []
    
    for line in raw_lines:
        # Heuristic: Start of new entry usually starts with "Name, I." or "Name, Name" and contains a year in parens early on
        # Or just ends with a dot.
        # Let's simple accumulate lines until we hit a blank line? No, they are stripped.
        
        # Let's assume each line starting with a capital letter and having a year (YYYY) in the first 50 chars is a new entry
        if re.match(r'^[A-Z].+?\(?\d{4}\)?', line):
            if current_entry:
                parsed_entries.append(current_entry)
            current_entry = line
        else:
            current_entry += " " + line
            
    if current_entry:
        parsed_entries.append(current_entry)

    references = []
    for entry in parsed_entries:
        # Extract fields
        # Year regex: Look for (YYYY) OR . YYYY: OR . YYYY. 
        year_match = re.search(r'[\(\. ](\d{4})[\):\.]', entry)
        year = year_match.group(1) if year_match else "n.d."
        
        # Short citation: Author Year
        # Take first 2 words? Or Author name until comma?
        author_part = entry.split('20')[0].split('19')[0].strip() # Hacky split before year?
        if '(' in author_part:
             author_part = author_part.split('(')[0]
        
        authors = author_part.split(',')[0].strip() # Just first surname
        if "et al" in entry or "ym." in entry:
            short_citation = f"{authors} ym. {year}"
        elif "&" in author_part:
             # Try to handle "Adadi, A. & Berrada, M." -> "Adadi & Berrada"
             # simplified: just take the two surnames if possible
             parts = author_part.split('&')
             if len(parts) == 2:
                 a1 = parts[0].split(',')[0].strip()
                 a2 = parts[1].split(',')[0].strip()
                 short_citation = f"{a1} & {a2} {year}"
             else:
                 short_citation = f"{authors} {year}"
        else:
            short_citation = f"{authors} {year}"

        # Link logic: Prefer DOI, fallback to generic URL
        link = ""
        # Find explicit DOI first
        doi_match = re.search(r'DOI:?\s*([^\s]+)', entry, re.IGNORECASE)
        if doi_match:
            raw_doi = doi_match.group(1).rstrip('.')
            if raw_doi.startswith('http'):
                link = raw_doi
            else:
                link = f"https://doi.org/{raw_doi}"
        else:
            # Fallback to any http/https link
            url_match = re.search(r'(https?://[^\s]+)', entry)
            if url_match:
                link = url_match.group(1).rstrip('].').rstrip('.')

        references.append({
            "citation": entry,
            "short_citation": short_citation,
            "link": link
        })


    output_json_path = r'c:\Users\risto\OneDrive\quorum\data\parsed_references.json'
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(references, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(references)} references to {output_json_path}")

except Exception as e:
    print(f"Error: {e}")

