import json
from pathlib import Path

def run_deduplication():
    seed_path = Path('c:/src/quorum/backend_v2/seed/seed_data.json')
    with open(seed_path, encoding='utf-8') as f:
        data = json.load(f)

    # 1. Fix Profiler schema name in task block
    for pb in data.get('prompt_blocks', []):
        if pb['id'] == 'block_taskprofiler':
            desc_node = pb.get('description', {}).get('translations', {})
            for lang, text in desc_node.items():
                if '(ProfilerAnalysis)' in text:
                    desc_node[lang] = text.replace('(ProfilerAnalysis)', '(ProfilerOutput)')
                    print("Fixed ProfilerAnalysis -> ProfilerOutput in block_taskprofiler")

    synthesis_steps = ['step_overseer', 'step_judge', 'step_coach', 'step_xai_reporter', 'step_cognitive_judge', 'step_panel', 'step_archivist']

    for step in data.get('steps', []):
        step_id = step['id']
        prompts = step.get('prompt_blocks', [])
        
        # Guard reordering
        if step_id == 'step_guard':
            # Remove kahneman
            if 'matrix_kahneman' in prompts:
                prompts.remove('matrix_kahneman')
            # Ensure matrix_guard is before block_taskguard
            if 'matrix_guard' in prompts and 'block_taskguard' in prompts:
                prompts.remove('matrix_guard')
                idx = prompts.index('block_taskguard')
                prompts.insert(idx, 'matrix_guard')
            print("Cleaned and reordered step_guard")

        else:
            # Universal Kahneman deduplication
            if 'matrix_kahneman' in prompts and step_id != 'step_profiler':
                prompts.remove('matrix_kahneman')
                print(f"Removed matrix_kahneman from {step_id}")
            
            # Universal Goodhart deduplication
            if 'matrix_goodhart' in prompts and step_id != 'step_performativity_detector':
                prompts.remove('matrix_goodhart')
                print(f"Removed matrix_goodhart from {step_id}")
            
            # Synthesis steps: remove any other matrices that aren't their own persona
            if step_id in synthesis_steps:
                allowed_matrix = f"matrix_{step_id.replace('step_', '')}"
                to_remove = []
                for p in prompts:
                    if p.startswith('matrix_') and p != allowed_matrix:
                        to_remove.append(p)
                for p in to_remove:
                    prompts.remove(p)
                    print(f"Removed {p} from synthesis step {step_id}")

        # Add Kahneman uniquely to step_profiler
        if step_id == 'step_profiler':
            if 'matrix_kahneman' not in prompts:
                try:
                    idx = prompts.index('block_taskprofiler')
                    prompts.insert(idx, 'matrix_kahneman')
                except ValueError:
                    prompts.append('matrix_kahneman')
                print("Added matrix_kahneman to step_profiler")

        step['prompt_blocks'] = prompts

    with open(seed_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("\nSuccessfully deduplicated matrices and optimized prompt blocks.")

if __name__ == "__main__":
    run_deduplication()
