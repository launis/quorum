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
            
        orig_content = content
        
        # 1. Unused type: ignore
        content = re.sub(r'\s*# type: ignore\n', '\n', content)
        
        # 2. Fix `repository=...` or `repo=...` in class instantiations that were changed to ISP
        # BlueprintTransformer(repository=mock_repo) -> BlueprintTransformer(workflow_repo=mock_repo, comp_repo=mock_repo, identity_repo=mock_repo)
        content = re.sub(
            r'BlueprintTransformer\(repository=([^,\)]+)\)',
            r'BlueprintTransformer(workflow_repo=\1, comp_repo=\1, identity_repo=\1)',
            content
        )
        content = re.sub(
            r'BlueprintTransformer\(repo=([^,\)]+)\)',
            r'BlueprintTransformer(workflow_repo=\1, comp_repo=\1, identity_repo=\1)',
            content
        )

        content = re.sub(
            r'PdfReportService\(repository=([^,\)]+)\)',
            r'PdfReportService(workflow_repo=\1)',
            content
        )

        content = re.sub(
            r'UsageService\(repo=([^,\)]+)\)',
            r'UsageService(audit_repo=\1)',
            content
        )

        content = re.sub(
            r'ExecutionService\(repo=([^,\)]+)\)',
            r'ExecutionService(exec_repo=\1)',
            content
        )

        content = re.sub(
            r'StudioService\(repo=([^,\)]+)\)',
            r'StudioService(workflow_repo=\1, component_repo=\1, knowledge_repo=\1, system_repo=\1)',
            content
        )

        content = re.sub(
            r'DAGExecutor\(repository=([^,\)]+)\)',
            r'DAGExecutor(exec_repo=\1, workflow_repo=\1, comp_repo=\1, system_repo=\1, identity_repo=\1, audit_repo=\1)',
            content
        )

        content = re.sub(
            r'HookDependencies\(repository=([^,\)]+)\)',
            r'HookDependencies(exec_repo=\1, workflow_repo=\1, comp_repo=\1, identity_repo=\1, audit_repo=\1, system_repo=\1)',
            content
        )
        
        content = re.sub(
            r'DummyStrategy\(repository=([^,\)]+)\)',
            r'DummyStrategy(exec_repo=\1, workflow_repo=\1, comp_repo=\1, identity_repo=\1, audit_repo=\1, system_repo=\1, prompt_compiler=MagicMock())',
            content
        )
        
        content = re.sub(
            r'LogicNodeStrategy\(repository=([^,\)]+)\)',
            r'LogicNodeStrategy(exec_repo=\1, workflow_repo=\1, comp_repo=\1, identity_repo=\1, audit_repo=\1, system_repo=\1, prompt_compiler=MagicMock())',
            content
        )

        content = re.sub(
            r'LLMNodeStrategy\(repository=([^,\)]+)\)',
            r'LLMNodeStrategy(exec_repo=\1, workflow_repo=\1, comp_repo=\1, identity_repo=\1, audit_repo=\1, system_repo=\1, prompt_compiler=MagicMock())',
            content
        )

        # 3. test_web_fetcher MockResponse
        # mypy complains about missing return type and missing argument types.
        # It's faster to just fix missing return types by adding `-> None:` where it's missing on tests
        
        # We will use regex to find `def test_...(...)` that doesn't have `->`
        # Simple approach: lines starting with `def test_` ending with `):`
        lines = content.split('\n')
        for i, line in enumerate(lines):
            # Fix def test_foo(): -> def test_foo() -> None:
            if line.startswith('def test_') and line.endswith('):'):
                lines[i] = line + ' -> None:'
            elif line.startswith('async def test_') and line.endswith('):'):
                lines[i] = line + ' -> None:'
            # Fix def mock_foo(): -> def mock_foo() -> Any:
            elif 'def mock_' in line and line.endswith('):'):
                if '->' not in line:
                    lines[i] = line + ' -> Any:'
            elif line.startswith('def test_') and '):' in line and not line.endswith('):'):
                pass # multi-line definition, slightly harder

        content = '\n'.join(lines)

        if content != orig_content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

print("Applied Regex Fixes for tests!")
