import re

# Fix test_dag_executor_atom_ceiling
path_ceiling = 'backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py'
with open(path_ceiling, 'r', encoding='utf-8') as f:
    cc = f.read()

cc = cc.replace(
    '"test_strategy": ModelProfile(',
    '"test_strategy": ModelProfile(provider="openai", model_name="gpt-4o", tpm_limit=40000, rpm_limit=100, temperature=0.0, max_tokens=4000),\n            "synthesis": ModelProfile('
)

with open(path_ceiling, 'w', encoding='utf-8') as f:
    f.write(cc)

# Fix test_dag_executor_preflight_ignores_system_keys
path_preflight = 'backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py'
with open(path_preflight, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    'mock_client.run_structured_task = AsyncMock(return_value=(MagicMock(), MagicMock()))',
    'mock_client.run_structured_task = AsyncMock(return_value=(MagicMock(), {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}))'
)

with open(path_preflight, 'w', encoding='utf-8') as f:
    f.write(c)

print("Tests fixed again!")
