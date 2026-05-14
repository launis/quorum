import json

def extract_block():
    with open('backend_v2/seed/seed_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for block in data.get('prompt_blocks', []):
        if block.get('id') == 'blk_80732a33fe1947ee':
            with open('scratch/block_8073.json', 'w', encoding='utf-8') as out_f:
                json.dump(block, out_f, indent=2, ensure_ascii=False)
            print("Wrote to scratch/block_8073.json")
            return
            
    print("Block not found!")

if __name__ == '__main__':
    extract_block()
