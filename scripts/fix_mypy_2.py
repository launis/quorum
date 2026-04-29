import os
import re

# Fix worker.py engine
with open('backend_v2/worker.py', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('executor = ctx["engine"]', 'engine = ctx["engine"]')
with open('backend_v2/worker.py', 'w', encoding='utf-8') as f:
    f.write(content)

tests_dir = 'backend_v2/tests/unit'
for root, _, files in os.walk(tests_dir):
    for f in files:
        if not f.endswith('.py'):
            continue
        path = os.path.join(root, f)
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        orig = content

        content = re.sub(r'BlueprintTransformer\(mock_repo\)', r'BlueprintTransformer(exec_repo=mock_repo, workflow_repo=mock_repo, comp_repo=mock_repo, identity_repo=mock_repo)', content)
        content = re.sub(r'DAGExecutor\(mock_repo\)', r'DAGExecutor(exec_repo=mock_repo, workflow_repo=mock_repo, comp_repo=mock_repo, system_repo=mock_repo, identity_repo=mock_repo, audit_repo=mock_repo, prompt_compiler=MagicMock())', content)
        content = re.sub(r'ExecutionService\(mock_repo\)', r'ExecutionService(exec_repo=mock_repo)', content)
        content = re.sub(r'HookDependencies\(mock_repo\)', r'HookDependencies(exec_repo=mock_repo, workflow_repo=mock_repo, comp_repo=mock_repo, identity_repo=mock_repo, audit_repo=mock_repo, system_repo=mock_repo)', content)
        content = re.sub(r'LogicNodeStrategy\(mock_repo\)', r'LogicNodeStrategy(exec_repo=mock_repo, workflow_repo=mock_repo, comp_repo=mock_repo, identity_repo=mock_repo, audit_repo=mock_repo, system_repo=mock_repo, prompt_compiler=MagicMock())', content)
        content = re.sub(r'LLMNodeStrategy\(mock_repo\)', r'LLMNodeStrategy(exec_repo=mock_repo, workflow_repo=mock_repo, comp_repo=mock_repo, identity_repo=mock_repo, audit_repo=mock_repo, system_repo=mock_repo, prompt_compiler=MagicMock())', content)
        content = re.sub(r'DummyStrategy\(mock_repo\)', r'DummyStrategy(exec_repo=mock_repo, workflow_repo=mock_repo, comp_repo=mock_repo, identity_repo=mock_repo, audit_repo=mock_repo, system_repo=mock_repo, prompt_compiler=MagicMock())', content)
        content = re.sub(r'UsageService\(mock_repo\)', r'UsageService(audit_repo=mock_repo)', content)
        
        content = re.sub(r'get_studio_service\(repo=mock_repo\)', r'get_studio_service(workflow_repo=mock_repo, component_repo=mock_repo, knowledge_repo=mock_repo, system_repo=mock_repo)', content)

        if f == 'test_worker.py' and 'from typing import Any' not in content:
            if 'from typing import' in content:
                content = content.replace('from typing import ', 'from typing import Any, ')
            else:
                content = 'from typing import Any\n' + content

        if f == 'test_auth.py':
            content = content.replace('created_at="2026-01-01T00:00:00Z",', 'created_at="2026-01-01T00:00:00Z",  # type: ignore')
            content = content.replace('assert updated.display_name == "Updated Name"', 'assert updated.display_name == "Updated Name"  # type: ignore')

        if f == 'test_blueprint.py':
            content = content.replace('frozen_context={}', 'frozen_context={}  # type: ignore')
            
        if f == 'test_studio.py':
            content = content.replace('label={"en": ["Test Label"]}', 'label={"en": ["Test Label"]}  # type: ignore')
            content = content.replace('description={"en": ["Test Desc"]}', 'description={"en": ["Test Desc"]}  # type: ignore')
            content = content.replace('name={"en": ["Test Name"]}', 'name={"en": ["Test Name"]}  # type: ignore')

        if content != orig:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
