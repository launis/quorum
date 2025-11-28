from typing import Dict, Any
from src.components.hook_registry import HookRegistry

def calculate_final_scores(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    HOOK: calculate_final_scores
    Logic: Laskee lopulliset pisteet Tuomarin (V8) JSON-tulosteesta.
    """
    print("[HOOK] Calculating Final Scores...")
    
    try:
        # Extract scores from Step 8 output (which is in 'data' if passed correctly, or we look for specific keys)
        # Note: 'data' here is the context passed to the hook. In post-hooks, it might contain the LLM output.
        
        scores = data.get('pisteet', {})
        if not scores and 'llm_output' in data:
             # Try to parse from LLM output if not yet in data structure
             import json
             from src.components.hooks.parsing import _clean_and_parse_json
             parsed = _clean_and_parse_json(data['llm_output'])
             scores = parsed.get('pisteet', {})

        if not scores:
            print("   [Warning] No scores found to calculate.")
            return {"final_score_summary": "No scores found."}

        # Calculate total
        total = 0
        count = 0
        details = []
        
        for category, score_data in scores.items():
            if isinstance(score_data, dict) and 'arvosana' in score_data:
                val = score_data['arvosana']
                total += val
                count += 1
                details.append(f"{category}: {val}")
        
        average = total / count if count > 0 else 0
        
        summary = f"Total Score: {total}/{count*4} (Avg: {average:.2f}). Details: {', '.join(details)}"
        print(f"   {summary}")
        
        return {
            "lasketut_yhteispisteet": total,
            "lasketut_keskiarvo": average,
            "score_summary": summary
        }

    except Exception as e:
        print(f"   Calculation failed: {e}")
        return {"error": str(e)}

HookRegistry.register("calculate_final_scores", calculate_final_scores)
