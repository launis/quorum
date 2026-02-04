
import asyncio
import os
import sys
import unittest

# Adjust path
sys.path.append(os.getcwd())

from backend.core.engine import GraphEngine
from backend.models.workflow import WorkflowDefinition


class TestEngineParsing(unittest.IsolatedAsyncioTestCase):
    async def test_engine_parses_history_text(self):
        engine = GraphEngine()

        # Mock Definition with NO steps to avoid registry lookups
        definition = WorkflowDefinition(
            id="test_workflow",
            steps=[], # EMPTY STEPS
            name="Test"
        )

        raw_text = "Hello world"
        initial_input = {
            "history_text": raw_text
        }

        result_state = await engine.execute_workflow(definition, initial_input)

        parsed_history = result_state["history_text"]
        with open("test_output.txt", "w") as f:
            f.write(f"Parsed: '{parsed_history}'")

        if parsed_history == "User: Hello world":
             return # Success
        else:
             raise Exception(f"Expected 'User: Hello world', got '{parsed_history}'")

if __name__ == '__main__':
    # unittest.main()
    print("Starting manual test execution...")
    import logging
    logging.basicConfig(filename='test_error.log', level=logging.DEBUG)
    try:
        t = TestEngineParsing()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(t.test_engine_parses_history_text())
        print("TEST PASSED!")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"TEST FAILED: {e}")
        sys.exit(1)

