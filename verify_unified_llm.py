
import os
import asyncio
import json

# Force Mock Mode for verification
os.environ["USE_MOCK_LLM"] = "True"
os.environ["GOOGLE_API_KEY"] = "fake"
os.environ["OPENAI_API_KEY"] = "fake"

from backend.core.llm_handler import LLMHandler
from backend.mock_llm import MockLLMService

async def main():
    print("--- Verifying Unified LLM Handler ---")
    handler = LLMHandler()
    
    # 1. Verify Available Models (Should return Mock List)
    print("\n[Test 1] Fetch Available Models")
    models = handler.fetch_all_available_models()
    print("Models:", json.dumps(models, indent=2))
    
    if "gemini-2.5-pro" in models.get("google", []) and "gpt-4o" in models.get("openai", []):
        print("PASS: Mock models returned.")
    else:
        print("FAIL: Real models or empty list returned.")

    # 2. Verify Call LLM (Mock)
    print("\n[Test 2] Call LLM (Generic)")
    resp = await handler.call_llm("google", "fast", "Hello World")
    print("Response:", resp)
    if not "Error" in resp and len(resp) > 0:
        print("PASS: Valid response received.")
    else:
        print("FAIL: Error or empty response.")

    # 3. Verify Logician Agent Mock Identification
    print("\n[Test 3] Verify Mock Logician Identification")
    mock_service = MockLLMService()
    
    # Simulate the prompt that caused the crash (ACTUAL from LogicianAgent.py override)
    logician_prompt = """
    TASK: Evaluate the logical structure of the argumentation.
    
    INPUT DATA:
    ---
    TODISTUSKARTTA (Edellisestä vaiheesta):
    ...
    """
    
    # Test strict identification
    # LogicianAgent.py overrides get_system_instruction with this:
    sys_instr = """
    You are the Logician Agent. Your task is to evaluate the logical structure of the student's argumentation.
    """
    
    # Check identify method directly (hack access)
    key = mock_service._identify_prompt_type(logician_prompt, sys_instr)
    print(f"Identified Key: {key}")
    
    if key == "logician_agent":
        print("PASS: Logician Agent correctly identified (Override Case).")
    else:
        print(f"FAIL: Identified as {key} instead of logician_agent (Override Case).")

    # [Test 3b] Verify Mock Logician Identification (DB Case - The Regression)
    # This case contains BOTH 'Todistuskartta' and 'ArgumentaatioAnalyysi'
    # Prior to fix, 'Todistuskartta' (Analyst) check was catching it first.
    print("\n[Test 3b] Verify Mock Logician DB-style Identification")
    db_sys_instr = """
    Olet Loogikko-agentti (Logician Agent). Tehtäväsi on analysoida edellisen vaiheen tuottama Todistuskartta ja alkuperäinen data argumentaation näkökulmasta.
    TÄRKEÄÄ: Sinun TÄYTYY tunnistaa argumentaatiovirheitä ja arvioida päättelyketjuja.
    Muodosta JSON-vastaus, joka noudattaa 'ArgumentaatioAnalyysi' -skeemaa.
    """
    # Prompt is same as above but system instruction is key here
    key_db = mock_service._identify_prompt_type(logician_prompt, db_sys_instr)
    print(f"Identified Key (DB Case): {key_db}")
    
    if key_db == "logician_agent":
        print("PASS: Logician Agent correctly identified (DB Case).")
    else:
        print(f"FAIL: Identification failed (DB Case), got {key_db}")

    # 4. Verify Logician Response Structure
    print("\n[Test 4] Verify Logician Fallback Structure")
    fallback_json = mock_service._generate_fallback("logician_agent")
    fallback_data = json.loads(fallback_json)
    
    req_fields = ["toulmin_analyysi", "kognitiivinen_taso", "walton_skeema"]
    missing = [f for f in req_fields if f not in fallback_data]
    
    if not missing:
        print("PASS: All required fields present in fallback.")
    else:
        print(f"FAIL: Missing fields: {missing}")

if __name__ == "__main__":
    asyncio.run(main())

    # [Test 5] Verify Judge Agent Identification (Conflict Case)
    # Judge prompt contains EVERY previous keyword. Must be prioritized.
    print("\n[Test 5] Verify Judge Agent Identification (Conflict Case)")
    mock_service = MockLLMService()
    
    judge_prompt = """
    TASK: Synthesize audit reports...
    INPUT DATA (AUDITOINTIRAPORTIT):
    {
        "logiikka": "... ArgumentaatioAnalyysi ...",
        "analyst": "... Todistuskartta ..."
    }
    """
    
    judge_sys = """
    You are the Judge Agent. Your task is to synthesize... 
    Output must be a valid JSON object matching the TuomioJaPisteet schema.
    """
    
    key_judge = mock_service._identify_prompt_type(judge_prompt, judge_sys)
    print(f"Identified Key (Judge): {key_judge}")
    
    if key_judge == "judge_agent":
        print("PASS: Judge Agent correctly identified (even with pollution).")
        
        # Verify Response Structure
        fallback_json = mock_service._generate_fallback("judge_agent")
        data = json.loads(fallback_json)
        pisteet = data.get("pisteet", {})
        
        required_keys = ["analyysi", "arviointi", "synteesi"]
        missing = [k for k in required_keys if k not in pisteet]
        
        if not missing:
            print("PASS: Judge schema keys are correct.")
        else:
            print(f"FAIL: Missing keys in Judge response: {missing}")

    else:
        print(f"FAIL: Judge Agent misidentified as {key_judge}.")
