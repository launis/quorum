import json

def fix_prompts():
    print("Loading seed_data.json...")
    with open('backend/seed/seed_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    for prompt in data.get('llm_prompts', []):
        name = prompt.get('name', '')
        text = prompt.get('text', '')

        bad_rule = "DO NOT calculate totals or averages. Only provide the raw qualitative score for each dimension. The Python backend will handle all mathematical calculations."
        
        # Remove the offending string introduced in the previous step
        if bad_rule in text:
            text = text.replace(bad_rule, "").strip()
            print(f"Removed bad rule from: {name}")

        # Distinguish between JUDGE and XAI REPORTER prompts
        if 'JUDGE' in name or 'Judge' in name:
            new_rule = "\n\nCRITICAL SCORING MANDATE: DO NOT calculate the `total_score` or averages. You MUST output 0.0 for `total_score` (the Python backend will calculate the true total). However, you MUST explicitly provide the `dimension_id`, `dimension_label`, `score`, and `reasoning` for EVERY dimension."
            if "CRITICAL SCORING MANDATE" not in text:
                text += new_rule
                print(f"Added precise scoring mandate to: {name}")
            prompt['text'] = text
            
        elif 'XAI' in name or 'REPORTER' in name:
            # XAI Reporter should not even attempt to output score cards
            new_rule = "\n\nCRITICAL DATA MANDATE: DO NOT attempt to populate `score_cards` or `flat_report`. The Python backend automatically injects these. You MUST omit them from your JSON response or return an empty list `[]` for `score_cards`."
            if "CRITICAL DATA MANDATE" not in text:
                text += new_rule
                print(f"Added data suppression mandate to: {name}")
            prompt['text'] = text

    print("Saving seed_data.json...")
    with open('backend/seed/seed_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Done!")

if __name__ == "__main__":
    fix_prompts()
