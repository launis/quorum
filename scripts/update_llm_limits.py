import json


def update_limits(filepath):
    print(f"Updating limits in {filepath}...")
    try:
        with open(filepath, encoding='utf-8') as f:
            data = json.load(f)

        updated = False

        # Etsitään system_config
        system_configs = []
        if isinstance(data, dict) and "system_config" in data:
            system_configs = data["system_config"]
        elif isinstance(data, list):
            # Mahdollisesti lista suoraan
            system_configs = data

        for config in system_configs:
            if isinstance(config, dict) and config.get("type") == "model_registry":
                models = config.get("models", {}).get("google", {})
                for model_key, model_props in models.items():
                    if isinstance(model_props, dict):
                        if model_key == "deep":
                            model_props["tpm_limit"] = 100000
                            model_props["rpm_limit"] = 10  # vertex pro limit
                            updated = True
                        elif model_key == "fast":
                            model_props["tpm_limit"] = 100000
                            model_props["rpm_limit"] = 15  # vertex flash limit
                            updated = True
                        elif model_key in ["precise", "strict"]:
                            model_props["tpm_limit"] = 100000
                            model_props["rpm_limit"] = 10
                            updated = True

        if updated:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("Päivitys onnistui.")
        else:
            print("Ei päivitettävää löytynyt tai tietorakenne ei vastannut oletusta.")

    except FileNotFoundError:
        print(f"Tiedostoa ei löytynyt: {filepath}")
    except Exception as e:
        print(f"Virhe: {e}")

# Päivitetään seed-data
update_limits("c:/src/quorum/backend/seed/seed_data.json")

# Päivitetään db_mock
update_limits("c:/src/quorum/backend/database/db_mock.json")
