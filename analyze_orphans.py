import json

SEED_FILE = r"C:\src\quorum\backend_v2\seed\seed_data.json"

target_prefixes = [
    "block_headerrules",
    "block_headerprotocols",
    "block_headerinstructions",
    "block_mandate2",
    "block_mandate3",
    "block_mandate5",
    "block_rule1",
    "block_rule2",
    "block_rule3",
    "block_rule4",
    "block_rule5",
    "block_rule6",
    "block_oprule1",
    "block_oprule2",
    "block_oprule3",
    "block_oprule4",
    "block_protocol1",
    "block_protocol3",
    "block_protocol4",
    "block_principle1",
    "block_requirement1",
    "block_heuristic1",
    "block_heuristic2",
    "block_heuristic3"
]

with open(SEED_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

for block in data.get("prompt_blocks", []):
    if block["id"] in target_prefixes:
        print(f"\n================ {block['id']} ================")
        trans = block.get('description', {}).get('translations', {})
        print(f"FI: {trans.get('fi', 'MISSING')[:200]}...")
        print(f"EN: {trans.get('en', 'MISSING')[:200]}...")
