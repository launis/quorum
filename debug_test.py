import asyncio
from backend_v2.tests.unit.test_dag_executor_prompt_blocks import test_dag_executor_uses_prompt_blocks_instead_of_matrices, mock_repo, mock_compiler
async def main():
  try:
    await test_dag_executor_uses_prompt_blocks_instead_of_matrices(mock_repo(), mock_compiler())
  except Exception as e:
    print('EXCEPTION_CAUGHT:')
    print(repr(e))
    if hasattr(e, 'details'): print(e.details)
asyncio.run(main())