from tinydb import TinyDB, Query

def fix_db():
    try:
        db = TinyDB('c:/src/quorum/data/db.json')
        steps_table = db.table('steps')
        
        all_ids = [s.get('id') for s in steps_table.all()]
        print(f"Total steps: {len(all_ids)}")
        if 'custom_reporter' in all_ids:
            print("Confirmed: 'custom_reporter' exists in step list.")
        else:
            print("WARNING: 'custom_reporter' NOT found in step list.")
            # Print closely matching
            for i in all_ids:
                if 'custom' in i:
                    print(f"  Found similar: '{i}'")

        # Force Update
        print("Attempting update...")
        Step = Query()
        result = steps_table.update({'task_key': 'report_generator'}, Step.id == 'custom_reporter')
        print(f"Update result: {result}")
        
        # Verify
        updated = steps_table.get(Step.id == 'custom_reporter')
        print(f"Post-update step: {updated}")

    except Exception as e:
        print(f"Error updating DB: {e}")

if __name__ == "__main__":
    fix_db()
