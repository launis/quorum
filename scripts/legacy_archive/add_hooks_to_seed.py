import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED_DATA_PATH = os.path.join(BASE_DIR, 'data', 'seed_data.json')

def main():
    with open(SEED_DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for step in data.get('steps', []):
        if step['id'] == 'STEP_6_PERFORMATIVITY': # This is the Performativity Detector
            config = step.get('execution_config', {})
            pre_hooks = config.get('pre_hooks', [])
            if "detect_performative_patterns" not in pre_hooks:
                pre_hooks.append("detect_performative_patterns")
            config['pre_hooks'] = pre_hooks
            step['execution_config'] = config
            print(f"Added hook to {step['id']}")
            
    with open(SEED_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
if __name__ == "__main__":
    main()
