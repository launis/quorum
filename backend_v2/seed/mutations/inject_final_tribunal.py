import json

SEED_FILE = r"c:\src\quorum\backend_v2\seed\seed_data.json"

# Load the seed data
with open(SEED_FILE, encoding="utf-8") as f:
    data = json.load(f)

new_profile = {
    "name": {
        "fi": "Lopullinen Tuomioistuin (Meta-Analyysi 1D)",
        "en": "Final Tribunal (Meta-Analysis 1D)"
    },
    "layouts": [
        {
            "preset_view": "1d_metrics",
            "steps": [],
            "target_blocks": [
                "blk_bf8a99a1b3514f6c93aff42a4cc52213", # Causal Analyst
                "blk_598f9d9fab3143e1b57ae999fc5d375d", # Judge
                "blk_3c3b6a9b67bf41e88ed4b59524d6c6f3"  # XAI Reporter
            ],
            "show_text": True
        }
    ]
}

mutated = False
for workflow in data.get("workflows", []):
    if workflow.get("slug") == "kokonaisvaltainen_auditointi":
        profiles = workflow.get("output_profiles", {})
        profiles["final_tribunal"] = new_profile
        mutated = True

if mutated:
    with open(SEED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Suoritettu! Luotu Lopullinen Tuomioistuin -tulostusmäärittely.")
