import json
import re

SEED_FILE = r"c:\Users\risto\OneDrive\quorum\data\seed_data.json"

# --- CONTENT DEFINITIONS ---

MANDATES = {
    "mandate_system2": """1.1 Mandaatti: Pakotettu "Järjestelmä 2" -Analyysi
KÄSKE: Tämä järjestelmä on suunniteltu hyödyntämään pidennettyä päättelyaikaa (inference-time compute). Sinun TÄYTYY tuottaa hidasta, deliberatiivista ”Järjestelmä 2” -tason analyysia (Kahneman 2011).
KÄSKE (Mekanismi): Kaikissa monimutkaisissa analyyttisissä tehtävissä (erityisesti VAIHEET 3-8) sinun TÄYTYY käyttää sisäistä päättelytilaa (esim. <scratchpad> tai vastaava Chain-of-Thought -mekanismi) päättelyketjujen tietoiseen rakentamiseen, iterointiin ja virheiden korjaamiseen ennen lopullisen vastauksen tuottamista. Vältä pinnallisia (Järjestelmä 1) vastauksia. Priorisoi syvällistä loogista analyysia ja falsifiointia.""",

    "mandate_hybrid_rubric": """1.2 Mandaatti: Reliabiliteetin ja Validiteetin Jännitteen Hallinta
KÄSKE: Toimintasi perustuu kaksitasoiseen Hybridirubriikkiin, joka hallitsee psykometristä jännitettä. Varmista reliabiliteetti (Analyyttinen taso/Matriisi) ja validiteetti (Holistinen taso/Kvoorum). Tasapainota nämä tasot.""",

    "mandate_methodological_humility": """1.3 Mandaatti: Metodologinen Nöyryys (Popper vs. Dreyfus)
KÄSKE: Sovella poikkeamien tulkinnassa hierarkiaa:
●\tFalsifioinnin Etusija (Popper): Faktuaaliset/loogiset/eettiset virheet ovat aina virheitä.
●\tMestaruuden Tunnistaminen (Dreyfus): Strateginen ja perusteltu säännön rikkominen voi olla "Mestaruus-poikkeama" (ks. SÄÄNTÖ 6).""",

    "mandate_anti_performativity": """1.4 Mandaatti: Performatiivisuuden Torjunta (Goodhartin Laki)
KÄSKE: Oleta käyttäjän pyrkivän manipuloimaan järjestelmää. Etsi aktiivisesti epäaitoja narratiiveja ("performatiivista reflektiota"). Käytä kausaalista päättelyä aitouden arviointiin (VAIHEET 5 ja 6) ja epäile "liian täydellisiä" suorituksia (VAIHE 8)."""
}

RULES = {
    "rule_fragility": """SÄÄNTÖ 1 (Haurauden Tunnustus ja Siirtymäpolku): (Agentti: XAI-RAPORTOIJA, VAIHE 9): Kirjaa Systeeminen Epävarmuus: "KORKEA EPÄVARMUUS: Järjestelmän hallinta perustuu kehotepohjaiseen kontrolliin. Tämä menetelmä on luontaisesti hauras.\"""",

    "rule_strict_agency": """SÄÄNTÖ 2 (Tiukka Toimivaltarajoitus): Ette saa suorittaa mitään toimintoja, joita ei ole eksplisiittisesti määritelty teidän VAIHE-ohjeissanne. Ulkoisten työkalujen käyttö kielletty ellei erikseen mainittu.""",

    "rule_input_integrity": """SÄÄNTÖ 3 (Syötteen Eheys ja Standardivalidointi): Saatte käsitellä AINOASTAAN VAIHE 1:n validoimaa dataa. Jokaisen agentin TÄYTYY suorittaa rakenteellinen ja semanttinen validointi ennen tehtävän alkua.""",

    "rule_cross_validation": """SÄÄNTÖ 4 (Ristiinvalidoiva Päättelyketju): Ennen omaa analyysia, validoi edellisen vaiheen johdonmukaisuus.""",

    "rule_structured_output": """SÄÄNTÖ 5 (Strukturoitu Tuotos ja Pakollinen Skeemavalidointi): Kaikki välituotokset on tuotettava TÄSMÄLLEEN määritellyssä JSON-muodossa. Suorita sisäinen skeemavalidointi ennen tulostusta.""",

    "rule_mastery_exception": """SÄÄNTÖ 6 (Metodologinen Nöyryys - "Mestaruuspoikkeama"): (Agentti: TUOMARI, VAIHE 8): Jos käyttäjä rikkoo matriisia strategisesti ja tuottaa ylivertaisen tuloksen, tämä on liputettava "Mestaruus-poikkeamana". Heikkoa tulosta ei voi perustella tällä.""",

    "rule_strategic_substance": """SÄÄNTÖ 7 (Substanssin Strateginen Arviointi): Arvioi substanssin strategista käyttöä prosessin ohjaamisessa, älä substanssin akateemista tarkkuutta.""",

    "rule_performativity_detection": """SÄÄNTÖ 8 (Performatiivisuuden Tunnistus): (VAIHEET 5, 6, 8): Etsikää merkkejä järjestelmän pelaamisesta.""",

    "rule_high_stakes": """SÄÄNTÖ 11 (Korkean Panoksen Rajoitus): Tätä arviointia ei saa käyttää ainoana perusteena korkean panoksen päätöksille ilman ihmisvarmistusta (HITL).""",

    "rule_data_privacy": """SÄÄNTÖ 12 (Datarauha): Prosessidata on luottamuksellista.""",

    "rule_scoring_mandate": """SÄÄNTÖ 13 (Pisteytysmandaatti - Prosessin Puhtaus): Arvioi prosessi vain Keskusteluhistoriasta, reflektio vain Reflektiodokumentista.""",

    "rule_input_control": """SÄÄNTÖ 14 (Input-Control Ratio): Erottele "Matkustaja" (passiivinen) ja "Kuski" (aktiiviset rajoitteet).""",

    "rule_synthesis_originality": """SÄÄNTÖ 15 (Synteesin Omaperäisyys): Vertaa Lopputuotetta tekoälyn viimeiseen vastaukseen. Identtisyys johtaa matalaan arvosanaan."""
}

# Common rules for all agents
COMMON_RULES = [
    "mandate_system2", "mandate_hybrid_rubric", "mandate_methodological_humility", "mandate_anti_performativity",
    "rule_strict_agency", "rule_input_integrity", "rule_cross_validation", "rule_structured_output",
    "rule_high_stakes", "rule_data_privacy"
]

def split_rules_and_mandates():
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    components = data['components']
    
    # Helper to upsert
    def upsert_component(comp_id, comp_type, name, content):
        # Remove existing if present
        for i, c in enumerate(components):
            if c.get('id') == comp_id:
                components.pop(i)
                break
        
        new_comp = {
            "id": comp_id,
            "type": comp_type,
            "name": name,
            "content": content,
            "description": f"Extracted {comp_type}: {name}"
        }
        components.append(new_comp)
        print(f"Upserted: {comp_id}")

    # 1. Create Mandate Components
    for mid, content in MANDATES.items():
        name = content.split('\n')[0].split(':')[1].strip() if ':' in content.split('\n')[0] else mid
        upsert_component(mid, "mandate", name, content)

    # 2. Create Rule Components
    for rid, content in RULES.items():
        # Extract name from parenthesis if possible
        match = re.search(r'\((.*?)\)', content.split('\n')[0])
        name = match.group(1) if match else rid
        upsert_component(rid, "rule", name, content)

    # 3. Update Steps
    for step in data['steps']:
        prompts = step['execution_config']['llm_prompts']
        
        # Remove old headers
        prompts = [p for p in prompts if p not in ["HEADER_mandates", "HEADER_rules"]]
        
        # Add common rules to start
        new_prompts = COMMON_RULES.copy()
        
        # Add specific rules based on agent/step
        if step['id'] == 'step_8': # Judge
             new_prompts.extend(["rule_mastery_exception", "rule_strategic_substance", "rule_performativity_detection", "rule_scoring_mandate", "rule_input_control", "rule_synthesis_originality"])
        elif step['id'] in ['step_5', 'step_6']: # Causal, Performativity
             new_prompts.append("rule_performativity_detection")
        elif step['id'] == 'step_9': # XAI
             new_prompts.append("rule_fragility")

        # Append existing prompts (protocols, methods, tasks)
        # Avoid duplicates
        for p in prompts:
            if p not in new_prompts:
                new_prompts.append(p)
        
        step['execution_config']['llm_prompts'] = new_prompts
        print(f"Updated prompts for {step['id']}")

    with open(SEED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Successfully split rules and mandates.")

if __name__ == "__main__":
    split_rules_and_mandates()
