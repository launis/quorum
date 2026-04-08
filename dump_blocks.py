import json
import sys

try:
    with open('c:\\src\\quorum\\backend_v2\\seed\\seed_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
except Exception as e:
    with open('c:\\src\\quorum\\backend_v2\\seed\\seed_data.json', 'r', encoding='utf-16') as f:
        data = json.load(f)

target_ids = [
    'blk_9e44687dff884ff6',
    'blk_bd7c5a9f27504a2c',
    'blk_9d68ceff695b4196',
    'blk_23ca73cf267d4078',
    'blk_2c13f67014094f3b',
    'blk_fb0b98da76e046dd',
    'blk_a5ce16009a514628',
    'blk_091db241c5154336',
    'blk_22e3598e06414409',
    'blk_f6e286f050c94d60'
]

blocks = data.get('prompt_blocks', [])
with open('c:\\src\\quorum\\blocks_analysis_dump.txt', 'w', encoding='utf-8') as out:
    for b in blocks:
        if b.get('id') in target_ids:
            out.write('----------------------------------------\n')
            out.write(f"ID: {b['id']}\n")
            
            # Helper to safely get translation
            def get_trans(node):
                if not isinstance(node, dict): return "N/A"
                trans = node.get("translations", {})
                return trans.get("fi", node.get("default_locale", "N/A"))

            out.write(f"Nimi (FI): {get_trans(b.get('name', {}))}\n")
            out.write(f"Kuvaus (FI): {get_trans(b.get('description', {}))}\n")
            out.write(f"Tyyppi: {b.get('type')}\n")
            out.write(f"AI Description:\n{b.get('ai_description', '')}\n")

print("Dumpattu tiedostoon: c:\\src\\quorum\\blocks_analysis_dump.txt")
