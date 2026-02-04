from tinydb import Query, TinyDB

DB_PATH = 'data/db.json'

def undo_fix():
    db = TinyDB(DB_PATH)
    steps_table = db.table('steps')

    # IDs defined in previous script
    stubs = [
        'step_guard', 'step_analyst', 'step_interaction',
        'step_profiler', 'step_logician', 'step_falsifier',
        'step_causal', 'step_detector', 'step_overseer',
        # Add others if generated, but these are the main ones
    ]

    # Safe delete: Only delete if description matches my stub description
    Step = Query()
    # "description": "Auto-generated stub to fix 404"

    removed = steps_table.remove(Step.description == "Auto-generated stub to fix 404")
    print(f"Removed {len(removed)} stubs.")

if __name__ == "__main__":
    undo_fix()
