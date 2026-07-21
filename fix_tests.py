import os

path = 'backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('patch.object(executor, "_execute_rag_preflight", new_callable=AsyncMock) as mock_preflight,', '')
c = c.replace('mock_preflight', 'executor.rag_preflight.execute')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

path2 = 'backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py'
with open(path2, 'r', encoding='utf-8') as f:
    c2 = f.read()
c2 = c2.replace('patch.object(executor, "_execute_rag_preflight", new_callable=AsyncMock) as mock_preflight,', '')
c2 = c2.replace('mock_preflight', 'executor.rag_preflight.execute')
with open(path2, 'w', encoding='utf-8') as f:
    f.write(c2)
