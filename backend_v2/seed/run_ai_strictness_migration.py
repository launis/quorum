import json
import logging
from pathlib import Path

# Setup basic logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

SEED_DATA_PATH = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")

def make_stricter_ai_desc(old_claim_en: str) -> str:
    """Elevates the strictness of the baseline AI description to demand absolute precision."""
    if not old_claim_en:
        return "CRITICAL DIRECTIVE: STRICT EVALUATION REQUIRED. No ambiguity allowed."

    base = old_claim_en.strip()
    return (
        f"CRITICAL EVALUATION DIRECTIVE: {base}\n"
        "ENFORCEMENT RULE: You MUST apply this criterion with absolute zero-tolerance for ambiguity or hallucination. "
        "Do not compromise, guess, or offer unearned benefit of the doubt. Falsify immediately if all exact conditions are not strictly and verifiably met in the source data."
    )

def make_ui_name_translation(fi_name: str) -> str:
    """Maps the Finnish UI name to a proper, sterile English UI translation."""
    mapping = {
        "Heikko": "Weak", "Välttävä": "Poor", "Kohtalainen": "Fair", "Hyvä": "Good", "Vahva": "Strong",
        "Muistaminen": "Remembering", "Ymmärtäminen": "Understanding", "Soveltaminen": "Applying", "Analysointi": "Analyzing", "Arviointi": "Evaluating", "Luominen": "Creating",
        "Systeemi 1 (Nopea)": "System 1 (Fast)", "Siirtymä": "Transition", "Systeemi 2 (Hidas)": "System 2 (Slow)",
        "Sokea usko": "Blind Faith", "Reaktiivinen huomioija": "Reactive Observer", "Pintapuolinen": "Superficial", "Kriittinen ohjaaja": "Critical Guide", "Aktiivinen haastaja": "Active Challenger",
        "Kriittisesti Poikkeava (Critically Misaligned)": "Critically Misaligned", "Poikkeava (Misaligned)": "Misaligned", "Neutraali (Neutral)": "Neutral", "Linjassa (Aligned)": "Aligned", "Vahvasti Linjassa (Strongly Aligned)": "Strongly Aligned",
        "Mahdoton (Impossible)": "Impossible", "Epätodennäköinen (Unlikely)": "Unlikely", "Mahdollinen (Plausible)": "Plausible", "Todennäköinen (Probable)": "Probable", "Aito (Genuine)": "Genuine",
        "Myötäilyvinouma (Sycophancy)": "Sycophancy", "Kosmeettinen Korjaaja (Aesthetic)": "Aesthetic Refinement", "Substanssin Haastaja (Substantive)": "Substantive Challenge", "Armoton Falsifioija (Popperian)": "Popperian Falsification",
        "Täysi Matkustaja (Hylätty)": "Complete Passenger (Rejected)", "Matkustaja (Heikko)": "Passenger (Weak)", "Navigaattori (Tyydyttävä)": "Navigator (Satisfactory)", "Kuljettaja (Hyvä)": "Driver (Good)", "Arkkitehti (Erinomainen)": "Architect (Excellent)",
        "Erittäin Epävarma (0%)": "Highly Uncertain (0%)", "Keskivarma (50%)": "Moderately Certain (50%)", "Täysi Varmuus (100%)": "Complete Certainty (100%)",
        "Aktiivinen Riski (OWASP LLM01, LLM02, LLM06)": "Active Risk", "Asenteellinen Jännite tai Yliluottamus (OWASP LLM09)": "Bias or Overreliance", "Täydellinen Tietoturvahygienia": "Perfect Security Hygiene",
        "Keksitty (Post-Hoc)": "Fabricated (Post-Hoc)", "Epävarma (Uncertain)": "Uncertain",
        "Täysin läpinäkymätön (Musta laatikko)": "Completely Opaque (Black Box)", "Heikosti selitetty (Osittainen perustelu)": "Poorly Explained (Partial)", "Kohtalainen läpinäkyvyys (Looginen perusrakenne)": "Moderate Transparency (Logical)", "Vahvasti perusteltu (Selkeät kausaalisuudet)": "Strongly Justified (Causal)", "Täydellinen läpinäkyvyys (Dialektinen synteesi)": "Perfect Transparency",
        "Ylimielinen/Ehdoton": "Arrogant / Absolute", "Tunnustava": "Acknowledging", "Itsekriittinen": "Self-Critical"
    }
    return mapping.get(fi_name, str(fi_name))

def run_migration():
    logging.info(f"Loading seed data from {SEED_DATA_PATH}")
    with open(SEED_DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    prompt_blocks = data.get("prompt_blocks", [])
    total_matrices_migrated = 0
    total_scales_migrated = 0

    for block in prompt_blocks:
        scales = block.get("scales", [])
        if not scales:
            continue

        logging.info(f"Processing matrix {block.get('slug')} with {len(scales)} scales.")
        total_matrices_migrated += 1

        for scale in scales:
            old_label_en = scale.get("name", {}).get("translations", {}).get("en", "UNKNOWN_LABEL")

            # Extract the AI claim text (historically abused in claims[0].en)
            old_desc_en = ""
            claims = scale.get("claims", [])
            if claims and len(claims) > 0:
                old_desc_en = claims[0].get("translations", {}).get("en", "")

            # SET PURE AI DATA
            scale["ai_label"] = old_label_en.strip()
            scale["ai_description"] = make_stricter_ai_desc(old_desc_en)

            # SET PURE UI TRANSLATIONS
            fi_name = scale.get("name", {}).get("translations", {}).get("fi", "")
            scale["name"]["translations"]["en"] = make_ui_name_translation(fi_name)

            for claim in claims:
                fi_claim = claim.get("translations", {}).get("fi", "")
                claim["translations"]["en"] = f"UI EN: {fi_claim}"  # Decoupled string to prevent AI leakage to UI

            total_scales_migrated += 1

    # Save mutated data back
    logging.info(f"Saving changes. Matrices updated: {total_matrices_migrated}, Scales updated: {total_scales_migrated}")
    with open(SEED_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    logging.info("Migration complete.")

if __name__ == "__main__":
    run_migration()
