import json
import sys
import traceback
from pathlib import Path

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path.cwd()))

from backend.seed.seed_registry import STANDARD_REGISTRY

def run_validation():
    try:
        with open('data/db.json', encoding='utf-8') as f:
            db = json.load(f)

        tables = db.get('_default', db)
        
        total_errors = 0
        total_validated = 0
        
        for table_key, registry_info in STANDARD_REGISTRY.items():
            table_name = registry_info.get("table", table_key)
            model_adapter = registry_info.get("model")

            if table_name not in tables:
                print(f'\n--- Skipping {table_name}: not in db.json ---')
                continue
                
            items = tables[table_name]
            
            if isinstance(items, dict):
                item_list = list(items.values())
            else:
                item_list = items
                
            print(f'\n--- Validating {table_name} ---')
            table_errors = 0
            for idx, item in enumerate(item_list):
                try:
                    model_adapter.validate_python(item)
                    total_validated += 1
                except Exception as e:
                    item_id = item.get('id', 'UNKNOWN')
                    print(f'Validation Error in {table_name} item {item_id}:')
                    print(e)
                    table_errors += 1
                    total_errors += 1
                    if table_errors > 3:
                        print('...too many errors, stopping for this table.')
                        break
            
            if table_errors == 0:
                print(f'✅ All {len(item_list)} records passed Pydantic layout validation.')

        print(f'\nTotal Records Validated: {total_validated}')
        print(f'Total Validation Errors: {total_errors}')
        
    except Exception as e:
        traceback.print_exc()

if __name__ == '__main__':
    run_validation()
