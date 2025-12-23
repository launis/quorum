import json
import os

DB_PATH = r"C:\Users\risto\OneDrive\quorum\data\db.json"

def update_db():
    print(f"Reading {DB_PATH}...")
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. JUDGE (TASK_JUDGE / ID 30) - Päivitetään kriteerit
    judge = data['components']['30']
    print("Updating TASK_JUDGE...")
    
    new_judge_content = judge['content'].replace(
        "- **Kriittinen sääntö**: Jos syöte on pelkkä tiedosto ilman ohjeita: MAKSIMI 2/4.",
        "- **Kriittinen sääntö**: Jos syöte on pelkkä tiedosto ilman ohjeita: MAKSIMI 2/4. **POIKKEUS:** Jos käyttäjä on toimittanut laajat Context Files -tiedostot (History/Product), se lasketaan VAHVAKSI OHJAUKSEKSI (Driver). Tällöin lyhyt prompti on sallittu."
    ).replace(
        "Käyttäjä on joko **Kuljettaja** (Driver) tai **Matkustaja** (Passenger).",
        "Käyttäjä on joko **Kuljettaja** (Driver) tai **Matkustaja** (Passenger). HUOM: Tiedostojen lataaminen on aktiivinen 'Driver'-teko (Grounding)."
    )
    judge['content'] = new_judge_content

    # 2. PROFILER (TASK_PROFILER / ID 23) - Poistetaan "Lazy Prompting" leima tiedostojen käyttäjiltä
    profiler = data['components']['23']
    print("Updating TASK_PROFILER...")
    
    new_profiler_content = profiler['content'].replace(
        "VAIHE 4: PROFILOIJA (Cognitive Bias Audit)\nTEHTÄVÄT:",
        "VAIHE 4: PROFILOIJA (Cognitive Bias Audit)\nKONTEKSTI: Käyttäjä voi toimittaa datan tiedostoina (History/Product Text). Jos nämä ovat laajoja, käyttäjä on aktiivinen.\nTEHTÄVÄT:"
    ).replace(
        "Hyväksyykö käyttäjä ensimmäisen vastauksen sokeasti?",
        "Hyväksyykö käyttäjä vastauksen sokeasti, vai onko hän toimittanut kattavan lähdeaineiston (Tiedostot)?"
    )
    profiler['content'] = new_profiler_content

    # 3. ANALYST (TASK_ANALYST / ID 22) - Etsitään RAG-todisteita tiedostoista
    analyst = data['components']['22']
    print("Updating TASK_ANALYST...")
    
    new_analyst_content = analyst['content'].replace(
        "Poimi suorat sitaatit promptista,",
        "Poimi suorat sitaatit promptista TAI toimitetuista tiedostoista (History/Product),"
    ).replace(
        "Jos tyhjä -> Käyttäjä on Matkustaja.",
        "Jos tyhjä JA tiedostot puuttuvat -> Käyttäjä on Matkustaja."
    )
    analyst['content'] = new_analyst_content

    # 4. VUOROVAIKUTUS (TASK_INTERACTION / ID 32)
    interaction = data['components']['32']
    print("Updating TASK_INTERACTION...")
    new_inter_content = interaction['content'].replace(
        "Jos alle 5%, liputa 'High Dependency'.",
        "Jos alle 5% JA ei liitetiedostoja, liputa 'High Dependency'."
    )
    interaction['content'] = new_inter_content

    # Tallenna
    print(f"Saving changes to {DB_PATH}...")
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False) # Ei indenttiä, jotta pysyy kompaktina kuten aiemmin (tai TinyDB tyyliin)
    
    print("Database updated successfully.")

if __name__ == "__main__":
    try:
        update_db()
    except Exception as e:
        print(f"Error: {e}")
