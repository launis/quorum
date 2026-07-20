"""LLM Debug Logging Utility."""

import datetime
import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend_v2.models.v2_core import PromptBlock

from backend_v2.settings import get_settings


def write_debug_prompt_log(
    execution_id: str,
    step_id: str,
    role_block: PromptBlock | None,
    protocol_block: PromptBlock | None,
    criteria_blocks: list[PromptBlock],
    base_system_prompt: str,
    user_payload: str,
    task_blueprint: str | None = None,
    expected_schema_name: str | None = None,
    trigger_reason: str = "initial",
) -> None:
    """Writes the generated LLM prompt and its origins to a debug log file.

    This function appends to the execution's specific llm_debug_prompts.md file.
    It is only active when environment == 'development'.

    Args:
        execution_id: The ID of the current execution.
        step_id: The ID of the current step.
        role_block: The PromptBlock defining the LLM persona/role.
        protocol_block: The PromptBlock defining the extraction protocol.
        criteria_blocks: A list of PromptBlocks used as evaluation criteria.
        base_system_prompt: The fully constructed system prompt.
        user_payload: The fully constructed XML payload for the user message.
        task_blueprint: The blueprint ID to explain how this command was triggered.
        expected_schema_name: The Pydantic model name the LLM is expected to return.
        trigger_reason: The dynamic reason why this call was triggered.

    Returns:
        None.
    """
    if get_settings().environment != "development":
        return

    target_dir = Path("data") / "files" / "executions" / execution_id
    target_dir.mkdir(parents=True, exist_ok=True)

    debug_file = target_dir / "llm_debug_prompts.md"

    lines = []
    lines.append("\n---\n")
    lines.append(f"# Step Debug Log: {step_id}")
    lines.append(f"Timestamp: {datetime.datetime.now(datetime.UTC).isoformat()}\n")

    lines.append("## 0. Context & Trigger")
    lines.append(f"- **Task Blueprint**: {task_blueprint if task_blueprint else 'N/A'}")
    lines.append(f"- **Trigger Reason**: {trigger_reason}\n")

    lines.append("## 1. Prompt Source Blocks")

    role_info = f"{role_block.id} ('{role_block.category_id}')" if role_block else "None"
    lines.append(f"- **Role Block**: {role_info}")

    protocol_info = f"{protocol_block.id} ('{protocol_block.category_id}')" if protocol_block else "None"
    lines.append(f"- **Protocol Block**: {protocol_info}")

    lines.append("- **Criteria Blocks**:")
    for cb in criteria_blocks:
        lines.append(f"  - {cb.id} ('{cb.category_id}')")

    lines.append("\n## 2. Base System Prompt")
    lines.append("```text")
    lines.append(base_system_prompt)
    lines.append("```\n")

    lines.append("## 3. User Payload")
    lines.append(f"- **Payload Size**: {len(user_payload)} characters")
    if expected_schema_name:
        lines.append(f"- **Expected Schema**: `{expected_schema_name}`")
    lines.append("```xml")
    lines.append(user_payload)
    lines.append("```\n")

    with open(debug_file, "a", encoding="utf-8") as df:
        df.write("\n".join(lines))


def write_llm_telemetry_log(
    execution_id: str,
    step_id: str,
    duration_ms: int,
    cache_hit: bool,
    tokens: int,
    trigger_reason: str,
) -> None:
    """Writes machine-readable telemetry data to a JSON Lines file after LLM execution.

    Args:
        execution_id: The ID of the current execution.
        step_id: The ID of the current step.
        duration_ms: Execution duration in milliseconds.
        cache_hit: Whether the response was served from cache.
        tokens: Number of tokens consumed/processed.
        trigger_reason: The reason for the trigger (e.g., 'retry', 'initial').

    Returns:
        None.
    """
    if get_settings().environment != "development":
        return

    target_dir = Path("data") / "files" / "executions" / execution_id
    target_dir.mkdir(parents=True, exist_ok=True)

    telemetry_file = target_dir / "llm_telemetry.jsonl"

    data = {
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "step_id": step_id,
        "duration_ms": duration_ms,
        "cache_hit": cache_hit,
        "tokens": tokens,
        "trigger_reason": trigger_reason,
    }

    with open(telemetry_file, "a", encoding="utf-8") as tf:
        tf.write(json.dumps(data) + "\n")
