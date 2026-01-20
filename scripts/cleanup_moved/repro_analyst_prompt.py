
import asyncio
from backend.agents.analyst import AnalystAgent
from backend.models.state import WorkflowState, InputData

async def main():
    agent = AnalystAgent()
    inputs = InputData(
        history_text="Asiakasnumero: 12345", 
        product_text="Tämä on tuote.", 
        reflection_text="Ei lisättävää."
    )
    state = WorkflowState(
        execution_id="test",
        inputs=inputs
    )
    
    # We need to fetch the system instruction that would be passed to it.
    # Usually this comes from TaskRegistry or the Engine logic.
    # But BaseAgent.construct_user_prompt is what builds the USER part.
    # The SYSTEM part comes from outside.
    
    # Let's verify what construct_user_prompt produces.
    user_prompt = agent.construct_user_prompt(state)
    print("--- USER PROMPT ---")
    print(user_prompt)
    print("-------------------")

if __name__ == "__main__":
    asyncio.run(main())
