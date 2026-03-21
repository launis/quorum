import json

with open('backend_v2/seed/seed_data.json', encoding='utf-8') as f:
    data = json.load(f)

for w in data['workflows']:
    profiles = w.get('output_profiles', {})
    
    # "default" profile mappings:
    if 'default' in profiles:
        for lay in profiles['default'].get('layouts', []):
            if lay['preset_view'] == '3d_complex':
                lay['target_blocks'] = ["blk_8b12be64227c4abd83e2f409b5c3ce28", "blk_d0e240184e0a40759d37138a250bd0aa", "blk_3c3b6a9b67bf41e88ed4b59524d6c6f3"]
                lay['show_text'] = True
    
    # "executive" profile mappings:
    if 'executive' in profiles:
        for lay in profiles['executive'].get('layouts', []):
            if lay['preset_view'] == '3d_complex':
                lay['target_blocks'] = ["blk_bf8a99a1b3514f6c93aff42a4cc52213", "blk_371c7724eeba40218409b5a3697ac1d3", "blk_a0405e121dbf44bfa8ee80566f8d0c2a"]
                lay['show_text'] = True 
    
    # "visual" profile mappings:
    if 'visual' in profiles:
        for lay in profiles['visual'].get('layouts', []):
            if lay['preset_view'] == '3d_complex':
                lay['target_blocks'] = ["blk_b5ec25bb352e4dc09de386f0da991a08", "blk_1e33ce78623943af9d5ce39ce6620478", "blk_9adcb55b7ba44baeaf8921cb2fb935dc"]
                lay['show_text'] = True
            if lay['preset_view'] == '2d_compare':
                lay['target_blocks'] = ["blk_bf8a99a1b3514f6c93aff42a4cc52213", "blk_635d07ae441d41e6a274911854ef8283", "blk_2878d1c8b5494180b1a5231466e2e0a9", "blk_a8e356b276f04ddeb7cc3a0eec58daf6", "blk_cf081a3325f44dc49bbe06d600f268fc"]
                lay['show_text'] = True

    # "deep_dive" profile mappings:
    if 'deep_dive' in profiles:
        for lay in profiles['deep_dive'].get('layouts', []):
            if lay['preset_view'] == '2d_compare':
                lay['target_blocks'] = ["blk_371c7724eeba40218409b5a3697ac1d3", "blk_a0405e121dbf44bfa8ee80566f8d0c2a", "blk_9adcb55b7ba44baeaf8921cb2fb935dc"]
                lay['show_text'] = True

with open('backend_v2/seed/seed_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
