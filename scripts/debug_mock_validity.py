
import sys
import os

# Ensure backend in path
sys.path.append(os.getcwd())

# Mock keys to avoid errors if they are checked
os.environ["OPENAI_API_KEY"] = "mock-key"
os.environ["GOOGLE_API_KEY"] = "mock-key"
os.environ["USE_MOCK_LLM"] = "true"
os.environ["USE_MOCK_DB"] = "true"
os.environ["STORAGE_BACKEND"] = "LOCAL"

try:
    print("Importing mock_data...")
    import backend.llm.mock_data
    print("Import successful. MOCK_REGISTRY keys:", len(backend.llm.mock_data.MOCK_REGISTRY))

    print("Checking model_copy for all items...")
    for model_cls, instance in backend.llm.mock_data.MOCK_REGISTRY.items():
        print(f"Validating {model_cls.__name__} copy...")
        try:
            instance.model_copy(deep=True)
            print("OK")
        except Exception as e:
            print(f"FAILED {model_cls.__name__}: {e}")
            raise e

except Exception as e:
    print(f"CRASH: {e}")
