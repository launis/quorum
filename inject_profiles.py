import json
import os

seed_path = r'backend_v2\seed\seed_data.json'

with open(seed_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for w in data.get('workflows', []):
    if w.get('slug') == 'kokonaisvaltainen_auditointi':
        steps = [s.get('id') for s in w.get('steps', [])]
        
        w['output_profiles'] = {
            "default": {     
                "name": {"fi": "Kokonaisraportti (Oletus)", "en": "Full Report (Default)"},
                "layouts": [
                    {"preset_view": "3d_complex", "steps": steps, "show_text": True},
                    {"preset_view": "1d_metrics", "steps": steps, "show_text": True}
                ]
            },
            "executive": {   
                "name": {"fi": "Johdon tiivistelmä", "en": "Executive Summary"},
                "layouts": [
                    {"preset_view": "text_only", "steps": steps[:3], "show_text": True},
                    {"preset_view": "3d_complex", "steps": steps, "show_text": False}
                ]
            },
            "employee": {    
                "name": {"fi": "Työntekijän raportti", "en": "Employee Report"},
                "layouts": [
                    {"preset_view": "1d_metrics", "steps": steps[3:8], "show_text": False}
                ]
            },
            "deep_dive": {   
                "name": {"fi": "Syväluotaus (Loppuosa)", "en": "Deep Dive (Latter half)"},
                "layouts": [
                    {"preset_view": "2d_compare", "steps": steps[8:12], "show_text": True},
                    {"preset_view": "1d_metrics", "steps": steps[8:], "show_text": True}
                ]
            },
            "financial": {   
                "name": {"fi": "Talousnäkökulma", "en": "Financial Perspective"},
                "layouts": [
                    {"preset_view": "1d_metrics", "steps": steps[:2], "show_text": True}
                ]
            },
            "visual": {      
                "name": {"fi": "Visuaalinen katsaus", "en": "Visual Overview"},
                "layouts": [
                    {"preset_view": "3d_complex", "steps": steps, "show_text": False},
                    {"preset_view": "2d_compare", "steps": steps[:5], "show_text": False}
                ]
            }
        }
        break

with open(seed_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Injected explicit steps into 6 profiles successfully.")
