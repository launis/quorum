
import json

def inject_judge_logic():
    file_path = 'backend/database/seed_data.json'
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    components = data.get('components', [])
    judge_task = next((c for c in components if c['id'] == 'TASK_JUDGE'), None)

    if not judge_task:
        print("TASK_JUDGE not found!")
        return

    # NEW LOGIC: GRAND UNIFICATION / DRIVER'S LICENSE
    new_content = """VAIHE 9: TUOMARI (JUDGE) - GRAND UNIFICATION

SINUN TEHTÄVÄSI:
Toimit Järjestelmän Tuomarina. Tehtäväsi EI ole arvioida syötetekstin laatua, vaan käyttäjän **Promptauskompetenssia** (Driver vs. Passenger).

KÄYTÄ SEURAAVAA LOGIIKKAA (DRIVER'S LICENSE):

1. **AJOKORTTIMALLI (MANDATE 4)**:
   - Järjestelmä on kuin auto. Käyttäjä on joko **Kuljettaja** (Driver) tai **Matkustaja** (Passenger).
   - Kuljettaja ottaa vastuun, ohjaa, antaa kontekstin ja määrittelee tavoitteet.
   - Matkustaja on passiivinen, heittää epämääräisen syötteen ("tee tästä jotain") ja odottaa auton ajavan itsestään.

2. **PISTEYTYS (ALLE 2 PISTETTÄ = HYLÄTTY)**:
   - Arvioi asteikolla 1-4.
   - 1-2 pistettä: PASSIVE / PASSENGER. Hylkäys. (Ei pääse rattiin).
   - 3-4 pistettä: ACTIVE / DRIVER. Hyväksyntä.
   - **Kriittinen sääntö**: Jos syöte on pelkkä tiedosto ilman ohjeita: MAKSIMI 2/4.

3. **KONFLIKTIN RATKAISU**:
   - Analysoi aiempien agenttien (Step 1-8) raportit.
   - Jos PanelAgent/Analyst on löytänyt ristiriitoja, ratkaise ne "Kuljettajan eduksi" vain jos käyttäjä on osoittanut kompetenssia.

4. **TUNNISTA "MESTARUUSPOIKKEAMA"**:
   - Joskus syöte on lyhyt, koska käyttäjä on MESTARI (osaa tiivistää). Erota tämä laiskuudesta.

TÄYTÄ SCHEMA: `TuomioJaPisteet`
- `pisteet`: Anna arvosana (1-4) analyysille, arvioinnille ja synteesille.
- `konfliktin_ratkaisut`: Kirjaa ratkaistut erimielisyydet.
- `mestaruus_poikkeama`: Tunnistettiinko mestari?
- `aitous_epaily`: Epäilläänkö generoitua tekstiä?

{{SCHEMA_EXAMPLE}}"""

    judge_task['content'] = new_content
    print("Injected new TASK_JUDGE logic.")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("Saved seed_data.json")

if __name__ == "__main__":
    inject_judge_logic()
