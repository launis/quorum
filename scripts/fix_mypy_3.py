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

        content = re.sub(r'BlueprintTransformer\(\s*repository\s*=\s*([^\s,\)]+)\s*\)', r'BlueprintTransformer(exec_repo=\1, workflow_repo=\1, comp_repo=\1, identity_repo=\1)', content)
        content = re.sub(r'BlueprintTransformer\(\s*workflow_repo\s*=\s*([^\s,\)]+),\s*comp_repo\s*=\s*\1,\s*identity_repo\s*=\s*\1\s*\)', r'BlueprintTransformer(exec_repo=\1, workflow_repo=\1, comp_repo=\1, identity_repo=\1)', content)

        content = re.sub(r'HookDependencies\(\s*repository\s*=\s*([^\s,\)]+)\s*\)', r'HookDependencies(exec_repo=\1, workflow_repo=\1, comp_repo=\1, identity_repo=\1, audit_repo=\1, system_repo=\1)', content)
        content = re.sub(r'HookDependencies\.\s*repository', r'HookDependencies.exec_repo', content)

        content = re.sub(r'DAGExecutor\(\s*repository\s*=\s*([^\s,\)]+)\s*\)', r'DAGExecutor(exec_repo=\1, workflow_repo=\1, comp_repo=\1, system_repo=\1, identity_repo=\1, audit_repo=\1, prompt_compiler=MagicMock())', content)
        content = re.sub(r'ExecutionService\(\s*repo\s*=\s*([^\s,\)]+)\s*\)', r'ExecutionService(exec_repo=\1)', content)
        content = re.sub(r'UsageService\(\s*repository\s*=\s*([^\s,\)]+)\s*\)', r'UsageService(audit_repo=\1)', content)
        content = re.sub(r'UsageService\(\s*repo\s*=\s*([^\s,\)]+)\s*\)', r'UsageService(audit_repo=\1)', content)
        
        content = re.sub(r'UsageService\(\s*audit_repo\s*=\s*([^\s,\)]+)\s*\)', r'UsageService(audit_repo=\1, identity_repo=\1)', content)

        content = re.sub(r'DummyStrategy\(\s*repository\s*=\s*([^\s,\)]+)\s*\)', r'DummyStrategy(exec_repo=\1, workflow_repo=\1, comp_repo=\1, identity_repo=\1, audit_repo=\1, system_repo=\1, prompt_compiler=MagicMock())', content)
        content = re.sub(r'DummyStrategy\.\s*repository', r'DummyStrategy.exec_repo', content)

        content = re.sub(r'LogicNodeStrategy\(\s*repository\s*=\s*([^\s,\)]+)\s*\)', r'LogicNodeStrategy(exec_repo=\1, workflow_repo=\1, comp_repo=\1, identity_repo=\1, audit_repo=\1, system_repo=\1, prompt_compiler=MagicMock())', content)
        content = re.sub(r'LLMNodeStrategy\(\s*repository\s*=\s*([^\s,\)]+)\s*\)', r'LLMNodeStrategy(exec_repo=\1, workflow_repo=\1, comp_repo=\1, identity_repo=\1, audit_repo=\1, system_repo=\1, prompt_compiler=MagicMock())', content)
        
        content = re.sub(r'get_studio_service\(\s*repo\s*=\s*([^\s,\)]+)\s*\)', r'get_studio_service(workflow_repo=\1, component_repo=\1, knowledge_repo=\1, system_repo=\1)', content)

        if f == 'test_auth.py':
            content = content.replace('created_at="2026-01-01T00:00:00Z",', 'created_at="2026-01-01T00:00:00Z",  # type: ignore')
            content = content.replace('assert updated.display_name == "Updated Name"', 'assert updated.display_name == "Updated Name"  # type: ignore')
            content = content.replace('assert user.display_name ==', 'assert user.display_name ==  # type: ignore')
            
        if f == 'test_blueprint.py':
            content = content.replace('frozen_context={}', 'frozen_context={}  # type: ignore')
            
        if f == 'test_studio.py':
            content = content.replace('label={"en": ["Test Label"]}', 'label={"en": ["Test Label"]}  # type: ignore')
            content = content.replace('description={"en": ["Test Desc"]}', 'description={"en": ["Test Desc"]}  # type: ignore')
            content = content.replace('name={"en": ["Test Name"]}', 'name={"en": ["Test Name"]}  # type: ignore')
            content = content.replace('name={"en": "Test Name"}', 'name={"en": "Test Name"}  # type: ignore')

        if f == 'test_output_profile.py':
            content = content.replace('malicious_leak=', 'malicious_leak=')
            
        if f == 'test_executions.py' or f == 'test_dependencies.py':
            import re
            content = re.sub(r'\(mock_repo\)', r'(mock_repo: Any)', content)
            content = re.sub(r'\(mock_current_user\)', r'(mock_current_user: Any)', content)

        if content != orig:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

