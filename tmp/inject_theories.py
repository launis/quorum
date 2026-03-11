import json
from pathlib import Path

def apply_theory_grounding():
    seed_path = Path('c:/src/quorum/backend_v2/seed/seed_data.json')
    with open(seed_path, encoding='utf-8') as f:
        data = json.load(f)

    # 1. Define the theories for each block
    theories = {
        'block_taskxai': {
            'citation_reference': "Hegel, G. W. F. (1807). Phenomenology of Spirit (Dialectical Synthesis); Gunning, D., et al. (2019). XAI—Explainable artificial intelligence.",
            'source_url': "https://doi.org/10.1126/scirobotics.aay7120"
        },
        'block_taskinteraction': {
            'citation_reference': "Argyris, C., & Schön, D. A. (1974). Theory in practice: Increasing professional effectiveness. (Espoused theory vs. Theory-in-use).",
            'source_url': "https://psycnet.apa.org/record/1975-08149-000"
        },
        'block_taskarchivist': {
            'citation_reference': "Schauer, F. (1987). Precedent. Stanford Law Review, 39(3), 571-605. (Stare Decisis).",
            'source_url': "https://doi.org/10.2307/1228760"
        },
        'block_taskcausal': {
            'citation_reference': "Pearl, J., & Mackenzie, D. (2018). The Book of Why: The New Science of Cause and Effect.",
            'source_url': "https://plato.stanford.edu/entries/causal-models/"
        },
        'block_taskguard': {
            'citation_reference': "OWASP Foundation (2025). OWASP Top 10 for Large Language Model Applications. (System Threat Modeling).",
            'source_url': "https://owasp.org/www-project-top-10-for-large-language-model-applications/"
        }
    }

    modified = []
    
    # 2. Inject them
    for pb in data.get('prompt_blocks', []):
        if pb['id'] in theories:
            # Change category if it's currently 'instruction' or something generic
            # Based on standard seed conventions, we'll set it to 'scientific_theory' 
            # if we are explicitly injecting a theory.
            pb['category_id'] = 'scientific_theory'
            pb['theory_grounding'] = theories[pb['id']]
            modified.append(pb['id'])
            
    # Save back
    with open(seed_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Theory grounding applied to: {modified}")

if __name__ == "__main__":
    apply_theory_grounding()
