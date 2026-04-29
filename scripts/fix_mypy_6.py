import os
import re

files_to_fix = [
    'backend_v2/tests/unit/test_web_fetcher.py',
    'backend_v2/tests/unit/test_localization.py',
    'backend_v2/tests/unit/test_output_profile.py',
    'backend_v2/tests/unit/test_progress.py',
    'backend_v2/tests/unit/test_blueprint.py',
    'backend_v2/tests/unit/test_logic.py',
    'backend_v2/tests/unit/test_studio.py',
    'backend_v2/tests/unit/test_llm.py',
    'backend_v2/tests/unit/test_dag_taskgroup.py',
    'backend_v2/tests/unit/test_dag_executor_prompt_blocks.py',
    'backend_v2/tests/unit/test_execution_service.py',
    'backend_v2/tests/unit/test_execution.py',
    'backend_v2/tests/unit/test_dependencies.py',
    'backend_v2/tests/unit/test_executions.py',
    'backend_v2/tests/unit/test_core_base.py',
    'backend_v2/tests/unit/test_base.py',
    'backend_v2/tests/unit/test_archival.py'
]

for path in files_to_fix:
    if not os.path.exists(path): continue
    with open(path, 'r', encoding='utf-8') as f: content = f.read()
    orig = content
    
    content = re.sub(r'BlueprintTransformer\(repository=([^,\)]+)\)', r'BlueprintTransformer(exec_repo=\1, workflow_repo=\1, comp_repo=\1, identity_repo=\1)', content)
    content = re.sub(r'DAGExecutor\(repository=([^,\)]+)\)', r'DAGExecutor(exec_repo=\1, workflow_repo=\1, comp_repo=\1, system_repo=\1, identity_repo=\1, audit_repo=\1, prompt_compiler=MagicMock())', content)
    content = re.sub(r'ExecutionService\(repo=([^,\)]+)\)', r'ExecutionService(exec_repo=\1)', content)
    content = re.sub(r'HookDependencies\(repository=([^,\)]+)\)', r'HookDependencies(exec_repo=\1, workflow_repo=\1, comp_repo=\1, identity_repo=\1, audit_repo=\1, system_repo=\1)', content)
    content = re.sub(r'LogicNodeStrategy\(repository=([^,\)]+)\)', r'LogicNodeStrategy(exec_repo=\1, workflow_repo=\1, comp_repo=\1, identity_repo=\1, audit_repo=\1, system_repo=\1, prompt_compiler=MagicMock())', content)
    content = re.sub(r'LLMNodeStrategy\(repository=([^,\)]+)\)', r'LLMNodeStrategy(exec_repo=\1, workflow_repo=\1, comp_repo=\1, identity_repo=\1, audit_repo=\1, system_repo=\1, prompt_compiler=MagicMock())', content)
    content = re.sub(r'DummyStrategy\(repository=([^,\)]+)\)', r'DummyStrategy(exec_repo=\1, workflow_repo=\1, comp_repo=\1, identity_repo=\1, audit_repo=\1, system_repo=\1, prompt_compiler=MagicMock())', content)
    content = re.sub(r'get_studio_service\(repo=([^,\)]+)\)', r'get_studio_service(workflow_repo=\1, component_repo=\1, knowledge_repo=\1, system_repo=\1)', content)

    if 'def mock_' in content and '-> Any:' not in content:
        content = re.sub(r'def mock_([a-zA-Z0-9_]+)\((.*?)\):', r'def mock_\1(\2) -> Any:', content)
    
    content = re.sub(r'def test_([a-zA-Z0-9_]+)\((.*?)\):', r'def test_\1(\2) -> None:', content)
    content = re.sub(r'async def test_([a-zA-Z0-9_]+)\((.*?)\):', r'async def test_\1(\2) -> None:', content)
    content = content.replace('-> None: -> None:', '-> None:')
    content = content.replace('-> Any: -> Any:', '-> Any:')
    
    if path.endswith('test_web_fetcher.py'):
        content = content.replace('def mock_post(*args, **kwargs):', 'def mock_post(*args: Any, **kwargs: Any) -> Any:')
        content = content.replace('def mock_get(*args, **kwargs):', 'def mock_get(*args: Any, **kwargs: Any) -> Any:')
    
    if path.endswith('test_document_extraction.py'):
        content = content.replace('invalid_input: dict[str, str] = "not_a_dict"  # type: ignore', 'invalid_input: dict[str, Any] = "not_a_dict"  # type: ignore')
        content = content.replace('assert invalid_input == "not_a_dict"  # type: ignore', 'assert invalid_input == "not_a_dict"  # type: ignore')

    if path.endswith('test_studio.py'):
        content = content.replace('name={"en": "Mock Workflow"}', 'name={"en": "Mock Workflow"}  # type: ignore')

    if content != orig:
        with open(path, 'w', encoding='utf-8') as f: f.write(content)
