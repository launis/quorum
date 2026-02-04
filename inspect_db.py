from tinydb import TinyDB


def inspect_db():
    try:
        db = TinyDB('c:/src/quorum/data/db.json')
        workflows_table = db.table('workflows')
        steps_table = db.table('steps')

        print("--- Workflows ---")
        print("--- Workflows (Embedded Steps Check) ---")
        for wf in workflows_table.all():
            print(f"Checking Workflow: {wf.get('id')} ({wf.get('name')})")
            steps = wf.get('steps', [])
            if not isinstance(steps, list):
                print(f"  [ERROR] 'steps' is not a list: {type(steps)}")
                continue

            for idx, step in enumerate(steps):
                if isinstance(step, dict):
                    # It's an object (V2 schema)
                    s_id = step.get('id', f'INDEX_{idx}')
                    t_key = step.get('task_key')

                    if t_key is None:
                        print(f"  [ERROR] Step '{s_id}' has NULL task_key")
                    elif not isinstance(t_key, str):
                        print(f"  [ERROR] Step '{s_id}' task_key is not string: {t_key}")

                elif isinstance(step, str):
                    # It's a reference (Legacy)
                    print(f"  [INFO] Step is a reference ID: {step} (Legacy Schema)")
                    # We could check steps table here, but the crash suggests we are treating it as object

                else:
                    print(f"  [ERROR] Unknown step format at index {idx}: {step}")

            print("  OK.")

    except Exception as e:
        print(f"Error reading DB: {e}")

if __name__ == "__main__":
    inspect_db()
