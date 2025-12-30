import json

SEED_FILE = r"c:\Users\risto\OneDrive\quorum\data\seed_data.json"

NEW_CONTENT = """SÄÄNTÖ 5 (Strukturoitu Tuotos):
Agentin on tuotettava vastauksensa TÄSMÄLLEEN pyydetyssä formaatissa (JSON).
- Älä lisää ylimääräistä tekstiä, markdown-muotoilua (kuten ```json) tai selityksiä JSON-objektin ulkopuolelle.
- Varmista, että JSON on validi ja sisältää kaikki vaaditut kentät.
- Noudata annettua skeemaa orjallisesti."""

def update_rule():
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    comp = next((c for c in data['components'] if c['id'] == 'rule_structured_output'), None)
    if comp:
        comp['content'] = NEW_CONTENT
        print("Updated rule_structured_output content.")
    else:
        print("rule_structured_output not found!")

    with open(SEED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Done.")

if __name__ == "__main__":
    update_rule()
