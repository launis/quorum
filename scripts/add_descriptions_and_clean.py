import json
import os

SEED_FILE = "backend/database/seed_data.json"

DESCRIPTIONS = {
    "GUARD_OUTPUT_CONFIG": "Määrittää Vartijan JSON-tulostusformaatin (SecurityCheck).",
    "ANALYST_OUTPUT_CONFIG": "Määrittää Analyytikon JSON-tulostusformaatin (TodistusKartta).",
    "PROFILER_OUTPUT_CONFIG": "Määrittää Profiloijan JSON-tulostusformaatin (KognitiivinenProfiili).",
    "LOGICIAN_OUTPUT_CONFIG": "Määrittää Loogikon JSON-tulostusformaatin (ArgumentaatioAnalyysi).",
    "FALSIFIER_OUTPUT_CONFIG": "Määrittää Falsifioijan JSON-tulostusformaatin (LogiikkaAuditointi).",
    "CAUSAL_OUTPUT_CONFIG": "Määrittää Kausaalisen analyytikon JSON-tulostusformaatin (KausaalinenAuditointi).",
    "PERFORMATIVITY_OUTPUT_CONFIG": "Määrittää Performatiivisuuden tunnistajan JSON-tulostusformaatin.",
    "OVERSEER_OUTPUT_CONFIG": "Määrittää Valvojan JSON-tulostusformaatin (EettinenKartta).",
    "ARCHIVIST_OUTPUT_CONFIG": "Määrittää Arkistonhoitajan JSON-tulostusformaatin (BestPractices).",
    "JUDGE_OUTPUT_CONFIG": "Määrittää Tuomarin JSON-tulostusformaatin (TuomioJaPisteet).",
    "COACH_OUTPUT_CONFIG": "Määrittää Valmentajan JSON-tulostusformaatin (CoachingPlan).",
    "XAI_OUTPUT_CONFIG": "Määrittää XAI-raportoijan JSON-tulostusformaatin (ExecutiveSummary).",
    "template_context_now": "Malline, joka alustaa aikakontekstin (replaced by prompt builder).",
    "template_output": "Yleinen palautusformaatin ohje JSON-skeemalle.",
    "common_scientific_method": "Yleinen tieteellisen menetelmän ohjeistus.",
    "common_bars_matrix": "Behaviorally Anchored Rating Scale -matriisi arviointiin.",
    "HEADER_TEXT": "Otsikko syötetekstille.",
    "DISCLAIMER_TEXT": "Vastuuvapauslauseke.",
}

def clean_and_describe():
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    components = data.get('components', [])
    updated_count = 0
    
    # 1. Add Descriptions
    for comp in components:
        cid = comp['id']
        if not comp.get('description'):
            if cid in DESCRIPTIONS:
                comp['description'] = DESCRIPTIONS[cid]
                updated_count += 1
            elif '_OUTPUT_' in cid:
                 comp['description'] = f"JSON Output configuration for {cid}."
                 updated_count += 1
            elif 'template_' in cid:
                 comp['description'] = f"Template component for {cid}."
                 updated_count += 1
                 
    print(f"Added descriptions to {updated_count} components.")
    
    data['components'] = components
    
    with open(SEED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print("Optimization complete.")

if __name__ == "__main__":
    clean_and_describe()
