import sys
import os
import json
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.executor import Executor
from src.components.hook_registry import HookRegistry
import src.components.hooks # Register hooks
from src.database.initialization import initialize_database
from src.engine.llm_handler import LLMHandler

# Force UTF-8 for Windows console output
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def mock_llm_response(prompt: str, model: str) -> str:
    """Mock LLM response generator based on prompt content."""
    if "VARTIJA-AGENTTI" in prompt:
        return json.dumps({
            "metadata": {"agent": "GUARD", "vaihe": 1, "luontiaika": "2025-01-01T12:00:00Z", "versio": "1.0"},
            "metodologinen_loki": "Mock log",
            "semanttinen_tarkistussumma": "Mock summary",
            "data": {"keskusteluhistoria": "raw", "lopputuote": "raw", "reflektiodokumentti": "raw"},
            "security_check": {"uhka_havaittu": False, "adversariaalinen_simulaatio_tulos": "Clean", "riski_taso": "MATALA"}
        })
    elif "ANALYYTIKKO-AGENTTI" in prompt:
        return json.dumps({
            "metadata": {"agent": "ANALYST", "vaihe": 2, "luontiaika": "2025-01-01T12:00:00Z", "versio": "1.0"},
            "metodologinen_loki": "Mock log",
            "semanttinen_tarkistussumma": "Mock summary",
            "hypoteesit": [{"id": "H1", "vaite_teksti": "Claim 1", "loytyyko_todisteita": True}],
            "rag_todisteet": [{"viittaa_hypoteesiin_id": "H1", "perusteet": "Evidence", "konteksti_segmentti": "Quote", "relevanssi_score": 9}]
        })
    elif "TUOMARI-AGENTTI" in prompt:
        return json.dumps({
            "metadata": {"agent": "JUDGE", "vaihe": 8, "luontiaika": "2025-01-01T12:00:00Z", "versio": "1.0"},
            "metodologinen_loki": "Mock log",
            "semanttinen_tarkistussumma": "Mock summary",
            "konfliktin_ratkaisut": [],
            "mestaruus_poikkeama": {"tunnistettu": False, "perustelu": ""},
            "aitous_epaily": {"automaattinen_lippu": False, "viesti_hitl_lle": ""},
            "pisteet": {
                "analyysi_ja_prosessi": {"arvosana": 3, "perustelu": "Good"},
                "arviointi_ja_argumentaatio": {"arvosana": 4, "perustelu": "Excellent"},
                "synteesi_ja_luovuus": {"arvosana": 3, "perustelu": "Good"}
            },
            "kriittiset_havainnot_yhteenveto": []
        })
    elif "FAKTUAALINEN JA EETTINEN VALVOJA" in prompt:
        return json.dumps({
            "metadata": {"agent": "FACT_CHECKER", "vaihe": 7, "luontiaika": "2025-01-01T12:00:00Z", "versio": "1.0"},
            "metodologinen_loki": "Mock log",
            "semanttinen_tarkistussumma": "Mock summary",
            "faktantarkistus_rfi": [{"vaite": "Claim 1", "verifiointi_tulos": "Vahvistettu", "lahde_tai_paattely": "Source"}],
            "eettiset_havainnot": [{"tyyppi": "Ei havaittu", "vakavuus": "N/A", "kuvaus": "None"}]
        })
    elif "XAI-RAPORTOIJA" in prompt:
        return json.dumps({
            "metadata": {"agent": "XAI", "vaihe": 9, "luontiaika": "2025-01-01T12:00:00Z", "versio": "1.0"},
            "metodologinen_loki": "Mock log",
            "semanttinen_tarkistussumma": "Mock summary",
            "summary": "This is a mock summary.",
            "critical_findings": ["Finding 1"],
            "hitl_required": False,
            "ethical_issues": [],
            "audit_questions": [],
            "uncertainty": {
                "aleatoric": "Low",
                "systemic": ["Log 1"],
                "epistemic": "Low"
            }
        })
    elif "Fact Extraction Agent" in prompt:
        # Mock response for Claim Extraction LLM in search hook
        return json.dumps(["Claim 1", "Claim 2", "Claim 3"])
    else:
        return json.dumps({"metadata": {"agent": "GENERIC"}, "metodologinen_loki": "Mock", "semanttinen_tarkistussumma": "Mock"})

def test_full_workflow():
    print("Initializing Database...")
    initialize_database()
    
    print("Initializing Executor...")
    executor = Executor()
    
    # Mock LLM Handler globally to catch hook calls too
    LLMHandler.call_llm = lambda self, prompts, model="gemini-1.5-flash": mock_llm_response(" ".join([p['content'] for p in prompts]), model)
    
    # Mock Input Data with PII to test Sanitization
    context = {
        "history_text": "User: Hello. AI: Hi.",
        "product_text": "My email is test@example.com and phone is 050 123 4567.",
        "reflection_text": "I learned a lot."
    }
    
    print("Running workflow steps...")
    
    try:
        # Test Step 1 (Guard)
        print("\n--- Testing Step 1 (Guard) ---")
        res1 = executor.execute_step("STEP_1_GUARD", context)
        print(f"Result Keys: {res1.keys()}")
        
        # Verify Sanitization
        if "data" in res1 and "lopputuote" in res1["data"]:
            sanitized_text = res1["data"]["lopputuote"]
            if "[REDACTED_EMAIL]" in sanitized_text and "[REDACTED_PHONE_FI]" in sanitized_text:
                print("PASS: PII Redaction worked.")
            else:
                print(f"FAIL: PII Redaction failed. Content: {sanitized_text}")
        
        context.update(res1)
        
        # Test Step 2 (Analyst)
        print("\n--- Testing Step 2 (Analyst) ---")
        res2 = executor.execute_step("STEP_2_ANALYST", context)
        context.update(res2)
        
        # Skip Steps 3-6 for brevity in this test, but normally we'd run them.
        # Let's mock their output to proceed to Step 7
        context.update({
            "toulmin_analyysi": [],
            "kognitiivinen_taso": {"bloom_taso": "Analyysi", "strateginen_syvyys": "Korkea"},
            "walton_skeema": {"tunnistettu_skeema": "Expert Opinion", "kriittiset_kysymykset": []}
        })

        # Test Step 7 (Fact Checker) - Verification of Search Hook
        print("\n--- Testing Step 7 (Fact Checker) ---")
        # We need to ensure the hook doesn't crash. 
        # The hook will use the mocked LLM for claim extraction.
        # It will try to use Google Search API. If keys are missing, it prints error but returns result with error.
        res7 = executor.execute_step("STEP_7_FACT_CHECKER", context)
        print(f"Result Keys: {res7.keys()}")
        if "faktantarkistus_rfi" in res7:
             print("PASS: Fact Checker ran.")
        
        context.update(res7)

        # Test Step 8 (Judge)
        print("\n--- Testing Step 8 (Judge) ---")
        res8 = executor.execute_step("STEP_8_JUDGE", context)
        
        if "lasketut_yhteispisteet" in res8:
            print(f"PASS: Python calculation hook worked. Total Score: {res8['lasketut_yhteispisteet']}")
        else:
            print("FAIL: Python calculation hook did not run or return data.")
        
        context.update(res8)

        # Test Step 9 (XAI)
        print("\n--- Testing Step 9 (XAI) ---")
        res9 = executor.execute_step("STEP_9_XAI", context)
        
        if "report_content" in res9:
             print("PASS: XAI Report generated successfully.")
             # Verify content
             if "This is a mock summary." in res9["report_content"]:
                 print("PASS: Report contains correct summary.")
             else:
                 print(f"FAIL: Report missing summary. Content snippet: {res9['report_content'][:200]}...")
        else:
             print("FAIL: XAI Report generation failed.")

    except Exception as e:
        with open("error_log.txt", "w") as f:
            f.write(f"Exception Type: {type(e)}\n")
            f.write(f"Exception: {str(e)}\n")
            if hasattr(e, 'errors'):
                import json
                f.write(f"Validation Errors:\n{json.dumps(e.errors(), indent=2)}\n")
            elif hasattr(e, 'json'):
                f.write(f"Validation JSON:\n{e.json()}\n")
        print("\n[ERROR] Execution failed. Details written to error_log.txt")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_workflow()
