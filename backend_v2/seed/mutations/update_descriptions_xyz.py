import json
import os

SEED_FILE = r"c:\src\quorum\backend_v2\seed\seed_data.json"

NEW_DESCRIPTIONS = {
    "analytical_synthesis": {
        0: {
            "fi": "Vahva argumentin oikeutus (X) vaatii ylivertaista kognitiivista syvyyttä (Y) ja tyypillisesti harkitsevaa hidasta prosessointia (Z). Jos malli tuottaa sokean 'täydellisen' väitteen System 1 nopeudella, kyseessä on merkittävä riski hallusinaatiosta.",
            "en": "Strong argument justification (X) requires superior cognitive depth (Y) and typically deliberate slow processing (Z). If the model produces a blind 'perfect' claim at System 1 speed, there is a significant risk of hallucination."
        },
        1: {
            "fi": "Korkea yrityksen lakien ja sääntöjen noudattaminen (X) heikentyy merkittävästi, jos auditoitu teksti vuotaa asenteellista dataa ulos (matala Y). Tämä matriisi paljastaa piilevät tietoturva- ja asenneongelmat sääntöjen näennäisen noudattamisen takaa.",
            "en": "High adherence to corporate laws and precedents (X) is significantly compromised if the audited text leaks biased data (low Y). This matrix exposes hidden security and bias issues behind the superficial adherence to rules."
        },
        2: {
            "fi": "Jos tekoäly tuijottaa sokeasti pelkkää indikaattoria optimoidakseen pistettään (X), se menettää objektiivisen kriittisen etäisyytensä analysoitavaan dataan (Y). Matala etäisyys tarkoittaa neutraaliuden ja auditoinnin luotettavuuden täydellistä menettämistä.",
            "en": "If the AI blindly focuses only on an indicator to optimize its score (X), it loses its objective critical distance to the analyzed data (Y). Low distance means a complete loss of neutrality and audit reliability."
        }
    },
    "causality_synthesis": {
        0: {
            "fi": "Mittaa onko auditoitava strategia oikeasti olemassa oleva kausaalinen suhde (X), vai pelkkää jälkiviisasta abduktiivista selittelyä. Arvioi samalla mallin kykyä toimia omien asettamiensa rajojen puitteissa (Y) sekä analyysin lopullista läpinäkyvyyttä (Z).",
            "en": "Measures whether the audited strategy is a genuine causal relationship (X), or mere post-hoc abductive rationalization. Simultaneously evaluates the model's ability to operate within its defined constraints (Y) and the ultimate transparency of the analysis (Z)."
        }
    },
    "final_tribunal": {
        0: {
            "fi": "Yhdistää analyysin kriittiset syy-seuraussuhteet (X), antaa lopullisen armottoman tuomion tekstin kelpoisuudesta (Y) ja avaa tekoälyn oman prosessilogiikan täysin läpinäkyväksi selosteeksi (Z).",
            "en": "Integrates the critical causal relationships of the analysis (X), delivers a final ruthless verdict on the text's validity (Y), and opens the AI's internal process logic into a completely transparent report (Z)."
        }
    }
}

def apply_mutations():
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    mutated = False
    for workflow in data.get("workflows", []):
        if workflow.get("slug") == "kokonaisvaltainen_auditointi":
            profiles = workflow.get("output_profiles", {})
            for pid, desc_map in NEW_DESCRIPTIONS.items():
                if pid in profiles:
                    layouts = profiles[pid].get("layouts", [])
                    for idx, texts in desc_map.items():
                        if idx < len(layouts):
                            desc_obj = layouts[idx].get("description", {})
                            if isinstance(desc_obj, dict) and "translations" in desc_obj:
                                desc_obj["translations"]["fi"] = texts["fi"]
                                desc_obj["translations"]["en"] = texts["en"]
                                mutated = True
                            elif isinstance(desc_obj, dict):
                                desc_obj["fi"] = texts["fi"]
                                desc_obj["en"] = texts["en"]
                                mutated = True
            
            if mutated:
                workflow["output_profiles"] = profiles

    if mutated:
        with open(SEED_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("[MUTATOR] Description narratives successfully updated with strict (X)(Y)(Z) coordinate integrations.")

if __name__ == "__main__":
    apply_mutations()
