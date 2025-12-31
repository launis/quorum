import asyncio
import os
import litellm
from dotenv import load_dotenv

# Load env including google creds and VERTEX_LOCATION
load_dotenv()
# Force US location for probing as User requested
os.environ["VERTEX_LOCATION"] = "us-central1"
# Force Vertex AI project
os.environ["VERTEX_PROJECT"] = "cognitive-quorum"

CANDIDATES = [
    "vertex_ai/gemini-3.0-pro",
    "vertex_ai/gemini-3.0-pro-001",
    "vertex_ai/gemini-3.0-flash",
    "vertex_ai/gemini-3.0-flash-001",
    "vertex_ai/gemini-3-pro",
    "vertex_ai/gemini-3-flash",
    "vertex_ai/gemini-3.0-flash-002", # hypothesis
    "vertex_ai/gemini-pro-3.0", # another var
]

async def probe_model(model_name):
    print(f"Probing {model_name} in us-central1...")
    try:
        response = await litellm.acompletion(
            model=model_name,
            messages=[{"role": "user", "content": "Hi"}],
            vertex_location="us-central1"
        )
        print(f"SUCCESS: {model_name} is available!")
        return model_name
    except Exception as e:
        error_str = str(e)
        if "404" in error_str or "NOT_FOUND" in error_str:
             print(f"FAIL: {model_name} not found.")
        else:
             # If it's another error (like 403 or quota), the model MIGHT exist but we have other issues.
             # But usually 404 is the 'name wrong' error.
             print(f"ERROR (but maybe exists): {model_name} gave {e}")
        return None

async def main():
    print(f"Starting probe using Creds: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
    print(f"Location: {os.getenv('VERTEX_LOCATION')}")
    
    found_flash = None
    found_pro = None
    
    # Probe sequentially to be clear
    for model in CANDIDATES:
        result = await probe_model(model)
        if result:
            if "flash" in result and not found_flash:
                found_flash = result
            if "pro" in result and not found_pro:
                found_pro = result
                
    print("\n--- RESULTS ---")
    print(f"Best Flash: {found_flash}")
    print(f"Best Pro: {found_pro}")
    
    # Save to file so we can read it
    with open("probe_result.txt", "w") as f:
        f.write(f"FLASH={found_flash or 'None'}\n")
        f.write(f"PRO={found_pro or 'None'}\n")

if __name__ == "__main__":
    asyncio.run(main())
