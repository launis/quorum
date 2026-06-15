import json


def check_invalid_scales():
    with open('backend_v2/seed/seed_data.json', encoding='utf-8') as f:
        data = json.load(f)
    for pb in data.get('prompt_blocks', []):
        if pb.get('category_id') == 'matrix' and 'scales' in pb:
            scores = [float(s['score']) for s in pb['scales']]
            if scores:
                if min(scores) >= max(scores):
                    print(f"Invalid scale found in block {pb['id']} ({pb.get('slug')}): scores={scores}")

if __name__ == "__main__":
    check_invalid_scales()
