import json
import re
from pathlib import Path

def clean_text(text: str) -> str:
    # Protect {{SCHEMA_EXAMPLE}} by splitting
    parts = text.split("{{SCHEMA_EXAMPLE}}")
    cleaned_parts = []
    
    for part in parts:
        # Remove Markdown formats
        part = re.sub(r'\*\*', '', part)          # bold
        part = re.sub(r'###\s*', '', part)        # headers
        part = re.sub(r'>\s*', '', part)          # blockquotes
        part = re.sub(r'(?<!\S)\*\s*', '', part)  # bullet points asterisks
        
        # Remove static chapter/section headers e.g. "OSA4:", "Luku 2.3.5:", "Menetelmä 1:"
        part = re.sub(r'(?i)\b(?:OSA|LUKU|MENETELMÄ|VAIHE)\s*\d+(?:\.\d+)*\s*:', '', part)
        
        # Replace newlines, carriage returns, and tabs with a single space
        part = re.sub(r'[\n\r\t]+', ' ', part)
        
        # Remove excessive spaces
        part = re.sub(r'\s{2,}', ' ', part)
        
        cleaned_parts.append(part.strip())
        
    # Re-join with exact SCHEMA_EXAMPLE placeholder, with newlines to ensure it parses correctly downstream
    # if there are multiple parts.
    return "\n{{SCHEMA_EXAMPLE}}\n".join(cleaned_parts).strip()


def run_cleanup():
    seed_path = Path('c:/src/quorum/backend_v2/seed/seed_data.json')
    with open(seed_path, encoding='utf-8') as f:
        data = json.load(f)

    changed_count = 0
    
    for pb in data.get('prompt_blocks', []):
        desc_node = pb.get('description', {}).get('translations', {})
        for lang, text in desc_node.items():
            if isinstance(text, str):
                new_text = clean_text(text)
                if new_text != text:
                    desc_node[lang] = new_text
                    changed_count += 1
                    print(f"Cleaned block: {pb.get('id')} ({lang})")

    with open(seed_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nSuccessfully cleaned {changed_count} prompt block translations.")

if __name__ == "__main__":
    run_cleanup()
