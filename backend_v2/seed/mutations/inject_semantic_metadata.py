import json
import os

SEED_FILE = r"c:\src\quorum\backend_v2\seed\seed_data.json"

META_MAP = {
    "default": [
        {
            "title": {"fi": "Kognitiivinen Äly (3D)", "en": "Cognitive Intelligence (3D)"},
            "desc": {
                "fi": "Arvioi tekstin älyllistä laatua, kognitiivista syvyyttä ja kriittistä harkintaa Toulminin ja Bloomin taksonomioiden avulla.",
                "en": "Evaluates the text's intellectual quality, cognitive depth, and critical judgment leveraging Toulmin and Bloom taxonomies."
            }
        },
        {
            "title": {"fi": "Hallinnollinen Riski (1D/2D)", "en": "Governance Risk (1D/2D)"},
            "desc": {
                "fi": "Mittaa tekstin sitoutumista organisaation sääntöihin ja arvioi sen tuottamia tietoturva- tai asennemuutoksia.",
                "en": "Measures the text's adherence to organizational precedent and evaluates generated security or bias implications."
            }
        }
    ],
    "analytical_synthesis": [
        {
            "title": {"fi": "Kognitiivinen Profiili (3D)", "en": "Cognitive Profile (3D)"},
            "desc": {
                "fi": "Paljastaa heti, onko tekoälyn 'fiksun kuuloinen' ulosanti todellisuudessa hallusinaatiota vai matalan prosessointinopeuden (System 1/2) kriittisen päättelyn tulosta.",
                "en": "Instantly reveals whether the AI's 'smart-sounding' output is actually a hallucination or the result of critical System 1/2 processing."
            }
        },
        {
            "title": {"fi": "Hallinnollinen Riskimatriisi (2D)", "en": "Governance Risk Matrix (2D)"},
            "desc": {
                "fi": "Tarjoaa Compliance-osastolle näkymän siihen, tekikö malli säännöistä huolimatta vaarallisen sokean pisteen päätöksen tai vuotiko asenteellista dataa.",
                "en": "Provides the Compliance department visibility into whether the model made dangerous blind-spot decisions or leaked biased data despite precedents."
            }
        },
        {
            "title": {"fi": "Indikaattorin Luotettavuus (2D)", "en": "Indicator Reliability & Distance (2D)"},
            "desc": {
                "fi": "Paljastaa, pystyikö malli arvioimaan sisältöä kriittisen etäältä, vai imeytyikö se alkuperäisen tekstin kapeaan 'totuuteen' tilastoharhan (Goodhartin laki) kera.",
                "en": "Reveals whether the model was able to evaluate the content from a critical distance, or if it absorbed the narrow 'truth' of the original text via Goodhart's law."
            }
        }
    ],
    "causality_synthesis": [
        {
            "title": {"fi": "Itsekritiikin ja Kausaliteetin Ulottuvuus (3D)", "en": "Dimension of Self-Criticism and Causality (3D)"},
            "desc": {
                "fi": "Kertoo, onko auditoitava strategia oikeasti olemassa, vai onko koko teksti vain jälkiviisasta selittelyä (Abduktiivinen Päätely), ja kuinka läpinäkyvästi teksti tunnistaa omat rajansa.",
                "en": "Determines if the audited strategy genuinely exists or if the entire text is simply post-hoc rationalization, and how transparently the text acknowledges its limitations."
            }
        }
    ],
    "final_tribunal": [
        {
            "title": {"fi": "Ihmisen Kaltainen Valvova Meta-Koneisto (1D)", "en": "Human-in-the-Loop Meta-Oversight Tribunal (1D)"},
            "desc": {
                "fi": "Meta-analyysi, joka kokoaa alleen syy-seuraussuhteet, antaa lopullisen armottoman leikkauksen ja avaa tekoälyn oman logiikan läpinäkyvästi.",
                "en": "A meta-analysis that consolidates causal relationships, delivers a final ruthless verdict, and transparently exposes the AI's internal logic."
            }
        }
    ]
}

def to_i18n(dict_val):
    return {
        "default_locale": "fi",
        "translations": dict_val
    }

def fix():
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    for workflow in data.get("workflows", []):
        if workflow.get("slug") == "kokonaisvaltainen_auditointi":
            profiles = workflow.get("output_profiles", {})
            for pid, profile_data in profiles.items():
                if pid in META_MAP:
                    layouts = profile_data.get("layouts", [])
                    meta_list = META_MAP[pid]
                    for i, layout in enumerate(layouts):
                        if i < len(meta_list):
                            layout["title"] = to_i18n(meta_list[i]["title"])
                            layout["description"] = to_i18n(meta_list[i]["desc"])
                            
    with open(SEED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Mutaatio valmis (I18nText format).")

if __name__ == "__main__":
    fix()
