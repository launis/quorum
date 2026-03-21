import json


def fix_dag_dependencies():
    path = 'c:/src/quorum/backend_v2/seed/seed_data.json'
    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    for rule in data['workflows'][0]['steps']:
        deps = rule.get('depends_on', [])
        if 'steprule_fact_checker_v2_001' in deps:
            deps.remove('steprule_fact_checker_v2_001')
            print(f"Removed ghost dependency from {rule.get('id')} ({rule.get('task_blueprint')})")

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        print("Scrubbed DAG cleanly.")

if __name__ == "__main__":
    fix_dag_dependencies()
