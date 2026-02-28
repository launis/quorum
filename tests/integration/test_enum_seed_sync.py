import json
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel

def load_seed_components() -> list[dict[str, Any]]:
    """Load all components from seed_data.json."""
    seed_path = Path("backend/seed/seed_data.json")
    if not seed_path.exists():
        return []
    with open(seed_path, encoding='utf-8') as f:
        data = json.load(f)
    return data.get("components", [])

def test_dynamic_schema_enum_sync():
    """
    Dynamically tests that if a prompt explicitly instructs the LLM
    to output specific string literals (e.g. 'POST_HOC', 'GENUINE'), 
    those string literals exist exactly in the corresponding Python 
    Pydantic Schema (Enum or Literal annotation), and vice versa.
    """
    components = load_seed_components()
    tasks = [c for c in components if c.get("type") == "task"]
    
    # 1. Find all Prompt instructions that specify strict string options
    # We look for lines in the content that dictate strict string outputs
    # Examples:
    # "TUNNISTA Strategia (pakollinen englanninkielinen arvo!): 'Zero-shot', 'Few-shot', 'Chain-of-Thought'."
    # "Arvioi: 'POST_HOC' (Virheellinen), 'UNCERTAIN' (Epävarma), 'GENUINE' (Aito)."
    
    # We dynamically load all python models in backend.models.domain
    import importlib
    import pkgutil
    import inspect
    import backend.models.domain as domain_models
    from typing import get_args

    # Discover all Pydantic models in the domain layer
    all_models: dict[str, type[BaseModel]] = {}
    for _, module_name, _ in pkgutil.iter_modules(domain_models.__path__):
        mod = importlib.import_module(f"backend.models.domain.{module_name}")
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            if issubclass(obj, BaseModel) and obj is not BaseModel:
                all_models[name] = obj

    errors = []

    for task in tasks:
        content = task.get("content", "")
        if not content:
            continue
            
        task_id = task.get("slug") or task.get("id")
        
        # Heuristic: We look for single-quoted terms that represent Enums in the prompt.
        # Often they follow a colon or are grouped together.
        lines = content.splitlines()
        for line in lines:
            # If the line explicitly defines multiple quoted strings as options, AND it's not a root schema instruction
            if "varmista, että vastaus sisältää" in line.lower() or "tulosta vastauksesi" in line.lower():
                continue
                
            quotes = re.findall(r"'([^']+)'", line)
            if len(quotes) > 1 and ("pakollinen" in line.lower() or "arvioi:" in line.lower() or "luokittele:" in line.lower() or "tunnista" in line.lower() or "uskottavuus" in line.lower() or "väite" in line.lower()):
                options_in_prompt = set(quotes)
                
                # To make this fully dynamic, we look at the expected OUTPUT SCHEMA of this task
                # and see if ANY field's Enum or Literal precisely matches these options.
                # However, tasks don't always directly link their schema names in the 'content',
                # so we scan all domain models to find the matching Enum/Literal.
                
                match_found = False
                closest_match_diff = 999
                closest_orphan_info = ""
                
                for model_name, model_cls in all_models.items():
                    for field_name, field_info in model_cls.model_fields.items():
                        # Extract allowed strings from Literal or Enum
                        allowed_strings = set()
                        
                        # Check Literal
                        from typing import get_origin, get_args
                        if get_origin(field_info.annotation) is getattr(importlib.import_module("typing"), "Literal", None):
                            allowed_strings = set(get_args(field_info.annotation))
                        else:
                            # Check Enum
                            annotation = field_info.annotation
                            # Handle Optional[Enum]
                            if get_origin(annotation) is getattr(importlib.import_module("typing"), "Union", None):
                                type_args = get_args(annotation)
                                for arg in type_args:
                                    if inspect.isclass(arg) and issubclass(arg, getattr(importlib.import_module("enum"), "Enum")):
                                        annotation = arg
                                        break
                                        
                            if inspect.isclass(annotation) and issubclass(annotation, getattr(importlib.import_module("enum"), "Enum")):
                                allowed_strings = {e.value for e in annotation}
                        
                        if not allowed_strings:
                            continue
                            
                        # Compare
                        orphans_in_prompt = options_in_prompt - allowed_strings
                        orphans_in_code = allowed_strings - options_in_prompt
                        total_diff = len(orphans_in_prompt) + len(orphans_in_code)
                        
                        if total_diff == 0:
                            match_found = True
                            break
                        elif total_diff < closest_match_diff and len(options_in_prompt.intersection(allowed_strings)) > 0:
                            closest_match_diff = total_diff
                            closest_orphan_info = f"Matched mostly with {model_name}.{field_name}. Orphans in LLM Prompt: {orphans_in_prompt}. Orphans in Code: {orphans_in_code}."
                    
                    if match_found:
                        break
                        
                if not match_found:
                    errors.append(
                        f"Unsynchronized Enums in Task '{task_id}': \n"
                        f"Prompt instructed LLM to use: {options_in_prompt}\n"
                        f"But no Pydantic Model precisely matched this list without orphans.\n"
                        f"Best guess: {closest_orphan_info}\n"
                    )

    assert not errors, "\n\n" + "\n".join(errors)
