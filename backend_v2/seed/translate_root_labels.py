import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
SEED_DATA_PATH = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")

SLUG_LABELS = {
    "matrix_toulmin": {"fi": "Toulminin Argumentaatiomalli", "en": "Toulmin Argumentation Model"},
    "matrix_bloom": {"fi": "Bloomin Taksonomia", "en": "Bloom's Taxonomy"},
    "matrix_kahneman": {"fi": "Kahnemanin Kaksoisprosessiteoria", "en": "Kahneman's Dual Process Theory"},
    "matrix_goodhart": {"fi": "Performatiivisuus ja Goodhartin Laki", "en": "Performativity & Goodhart's Law"},
    "matrix_input_processing": {"fi": "Syötteiden Prosessointi", "en": "Input Processing"},
    "block_role_analyst": {"fi": "Analyytikko", "en": "Analyst"},
    "block_role_prosecutor": {"fi": "Syyttäjä (Prosecutorial Audit)", "en": "Prosecutorial Audit"},
    "block_mandate_zerotrust": {"fi": "Zero-Trust -Protokolla", "en": "Zero-Trust Protocol"},
    "block_rule_cognitiverequirement": {"fi": "Todistusaineiston Vaatimus", "en": "Evidentiary Rigor"},
    "matrix_archivist": {"fi": "Arkistointistandardien Auditointi", "en": "Archival Compliance Audit"},
    "matrix_causal_analyst": {"fi": "Kausaalisuuden Analyysi", "en": "Causal Analyst"},
    "block_role_coach": {"fi": "Sokraattinen Valmentaja", "en": "Socratic Coach"},
    "matrix_falsifier": {"fi": "Falsifioinnin Auditointi", "en": "Falsification Audit"},
    "block_role_guard": {"fi": "Turvallisuusrajoitteiden Valvoja", "en": "Guardrail Integrity"},
    "matrix_judge": {"fi": "Ylituomari", "en": "Supreme Adjudicator"},
    "block_role_logician": {"fi": "Loogisuuden Valvoja", "en": "Logical Rigor"},
    "block_role_overseer": {"fi": "Työnkulun Valvoja", "en": "Overseer"},
    "block_role_profiler": {"fi": "Psykologinen Profiloija", "en": "Psychological Profiler"},
    "matrix_xai_reporter": {"fi": "XAI-Raportoija", "en": "XAI Synthesis Reporter"},
    "block_headermandates": {"fi": "Ehdottomat Määräykset", "en": "Irrevocable Mandates"},
    "block_instructionstrictscale": {"fi": "Pisteytysprotokollan Noudattaminen", "en": "Scoring Protocol Compliance"},
    "block_headerrules": {"fi": "Operatiiviset Säännöt", "en": "Operational Rules"},
    "block_headerprotocols": {"fi": "Työkalut ja Menetelmät", "en": "Tools & Methods"},
    "block_headerinstructions": {"fi": "Ohjeet", "en": "Instructions"},
    "block_mandate2": {"fi": "Kognitiivisten Vinoumien Hallinta", "en": "Cognitive Bias Mitigation"},
    "block_mandate3": {"fi": "Asiantuntijuuden Erottelu", "en": "Mastery Distinction"},
    "block_mandate5": {"fi": "Nollahypoteesin Noudattaminen", "en": "Null Hypothesis Adherence"},
    "block_rule1": {"fi": "Zero-Trust -Raja", "en": "Zero-Trust Perimeter"},
    "block_rule2": {"fi": "Toimivallan Rajat", "en": "Jurisdictional Boundaries"},
    "block_rule3": {"fi": "Sisältö Ennen Muotoa", "en": "Substance Over Form"},
    "block_rule4": {"fi": "Prosessin Integriteetti", "en": "Process Integrity"},
    "block_rule5": {"fi": "Episteeminen Nöyryys", "en": "Epistemic Humility"},
    "block_rule6": {"fi": "Falsifiointi ja Faktojen Ensisijaisuus", "en": "Falsification & Factual Primacy"},
    "block_globalcontext": {"fi": "Järjestelmän Konteksti", "en": "System Context"},
    "block_oprule1": {"fi": "Faktuaalisuus ja Perustelut", "en": "Factuality & Grounding"},
    "block_oprule2": {"fi": "Todennettava Alkuperä", "en": "Verifiable Authorship"},
    "block_oprule3": {"fi": "Ero Todisteiden ja Väitteiden Välillä", "en": "Evidence-Claim Distinction"},
    "block_oprule4": {"fi": "Passiivisuusrangaistus", "en": "Passivity Penalty"},
    "block_instructionnohallucination": {"fi": "Nollatoleranssi Hallusinaatioille", "en": "Zero-Tolerance Grounding"},
    "block_instructioncoachcitation": {"fi": "Lähdeviittausvaatimus", "en": "Citation Mandate"},
    "block_instructionnodataleak": {"fi": "Datan Eristämisprotokolla", "en": "Data Isolation Protocol"},
    "block_instructionbiblicalgrounding": {"fi": "Ehdoto Lähdeuskollisuus", "en": "Absolute Source Adherence"},
    "block_instructionlanguage_dynamic": {"fi": "Kielellinen Mukautuminen", "en": "Linguistic Conformity"},
    "matrix_taskguard": {"fi": "Turvallisuus- ja Etiikkasuodatin", "en": "Security & Ethics Guardrail"},
    "block_taskanalyst": {"fi": "Väitteiden Purku ja Kyselyn Muodostaminen", "en": "Claim Deconstruction"},
    "block_taskprofiler": {"fi": "Kognitiivinen Profilointi", "en": "Cognitive Profiling"},
    "block_tasklogician": {"fi": "Loogisuuden Validointi", "en": "Logical Validation"},
    "block_taskfalsifier": {"fi": "Tehtävien Falsifioija", "en": "Task Falsifier"},
    "block_taskoverseer": {"fi": "Tehtävien Valvoja", "en": "Task Overseer"},
    "matrix_causal_abductive": {"fi": "Kausaalinen ja Abduktiivinen Integriteetti", "en": "Causal & Abductive Integrity"},
    "block_taskcausal": {"fi": "Kausaalivaikutusten Todentaminen", "en": "Causal Impact Verification"},
    "block_taskarchivist": {"fi": "Ennakkotapausten Auditointi", "en": "Precedent Audit"},
    "block_taskjudge": {"fi": "Tuomari", "en": "Task Judge"},
    "block_taskcoach": {"fi": "Teknisen Korjauksen Valmentaja", "en": "Technical Remediation Coach"},
    "matrix_taskxai_clarity": {"fi": "Selitettävyys ja Läpinäkyvyys", "en": "Explainability & Transparency"},
    "block_protocol1": {"fi": "Negatiivisen Lokin Protokolla", "en": "Negative Logging Protocol"},
    "block_protocol3": {"fi": "RFI-Protokollan Noudattaminen", "en": "RFI Protocol Enforcement"},
    "block_protocol4": {"fi": "Eskalointi Ihmiselle", "en": "Human-In-The-Loop Escalation"},
    "block_instructionanon": {"fi": "PII-Datan Sanitointi", "en": "PII Sanitization"},
    "block_instructionragopt": {"fi": "RAG-Kontekstin Optimointi", "en": "RAG Context Optimization"},
    "block_principle1": {"fi": "Popperilainen Falsifiointi", "en": "Popperian Falsification"},
    "block_requirement1": {"fi": "Parametrien Diversifiointi", "en": "Parameter Diversification"},
    "block_heuristic1": {"fi": "RAG-Perustelut ja Lähdeviittaukset", "en": "RAG Grounding & Citation Protocol"},
    "block_heuristic2": {"fi": "Kausaalisen Ketjun Todentaminen", "en": "Causal Sequence Verification"},
    "block_heuristic3": {"fi": "Occamin Partaveitsi", "en": "Principle of Parsimony (Occam's Razor)"},
    "block_taskperformativity": {"fi": "Performatiivisuuden Auditointi", "en": "Task Performativity Audit"},
    "block_role_saboteur": {"fi": "Red Team (Sabotööri)", "en": "Red Team (Saboteur)"},
    "block_rule_falsification_first": {"fi": "Falsifiointi Ensin -Protokolla", "en": "Falsification-First Protocol"},
    "matrix_epistemic_humility": {"fi": "Episteeminen Nöyryys", "en": "Epistemic Humility"}
}

def translate_labels():
    logging.info(f"Loading data from {SEED_DATA_PATH}")
    with open(SEED_DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    for block in data.get("prompt_blocks", []):
        slug = block.get("slug")
        if slug in SLUG_LABELS:
            block["label"]["translations"]["fi"] = SLUG_LABELS[slug]["fi"]
            block["label"]["translations"]["en"] = SLUG_LABELS[slug]["en"]
            count += 1
        else:
            # Fallback title casing for unmapped
            lbl_fi = block.get("label", {}).get("translations", {}).get("fi", "")
            if lbl_fi.isupper() or "_" in lbl_fi:
                block["label"]["translations"]["fi"] = lbl_fi.replace("_", " ").title()
                count += 1
                
    if count > 0:
        with open(SEED_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info(f"Translated {count} labels successfully.")
    else:
        logging.info("No labels required translation.")

if __name__ == "__main__":
    translate_labels()
