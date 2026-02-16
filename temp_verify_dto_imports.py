import sys
import os

# Add project root to path
sys.path.insert(0, os.getcwd())

def test_imports():
    print("Testing DTO imports...")
    try:
        from backend.models.dtos.llm import LLMResponse, BatchLLMResponse
        from backend.models.dtos.tools import TextExtractionResponse, ConceptExtractionResponse
        print("✅ DTOs imported successfully.")
    except ImportError as e:
        print(f"❌ Failed to import DTOs: {e}")
        sys.exit(1)

    print("Testing Router imports...")
    try:
        from backend.api import llm_router
        from backend.api import tools_router
        print("✅ Routers imported successfully.")
    except ImportError as e:
        print(f"❌ Failed to import Routers: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error importing Routers: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_imports()
