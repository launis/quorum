import re
import os
import json
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- 1. Sanitization Hook ---

def sanitize_and_anonymize_input(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Step 1 Pre-hook: Sanitizes and anonymizes input data.
    """
    print("[HOOK] Running sanitize_and_anonymize_input...")
    
    # Define Regex patterns for PII
    pii_patterns = {
        "EMAIL": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "PHONE_FI": r"(?:\+358|0)\s?(?:4[0-9]|50|457)\s?[0-9]{3,4}\s?[0-9]{3,4}",
        "HETU": r"[0-3][0-9][0-1][0-9][0-9]{2}[+-A][0-9]{3}[0-9A-FHJ-NPR-Y]",
        "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b",
        "IP_ADDRESS": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
    }

    sanitized = {}
    threats_detected = []

    for key, value in inputs.items():
        if isinstance(value, str):
            # 1. Normalize Unicode (Basic)
            clean_value = "".join(ch for ch in value if ch.isprintable())
            
            # 2. Robust PII Redaction
            for pii_type, pattern in pii_patterns.items():
                matches = re.findall(pattern, clean_value)
                if matches:
                    threats_detected.append(f"{pii_type} detected in {key}")
                    clean_value = re.sub(pattern, f"[REDACTED_{pii_type}]", clean_value)
            
            sanitized[key] = clean_value
        else:
            sanitized[key] = value
            
    # Add metadata about sanitization
    from datetime import datetime
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if 'metadata' not in sanitized:
        sanitized['metadata'] = {}
    
    sanitized['metadata']['timestamp'] = timestamp_str
    
    sanitized['security_check'] = {
        "threats_detected": threats_detected,
        "is_safe": True
    }
    return sanitized

# --- 2. Retrieval Hook ---

def execute_rag_retrieval(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Step 2 Pre-hook: Executes RAG retrieval.
    Currently a placeholder for the actual RAG logic.
    """
    print("[HOOK] Running execute_rag_retrieval...")
    # In a real implementation, this would query a vector DB.
    return inputs

# --- 3. Search Hook ---

def execute_google_search(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Step 7 Pre-hook: Executes Google Search using Custom Search JSON API.
    """
    print("[HOOK] Running execute_google_search...")
    
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    cx = os.getenv("GOOGLE_SEARCH_CX")
    
    if not api_key or not cx:
        print("   [Warning] Missing GOOGLE_SEARCH_API_KEY or GOOGLE_SEARCH_CX")
        inputs['google_search_results'] = "Search disabled (Missing API Keys)"
        return inputs

    queries = []
    # Simple fallback query extraction
    if 'hypoteesit' in inputs:
        # Try to extract a query from hypotheses if available (simplified)
        queries.append("Cognitive Quorum fact check") 
    else:
        queries.append("Cognitive Quorum verification")

    all_results = []
    try:
        service = build("customsearch", "v1", developerKey=api_key)
        
        for query in queries[:1]: # Limit to 1 query for now to save quota
            print(f"   Query: {query}")
            res = service.cse().list(q=query, cx=cx, num=3).execute()
            
            for item in res.get('items', []):
                all_results.append({
                    "title": item.get('title'),
                    "link": item.get('link'),
                    "snippet": item.get('snippet')
                })
                
        inputs['google_search_results'] = json.dumps(all_results, indent=2)
        
    except Exception as e:
        print(f"   Search failed: {e}")
        inputs['google_search_results'] = f"Search failed: {str(e)}"

    return inputs

# --- 4. Calculation Hook ---

def calculate_final_scores(inputs: Dict[str, Any], output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Step 8 Post-hook: Calculates final scores.
    """
    print("[HOOK] Running calculate_final_scores...")
    
    try:
        # Extract scores from Step 8 output
        scores = output.get('pisteet', {})
        
        if not scores:
            print("   [Warning] No scores found to calculate.")
            return output

        total = 0
        count = 0
        details = []
        
        for category, score_data in scores.items():
            if isinstance(score_data, dict) and 'arvosana' in score_data:
                try:
                    val = float(score_data['arvosana'])
                    total += val
                    count += 1
                    details.append(f"{category}: {val}")
                except (ValueError, TypeError):
                    pass
        
        average = total / count if count > 0 else 0
        summary = f"Total Score: {total}/{count*4} (Avg: {average:.2f})"
        print(f"   {summary}")
        
        # Inject calculated stats into output
        output['lasketut_yhteispisteet'] = total
        output['lasketut_keskiarvo'] = average
        output['score_summary'] = summary
        
    except Exception as e:
        print(f"   Calculation failed: {e}")
        
    return output

# --- 5. Reporting Hook ---

def generate_jinja2_report(inputs: Dict[str, Any], output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Step 9 Post-hook: Generates the final report using Jinja2.
    """
    print("[HOOK] Running generate_jinja2_report...")
    
    try:
        # Locate templates directory
        # Assuming we are in backend/hooks.py, templates are in ../src/components/templates
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # c:\Users\risto\OneDrive\quorum
        template_dir = os.path.join(base_dir, 'src', 'components', 'templates')
        
        if not os.path.exists(template_dir):
            print(f"   [Error] Template directory not found: {template_dir}")
            return output

        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template('report_template.jinja2')
        
        # Prepare data for template
        # We need to gather data from the 'inputs' which contains the context (history of all steps)
        # 'output' contains the XAI report content, but the template might need structured data
        
        # The context (inputs) has keys like 'pisteet', 'critical_findings', etc.
        data = inputs 
        scores = data.get('pisteet', {})
        
        report_data = {
            "summary": data.get('kriittiset_havainnot_yhteenveto') or data.get('score_summary') or 'Yhteenveto puuttuu.',
            "critical_findings": data.get('kriittiset_havainnot_yhteenveto') if isinstance(data.get('kriittiset_havainnot_yhteenveto'), list) else data.get('eettiset_havainnot', []),
            "pre_mortem_signals": data.get('pre_mortem_analyysi'),
            "hitl_required": data.get('aitous_epaily', False), # Using aitus_epaily as proxy for HITL
            "ethical_issues": data.get('eettiset_havainnot', []),
            "audit_questions": data.get('faktantarkistus_rfi', []),
            "uncertainty": data.get('uncertainty', {}),
            "scores": {
                "analysis": {
                    "score": scores.get('analyysi_ja_prosessi', {}).get('arvosana', 'N/A'),
                    "reasoning": scores.get('analyysi_ja_prosessi', {}).get('perustelu', '')
                },
                "evaluation": {
                    "score": scores.get('arviointi_ja_argumentaatio', {}).get('arvosana', 'N/A'),
                    "reasoning": scores.get('arviointi_ja_argumentaatio', {}).get('perustelu', '')
                },
                "synthesis": {
                    "score": scores.get('synteesi_ja_luovuus', {}).get('arvosana', 'N/A'),
                    "reasoning": scores.get('synteesi_ja_luovuus', {}).get('perustelu', '')
                }
            }
        }

        # Check if we have valid data to render
        if not scores and output.get('xai_report_content'):
            print("   [HOOK] Missing 'pisteet' in inputs, but Mock content exists. Skipping template rendering to avoid broken report.")
            return output

        rendered_report = template.render(
            report_content=report_data,
            final_verdict="KATSO PISTEYTYS",
            reliability_score="EHDOLLEINEN" if data.get('hitl_required') else "KORKEA",
            disclaimer="Tämä on automaattisesti generoitu raportti." # Placeholder
        )
        
        # If output already has content (e.g. from Mock LLM), append the detailed report
        if output.get('xai_report_content'):
            print("   [HOOK] Appending rendered report to existing content.")
            output['xai_report_content'] += "\n\n---\n\n" + rendered_report
        else:
            output['xai_report_content'] = rendered_report
            
        print("   Report generated successfully.")
        
    except Exception as e:
        print(f"   Report generation failed: {e}")
        output['xai_report_error'] = str(e)
        
    return output

# --- 6. Parsing Helpers & Hooks ---

def _repair_json_string(text: str) -> str:
    """
    Attempts to repair common JSON syntax errors.
    """
    # 1. Fix invalid \u escapes
    text = re.sub(r'\\u(?![0-9a-fA-F]{4})', r'\\\\u', text)
    # 2. Fix unescaped backslashes
    text = re.sub(r'\\(?![/\"\\bfnrtu])', r'\\\\', text)
    
    def escape_controls(match):
        content = match.group(0)
        inner = content[1:-1]
        inner = inner.replace('\n', '\\n').replace('\r', '').replace('\t', '\\t')
        return f'"{inner}"'

    if '\n' in text or '\t' in text:
        json_string_pattern = r'"(?:[^"\\]|\\.)*"'
        text = re.sub(json_string_pattern, escape_controls, text)

    return text

def _balance_braces(text: str) -> str:
    """
    Attempts to balance unclosed braces.
    """
    stack = []
    escape = False
    in_string = False
    
    for char in text:
        if char == '\\':
            escape = not escape
            continue
        if char == '"' and not escape:
            in_string = not in_string
        if not in_string:
            if char == '{': stack.append('}')
            elif char == '[': stack.append(']')
            elif char == '}' or char == ']':
                if stack: stack.pop()
        escape = False

    while stack:
        text += stack.pop()
        
    return text

def _clean_and_parse_json(text: str) -> Dict[str, Any]:
    """
    Helper to extract and parse JSON from LLM output.
    """
    if not text: return {}
    
    candidates = []
    decoder = json.JSONDecoder()
    repaired_text = _repair_json_string(text)
    
    # Try finding code blocks
    matches = re.findall(r'```(?:json)?\s*(\{.*?\})\s*```', repaired_text, re.DOTALL)
    for json_str in matches:
        try:
            candidates.append(json.loads(json_str))
        except json.JSONDecodeError:
            try:
                candidates.append(json.loads(_balance_braces(json_str)))
            except: pass

    # Scan for JSON objects and arrays
    idx = 0
    while idx < len(repaired_text):
        # Find next potential start
        start_obj = repaired_text.find('{', idx)
        start_arr = repaired_text.find('[', idx)
        
        if start_obj == -1 and start_arr == -1:
            break
            
        if start_obj != -1 and (start_arr == -1 or start_obj < start_arr):
            start_idx = start_obj
        else:
            start_idx = start_arr
            
        try:
            obj, end_idx = decoder.raw_decode(repaired_text, start_idx)
            if isinstance(obj, (dict, list)): candidates.append(obj)
            idx = end_idx
        except json.JSONDecodeError:
            idx = start_idx + 1

    # Select best candidate (prefer 'metadata')
    for obj in candidates:
        if 'metadata' in obj: return obj
    
    return candidates[-1] if candidates else {"raw_output": text}

def parse_analyst_output(inputs: Dict[str, Any], output: Dict[str, Any]) -> Dict[str, Any]:
    print("[HOOK] Parsing Analyst Output...")
    # If output is already a dict (from engine), use it. If string, parse it.
    if isinstance(output, dict): return output
    return _clean_and_parse_json(str(output))

def parse_logician_output(inputs: Dict[str, Any], output: Dict[str, Any]) -> Dict[str, Any]:
    print("[HOOK] Parsing Logician Output...")
    if isinstance(output, dict): return output
    return _clean_and_parse_json(str(output))

def parse_judge_output(inputs: Dict[str, Any], output: Dict[str, Any]) -> Dict[str, Any]:
    print("[HOOK] Parsing Judge Output...")
    if isinstance(output, dict): return output
    return _clean_and_parse_json(str(output))

def ensure_tainted_data_content(inputs: Dict[str, Any], output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensures TaintedDataContent fields are populated.
    """
    print("[HOOK] Ensuring TaintedData content...")
    
    # If output is string, try to parse it first
    if isinstance(output, str):
        output = _clean_and_parse_json(output)

    if 'data' not in output or not isinstance(output['data'], dict):
        output['data'] = {}

    tainted_content = output['data']
    mapping = {
        'keskusteluhistoria': 'history_text',
        'lopputuote': 'product_text',
        'reflektiodokumentti': 'reflection_text'
    }
    
    for target_key, source_key in mapping.items():
        if not tainted_content.get(target_key):
            if source_key in inputs:
                print(f"[HOOK] Copying {source_key} to {target_key}")
                tainted_content[target_key] = inputs[source_key]
    
    output['data'] = tainted_content
    return output
