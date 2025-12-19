from tinydb import TinyDB, Query
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Use the path from the user logs confirming REAL DB location
DB_PATH = r"C:\Users\risto\OneDrive\quorum\data\db.json"

def patch_db():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: DB not found at {DB_PATH}")
        return

    print(f"Opening DB at {DB_PATH}...")
    db = TinyDB(DB_PATH)
    components = db.table('components')
    Q = Query()
    
    comp_id = "instruction_analyst"
    # Content must match the update in seed_data.json
    new_content = "### ROOLI: ANALYYTIKKO (ANALYST AGENT) ###\nTehtäväsi on luoda 'Todistuskartta' (Evidence Map) ankkuroimalla väitteet suoraan lähdetekstiin.\nTAVOITTEET:\n1. Pura syöte KESKEISIMMIKSI väitteiksi (MAX 15 tärkeintä).\n2. Etsi jokaiselle väitteelle suora lainaus (sitaatti) lähdemateriaalista.\n3. Tunnista keskeiset teemat ja niiden väliset yhteydet.\n4. MÄÄRITÄ HAKUSANAT LUOTETTAVUUDEN TARKISTUKSEEN:\n   - Jos väite on ULKOINEN FAKTA (esim. \"Suomi itsenäistyi 1917\", \"Toulminin malli\", \"J.K. Rowling sanoi\"), kirjaa kenttään 'hakusana_ehdotus' tarkka hakulauseke.\n   - Jos väite on SISÄINEN HAVAINTO (esim. \"Opiskelija pohtii\", \"Teksti on hyvin jäsennelty\"), jätä 'hakusana_ehdotus' TYHJÄKSI (null).\nKRIITTISET SÄÄNNÖT:\n- Jokaisella havainnolla on oltava viite (line reference/quote)."
    
    # Check if exists
    items = components.search(Q.id == comp_id)
    if not items:
        print(f"Component {comp_id} not found!")
        return

    print(f"Found {len(items)} items for {comp_id}. Updating...")
    components.update({'content': new_content}, Q.id == comp_id)
    print(f"Updated {comp_id} successfully.")

if __name__ == "__main__":
    try:
        patch_db()
    except Exception as e:
        print(f"Failed: {e}")
