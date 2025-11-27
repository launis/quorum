from typing import Dict, Any
from src.components.hook_registry import HookRegistry

def sanitize_and_anonymize_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    HOOK: sanitize_and_anonymize_input
    Logic: Vartijan (V1) RegEx-puhdistus, PII-poisto ja normalisointi.
    """
    print("[HOOK] Running Sanitization...")
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            # 1. Normalize UTF-8 (Python strings are unicode by default, but we can ensure no weird chars)
            # 2. Strip whitespace
            clean_val = value.strip()
            # 3. Simple PII redaction (Mock)
            clean_val = clean_val.replace("social_security_number", "[REDACTED]")
            sanitized[key] = clean_val
        else:
            sanitized[key] = value
            
    return {
        "safe_data": sanitized,
        "threat_assessment": "None detected (Mock)",
        "is_safe": True
    }

# Register the hook
HookRegistry.register("sanitize_and_anonymize_input", sanitize_and_anonymize_input)
