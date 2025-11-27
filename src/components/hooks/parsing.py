import json
import re
from typing import Dict, Any
from src.components.hook_registry import HookRegistry

def _clean_and_parse_json(text: str) -> Dict[str, Any]:
    """
    Helper to extract and parse JSON from LLM output.
    Handles markdown code blocks.
    """
    try:
        # Remove markdown code blocks if present
        cleaned = re.sub(r'```json\s*', '', text)
        cleaned = re.sub(r'```', '', cleaned)
        return json.loads(cleaned.strip())
    except json.JSONDecodeError:
        print(f"[Parsing] Warning: Failed to parse JSON. Returning raw text.")
        return {"raw_output": text}

def parse_analyst_output(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    HOOK: parse_analyst_output
    Logic: Parses LLM output into AnalysisSummary schema.
    """
    print("[HOOK] Parsing Analyst Output...")
    llm_output = data.get('llm_output', '')
    parsed = _clean_and_parse_json(llm_output)
    
    return {
        "analysis_summary": parsed.get('analysis_summary', llm_output),
        "citations": parsed.get('citations', [])
    }

def parse_logician_output(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    HOOK: parse_logician_output
    Logic: Parses LLM output into HypothesisArgument schema.
    """
    print("[HOOK] Parsing Logician Output...")
    llm_output = data.get('llm_output', '')
    parsed = _clean_and_parse_json(llm_output)
    
    return {
        "hypothesis_argument": parsed.get('hypothesis_argument', llm_output),
        "toulmin_structure": parsed.get('toulmin_structure', {}),
        "citations": parsed.get('citations', [])
    }

def parse_judge_output(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    HOOK: parse_judge_output
    Logic: Parses LLM output into FinalVerdict schema.
    """
    print("[HOOK] Parsing Judge Output...")
    llm_output = data.get('llm_output', '')
    parsed = _clean_and_parse_json(llm_output)
    
    return {
        "final_verdict": parsed.get('final_verdict', llm_output),
        "citations": parsed.get('citations', [])
    }

HookRegistry.register("parse_analyst_output", parse_analyst_output)
HookRegistry.register("parse_logician_output", parse_logician_output)
HookRegistry.register("parse_judge_output", parse_judge_output)
