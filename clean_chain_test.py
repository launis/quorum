import json

def clean_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        workflows = data.get('workflows', {})
        
        if isinstance(workflows, dict):
            # data/db.json format
            to_delete = []
            for wf_id, wf_data in workflows.items():
                if 'chain test' in wf_data.get('name', '').lower():
                    to_delete.append(wf_id)
            if to_delete:
                for wf_id in to_delete:
                    del workflows[wf_id]
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4)
                print(f"Removed {len(to_delete)} workflows from {filepath}")
            else:
                print(f"No 'Chain Test' workflows found in {filepath}")
                
        elif isinstance(workflows, list):
            # backend/seed/seed_data.json format
            original_len = len(workflows)
            filtered_workflows = [wf for wf in workflows if 'chain test' not in wf.get('name', '').lower()]
            
            if len(filtered_workflows) < original_len:
                data['workflows'] = filtered_workflows
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4)
                print(f"Removed {original_len - len(filtered_workflows)} workflows from {filepath}")
            else:
                print(f"No 'Chain Test' workflows found in {filepath}")

    except Exception as e:
        print(f"Error processing {filepath}: {e}")

clean_file('data/db.json')
clean_file('backend/seed/seed_data.json')
