import json

SEED_FILE = "c:/src/quorum/backend_v2/seed/seed_data.json"

def get_i18n(fi_text, en_text):
    return {
        "default_locale": "fi",
        "translations": {
            "fi": fi_text,
            "en": en_text
        }
    }

MATRIX_COLUMN_LABELS = {
    "label": get_i18n("Matriisi", "Matrix"),
    "score": get_i18n("Pisteet", "Score"),
    "distribution": get_i18n("Jakauma", "Distribution"),
    "row_explanation": get_i18n("Selite", "Explanation"),
    "quotes": get_i18n("Lainaukset (quotes)", "Quotes (quotes)"),
    "normalized_score": get_i18n("Skaalattu", "Normalized")
}

# The spec didn't give English for extensions, so we'll use the Finnish for both or provide reasonable defaults.
# "These are dictionaries of I18nText format"
EXTENSION_LABELS = {
    "citation": get_i18n("VIITTEET", "CITATIONS"),
    "justification": get_i18n("PERUSTELUT", "JUSTIFICATIONS"),
    "falsification": get_i18n("⚖️ VASTA-ARGUMENTTI", "⚖️ COUNTER-ARGUMENT"),
    "theory_link": get_i18n("📚 TEOREETTINEN YHTEYS", "📚 THEORETICAL LINK"),
    "risk_flag": get_i18n("⚠️ VAKAVA RISKI HAVAITTU", "⚠️ SEVERE RISK DETECTED"),
    "coaching": get_i18n("💡 ARJEN VINKKI", "💡 DAILY TIP"),
    "missing_context": get_i18n("🔍 PUUTTUVA KONTEKSTI", "🔍 MISSING CONTEXT"),
    "remediation_steps": get_i18n("🛠️ KORJAAVAT TOIMENPITEET", "🛠️ REMEDIATION STEPS"),
    "emotional_sentiment": get_i18n("🎭 EMOTIONAALINEN SÄVY", "🎭 EMOTIONAL SENTIMENT"),
    "confidence": get_i18n("LUOTETTAVUUS JA VARMUUS", "RELIABILITY AND CONFIDENCE"),
    "variance_validation": get_i18n("🤖 VARIAATIO (KOGNITIIVINEN VS. MEKAANINEN)", "🤖 VARIANCE (COGNITIVE VS. MECHANICAL)")
}

def migrate():
    with open(SEED_FILE, encoding='utf-8') as f:
        data = json.load(f)

    changed = False

    def update_layouts(layouts):
        nonlocal changed
        for layout in layouts:
            if "matrix_column_labels" not in layout:
                layout["matrix_column_labels"] = MATRIX_COLUMN_LABELS
                changed = True
            if "extension_labels" not in layout:
                layout["extension_labels"] = EXTENSION_LABELS
                changed = True

    # Check root level output_profiles list
    if "output_profiles" in data and isinstance(data["output_profiles"], list):
        for profile in data["output_profiles"]:
            if "layouts" in profile:
                update_layouts(profile["layouts"])

    # Check workflows which have embedded output_profiles
    if "workflows" in data and isinstance(data["workflows"], list):
        for workflow in data["workflows"]:
            if "output_profiles" in workflow and isinstance(workflow["output_profiles"], dict):
                for prof_id, profile in workflow["output_profiles"].items():
                    if "layouts" in profile:
                        update_layouts(profile["layouts"])

            # Also check default layouts if workflows have them directly? Workflows don't have layouts directly according to schema, they are in embedded output profiles.

    if changed:
        with open(SEED_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Migration applied successfully.")
    else:
        print("No changes needed. Migration already applied.")

if __name__ == "__main__":
    migrate()
