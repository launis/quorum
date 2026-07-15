import asyncio
from backend_v2.tests.integration.test_epic_chain_e2e import test_epic_93_e2e_golden_master
try:
    asyncio.run(test_epic_93_e2e_golden_master())
except AssertionError as e:
    import traceback
    traceback.print_exc()
