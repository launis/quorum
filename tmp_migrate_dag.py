import json
import sys
import copy

def main():
    seed_path = 'c:/src/quorum/backend_v2/seed/seed_data.json'
    
    print("Loading seed_data.json...")
    with open(seed_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"Loaded {len(data.get('steps', []))} steps and {len(data.get('workflows', []))} workflows.")

    # 1. Remove apply_scoring_logic from step_judge
    judge_step = next((s for s in data.get("steps", []) if s.get("id") == "step_64a49f52b7394d9e99b92bb0397a6049"), None)
    if judge_step and "post_hooks" in judge_step:
        if "apply_scoring_logic" in judge_step["post_hooks"]:
            judge_step["post_hooks"].remove("apply_scoring_logic")
            print("SUCCESS: Removed 'apply_scoring_logic' from step_judge.")
        else:
            print("INFO: 'apply_scoring_logic' not found in step_judge post_hooks. Already removed?")

    # 2. Create the Sink 2 Scoring Step at root
    scoring_step_exists = any(s.get("id") == "step_scoreengine1" for s in data.get("steps", []))
    if not scoring_step_exists:
        data["steps"].append({
            "id": "step_scoreengine1",
            "slug": "step_scoreengine1",
            "type": "logic",
            "hook": "apply_scoring_logic",
            "name": {
                "default_locale": "en",
                "translations": {"en": "Scoring Engine", "fi": "Scoring Engine"}
            },
            "description": {
                "default_locale": "en",
                "translations": {"en": "Aggregates final holistic scores", "fi": "Laskee loppupisteet"}
            }
        })
        print("SUCCESS: Appended 'step_scoring' root logical step.")

    # 3. Update Workflows (Sink 1 and Sink 2 connections)
    target_workflow_ids = ["wf_d653170e174847559e08af42b938d826", "wf_2d708ece6cd9"]
    for w in data.get("workflows", []):
        if w.get("id") in target_workflow_ids:
            print(f"Processing workflow {w.get('id')} ({w.get('name', {}).get('default_locale', '')})")
            
            xai_reporter_rule = next((r for r in w.get("steps", []) if r.get("id") == "steprule_8071dfe6c2a84663b4429bc44a83381e1"), None)
            
            if xai_reporter_rule:
                # Find its current parent (factcheck)
                parents = xai_reporter_rule.get("depends_on", [])
                if parents:
                    primary_parent = parents[0] # Usually steprule_factcheck1234ab
                    
                    # Find all other siblings that depend on this primary parent
                    siblings = [r['id'] for r in w["steps"] if primary_parent in r.get("depends_on", []) and r['id'] != xai_reporter_rule['id']]
                    
                    if siblings:
                        # Make XAI reporter depend on all these siblings
                        xai_reporter_rule["depends_on"] = copy.deepcopy(siblings)
                        print(f"SUCCESS: XAI Reporter now depends on {len(siblings)} parallel evaluators.")
                    else:
                        print("WARNING: Found no parallel siblings to funnel into XAI Reporter.")

                # Add the Sink 2 rule
                rule_scoring_id = "steprule_scoreengine1"
                scoring_rule_exists = any(r.get("id") == rule_scoring_id for r in w.get("steps", []))
                
                if not scoring_rule_exists:
                    w["steps"].append({
                        "id": rule_scoring_id,
                        "task_blueprint": "step_scoreengine1",
                        "depends_on": [xai_reporter_rule["id"]]
                    })
                    print("SUCCESS: Appended 'steprule_scoreengine1' to DAG funnel.")
            else:
                print(f"WARNING: XAI Reporter rule not found in workflow {w.get('id')}! Skipping DAG wire...")

    print("Saving modified seed_data.json...")
    with open(seed_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print("Migration script completed seamlessly!")

if __name__ == '__main__':
    main()
