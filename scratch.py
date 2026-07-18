import asyncio
import pytest
from backend_v2.tests.unit.services.orchestrator.test_dag_executor_atom_ceiling import test_dag_executor_atom_ceiling, mock_repo, mock_compiler

async def run():
    repo = mock_repo()
    compiler = mock_compiler()
    try:
        await test_dag_executor_atom_ceiling(repo, compiler)
        print("TEST PASSED")
    except AssertionError as e:
        print("TEST FAILED ASSERTION:", repr(e))
    except Exception as e:
        print("TEST CRASHED:", repr(e))
        import traceback
        traceback.print_exc()

asyncio.run(run())
