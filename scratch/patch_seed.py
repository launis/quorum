import json
import re

with open('backend_v2/seed/seed_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for profile in data.get('output_profiles', []):
    profile['target_block_order'] = [
        'metadata_block',
        'executive_summary_block',
        'matrix_graphs_block',
        'grouped_extensions_block',
        'penalties_block',
        'matrix_summary_table_block',
        'variance_validation_block',
        'authenticity_evaluation_block',
        'synthesis_text_block'
    ]

    for layout in profile.get('layouts', []):
        if layout.get('preset_view') in ['2d_compare', '3d_matrix', '1d_metrics', 'matrix_summary']:
            layout['text_delivery_mode'] = 'none'
        
        synthesis = layout.get('synthesis')
        if synthesis and 'ai_description' in synthesis:
            desc = synthesis['ai_description']
            desc = re.sub(r'\*\*(.*?)\*\*\\\\n\\\\n', r'### \1\\\\n\\\\n', desc)
            desc = re.sub(r'\*\*(.*?)\*\*\\n\\n', r'### \1\\n\\n', desc)
            synthesis['ai_description'] = desc

with open('backend_v2/seed/seed_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Seed data patched successfully.")
