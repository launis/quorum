import json

translations = {
    "Imported from sequential_audit_chain": "Imported from sequential_audit_chain",
    "Input Processing": "Input Processing",
    "Impact Verification": "Impact Verification",
    "Kognitiivinen syvyys": "Cognitive Depth",
    "Best Practices Audit": "Best Practices Audit",
    "Luottamustaso (Confidence Score)": "Confidence Level",
    "Critical Loop Audit": "Critical Loop Audit",
    "Overseer": "Overseer",
    "Archivist": "Archivist",
    "Performativiteetti ja ajaminen": "Performativity and Steering",
    "Logician": "Logician",
    "Ajattelun modaliteetti": "Modality of Thought",
    "Analyst": "Analyst",
    "Argumentaation laatu": "Argumentation Quality",
    "Lopullinen Tuomioasteikko": "Final Judgment Scale",
    "Coach": "Coach",
    "Judge": "Judge",
    "Critical Distance Score": "Critical Distance Score",
    "Profiler": "Profiler",
    "Parses files and raw text into standard variables.": "Parses files and raw text into standard variables.",
    "XAI Reporter": "XAI Reporter",
    "Falsifier": "Falsifier",
    "Guard": "Guard",
    "Performativity Detector": "Performativity Detector",
    "Causal Analyst": "Causal Analyst",
    "Kausaalinen Uskottavuus": "Causal Plausibility",
    "Illusion of Control Audit": "Illusion of Control Audit"
}

def fix_translations():
    with open('backend_v2/seed/seed_data.json', encoding='utf-8') as f:
        data = json.load(f)
        
    count = 0
    def walk(d):
        nonlocal count
        if isinstance(d, dict):
            if 'fi' in d and 'en' in d and 'Auto-filled' in d['en']:
                fi_text = d['fi']
                if fi_text in translations:
                    d['en'] = translations[fi_text]
                    count += 1
            for v in d.values():
                walk(v)
        elif isinstance(d, list):
            for i in d:
                walk(i)
                
    walk(data)
    
    with open('backend_v2/seed/seed_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Fixed {count} translations.")

fix_translations()
