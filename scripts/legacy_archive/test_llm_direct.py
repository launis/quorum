import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.llm_handler import LLMHandler
from dotenv import load_dotenv

load_dotenv()

def test_llm():
    handler = LLMHandler()
    prompts = [{"content": "Hello, are you working?"}]
    model = "models/gemini-2.5-pro"
    
    print(f"Testing LLM with model: {model}")
    try:
        response = handler.call_llm(prompts, model=model)
        print("Response received:")
        print(response)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_llm()
