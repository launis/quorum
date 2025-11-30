import json
import re
from typing import Any
from src.components.hook_registry import HookRegistry

def _repair_json_string(text: str) -> str:
    """
    Attempts to repair common JSON syntax errors, specifically invalid escape sequences and unescaped control characters.
    """
    # 1. Fix invalid \u escapes (e.g., \u00 or \uXXXX where X is not hex)
    text = re.sub(r'\\u(?![0-9a-fA-F]{4})', r'\\\\u', text)

    # 2. Fix unescaped backslashes that aren't part of a valid escape sequence
    text = re.sub(r'\\(?![/\"\\bfnrtu])', r'\\\\', text)

    # 3. Fix unescaped control characters (newlines, tabs) inside strings
    # We use a regex to identify JSON strings and then escape control chars within them.
    # Pattern matches a double-quoted string, handling escaped quotes.
    # We use a callback to process the content of the string.
    def escape_controls(match):
        content = match.group(0)
        # Don't escape the surrounding quotes
        inner = content[1:-1]
        # Replace literal newlines with \n and tabs with \t
        inner = inner.replace('\n', '\\n').replace('\r', '').replace('\t', '\\t')
        return f'"{inner}"'

    # Regex for JSON string: " ( escaped char OR non-quote/non-backslash )* "
    # We need to be careful not to match across the whole file if quotes are unbalanced, 
    # but for repair we assume somewhat valid structure.
    # [^"\\] matches any char that is not " or \
    # \\. matches any escaped char (e.g. \", \\, \n)
    # We use DOTALL to match newlines in [^"\\] implicitly (since it's a negated class)
    # Actually [^...] matches newlines by default.
    json_string_pattern = r'"(?:[^"\\]|\\.)*"'
    
    # We only apply this if we detect potential unescaped newlines to avoid performance hit on huge files
    if '\n' in text or '\t' in text:
        text = re.sub(json_string_pattern, escape_controls, text)

    return text

def _balance_braces(text: str) -> str:
    """
    Attempts to balance unclosed braces and quotes in a truncated JSON string.
    """
    # 1. Check for unclosed string
    # Count unescaped quotes
    # We can iterate to find if we are inside a string
    in_string = False
    escape = False
    for char in text:
        if char == '\\':
            escape = not escape
        elif char == '"' and not escape:
            in_string = not in_string
            escape = False
        else:
            escape = False
            
    if in_string:
        text += '"'

    # 2. Balance braces
    open_braces = text.count('{')
    close_braces = text.count('}')
    open_brackets = text.count('[')
    close_brackets = text.count(']')
    
    # Simple appending (stack-based would be better but this is a heuristic)
    # Usually truncation happens at the end, so we just need to close what's open.
    # But we need to close them in correct order?
    # If we have `{"key": [ ...`, we need `]}`.
    # Let's do a stack approach.
    stack = []
    escape = False
    in_string = False
    
    # Re-scan with stack
    for char in text:
        if char == '\\':
            escape = not escape
            continue
            
        if char == '"' and not escape:
            in_string = not in_string
        
        if not in_string:
            if char == '{':
                stack.append('}')
            elif char == '[':
                stack.append(']')
            elif char == '}' or char == ']':
                if stack:
                    # Ideally we check if it matches stack[-1], but if it's malformed we might just pop
                    if stack[-1] == char:
                        stack.pop()
        
        escape = False

    # Append missing closers in reverse order
    while stack:
        text += stack.pop()
        
    return text

def _clean_and_parse_json(text: str) -> dict[str, Any]:
    """
    Helper to extract and parse JSON from LLM output.
    Iterates through all potential JSON objects and returns the one that looks like the expected result (has 'metadata').
    """
    if not text:
        return {}

    print(f"[Parsing] Raw text length: {len(text)}")
    
    candidates = []
    decoder = json.JSONDecoder()
    
    # Pre-process: Repair the text
    repaired_text = _repair_json_string(text)
    
    # Attempt to balance braces if it looks truncated
    # We apply this to the whole text if it doesn't end with } or ]
    stripped = repaired_text.strip()
    if stripped and stripped[-1] not in ['}', ']']:
        print("[Parsing] Text seems truncated. Applying brace balancing.")
        repaired_text = _balance_braces(repaired_text)

    if repaired_text != text:
        print("[Parsing] Applied JSON repair (escapes/newlines/balancing).")
    
    # 1. Try to find Markdown code blocks first (using repaired text)
    code_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    matches = re.findall(code_block_pattern, repaired_text, re.DOTALL)
    for json_str in matches:
        try:
            obj = json.loads(json_str)
            if isinstance(obj, dict):
                candidates.append(obj)
        except json.JSONDecodeError:
            # Try balancing the code block content too
            try:
                balanced = _balance_braces(json_str)
                obj = json.loads(balanced)
                if isinstance(obj, dict):
                    candidates.append(obj)
            except json.JSONDecodeError:
                continue

    # 2. Scan the entire text for JSON objects using raw_decode
    # We use the repaired text
    text_to_scan = repaired_text
    idx = 0
    while idx < len(text_to_scan):
        start_idx = text_to_scan.find('{', idx)
        if start_idx == -1:
            break
        
        try:
            obj, end_idx = decoder.raw_decode(text_to_scan, start_idx)
            if isinstance(obj, dict):
                candidates.append(obj)
            idx = end_idx 
        except json.JSONDecodeError as e:
            # If raw_decode fails, it might be due to truncation at the very end
            # We can try to extract from start_idx to the end and balance it
            try:
                potential_json = text_to_scan[start_idx:]
                balanced_json = _balance_braces(potential_json)
                obj = json.loads(balanced_json)
                if isinstance(obj, dict):
                    print(f"[Parsing] Successfully parsed balanced JSON starting at {start_idx}")
                    candidates.append(obj)
                    break
            except json.JSONDecodeError:
                pass
            
            idx = start_idx + 1 # Move past this '{' and try again

    print(f"[Parsing] Found {len(candidates)} JSON candidates.")

    # 3. Select the best candidate
    # Priority: Has 'metadata' key (strongest indicator of our schema)
    for i, obj in enumerate(candidates):
        keys = list(obj.keys())
        # print(f"[Parsing] Candidate {i} keys: {keys}")
        if 'metadata' in obj:
            print(f"[Parsing] Selected candidate {i} with 'metadata' key.")
            return obj
            
    # Fallback: Return the last valid dictionary found (often the final answer)
    if candidates:
        print("[Parsing] No candidate with 'metadata' found. Returning the last candidate.")
        return candidates[-1]

    print("[Parsing] Warning: No valid JSON objects found.")
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

def ensure_tainted_data_content(data: dict[str, Any]) -> dict[str, Any]:
    """
    HOOK: ensure_tainted_data_content
    Logic: Ensures TaintedDataContent fields are populated.
           If LLM returned null/missing, copy from input.
    """
    print("[HOOK] Ensuring TaintedData content...")
    
    # Check if 'data' key exists (from LLM)
    if 'data' not in data or not isinstance(data['data'], dict):
        print("[HOOK] Warning: 'data' field missing from LLM output.")
        return {} 

    tainted_content = data['data']
    
    # Map input keys to TaintedData keys
    mapping = {
        'keskusteluhistoria': 'history_text',
        'lopputuote': 'product_text',
        'reflektiodokumentti': 'reflection_text'
    }
    
    updates = {}
    for target_key, source_key in mapping.items():
        if not tainted_content.get(target_key):
            # If missing or null/empty in LLM output, copy from input
            if source_key in data:
                print(f"[HOOK] Copying {source_key} to {target_key}")
                updates[target_key] = data[source_key]
            else:
                 print(f"[HOOK] Warning: Source key {source_key} not found in input data.")

    # Return the updated 'data' dictionary
    full_data_content = tainted_content.copy()
    full_data_content.update(updates)
    
    return {"data": full_data_content}

HookRegistry.register("ensure_tainted_data_content", ensure_tainted_data_content)
