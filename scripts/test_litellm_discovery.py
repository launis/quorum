
import litellm
import os
from dotenv import load_dotenv

load_dotenv(override=True)

def test_litellm():
    print("Scanning litellm attributes for model lists...")
    for attr_name in dir(litellm):
        if attr_name.startswith("_"): continue
        try:
            val = getattr(litellm, attr_name)
            if isinstance(val, list):
                # Check if it looks like a model list (strings)
                if val and isinstance(val[0], str):
                    # Check for Gemini or Vertex
                    gemini_matches = [m for m in val if "gemini" in m.lower()]
                    if gemini_matches:
                        print(f"\n✅ Found Gemini models in 'litellm.{attr_name}':")
                        print(f"   Count: {len(gemini_matches)}")
                        print(f"   Sample: {gemini_matches[:5]}...")
                        
                    vertex_matches = [m for m in val if "vertex" in m.lower()]
                    if vertex_matches and not gemini_matches:
                        print(f"\n✅ Found Vertex models in 'litellm.{attr_name}':")
                        print(f"   Sample: {vertex_matches[:5]}...")
                        
        except Exception:
            pass

if __name__ == "__main__":
    test_litellm()
