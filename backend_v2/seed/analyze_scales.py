import json


def main():
    with open('backend_v2/seed/seed_data.json', encoding='utf-8') as f:
        data = json.load(f)

    prompt_blocks = data.get('prompt_blocks', [])

    with open('matrix_analysis.txt', 'w', encoding='utf-8') as out:
        for block in prompt_blocks:
            scales = block.get('scales')
            if not scales:
                continue

            out.write(f"PromptBlock: {block.get('slug')} (ID: {block.get('id')})\n")
            for scale in scales:
                score = scale.get('score')
                name = scale.get('name', {})
                en_name = name.get('translations', {}).get('en', 'N/A')
                fi_name = name.get('translations', {}).get('fi', 'N/A')
                ai_desc = scale.get('ai_description', 'N/A')

                out.write(f"  Score {score}:\n")
                out.write(f"    Name (fi): {fi_name}\n")
                out.write(f"    Name (en): {en_name}\n")
                out.write(f"    ai_desc:   {ai_desc}\n")

                claims = scale.get('claims', [])
                for i, claim in enumerate(claims):
                    en_claim = claim.get('translations', {}).get('en', 'N/A')
                    fi_claim = claim.get('translations', {}).get('fi', 'N/A')
                    out.write(f"    Claim {i+1} (fi): {fi_claim}\n")
                    out.write(f"    Claim {i+1} (en): {en_claim}\n")
            out.write("\n")

if __name__ == "__main__":
    main()
