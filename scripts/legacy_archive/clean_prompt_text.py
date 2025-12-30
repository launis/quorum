import json
import re

SEED_FILE = r"c:\Users\risto\OneDrive\quorum\data\seed_data.json"

def clean_text(text):
    if not isinstance(text, str):
        return text
    
    # 1. Remove "Perustuu:" lines (bullet points)
    # Pattern: ●\tPerustuu:.* or ● Perustuu:.*
    text = re.sub(r'●\s*Perustuu:.*', '', text)
    
    # 2. Remove "VIITE (...):" lines
    text = re.sub(r'VIITE\s*\(.*?\):.*', '', text)
    
    # 3. Remove academic citations in parentheses, e.g., (Kahneman 2011), (vrt. Ye ym. 2025)
    # We need to be careful not to remove (Agentti: ...) or (VAIHE X)
    # Strategy: Look for (Name et al. Year) or (Name Year) patterns.
    # Regex: \([A-Za-zäöåÄÖÅ&,.\s]+ \d{4}[a-z]?\)
    # Also handles "vrt." prefix.
    text = re.sub(r'\((?:vrt\.\s*)?[A-Za-zäöåÄÖÅ&,.\s]+ \d{4}[a-z]?(?:;.*?)?\)', '', text)
    
    # 4. Remove "extracted from Chapter X" from descriptions (usually not in content, but good to clean)
    text = re.sub(r' extracted from Chapter \d+', '', text)

    # 5. Clean up double spaces and trailing newlines
    text = re.sub(r'\n{3,}', '\n\n', text) # Max 2 newlines
    text = text.strip()
    
    return text

def clean_seed_data():
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    count = 0
    for comp in data['components']:
        original_content = comp.get('content', '')
        original_desc = comp.get('description', '')
        
        if original_content:
            new_content = clean_text(original_content)
            if new_content != original_content:
                comp['content'] = new_content
                count += 1
        
        if original_desc:
            new_desc = clean_text(original_desc)
            if new_desc != original_desc:
                comp['description'] = new_desc
                # count += 1 # Don't count description only changes as major content updates
    
    with open(SEED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Cleaned {count} components.")

if __name__ == "__main__":
    clean_seed_data()
