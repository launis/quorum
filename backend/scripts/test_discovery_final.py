import logging
import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.llm.handler import LLMHandler

logging.basicConfig(level=logging.INFO)

def main():
    print("Testing LLMHandler Discovery (Pure Vertex)...")
    handler = LLMHandler(db_client=None)
    models = handler.fetch_all_available_models()
    
    print("-" * 40)
    print(f"Google Models ({len(models.get('google', []))}):")
    print(models.get('google'))
    print("-" * 40)
    
    if models.get('google_error'):
        print(f"ERROR: {models['google_error']}")
    else:
        print("SUCCESS: Google discovery passed.")

if __name__ == "__main__":
    main()
