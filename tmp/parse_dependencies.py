import ast
import os

target_models = {
    'step_guard': 'GuardInput',
    'step_retrieval_agent': 'RetrievalInput',
    'step_analyst': 'AnalystInput',
    'step_interaction_analyst': 'InteractionInput',
    'step_profiler': 'ProfilerInput',
    'step_logician': 'LogicianInput',
    'step_falsifier': 'FalsifierInput',
    'step_causal_analyst': 'CausalInput',
    'step_performativity_detector': 'PerformativityInput',
    'step_overseer': 'OverseerInput',
    'step_archivist': 'ArchivistInput',
    'step_judge': 'JudgeInput',
    'step_coach': 'CoachInput',
    'step_xai_reporter': 'XAIReporterInput'
}

domain_path = 'c:/src/quorum/backend_v2/models/domain'
requirements = {}

for filename in os.listdir(domain_path):
    if not filename.endswith('.py'): continue
    filepath = os.path.join(domain_path, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name in target_models.values():
            reqs = []
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    if item.target.id.startswith('step_'):
                        reqs.append(item.target.id)
            
            # Find the step id mapping
            step_id = [k for k, v in target_models.items() if v == node.name][0]
            requirements[step_id] = reqs

print("--- EXPLICIT REQUIRED 'step_' FIELDS ---")
for s_id, reqs in requirements.items():
    print(f"{s_id}: {reqs}")
