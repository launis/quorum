import json

SEED_FILE = r"c:\src\quorum\backend_v2\seed\seed_data.json"

NEW_DESCRIPTIONS = {
    "default": {
        0: {
            "fi": "Vahva argumentointi (X) ilman kognitiivista syvyyttä (Y) jää ontoksi retoriikaksi. Korkea kognitiivinen syvyys (Y) taas on välttämätön, jotta sitä voidaan arvioida hitaan ja kriittisen harkinnan (Z) kehyksessä. Kaikki kolme määrittävät aidon älykkyyden.",
            "en": "Strong argumentation (X) without cognitive depth (Y) remains hollow rhetoric. High cognitive depth (Y) is necessary to evaluate the text within the framework of slow, critical judgment (Z). All three define genuine intellectual robustness."
        },
        1: {
            "fi": "Organisaation sääntöjen noudattaminen (X) rinnakkain piilevien asenteiden tunnistamisen (Y) kanssa. Korkea sääntöjen noudattaminen (X) voi silti piilottaa taakseen vakavia kielellisiä vääristymiä (Y), jolloin todellinen implementaatioriski kasvaa.",
            "en": "Adherence to organizational rules (X) alongside the identification of hidden biases (Y). High rule adherence (X) can still obscure severe linguistic distortions (Y), increasing the actual implementation risk."
        }
    },
    "analytical_synthesis": {
        0: {
            "fi": "Argumentin oikeutuksen (X) tulisi kasvaa rinta rinnan kognitiivisen syvyyden (Y) kanssa. Jos korkea oikeutus (X) ja syvyys (Y) saavutetaan rutiininomaisella, nopealla System 1 -prosessoinnilla (matala Z), tekoäly todennäköisesti hallusinoi itseluottamuksensa. Vahva analyysi edellyttää aina hidasta harkintaa (korkea Z).",
            "en": "Argument justification (X) should grow hand-in-hand with cognitive depth (Y). If high justification (X) and depth (Y) are achieved with routine, fast System 1 processing (low Z), the AI is likely hallucinating its confidence. Strong analysis always requires slow deliberation (high Z)."
        },
        1: {
            "fi": "Korkea yrityksen sääntöjen noudattaminen (X) heikentyy merkittävästi, jos auditoitu teksti vuotaa asenteellista dataa ulos (matala Y). Sääntöjen mekaaninen seuraaminen (X) luo turvallisuudentunnetta, mutta vinoutunut kieli (Y) todentaa varsinaisen riskin compliance-valvonnalle.",
            "en": "High adherence to corporate rules (X) is significantly compromised if the audited text leaks biased data (low Y). Mechanical adherence to rules (X) creates a false sense of security, but distorted language (Y) proves the actual risk for compliance oversight."
        },
        2: {
            "fi": "Jos tekoäly optimoi pelkkää sisäistä indikaattoria (X), se voi samalla sokeutua ja menettää objektiivisen kriittisen etäisyytensä dataan (Y). Korkea tulos (X) yhdistettynä matalaan etäisyyteen (Y) paljastaa vaarallisen mittausharhan.",
            "en": "If the AI optimizes solely for an internal indicator (X), it may become blind and lose its objective critical distance to the data (Y). A high score (X) combined with low distance (Y) exposes a dangerous measurement bias."
        }
    },
    "causality_synthesis": {
        0: {
            "fi": "Kausaalisten suhteiden todellinen olemassaolo (X) menettää merkityksensä, jos tekoäly ei tunnista omia rajoituksiaan (Y). Vahva näyttö kausaatiosta (X) ylittää rehellisyyden kynnyksen vain silloin, kun malli pystyy avaamaan oman päättelynsä täydellisen läpinäkyvästi (Z).",
            "en": "The actual existence of causal relationships (X) loses its meaning if the AI fails to recognize its own limits (Y). Strong evidence of causality (X) only crosses the threshold of honesty when the model can completely transparently unpack its own reasoning (Z)."
        }
    },
    "final_tribunal": {
        0: {
            "fi": "Jos analyysin syy-seuraussuhteet ovat ristiriitaisia (X), lopullisen tuomion kovuus (Y) peilaa suoraan tekstin hylättävyyttä. Armoton tuomio (Y) on kuitenkin validi vain, jos tekoäly kykenee selittämään prosessinsa läpinäkyvästi (Z). X, Y ja Z yhdessä estävät mustan laatikon päätökset.",
            "en": "If the causal relationships of the analysis are contradictory (X), the severity of the final verdict (Y) directly mirrors the text's rejectability. However, a ruthless verdict (Y) is valid only if the AI can transparently explain its process (Z). Together, X, Y, and Z prevent black-box decisions."
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
        print("[MUTATOR] Description narratives successfully updated with rigorous XYZ dependency integrations.")

if __name__ == "__main__":
    apply_mutations()
