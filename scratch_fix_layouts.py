import json

with open("backend_v2/seed/seed_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data.get("output_profiles", []):
    if item.get("slug") == "holistic_audit":
        old_layouts = item["layouts"]
        
        idx_0 = old_layouts[0] 
        idx_rest = old_layouts[4:]
        
        # Strip the errant description from [4]
        if "description" in idx_rest[0]:
            del idx_rest[0]["description"]
            
        c1 = {
            "preset_view": "2d_compare",
            "is_synthesis_enabled": True,
            "title": {
                "default_locale": "en",
                "translations": { "en": "DETAILED SCORING ASSESSMENT", "fi": "ARVIOINNIN YKSITYISKOHTAINEN PISTEYTYS" }
            },
            "description": {
                "default_locale": "en",
                "translations": { "en": "Data verifiability and logical structure.", "fi": "Datan todennettavuus ja looginen rakenne." }
            },
            "target_blocks": ["blk_440a5fef9331451b", "blk_53f32679aa514fcb", "blk_109dab5b6b3f403a"],
            "synthesis": {
                "row_explanations_block_id": "sp_row_explanations",
                "system_prompt": "You are an objective analytical reporting engine. Synthesize the provided execution data into a professional summary. Do not re-evaluate the raw claims or perform independent logical deduction. Output clear, concise, and highly readable text.",
                "length_constraint": 800,
                "preamble_text": {
                    "default_locale": "fi",
                    "translations": {
                        "fi": "**Looginen perusta (Toulmin), ajatteluvääristymät (Kahneman) ja suorituskykyharha (Goodhart)**",
                        "en": "**Structural Logic (Toulmin), Cognitive Bias (Kahneman), and Performativity Risk (Goodhart)**"
                    }
                }
            }
        }
        
        c2 = old_layouts[3]
        
        c3 = {
            "preset_view": "2d_compare",
            "is_synthesis_enabled": True,
            "title": {
                "default_locale": "en",
                "translations": { "en": "DETAILED SCORING ASSESSMENT", "fi": "ARVIOINNIN YKSITYISKOHTAINEN PISTEYTYS" }
            },
            "description": {
                "default_locale": "fi",
                "translations": {
                    "en": "Risk measure of cryptic assumptions, internal contradiction, and post-hoc rationalization.",
                    "fi": "Kryptisten oletusten, sisäisen ristiriitaisuuden ja jälkikäteisen selittelyn riskimitta."
                }
            },
            "target_blocks": ["blk_6b8c766185294f7e", "blk_f6e286f050c94d60"],
            "synthesis": {
                "row_explanations_block_id": "sp_row_explanations",
                "system_prompt": "You are an objective analytical reporting engine. Synthesize the provided execution data into a professional summary. Do not re-evaluate the raw claims or perform independent logical deduction. Output clear, concise, and highly readable text.",
                "length_constraint": 800,
                "preamble_text": {
                    "default_locale": "fi",
                    "translations": {
                        "fi": "**Datan ankkurointi, sisäinen logiikka ja jälkikäteinen selittely**",
                        "en": "**Data anchoring, internal logic, and post-hoc rationalization**"
                    }
                }
            }
        }
        
        m3d = old_layouts[2].copy()
        m3d["preset_view"] = "3d_matrix"
        m3d["is_synthesis_enabled"] = False
        m3d["title"] = {
            "default_locale": "en",
            "translations": { "en": "MATRIX SUMMARY", "fi": "YHTEENVETO / MATRIX SUMMARY" }
        }
        m3d["description"] = {
            "default_locale": "en",
            "translations": { "en": "Detailed explanations and corrective actions.", "fi": "Yksityiskohtaiset selitykset ja korjaavat toimenpiteet." }
        }
        m3d["target_blocks"] = [
            "blk_440a5fef9331451b", "blk_53f32679aa514fcb", "blk_109dab5b6b3f403a",
            "blk_c5804a9143c34cb1", "blk_b476f89fb732448c",
            "blk_6b8c766185294f7e", "blk_f6e286f050c94d60"
        ]
        if "synthesis" in m3d:
            del m3d["synthesis"]
            
        new_layouts = [idx_0, c1, c2, c3, m3d] + idx_rest
        item["layouts"] = new_layouts

with open("backend_v2/seed/seed_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
