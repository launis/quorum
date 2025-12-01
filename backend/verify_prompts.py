import json
import os
import sys
from typing import Dict, Any, Optional
from tinydb import TinyDB, Query

# Add project root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.engine import WorkflowEngine
from backend.agents.base import BaseAgent

# Global list to capture interactions
CAPTURED_INTERACTIONS = []

# Save original method to call it later
original_call_llm = BaseAgent._call_llm

def capture_and_call_llm(self, prompt: str, system_instruction: Optional[str] = None, json_mode: bool = False) -> str:
    """
    Interceptor for LLM calls. Captures the prompt and the real response.
    """
    agent_name = self.__class__.__name__
    print(f"[{agent_name}] Intercepting LLM call...")
    
    # 1. Call the REAL LLM
    try:
        response = original_call_llm(self, prompt, system_instruction, json_mode)
    except Exception as e:
        response = f"[ERROR IN LLM CALL]: {str(e)}"
        print(f"[{agent_name}] Real LLM call failed: {e}")

    # 2. Capture everything
    CAPTURED_INTERACTIONS.append({
        "agent": agent_name,
        "system_instruction": system_instruction,
        "user_content": prompt,
        "response": response
    })
    
    return response

# Monkey-patch the BaseAgent
BaseAgent._call_llm = capture_and_call_llm

# Define realistic starting inputs
MOCK_INPUTS = {
    "history_text": "Käyttäjä: Haluaisin arvioida tämän uuden kahvinkeittimen designia. Se on futuristinen ja kromattu.\nAI: Selvä, aloitetaan arviointi.",
    "product_text": "SuperKahvi 3000 on täysin automaattinen kahvinkeitin, jossa on integroitu tekoäly ja kromattu ulkokuori. Se lupaa täydellisen kahvin joka kerta.",
    "reflection_text": "Olen hieman epävarma, onko kromi liian kiiltävä makuuni, mutta teknologia vaikuttaa lupaavalta."
}

def verify_prompts():
    print("Initializing Engine...")
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'db.json')
    engine = WorkflowEngine(db_path)
    
    print("Executing Workflow Simulation (REAL LLM CALLS)...")
    # We need to find the workflow ID.
    # Using the correct ID found in DB.
    try:
        engine.execute_workflow('WORKFLOW_MAIN', MOCK_INPUTS)
    except Exception as e:
        print(f"Simulation finished (or failed): {e}")

    print(f"Captured {len(CAPTURED_INTERACTIONS)} interactions.")

    output_file = 'verification_output.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=== VERIFICATION OUTPUT: FULL PROMPTS AND RESPONSES ===\n")
        f.write("This file contains the EXACT prompts sent to the LLM and the REAL responses received.\n")
        f.write("="*80 + "\n\n")
        
        for i, capture in enumerate(CAPTURED_INTERACTIONS):
            f.write(f"--- STEP {i+1}: {capture['agent']} ---\n\n")
            
            f.write("### SYSTEM INSTRUCTION (Säännöt ja Roolit) ###\n")
            f.write(capture['system_instruction'] or "[NO SYSTEM INSTRUCTION]")
            f.write("\n\n")
            
            f.write("### USER CONTENT (Syöte ja Data) ###\n")
            f.write(capture['user_content'])
            f.write("\n\n")
            
            f.write("### LLM RESPONSE (Vastaus) ###\n")
            f.write(capture['response'])
            f.write("\n\n")
            f.write("="*80 + "\n\n")

    print(f"Verification output written to {output_file}")

if __name__ == "__main__":
    verify_prompts()
