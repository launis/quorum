"""Database export utility."""

import json
import os

from tinydb import TinyDB

# from backend_v2.config import DB_PATH # Removed

# Paths (mirroring seeder.py)
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
# DB_PATH imported from config
SEED_DATA_PATH = os.path.join(DATA_DIR, "seed_data.json")


def export_db_to_files(source_db_path=None):  # type: ignore
    """Exports the current state of the database back to `seed_data.json`."""
    from backend_v2.settings import get_settings

    settings = get_settings()

    db_path_to_use = source_db_path if source_db_path else settings.start_db_path
    print(f"Starting export from DB ({db_path_to_use}) to files...")

    db = TinyDB(db_path_to_use, encoding="utf-8")
    components_table = db.table("components")
    workflows_table = db.table("workflows")
    steps_table = db.table("steps")

    # 2. Export Workflows and Steps to seed_data.json
    # We need to reconstruct the seed_data.json structure
    # Note: We are NOT exporting fragments here, as they are not currently stored as distinct entities in the DB
    # (they are rendered into components).

    try:
        # Read existing seed_data to preserve other fields if any
        if os.path.exists(settings.seed_data_path):
            with open(settings.seed_data_path, encoding="utf-8") as f:
                seed_data = json.load(f)
        else:
            seed_data = {"components": [], "steps": [], "workflows": []}

        # Update workflows
        seed_data["workflows"] = workflows_table.all()

        # Update steps
        seed_data["steps"] = steps_table.all()

        # Update components
        seed_data["components"] = components_table.all()

        # Update system_config (CRITICAL for Model Mapping and BARS)
        system_config_table = db.table("system_config")
        if system_config_table:
            seed_data["system_config"] = system_config_table.all()

        # Update Knowledge Base
        kb_tables = ["concepts", "references", "claims"]
        for t in kb_tables:
            if t in db.tables():
                seed_data[t] = db.table(t).all()
            else:
                seed_data[t] = []
            # We filter out claims or concepts?
            # CoachAgent loads ALL types (concept + reference).
            # But seed_data.json usually only needs references if we want to bootstrap Mock.
            # However, for full state, export EVERYTHING.
            # But wait: 'claims' are huge and verbose.
            # CoachAgent prepare_context only looks for 'concept' and 'reference'.
            # And user specifically wants REFERENCES (bibliography).
            # Let's export everything.

        # Remove 'content' from components in seed_data if it maps to a template?
        # seeder.py logic:
        # if comp_id in template_map: render template -> legacy_prompt_block['content']
        # So seed_data.json usually DOES NOT contain the content for templated items.
        # If we write the content back to seed_data.json, seeder.py will overwrite it with the template render anyway.
        # So it's safe to write it, but redundant.
        # However, for NON-templated components (if any), we MUST write the content.

        with open(settings.seed_data_path, "w", encoding="utf-8") as f:
            json.dump(seed_data, f, indent=2, ensure_ascii=False)
        print(f"Exported workflows and steps to {settings.seed_data_path}")

    except Exception as e:
        print(f"Error exporting seed data: {e}")
        raise e

    return {"status": "success", "message": "Configuration exported to files."}


if __name__ == "__main__":
    export_db_to_files()  # type: ignore
