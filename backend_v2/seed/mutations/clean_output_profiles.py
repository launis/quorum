import json
import os

SEED_FILE = r"c:\src\quorum\backend_v2\seed\seed_data.json"

ALLOWED_PROFILES = ["default", "analytical_synthesis", "causality_synthesis", "final_tribunal"]

SYNTHESIS_DESCRIPTIONS = {
    "analytical_synthesis": {
        0: {
            "fi": "Vahva argumentin oikeutus (Toulmin) vaatii ylivertaista kognitiivista syvyyttä (Bloom) ja yleensä harkitsevaa hidasta prosessointia (System 2). Jos malli tuottaa sokean 'täydellisen' väitteen System 1 nopeudella, kyseessä on usein hallusinaatio.",
            "en": "Strong argument justification (Toulmin) requires superior cognitive depth (Bloom) and generally deliberate slow processing (System 2). If the model produces a blind 'perfect' claim at System 1 speed, it is often a hallucination."
        },
        1: {
            "fi": "Ne muodostavat 'Riskimatriisin'. Korkea yrityksen lakien noudattaminen (X) on arvotonta, jos teksti vuotaa asenteellista dataa ulos (matala Y). Tämä 2D-pinta on täydellinen Executive-tason raportointiin compliance-osastolle.",
            "en": "They form the 'Risk Matrix'. High corporate compliance (X) is worthless if the text leaks biased data (low Y). This 2D surface is perfect for Executive-level reporting to the compliance department."
        },
        2: {
            "fi": "Goodhartin laki vs Kriittinen etäisyys. Jos tekoäly tuijottaa sokeasti vain indikaattoria optimoidakseen pistettään (X), se menettää objektiivisen etäisyytensä analysoitavaan dataan (Y). Matala etäisyys tarkoittaa neutraaliuden menettämistä.",
            "en": "Goodhart's law vs Critical distance. If the AI blindly stares only at the indicator to optimize its score (X), it loses its objective distance to the analyzed data (Y). Low distance means a loss of neutrality."
        }
    },
    "causality_synthesis": {
        0: {
            "fi": "Kertoo, onko auditoitava strategia oikeasti olemassa, vai onko koko teksti vain jälkiviisasta selittelyä (Abduktiivinen Päättely / Judea Pearl), ja kuinka läpinäkyvästi teksti tunnistaa omat rajansa.",
            "en": "Determines if the audited strategy genuinely exists or if the entire text is simply post-hoc rationalization (Abductive Reasoning / Judea Pearl), and how transparently the text acknowledges its own limits."
        }
    },
    "final_tribunal": {
        0: {
            "fi": "Meta-analyysi, joka kokoaa alleen syy-seuraussuhteet (Causal Analyst), antaa lopullisen armottoman leikkauksen (Judge) ja avaa tekoälyn oman prosessin läpinäkyvästi (XAI Reporter).",
            "en": "Meta-analysis that consolidates causal relationships (Causal Analyst), delivers a final ruthless verdict (Judge), and transparently exposes the AI's internal process (XAI Reporter)."
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
            
            # Prune Legacy Profiles
            keys_to_delete = [k for k in profiles.keys() if k not in ALLOWED_PROFILES]
            if keys_to_delete:
                for k in keys_to_delete:
                    del profiles[k]
                mutated = True
                print(f"[MUTATOR] Deleted legacy profiles: {keys_to_delete}")

            # Inject Synthesis Descriptions
            for pid, desc_map in SYNTHESIS_DESCRIPTIONS.items():
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
                                # If flat dict (fallback fallback)
                                desc_obj["fi"] = texts["fi"]
                                desc_obj["en"] = texts["en"]
                                mutated = True

            if mutated:
                workflow["output_profiles"] = profiles

    if mutated:
        with open(SEED_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("[MUTATOR] Profiles successfully consolidated and synthesis narratives injected.")
    else:
        print("[MUTATOR] No targets required upgrading.")

if __name__ == "__main__":
    apply_mutations()
