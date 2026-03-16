import json


def fix_rate_limits():
    path = "c:/src/quorum/backend/seed/seed_data.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    configs = data.get("system_config", [])
    updated = 0

    for c in configs:
        if c.get("id") == "model_registry":
            models = c.get("models", {}).get("google", {})

            # Heavy reasoning (Gemini 2.5 Pro) -> deep, precise, strict
            for strat in ["deep", "precise", "strict"]:
                if strat in models:
                    models[strat]["rpm_limit"] = 15
                    models[strat]["tpm_limit"] = 100000
                    updated += 1

            # Fast interaction (Gemini 2.5 Flash) -> fast
            if "fast" in models:
                models["fast"]["rpm_limit"] = 60
                models["fast"]["tpm_limit"] = 500000
                updated += 1

    print(f"Updated {updated} Google models in model_registry.")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    fix_rate_limits()
