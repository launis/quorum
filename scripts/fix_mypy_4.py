import os
import re

tests_dir = 'backend_v2/tests/unit'
for root, _, files in os.walk(tests_dir):
    for f in files:
        if not f.endswith('.py'):
            continue
        path = os.path.join(root, f)
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        orig = content

        # Fix single argument instantiations
        content = re.sub(r'BlueprintTransformer\(\s*([a-zA-Z0-9_]+)\s*\)', r'BlueprintTransformer(exec_repo=\1, workflow_repo=\1, comp_repo=\1, identity_repo=\1)', content)
        content = re.sub(r'DAGExecutor\(\s*([a-zA-Z0-9_]+)\s*\)', r'DAGExecutor(exec_repo=\1, workflow_repo=\1, comp_repo=\1, system_repo=\1, identity_repo=\1, audit_repo=\1, prompt_compiler=MagicMock())', content)
        content = re.sub(r'ExecutionService\(\s*([a-zA-Z0-9_]+)\s*\)', r'ExecutionService(exec_repo=\1)', content)
        content = re.sub(r'HookDependencies\(\s*([a-zA-Z0-9_]+)\s*\)', r'HookDependencies(exec_repo=\1, workflow_repo=\1, comp_repo=\1, identity_repo=\1, audit_repo=\1, system_repo=\1)', content)
        content = re.sub(r'LogicNodeStrategy\(\s*([a-zA-Z0-9_]+)\s*\)', r'LogicNodeStrategy(exec_repo=\1, workflow_repo=\1, comp_repo=\1, identity_repo=\1, audit_repo=\1, system_repo=\1, prompt_compiler=MagicMock())', content)
        content = re.sub(r'LLMNodeStrategy\(\s*([a-zA-Z0-9_]+)\s*\)', r'LLMNodeStrategy(exec_repo=\1, workflow_repo=\1, comp_repo=\1, identity_repo=\1, audit_repo=\1, system_repo=\1, prompt_compiler=MagicMock())', content)
        content = re.sub(r'DummyStrategy\(\s*([a-zA-Z0-9_]+)\s*\)', r'DummyStrategy(exec_repo=\1, workflow_repo=\1, comp_repo=\1, identity_repo=\1, audit_repo=\1, system_repo=\1, prompt_compiler=MagicMock())', content)
        content = re.sub(r'UsageService\(\s*([a-zA-Z0-9_]+)\s*\)', r'UsageService(audit_repo=\1, identity_repo=\1)', content)

        if content != orig:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

