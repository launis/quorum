import json
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.api.bff_transformer import ReportTransformer
from backend.models.view import SectionType

DB_PATH = 'c:/src/quorum/data/db.json'

def main():
    try:
        with open(DB_PATH, encoding='utf-8') as f:
            data = json.load(f)

        target_table = data.get("executions", data.get("_default"))
        if not target_table:
            print("No executions found.")
            return

        sorted_keys = sorted(target_table.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))

        found_rich = False
        transformer = ReportTransformer()

        for key in reversed(sorted_keys):
            execution = target_table[key]
            # Use generous range to avoid strict errors on legacy data
            try:
                view = transformer.transform(execution, valid_range=(0.0, 10.0))

                # Check for interesting sections
                types = [s.type for s in view.sections]
                if SectionType.DATA_TABLE in types or SectionType.KEY_VALUE_GRID in types:
                    print(f"--- Rich Execution Found: {execution.get('id')} ---")
                    print("FOUND SECTIONS:")
                    for s in view.sections:
                        print(f"- {s.type} (ID: {s.id})")
                    found_rich = True
                    break
            except Exception:
                continue

        if not found_rich:
            print("No execution with Analyst/Guard data found in DB.")


    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
