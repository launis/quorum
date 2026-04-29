import os
import re

tests_dir = 'backend_v2/tests/unit'

new_deps = '''HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock()
    )  # type: ignore'''

for root, _, files in os.walk(tests_dir):
    for f in files:
        if not f.endswith('.py'):
            continue
        path = os.path.join(root, f)
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        original_content = content
        
        # 1. Clean up old HookDependencies patterns
        content = re.sub(
            r'HookDependencies\(exec_repo=cast\(Any, MagicMock\(\)\), workflow_repo=cast\(Any, MagicMock\(\)\), comp_repo=cast\(Any, MagicMock\(\)\), identity_repo=cast\(Any, MagicMock\(\)\), audit_repo=cast\(Any, MagicMock\(\)\), system_repo=cast\(Any, MagicMock\(\)\)\)',
            new_deps,
            content
        )
        
        content = re.sub(
            r'HookDependencies\(exec_repo=None, workflow_repo=None, comp_repo=None, identity_repo=None, audit_repo=None, system_repo=None\)\s*# type: ignore',
            new_deps,
            content
        )
        
        # 2. Remove stray # mock_repository) or # MagicMock())) comments
        content = re.sub(r'\n\s*# mock_repository\)', '', content)
        content = re.sub(r'\n\s*# MagicMock\(\)\)\)', '', content)
        content = re.sub(r'\n\s*# MagicMock\(\)\)', '', content)
        
        # 3. Add MagicMock import if missing and used
        if 'MagicMock(' in content and 'from unittest.mock import MagicMock' not in content and 'import MagicMock' not in content:
            if 'from unittest.mock import ' in content:
                content = content.replace('from unittest.mock import ', 'from unittest.mock import MagicMock, ')
            else:
                content = "from unittest.mock import MagicMock\n" + content
                
        if f == 'test_hooks_validation.py':
            content = content.replace('    mock_repo = MagicMock()\n', '')
            
        if f == 'test_progress.py':
            content = content.replace('AsyncMock(spec=Any)', 'AsyncMock()')

        if f == 'test_interfaces.py':
            content = content.replace(', "_is_protocol", False) or type(protocol_class).__name__ in ("_ProtocolMeta", "ProtocolMeta")', ',\\n            "_is_protocol", False\\n        ) or type(protocol_class).__name__ in ("_ProtocolMeta", "ProtocolMeta")')

        if f == 'test_llm.py':
            content = content.replace('HookDependencies(exec_repo=MagicMock(), workflow_repo=MagicMock(), comp_repo=MagicMock(), identity_repo=MagicMock(), audit_repo=MagicMock(), system_repo=MagicMock())', new_deps)
            
        # Write back if changed
        if content != original_content:
            with open(path, 'w', encoding='utf-8') as file:
                file.write(content)
