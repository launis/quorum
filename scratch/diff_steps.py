import json
import sys

def load_steps(exe_id):
    path = f'data/files/executions/{exe_id}/execution_trace.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    steps = {}
    for step in data:
        name = step.get('step_name')
        if name and name.startswith('sr_'):
            steps[name] = step.get('content', {})
    return steps

def main():
    if len(sys.argv) < 3:
        print("Usage: python diff_steps.py <exe1> <exe2>")
        sys.exit(1)
        
    exe1 = sys.argv[1]
    exe2 = sys.argv[2]
    
    steps1 = load_steps(exe1)
    steps2 = load_steps(exe2)
    
    common_steps = set(steps1.keys()).intersection(set(steps2.keys()))
    
    out_path = 'scratch/step_comparison.md'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"# Steppikohtainen vertailu\n")
        f.write(f"- **Ajo 1:** {exe1} (Vanha/Hyvä)\n")
        f.write(f"- **Ajo 2:** {exe2} (Uusi/Ankara)\n\n")
        
        for step_name in common_steps:
            s1 = steps1[step_name]
            s2 = steps2[step_name]
            
            f.write(f"## Step: `{step_name}`\n\n")
            
            for key in ['extracted_facts', 'reasoning_trace', 'evaluation_notes']:
                v1 = s1.get(key, 'N/A')
                v2 = s2.get(key, 'N/A')
                
                f.write(f"### {key.upper()}\n")
                f.write(f"**Ajo 1:**\n> {v1}\n\n")
                f.write(f"**Ajo 2:**\n> {v2}\n\n")
                f.write("---\n")
                
    print(f"Raportti luotu: {out_path}")

if __name__ == "__main__":
    main()
