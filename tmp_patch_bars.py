import json
import os
from datetime import datetime

seed_path = 'c:/src/quorum/backend_v2/seed/seed_data.json'
backup_dir = 'c:/src/quorum/backend_v2/seed/backups'

# Backup first
with open(seed_path, 'r', encoding='utf-8') as f:
    db = json.load(f)
    
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
backup_file = f'{backup_dir}/seed_data_backup_bars_float_patch_{timestamp}.json'
with open(backup_file, 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print(f"Backed up to {backup_file}")

score_map = {0: 1, 25: 2, 50: 3, 75: 4, 100: 5}

for block in db.get('prompt_blocks', []):
    # 1. Update block_taskxai scores from 0,25... -> 1,2,3...
    if block.get('id') == 'block_taskxai':
        scales = block.get('scales', [])
        for scale in scales:
            old_score = scale.get('score')
            if old_score in score_map:
                scale['score'] = score_map[old_score]
                
    # 2. Ensure ALL matrix blocks allow decimals
    if 'scales' in block and len(block['scales']) > 0:
        block['allow_decimals'] = True
        
    # 3. Update instructions
    if block.get('id') == 'block_instructionstrictscale':
        desc = block.setdefault('description', {})
        trans = desc.setdefault('translations', {})
        trans['fi'] = "Arvioi jokainen kriteeri EHDOTTOMASTI sille annetun pisteytysmatriisin (BARS) pohjalta. Voit käyttää arvioinnissa vapaasti yhtä desimaalia (esim. 2.1, 3.5, 4.9), jos konteksti sijoittuu kahden annetun arvon väliin. ÄLÄ hallusinoi ohjeistamattomia skaaloja."
        trans['en'] = "Evaluate every criterion STRICTLY based on the provided BARS matrix. You may freely use one decimal place (e.g. 2.1, 3.5, 4.9) if the context falls between two defined values. DO NOT hallucinate arbitrary scales."

with open(seed_path, 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("Updated seed_data.json successfully.")
