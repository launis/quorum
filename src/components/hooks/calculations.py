from typing import Dict, Any
from src.components.hook_registry import HookRegistry

def calculate_input_control_ratio(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    HOOK: calculate_input_control_ratio
    Logic: Tuomarin (V8) Input-Control Ratio -laskenta.
    """
    print("[HOOK] Calculating Input-Control Ratio...")
    # Mock calculation based on text length
    prompt_len = len(data.get('prompt_text', ''))
    history_len = len(data.get('history_text', ''))
    
    ratio = prompt_len / (history_len + 1) # Avoid div by zero
    
    return {
        "input_control_ratio": ratio,
        "calculation_summary": f"Ratio calculated: {ratio:.2f}"
    }

HookRegistry.register("calculate_input_control_ratio", calculate_input_control_ratio)
