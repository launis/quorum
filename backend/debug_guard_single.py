
import asyncio
import logging
import sys
import json
import os
import fitz # PyMuPDF

# Adjust path to allow imports
sys.path.append("c:/src/quorum")

from backend.agents.guard import GuardAgent
from backend.models.state import WorkflowState, InputData
from backend.models.domain import TaintedData

# Configure logging
# FORCE UTF-8 for Windows Console/Redirection
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger("backend")
logger.setLevel(logging.INFO)

def extract_pdf_text(filepath):
    try:
        if not os.path.exists(filepath):
            return f"[ERROR: File not found: {filepath}]"
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()
    except Exception as e:
        return f"[ERROR Extracting PDF: {e}]"

async def run_single_guard_query():
    print("=== INITIALIZING GUARD AGENT WITH REAL DATA ===")
    
    base_dir = r"c:\src\quorum\data\files\1e205b2c-c907-45a1-a5e5-3fa4cc10952f"
    
    # Map files
    history_file = os.path.join(base_dir, "keskusteluhistoria SITRA.pdf")
    product_file = os.path.join(base_dir, "lopputuote sitra.pdf")
    reflection_file = os.path.join(base_dir, "Reflektiodokumentti sitra.pdf")
    
    print(f"Reading files from: {base_dir}...", flush=True)
    
    history_text = extract_pdf_text(history_file)
    product_text = extract_pdf_text(product_file)
    reflection_text = extract_pdf_text(reflection_file)
    
    print(f"History Length: {len(history_text)}")
    print(f"Product Length: {len(product_text)}")
    print(f"Reflection Length: {len(reflection_text)}")

    # 1. Mock State
    dummy_inputs = InputData(
        history_text=history_text,  
        product_text=product_text,
        reflection_text=reflection_text
    )
    
    state = WorkflowState(
        execution_id="debug-exec-real-1",
        step_id="step_guard",
        inputs=dummy_inputs,
        aux_data={"banned_phrases": []} # No bans
    )
    
    # 2. Initialize Agent
    agent = GuardAgent()
    agent.set_model("gemini-2.5-pro", provider="google")

    # 3. Intercept LLM Call to see the prompt
    original_generate = agent.llm_provider.generate
    
    async def intercepted_generate(*args, **kwargs):
        print("\n\n################################################################################", flush=True)
        print("###                   LLM QUERY (SIMULATED/CAPTURED)                         ###", flush=True)
        print("################################################################################", flush=True)
        
        prompt = kwargs.get("prompt")
        if not prompt and args:
            prompt = args[0]
        if not prompt:
            prompt = "No Prompt arg? (Extraction Error)"
            
        sys_inst = kwargs.get("system_instruction") or "No System Instruction"
        
        print(f"\n[SYSTEM INSTRUCTION]:\n{sys_inst}", flush=True)
        print(f"\n[USER PROMPT]:\n{prompt}", flush=True)
        print("\n################################################################################\n", flush=True)
        
        # Call original
        return await original_generate(*args, **kwargs)
        
    agent.llm_provider.generate = intercepted_generate

    print("=== EXECUTING AGENT ===")
    try:
        # Simulate the resolved prompt from the registry (Same as before)
        mock_system_instruction = f"""
ROLE: Guard Agent (Vartija)
TASK: Analyze the incoming input for PII, malicious intent, and data hygiene.
OUTPUT SCHEMA: TaintedData (JSON)

Mandaatti 1: Sinun on käytettävä hidasta, deliberatiivista päättelyä.
Sääntö 1: Luota vain Vartija-agentin validoimaan dataan.

INPUT DATA:
--------------------------------------------------
HISTORY TEXT:
{history_text}
--------------------------------------------------
PRODUCT TEXT:
{product_text}
--------------------------------------------------
REFLECTION TEXT:
{reflection_text}
--------------------------------------------------

VAIHE 1: VARTIJA (Input Hygiene Audit)
1. SUORITA TEKNINEN TARKASTUS.
2. TÄYTÄ 'safe_data': Palauta syöteteksi ANONYMISOITUNA.
"""
        
        state = await agent.execute(state=state, system_instruction=mock_system_instruction)
        
        print("\n=== OUTPUT (step_guard.safe_data) ===")
        if state.step_guard:
            print(state.step_guard.safe_data.model_dump_json(indent=2))
        else:
            print("No output in step_guard.")
            
    except Exception as e:
        print(f"Execution Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_single_guard_query())
