"""Security Tasks.

Functional tasks for security operations, registered for workflow execution.
"""

import logging
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from backend.core.registry import TaskRegistry
from backend.core.security import sanitize_text

logger = logging.getLogger(__name__)


# --- Schemas ---

class RawInput(BaseModel):
    """Input schema for the Guard task."""
    
    # We allow optional inputs, but at least one should usually be present.
    history_text: str | None = Field(default=None, description="Conversation history.")
    product_text: str | None = Field(default=None, description="Product description.")
    reflection_text: str | None = Field(default=None, description="Reflection text.")
    
    model_config = ConfigDict(extra="ignore")


class GuardResult(BaseModel):
    """Output schema for the Guard task."""
    
    is_safe: bool = Field(..., description="Whether the content is considered safe.")
    sanitized_inputs: dict[str, str] = Field(..., description="Map of sanitized text fields.")
    threats_detected: List[str] = Field(default_factory=list, description="List of detected threats.")
    
    model_config = ConfigDict(extra="ignore")


# --- Handler ---

@TaskRegistry.register_task(
    name="guard",
    input_schema=RawInput,
    output_schema=GuardResult,
    description="Sanitizes input text and detects PII/banned phrases."
)
async def guard_task(input_data: RawInput) -> GuardResult:
    """
    Sanitizes all text fields in the input.
    """
    logger.info("Running Guard Task...")
    
    sanitized_map = {}
    all_threats = []
    
    # Process each field
    # We iterate over the model dump to be generic
    input_dict = input_data.model_dump(exclude_unset=True)
    
    for key, text in input_dict.items():
        if isinstance(text, str):
            clean_text, threats = sanitize_text(text)
            sanitized_map[key] = clean_text
            if threats:
                all_threats.extend([f"{key}: {t}" for t in threats])
        else:
            # Pass through non-string types? or ignore?
            # Security hook only handles text.
            pass
            
    is_safe = len(all_threats) == 0
    
    if not is_safe:
        logger.warning(f"Guard Task detected threats: {all_threats}")
    else:
        logger.info("Guard Task passed: No threats detected.")
        
    return GuardResult(
        is_safe=is_safe,
        sanitized_inputs=sanitized_map,
        threats_detected=all_threats
    )
