import json
import os

src_path = 'c:/src/quorum/backend/seed/seed_data.json'
dst_path = 'c:/src/quorum/backend_v2/seed/seed_data.json'

with open(src_path, 'r', encoding='utf-8') as f:
    v1_data = json.load(f)

# Extract only SystemConfig (model registry)
configs = [c for c in v1_data.get('system_config', []) if c.get('type') == 'model_registry']
system_config = []
if configs:
    system_config.append({
        "id": "global_settings",
        "model_mappings": {
            "analyst_model": configs[0]["models"]["google"]["fast"]["model_name"],
            "judge_model": configs[0]["models"]["google"]["precise"]["model_name"],
        },
        "active_settings": {}
    })

# V2: We need Workflow, Agent, and UniversalMatrix
v2_data = {
    "system_config": system_config,
    "workflows": [],
    "agents": [],
    "matrices": []
}

# Add some fundamental agents (instead of steps config)
v2_data["agents"] = [
    {
        "id": "agent_analyst",
        "name": {
            "default_locale": "fi",
            "translations": {"fi": "Analyytikko", "en": "Analyst"}
        },
        "model_role": "analyst_model",
        "pre_hooks": ["calculate_text_metrics"],
        "post_hooks": ["verify_citation_integrity"]
    },
    {
        "id": "agent_judge",
        "name": {
            "default_locale": "fi",
            "translations": {"fi": "Tuomari", "en": "Judge"}
        },
        "model_role": "judge_model",
        "pre_hooks": [],
        "post_hooks": ["apply_scoring_logic"]
    }
]

# Add a sample matrix constraint
v2_data["matrices"] = [
    {
        "id": "matrix_logic_fallacy",
        "label": {
            "default_locale": "fi",
            "translations": {"fi": "Looginen Virhepäätelmä", "en": "Logical Fallacy"}
        },
        "description": {
            "default_locale": "fi",
            "translations": {"fi": "Etsii loogisia virhepäätelmiä argumentaatiosta.", "en": "Looks for logical fallacies."}
        },
        "type": "float",
        "allow_decimals": True,
        "strictness_level": 90,
        "require_justification": True,
        "theory_grounding": None
    }
]

# Write out the clean V2 seed
os.makedirs(os.path.dirname(dst_path), exist_ok=True)
with open(dst_path, 'w', encoding='utf-8') as f:
    json.dump(v2_data, f, indent=4)

print(f"Wrote clean V2 seed to {dst_path}")
