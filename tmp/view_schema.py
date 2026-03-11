import json

def preview_prompt_schema():
    with open('c:/src/quorum/backend_v2/seed/seed_data.json', encoding='utf-8') as f:
        data = json.load(f)
    
    # Just show a random prompt block that works
    sample = [b for b in data.get('prompt_blocks', []) if b['id'] != 'block_instruction_strictness'][0]
    print(json.dumps(sample, indent=2))

if __name__ == "__main__":
    preview_prompt_schema()
