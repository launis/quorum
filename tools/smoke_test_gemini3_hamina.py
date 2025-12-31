import asyncio
import os
import litellm
from dotenv import load_dotenv

load_dotenv()
os.environ["VERTEX_LOCATION"] = "europe-north1"

CANDIDATES = [
    "vertex_ai/gemini-3.0-pro-preview",
    "vertex_ai/gemini-3.0-flash-preview",
    "vertex_ai/gemini-3.0-pro-preview-001",
    "vertex_ai/gemini-3.0-flash-preview-001",
    "vertex_ai/gemini-3.0-pro-preview-002", # hypothesis
    "vertex_ai/gemini-experimental",
]

async def probe_model(model_name, f):
    print(f"Probing {model_name} in europe-north1...")
    try:
        response = await litellm.acompletion(
            model=model_name,
            messages=[{"role": "user", "content": "Hi"}],
            vertex_location="europe-north1"
        )
        msg = f"SUCCESS: {model_name} found! Response: {response.choices[0].message.content}\n"
        print(msg)
        f.write(msg)
        return True
    except Exception as e:
        error_str = str(e)
        if "404" in error_str or "NOT_FOUND" in error_str:
             msg = f"FAIL: {model_name} (404 Not Found)\n"
        else:
             msg = f"ERROR: {model_name} ({e})\n"
        print(f"{model_name}: {msg.strip()}")
        f.write(msg)
        return False

async def main():
    with open("gemini3_probe_results.txt", "w", encoding="utf-8") as f:
        f.write("--- GEMINI 3.0 PREVIEW PROBE (HAMINA) ---\n")
        
        found_any = False
        for model in CANDIDATES:
            if await probe_model(model, f):
                found_any = True
        
        if not found_any:
            f.write("\nCONCLUSION: No Gemini 3.0 Preview models found in europe-north1.\n")

if __name__ == "__main__":
    asyncio.run(main())
