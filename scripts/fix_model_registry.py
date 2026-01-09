from tinydb import Query, TinyDB


def fix_registry():
    db_path = "data/db.json"
    db = TinyDB(db_path)
    table = db.table("system_config")
    Q = Query()

    # 1. Locate Registry
    registry_list = table.search(Q.type == "model_registry")
    if not registry_list:
        print("No model registry found in DB.")
        return

    # 2. Prepare Update
    # We want to force a safe configuration for "deep" in "google"
    # SAFE MODEL: gemini-2.5-pro (Confirmed available in europe-north1)
    SAFE_DEEP = "vertex_ai/gemini-2.5-pro"
    SAFE_FAST = "vertex_ai/gemini-2.5-flash"

    current_models = registry_list[0].get("models", {})

    if "google" not in current_models:
        print("No google config found.")
        return

    google_conf = current_models["google"]
    deep_conf = google_conf.get("deep", {})
    fast_conf = google_conf.get("fast", {})

    print(f"Current Deep: {deep_conf.get('model_name')}")
    print(f"Current Fast: {fast_conf.get('model_name')}")

    # Always update to match the "Scientific Truth" of availability
    deep_conf["model_name"] = SAFE_DEEP
    fast_conf["model_name"] = SAFE_FAST

    google_conf["deep"] = deep_conf
    google_conf["fast"] = fast_conf
    current_models["google"] = google_conf

    # 3. Apply Update
    table.update({"models": current_models}, Q.type == "model_registry")
    print(f"✅ Registry updated to Deep={SAFE_DEEP}, Fast={SAFE_FAST}")


if __name__ == "__main__":
    fix_registry()
