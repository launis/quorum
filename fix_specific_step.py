from tinydb import Query, TinyDB


def fix_specific_step():
    try:
        db = TinyDB('c:/src/quorum/data/db.json')
        steps_table = db.table('steps')

        target_id = 'custom_reporter_710fcf'
        print(f"Targeting step: {target_id}")

        Step = Query()
        target = steps_table.get(Step.id == target_id)

        if target:
            print(f"Found step: {target}")
            if target.get('task_key') is None:
                print("task_key is NULL. Patching...")
                steps_table.update({'task_key': 'custom_reporter'}, Step.id == target_id)
                print("Patch applied.")
            else:
                print(f"task_key is {target.get('task_key')}. No patch needed (unless it is not a string).")
        else:
            print(f"Step {target_id} NOT FOUND.")

    except Exception as e:
        print(f"Error updating DB: {e}")

if __name__ == "__main__":
    fix_specific_step()
