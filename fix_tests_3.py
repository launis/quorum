import re

path_preflight = 'backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py'
with open(path_preflight, 'r', encoding='utf-8') as f:
    c = f.read()

tests = re.split(r'(?=@pytest\.mark\.asyncio)', c)
new_c = tests[0]
for test in tests[1:]:
    if 'test_dag_executor_preflight_ignores_system_keys' not in test:
        new_test = re.sub(r'RAGPreflightService\([^)]+\)', 'AsyncMock()', test)
        new_c += new_test
    else:
        # Fix the execute call
        old_call = """await executor.rag_preflight.execute(
            workflow=workflow,
            exec_record=exec_record,
            projector=MagicMock(),
            virtual_step_id="stp_1234567890abcdef",
            _emit_progress=AsyncMock(),
        )"""
        new_call = """await executor.rag_preflight.execute(
            target_step=workflow.steps[0],
            step_def=Step.model_validate(mock_repo.get_step_by_id.return_value),
            exec_record=exec_record,
            emit_progress=AsyncMock(),
        )"""
        test = test.replace(old_call, new_call)
        
        if 'from backend_v2.models.v2_core import Step\n' not in new_c:
            new_c = 'from backend_v2.models.v2_core import Step\n' + new_c
            
        new_c += test

with open(path_preflight, 'w', encoding='utf-8') as f:
    f.write(new_c)

path_ceiling = 'backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py'
with open(path_ceiling, 'r', encoding='utf-8') as f:
    cc = f.read()
cc = re.sub(r'RAGPreflightService\([^)]+\)', 'AsyncMock()', cc)
with open(path_ceiling, 'w', encoding='utf-8') as f:
    f.write(cc)
