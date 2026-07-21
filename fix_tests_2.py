import glob
import re

path1 = 'backend_v2/tests/unit/test_dag_taskgroup.py'
with open(path1, 'r', encoding='utf-8') as f:
    c1 = f.read()
c1 = c1.replace('"id": "mock",', '"id": "stp_1234567890abcdef",')
with open(path1, 'w', encoding='utf-8') as f:
    f.write(c1)

files = [
    'backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py',
    'backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py'
]

for p in files:
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()
    
    if 'AsyncMock' not in c:
        c = 'from unittest.mock import AsyncMock\n' + c
        
    c = c.replace('rag_preflight=MagicMock()', 'rag_preflight=AsyncMock()')
    c = re.sub(r'DAGExecutor\(\s*(?!rag_preflight=)', 'DAGExecutor(rag_preflight=AsyncMock(), ', c)
    c = c.replace('patch.object(executor, "_execute_rag_preflight", new_callable=AsyncMock) as mock_preflight,', 'patch.object(executor.rag_preflight, "execute", new_callable=AsyncMock) as mock_preflight,')
    c = c.replace('executor._execute_rag_preflight(', 'executor.rag_preflight.execute(')

    c = c.replace('rag_preflight=AsyncMock()', 'rag_preflight=RAGPreflightService(system_repo=mock_repo, prompt_compiler=mock_compiler)')
    if 'RAGPreflightService' not in c:
        c = 'from backend_v2.services.orchestrator.rag_preflight_service import RAGPreflightService\n' + c
        
    with open(p, 'w', encoding='utf-8') as f:
        f.write(c)
