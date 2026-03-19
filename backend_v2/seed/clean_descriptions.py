import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

SEED_DATA_PATH = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")

CLEAN_MAP = {
    "block_taskarchivist": {
        "fi": "Varmistaa aineiston ja päätöksenteon vastaavuus aiempien ennakkotapausten sekä organisaatiostandardien kanssa.",
        "en": "Ensures the material and decision-making align with previous precedent cases and organizational standards."
    },
    "block_taskjudge": {
        "fi": "Yhdistää kaikkien asiantuntijoiden arviot lopulliseksi, painotetuksi tuomioksi.",
        "en": "Synthesizes evaluations from all experts into a final, weighted verdict."
    },
    "block_taskcoach": {
        "fi": "Antaa rakentavaa palautetta havaintojen pohjalta.",
        "en": "Provides constructive feedback based on observations."
    },
    "matrix_taskxai_clarity": {
        "fi": "Arvioi tuomion ymmärrettävyyttä ja läpinäkyvyyttä.",
        "en": "Evaluates the comprehensibility and transparency of the verdict."
    },
    "block_protocol1": {
        "fi": "Sääntö: Negatiivinen loki puutteista.",
        "en": "Rule: Negative log of omissions."
    },
    "block_protocol3": {
        "fi": "Heuristiikka: Tiedonhankinnan RFI-laadunvarmistus.",
        "en": "Heuristic: Quality assurance of information retrieval via RFI."
    },
    "block_protocol4": {
        "fi": "Protokolla: Vastuunsiirto ihmiselle epävarmassa tilanteessa.",
        "en": "Protocol: Responsibility handover to a human in uncertain situations."
    },
    "block_instructionanon": {
        "fi": "Sääntö: PII-datan anonymisointi.",
        "en": "Rule: Anonymization of PII data."
    },
    "block_instructionragopt": {
        "fi": "Sääntö: RAG-kontekstin optimointi 'Lost in the Middle' -ilmiön välttämiseksi.",
        "en": "Rule: RAG context optimization to avoid the 'Lost in the Middle' phenomenon."
    },
    "block_principle1": {
        "fi": "Periaate: Popperilainen falsifiointi tieteenfilosofiana.",
        "en": "Principle: Popperian falsification as philosophy of science."
    },
    "block_requirement1": {
        "fi": "Vaatimus: Mallin diversiteetti kriittisissä vaiheissa.",
        "en": "Requirement: Model diversity in critical phases."
    },
    "block_instructioncoachcitation": {
        "fi": "Sääntö: Tieteellisten lähdeviittausten vaatimus RAG-aineistoissa.",
        "en": "Rule: Requirement for scientific in-text citations in RAG materials."
    },
    "block_heuristic1": {
        "fi": "Heuristiikka: Temporaalinen tarkistus syy-seuraussuhteelle.",
        "en": "Heuristic: Temporal check for causality."
    },
    "block_heuristic2": {
        "fi": "Heuristiikka: Kontrafaktuaalinen tarkistus intervention vaikuttavuudesta.",
        "en": "Heuristic: Counterfactual check of intervention impact."
    },
    "block_heuristic3": {
        "fi": "Heuristiikka: Occamin partaveitsi yksinkertaisimmalle selitykselle.",
        "en": "Heuristic: Occam's razor for the simplest explanation."
    },
    "block_taskperformativity": {
        "fi": "Rooli: Illuusiivisen tai performatiivisen ohjaamisen tunnistaminen.",
        "en": "Role: Identifying illusory or performative guidance."
    },
    "block_instruction_strictness": {
        "fi": "Ohjeistus: Analyysin tiukkuustason dynaaminen säätely.",
        "en": "Instruction: Dynamic strictly calibration for analysis."
    },
    "block_role_prosecutor": {
        "fi": "Rooli: Syyttäjä, joka etsii järjestelmällisesti ristiriitaisuuksia.",
        "en": "Role: Prosecutor who systematically looks for contradictions."
    },
    "block_mandate_zerotrust": {
        "fi": "Sääntö: Zero-Trust -menetelmä empiiristen todisteiden vaatimiseksi.",
        "en": "Rule: Zero-Trust methodology requiring empirical evidence."
    },
    "block_rule_cognitiverequirement": {
        "fi": "Sääntö: Metakognitiivinen puolustus ja logiikan perustelu.",
        "en": "Rule: Metacognitive defense and logical justification."
    },
    "block_role_saboteur": {
        "fi": "Rooli: Red Team, joka testaa kilpailevia argumentteja.",
        "en": "Role: Red Team testing competing arguments."
    },
    "block_rule_falsification_first": {
        "fi": "Sääntö: Käänteinen todistustaakka kriittisten virheiden etsimiseen.",
        "en": "Rule: Reverse burden of proof for finding critical errors."
    },
    "matrix_epistemic_humility": {
        "fi": "Matriisi: Tekstin omien rajoitteiden ja riskien tunnistus.",
        "en": "Matrix: Recognition of the text's own limitations and risks."
    }
}

def clean_descriptions():
    logging.info(f"Loading seed data from {SEED_DATA_PATH}")
    with open(SEED_DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    prompt_blocks = data.get("prompt_blocks", [])
    count = 0

    for block in prompt_blocks:
        slug = block.get("slug")
        if slug in CLEAN_MAP:
            block["description"]["translations"]["fi"] = CLEAN_MAP[slug]["fi"]
            block["description"]["translations"]["en"] = CLEAN_MAP[slug]["en"]
            count += 1
            logging.info(f"Cleaned generic description for {slug}")

        # Safety Fallback for ANY block description having ROOLI or TEHTÄVÄ
        desc_en = block.get("description", {}).get("translations", {}).get("en", "")
        desc_fi = block.get("description", {}).get("translations", {}).get("fi", "")
        
        # If it hasn't been explicitly mapped but looks contaminated:
        if "ROOLI:" in desc_fi or "SÄÄNTÖ:" in desc_fi or "KÄSKE:" in desc_fi or "MÄÄRÄYS:" in desc_fi or desc_fi == desc_en:
            if slug not in CLEAN_MAP:
                logging.warning(f"Unmapped contaminated description found for block: {slug}. Manual fix may be required.")
            
    if count > 0:
        with open(SEED_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info(f"Cleanup complete. Replaced {count} descriptions.")
    else:
        logging.info("No descriptions needed cleaning.")

if __name__ == "__main__":
    clean_descriptions()
