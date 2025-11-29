import json
import re
from typing import Any
from src.components.hook_registry import HookRegistry

def _clean_and_parse_json(text: str) -> dict[str, Any]:
    """
    Helper to extract and parse JSON from LLM output.
    Handles markdown code blocks and extra text by finding the first '{' and last '}'.
    """
    try:
        if not text:
            return {}

        # Find the first '{' and last '}'
        start = text.find('{')
        end = text.rfind('}')
        
        if start != -1 and end != -1 and end > start:
            cleaned = text[start:end+1]
            # Remove trailing commas (common LLM error)
            cleaned = re.sub(r',\s*}', '}', cleaned)
            cleaned = re.sub(r',\s*]', ']', cleaned)
            return json.loads(cleaned, strict=False)
        
        # Fallback: try cleaning markdown if braces logic failed (unlikely for valid objects)
        cleaned = re.sub(r'```json\s*', '', text)
        cleaned = re.sub(r'```', '', cleaned)
        # Remove trailing commas here too
        cleaned = re.sub(r',\s*}', '}', cleaned)
        cleaned = re.sub(r',\s*]', ']', cleaned)
        return json.loads(cleaned.strip(), strict=False)

    except json.JSONDecodeError as e:
        print(f"[Parsing] Warning: Failed to parse JSON: {e}")
        # Try AST literal_eval as fallback (handles trailing commas, single quotes)
        try:
            import ast
            # Fix JSON booleans/null for Python AST
            ast_text = cleaned.replace("true", "True").replace("false", "False").replace("null", "None")
            return ast.literal_eval(ast_text)
        except Exception as ast_e:
            print(f"[Parsing] Warning: AST parsing also failed: {ast_e}")
            print(f"[Parsing] Raw output start: {text[:500]}...")
            return {"raw_output": text}

def parse_analyst_output(data: dict[str, Any]) -> dict[str, Any]:
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

def parse_logician_output(data: dict[str, Any]) -> dict[str, Any]:
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

def parse_judge_output(data: dict[str, Any]) -> dict[str, Any]:
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
