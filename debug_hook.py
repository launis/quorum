import asyncio
import json
import logging
from backend_v2.hooks.input_processing import process_inputs
from backend_v2.exceptions import AppException

logging.basicConfig(level=logging.DEBUG)

class MockRepo:
    pass

async def test_hook():
    test_data = {
        "history_text": "This is raw unstructured chat text...",
        "product_text": "Product text here.",
        "reflection_text": "Initial reflection.",
        "guided_reflection": {
            "q1": "Mikä on oppimistavoite?",
            "a1": "Käsitteiden mieleenpalautus",
        },
        "_sys_repository": MockRepo()
    }
    
    import traceback
    try:
        result = await process_inputs(test_data)
        with open("error.log", "w", encoding="utf-8") as f:
            f.write(json.dumps(result, indent=2))
        print("SUCCESS")
    except Exception as e:
        with open("error.log", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        print("FAILED")

if __name__ == "__main__":
    asyncio.run(test_hook())
