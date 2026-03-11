import json
from pathlib import Path

db_backup_path = r'C:\src\quorum\data\backups\db_v2.json.20260311_144330.bak'
backup_dir = Path(r'c:\src\quorum\backend_v2\seed\backups')
backup_dir.mkdir(parents=True, exist_ok=True)
backup_out = backup_dir / 'seed_data_pre_purge.json'

with open(db_backup_path, encoding='utf-8') as f:
    tinydb_data = json.load(f)

def extract_table(table_name):
    table = tinydb_data.get('_default', {}) if table_name == '_default' else tinydb_data.get(table_name, {})
    return list(table.values())

pre_purge_seed = {
    'system_config': extract_table('system_config'),
    'workflows': extract_table('workflows'),
    'agents': extract_table('agents'),
    'steps': extract_table('steps'),
    'prompt_blocks': extract_table('prompt_blocks'),
    'output_configs': extract_table('output_configs'),
    'dimensions': extract_table('dimensions'),
    'references': extract_table('references'),
    'organizations': extract_table('organizations'),
    'users': extract_table('users')
}

with open(backup_out, 'w', encoding='utf-8') as f:
    json.dump(pre_purge_seed, f, indent=2, ensure_ascii=False)

print(f"Successfully reconstructed pre-purge seed_data.json to {backup_out}")
print(f"Workflows: {len(pre_purge_seed['workflows'])}")
print(f"Steps: {len(pre_purge_seed['steps'])}")
print(f"Prompt Blocks: {len(pre_purge_seed['prompt_blocks'])}")
