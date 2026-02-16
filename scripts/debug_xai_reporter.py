import asyncio
import logging
import os
import sys

# Ensure backend can be imported
sys.path.append(os.getcwd())

# Configure logging
logging.basicConfig(level=logging.INFO)


from backend.agents.xai import XAIReporterAgent
from backend.models.domain import XAIOutput


async def main():
    print("--- STARTING XAI REPORTER DEBUG ---")

    # 1. Instantiate Agent
    agent = XAIReporterAgent()

    # 2. Mock Internal LLM call to return a Pydantic Model (Simulation)
    class MockXAIAgent(XAIReporterAgent):
        async def _execute_llm(self, *args, **kwargs):
            print("[Mock] Simulating LLM response...")
            return XAIOutput(
                reasoning_trace="Mock reasoning",
                report_content="Mock Report",
                score_cards=[] # LLM usually returns empty or None for this computed field
            )

    debug_agent = MockXAIAgent()

    # 3. Define Input with Judge Data (to trigger injection logic)
    input_data = {
        "step_judge": {
            "matrix_id": "matrix_standard_v1",
            "total_score": 2.5,
            "scale_max": 3,
            "dimensions": [
                {"dimension_id": "logic", "score": 2.5, "reasoning": "Good"}
            ]
        }
    }

    print("Executing agent with judge data...")
    try:
        # We need to mock super().execute, but XAIReporterAgent calls super().execute().
        # BaseAgent calls self._execute_llm().
        # So overriding _execute_llm on subclass should work.

        # However, BaseAgent.execute performs validation.
        # XAIOutput schema match? Yes.

        result = await debug_agent.execute(input_data)

        print("\n--- RESULT ---")
        print(f"Type: {type(result)}")
        # print(f"Data: {result}")

        # Verify Injection
        if isinstance(result, XAIOutput):
            print("PASS: Result is XAIOutput model.")
            cards = result.score_cards
            if len(cards) == 1:
                card = cards[0]
                print(f"PASS: 1 ScoreCard found. Agent: {card.agent_name}")
                if card.total_score == 2.5:
                    print("PASS: Score matches.")
                else:
                    print(f"FAIL: Score mismatch: {card.total_score}")
            else:
                 print(f"FAIL: Score cards count: {len(cards)}")
        else:
            print(f"FAIL: Result is not XAIOutput: {type(result)}")

    except Exception as e:
        print(f"\nCRASHED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
