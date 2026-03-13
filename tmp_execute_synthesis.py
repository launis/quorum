import json
import os
from datetime import datetime

# Paths
seed_path = 'c:/src/quorum/backend_v2/seed/seed_data.json'
backup_dir = 'c:/src/quorum/backend_v2/seed/backups'

# 1. Load the backups
# BASE: The one with 50+ citations but corrupted scales
with open(f'{backup_dir}/seed_data_backup_2026-03-12_22-40-06.json', 'r', encoding='utf-8') as f:
    db_base = json.load(f)

# SOURCE: The pristine one with correct human-readable Finnish scales for OTHER blocks
with open(f'{backup_dir}/seed_data_backup_2026-03-12_18-56-58.json', 'r', encoding='utf-8') as f:
    db_source = json.load(f)

# Optional: Back up current seed data just in case
if os.path.exists(seed_path):
    with open(seed_path, 'r', encoding='utf-8') as f:
        current_db = json.load(f)
    pre_synthesis_backup = f'{backup_dir}/seed_data_backup_pre_synthesis_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}_2.json'
    with open(pre_synthesis_backup, 'w', encoding='utf-8') as f:
        json.dump(current_db, f, indent=2, ensure_ascii=False)

# 2. Extract specific source blocks
source_blocks = { m.get('id'): m for m in db_source.get('prompt_blocks', []) }

# 3. Custom text generation for XAI
xai_custom_texts = {
    0: "Täysin läpinäkymätön (Musta laatikko)",
    25: "Heikosti selitetty (Osittainen perustelu)",
    50: "Kohtalainen läpinäkyvyys (Looginen perusrakenne)",
    75: "Vahvasti perusteltu (Selkeät kausaalisuudet)",
    100: "Täydellinen läpinäkyvyys (Dialektinen synteesi)"
}

# 4. Surgical merge
for block in db_base.get('prompt_blocks', []):
    bid = block.get('id')
    
    # Custom injection for XAI
    if bid == 'block_taskxai':
        block['scale_min'] = 4
        block['scale_max'] = 10
        # Overwrite the barsConf placeholders with our new texts
        for s in block.get('scales', []):
            score = s.get('score', 0)
            text = xai_custom_texts.get(score, f"barsConf{score}")
            if 'name' not in s: s['name'] = {'translations': {}}
            if 'fi' not in s['name'].get('translations', {}): s['name'] = {'translations': {'fi': text}}
            else: s['name']['translations']['fi'] = text
            if 'claims' in s and len(s['claims']) > 0:
                s['claims'][0]['translations']['fi'] = text

    # Standard merge for everything else
    elif bid in source_blocks:
        s_block = source_blocks[bid]
        if 'scales' in s_block: block['scales'] = s_block['scales']
        if 'scale_min' in s_block: block['scale_min'] = s_block['scale_min']
        if 'scale_max' in s_block: block['scale_max'] = s_block['scale_max']

# 5. Write back to active seed_data.json
with open(seed_path, 'w', encoding='utf-8') as f:
    json.dump(db_base, f, indent=2, ensure_ascii=False)

print("Database Synthesis Complete. Active seed_data.json has been restored and repaired.")
