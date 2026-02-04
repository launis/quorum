
import json

DB_PATH = "c:/src/quorum/data/db.json"

OLD_CONTENT = "KÄSKE: Poista kaikki PII-data (Nimet, Email)."
NEW_CONTENT = "TARKISTA: Etsi tekstistä PII-dataa (Nimet, Email). JOS JA VAIN JOS löydät sitä, poista se ja kirjaa raporttiin. Jos dataa ei löydy, kirjaa 'Ei havaittu' ja jatka."

def patch_db():
    print(f"Reading {DB_PATH}...")
    try:
        with open(DB_PATH, encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Failed to read file: {e}")
        return

    # Check for presence
    # simplistic check, might need to handle unicode escapes if text read didn't handle them (it won't unescape them)
    # If the file has \u00c4, reading as text keeps \u00c4 unless we decodes.
    # Let's try to match both forms.

    old_unicode = OLD_CONTENT.replace("Ä", "\\u00c4").replace("ä", "\\u00e4").replace("Ö", "\\u00d6").replace("ö", "\\u00f6")
    # Simple replace doesn't cover all chars but handles the Ä in KÄSKE

    # "K\u00c4SKE"
    old_target_1 = "K\\u00c4SKE: Poista kaikki PII-data (Nimet, Email)."
    old_target_2 = "KÄSKE: Poista kaikki PII-data (Nimet, Email)."

    count_1 = content.count(old_target_1)
    count_2 = content.count(old_target_2)

    print(f"Found {count_1} occurrences of escaped format.")
    print(f"Found {count_2} occurrences of raw UTF-8 format.")

    if count_1 == 0 and count_2 == 0:
        print("Target string not found!")
        # Debugging: print a snippet that SHOULD contain it if we knew where it was.
        # But we don't.
        return

    new_content_str = content

    # We replace with the Raw UTF-8 version mostly, or the escaped version if the file uses escaped.
    # To be safe, if we found escaped, we replace with escaped new content.

    # Prepare escaped new content just in case
    # This is rough, json.dumps avoids manual mapping
    new_content_escaped = json.dumps(NEW_CONTENT).strip('"')
    # Use ensure_ascii=True to get \u escapes
    new_content_escaped_ascii = json.dumps(NEW_CONTENT, ensure_ascii=True).strip('"')

    if count_1 > 0:
        print("Replacing escaped format...")
        # We need to be careful matching the exact escape sequence json.dumps produces vs what is in file.
        # simpler: just replace the specific substring we know.
        # The file has "K\u00c4SKE". Our new content "TARKISTA" might be "TARKISTA".
        # The new content has "tekstistä" -> "tekstist\u00e4"

        # Let's iterate manually or just use string replace for the specific old string.
        new_text = new_content_escaped_ascii
        # remove the quotes json.dumps adds

        if new_text.startswith('"') and new_text.endswith('"'):
             new_text = new_text[1:-1]

        # Fix: json.dumps escapes double quotes too, which we might not want if we are just replacing content text.
        # But here content is inside json string value, so escaped quotes are good?
        # The old string in file doesn't have quotes inside it.

        new_content_str = new_content_str.replace(old_target_1, new_text)

    if count_2 > 0:
        print("Replacing raw format...")
        new_content_str = new_content_str.replace(old_target_2, NEW_CONTENT)

    with open(DB_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content_str)

    print("Database patched successfully.")

if __name__ == "__main__":
    patch_db()
