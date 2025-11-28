from typing import Dict, Any
from src.components.hook_registry import HookRegistry

def sanitize_and_anonymize_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    HOOK: sanitize_and_anonymize_input
    Logic: Vartijan (V1) RegEx-puhdistus, PII-poisto ja normalisointi.
    """
    print("[HOOK] Running Sanitization...")
    import re
    
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

    for key, value in data.items():
        if isinstance(value, str):
            # 1. Normalize UTF-8 and whitespace
            clean_val = value.strip()
            
            # 2. Robust PII Redaction
            for pii_type, pattern in pii_patterns.items():
                matches = re.findall(pattern, clean_val)
                if matches:
                    threats_detected.append(f"{pii_type} detected in {key}")
                    clean_val = re.sub(pattern, f"[REDACTED_{pii_type}]", clean_val)
            
            sanitized[key] = clean_val
        else:
            sanitized[key] = value
            
    return {
        "safe_data": sanitized,
        "threat_assessment": f"Detected: {', '.join(threats_detected)}" if threats_detected else "None detected",
        "is_safe": True
    }

# Register the hook
HookRegistry.register("sanitize_and_anonymize_input", sanitize_and_anonymize_input)
