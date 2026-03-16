import json

file_path = r'c:\src\quorum\backend_v2\seed\seed_data.json'
with open(file_path, encoding='utf-8') as f:
    data = json.load(f)

count_text_input = 0
count_gauge = 0

if 'prompt_blocks' in data:
    for block in data['prompt_blocks']:
        slug = block.get('slug', '')
        dc = block.get('display_config')
        if not dc:
            continue

        widget_type = dc.get('widget')

        # 1. Fix text_input errors
        if widget_type == 'text_input':
            # It's an unsupported widget type in SDUI for prompt blocks, change to hidden
            dc['widget'] = 'hidden'
            count_text_input += 1

        # 2. Fix gauge missing label errors
        elif widget_type == 'gauge':
            options = dc.get('options', [])
            has_label_in_options = False
            if options and isinstance(options, list) and len(options) > 0 and isinstance(options[0], dict) and 'label' in options[0]:
                has_label_in_options = True

            has_instruction = 'instruction' in dc

            if not has_instruction and not has_label_in_options:
                translations = block.get('translations', {})
                name_en = translations.get('en', {}).get('name', slug)
                name_fi = translations.get('fi', {}).get('name', slug)

                # Add instruction to satisfy SDUIBuilder
                dc['instruction'] = {
                    "en": name_en,
                    "fi": name_fi
                }
                count_gauge += 1

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Fixed {count_text_input} hidden blocks and {count_gauge} gauge blocks.")
