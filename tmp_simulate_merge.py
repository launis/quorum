import json

# 1. Load the backups
# BASE: The one with 50+ citations but corrupted scales
with open('c:/src/quorum/backend_v2/seed/backups/seed_data_backup_2026-03-12_22-40-06.json', 'r', encoding='utf-8') as f:
    db_base = json.load(f)

# SOURCE: The pristine one with correct human-readable Finnish scales for OTHER blocks
with open('c:/src/quorum/backend_v2/seed/backups/seed_data_backup_2026-03-12_18-56-58.json', 'r', encoding='utf-8') as f:
    db_source = json.load(f)

# 2. Extract specific source blocks
source_blocks = { m.get('id'): m for m in db_source.get('prompt_blocks', []) }

# 3. Custom text generation for XAI (since it never had them)
xai_custom_texts = {
    0: "Täysin läpinäkymätön (Musta laatikko)",
    25: "Heikosti selitetty (Osittainen perustelu)",
    50: "Kohtalainen läpinäkyvyys (Looginen perusrakenne)",
    75: "Vahvasti perusteltu (Selkeät kausaalisuudet)",
    100: "Täydellinen läpinäkyvyys (Dialektinen synteesi)"
}

# 4. Simulate surgical merge in-memory
for block in db_base.get('prompt_blocks', []):
    bid = block.get('id')
    
    # Custom injection for XAI
    if bid == 'block_taskxai':
        # The scale min/max for XAI must be 4-10
        block['scale_min'] = 4
        block['scale_max'] = 10
        # Overwrite the barsConf placeholders with our new texts
        for s in block.get('scales', []):
            score = s.get('score', 0)
            text = xai_custom_texts.get(score, f"barsConf{score}")
            
            # Create translation structures if missing
            if 'name' not in s: s['name'] = {'translations': {}}
            if 'fi' not in s['name'].get('translations', {}): s['name'] = {'translations': {'fi': text}}
            else: s['name']['translations']['fi'] = text
            
            # Match claims text to the name
            if 'claims' in s and len(s['claims']) > 0:
                s['claims'][0]['translations']['fi'] = text

    # Standard merge for everything else (like block_taskguard)
    elif bid in source_blocks:
        s_block = source_blocks[bid]
        if 'scales' in s_block: block['scales'] = s_block['scales']
        if 'scale_min' in s_block: block['scale_min'] = s_block['scale_min']
        if 'scale_max' in s_block: block['scale_max'] = s_block['scale_max']

# 5. Print the final states of the requested blocks to prove the fix
guard = next((m for m in db_base.get('prompt_blocks', []) if m.get('id') == 'block_taskguard'), None)
xai = next((m for m in db_base.get('prompt_blocks', []) if m.get('id') == 'block_taskxai'), None)

print("=== PROOF: FINAL STATE OF block_taskguard ===")
print(json.dumps({
    "scales": [s.get("name", {}).get("translations", {}).get("fi") for s in guard.get("scales", [])],
    "scale_min": guard.get("scale_min"),
    "scale_max": guard.get("scale_max"),
    "theory_grounding": guard.get("theory_grounding")
}, indent=2, ensure_ascii=False))

print("\n=== PROOF: FINAL STATE OF block_taskxai ===")
print(json.dumps({
    "scales": [s.get("name", {}).get("translations", {}).get("fi") for s in xai.get("scales", [])],
    "scale_min": xai.get("scale_min"),
    "scale_max": xai.get("scale_max"),
    "theory_grounding": xai.get("theory_grounding")
}, indent=2, ensure_ascii=False))
