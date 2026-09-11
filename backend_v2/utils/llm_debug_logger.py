"""LLM Debug Logging Utility."""

from __future__ import annotations

import asyncio
import datetime
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend_v2.models.domain.prompt_blocks import PromptBlock
    from backend_v2.models.prompt import CompiledPrompt

from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = ["log_structured_task_prompt", "write_debug_prompt_log", "write_llm_telemetry_log"]

_debug_file_locks: dict[asyncio.AbstractEventLoop, asyncio.Lock] = {}


def _get_debug_file_lock() -> asyncio.Lock:
    """Lazily resolves or creates an asyncio.Lock bound to the active event loop.

    Returns:
        The event loop-specific asyncio.Lock instance.
    """
    loop = asyncio.get_running_loop()
    if loop not in _debug_file_locks:
        _debug_file_locks[loop] = asyncio.Lock()
    return _debug_file_locks[loop]


async def write_debug_prompt_log(
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
    """Writes the generated LLM prompt and its origins to a debug log file asynchronously.

    This function appends to the execution's specific llm_debug_prompts.md file under an asyncio lock.
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
    if task_blueprint is not None:
        blueprint_label = task_blueprint
    else:
        blueprint_label = "N/A"
    lines.append(f"- **Task Blueprint**: {blueprint_label}")
    lines.append(f"- **Trigger Reason**: {trigger_reason}\n")

    lines.append("## 1. Prompt Source Blocks")

    if role_block is not None:
        role_info = f"{role_block.id} ('{role_block.category_id}')"
    else:
        role_info = "None"
    lines.append(f"- **Role Block**: {role_info}")

    if protocol_block is not None:
        protocol_info = f"{protocol_block.id} ('{protocol_block.category_id}')"
    else:
        protocol_info = "None"
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

    lock = _get_debug_file_lock()
    async with lock:
        try:
            with open(debug_file, "a", encoding="utf-8") as df:
                df.write("\n".join(lines) + "\n")
        except (OSError, ValueError, TypeError) as exc:
            logger.warning("[LLMDebugLogger] Failed to write debug prompt log: %s", exc)


async def log_structured_task_prompt(
    execution_id: str,
    step_id: str,
    sub_task: str | None,
    compiled_prompt: CompiledPrompt,
    expected_schema_name: str,
    attempt: int = 1,
) -> None:
    """Writes the structured task prompt (static prefix + dynamic messages) to a debug log asynchronously.

    Appends to data/files/executions/{execution_id}/llm_debug_prompts.md under an asyncio lock.
    Active only in development environment.

    Args:
        execution_id: The ID of the current execution.
        step_id: The ID of the current step.
        sub_task: Optional sub-task identifier (e.g., 'extractive_sensor_bo3_call_0').
        compiled_prompt: The strictly compiled prompt containing static and dynamic messages.
        expected_schema_name: The Pydantic model name the LLM is expected to return.
        attempt: The retry attempt number (1-based).

    Returns:
        None.
    """
    if get_settings().environment != "development":
        return

    target_dir = Path("data") / "files" / "executions" / execution_id
    target_dir.mkdir(parents=True, exist_ok=True)

    debug_file = target_dir / "llm_debug_prompts.md"

    task_label = "main"
    if sub_task:
        task_label = sub_task
    lines = []
    lines.append("\n---\n")
    lines.append(f"# Sub-Step Debug Log: {step_id} - {task_label} [Attempt {attempt}]")
    lines.append(f"Timestamp: {datetime.datetime.now(datetime.UTC).isoformat()}\n")

    lines.append("## 0. Context & Sub-Task")
    lines.append(f"- **Step ID**: `{step_id}`")
    lines.append(f"- **Sub-Task**: `{task_label}`")
    lines.append(f"- **Attempt**: {attempt}")
    lines.append(f"- **Expected Schema**: `{expected_schema_name}`\n")

    lines.append("## 1. Static Prefix Messages (Cacheable System & Context)")
    for idx, msg in enumerate(compiled_prompt.static_messages):
        lines.append(f"### Static Message [{idx}] ({msg.role})")
        lines.append("```xml")
        lines.append(msg.content)
        lines.append("```\n")

    lines.append("## 2. Dynamic Payload Messages (Tail)")
    for idx, msg in enumerate(compiled_prompt.dynamic_messages):
        lines.append(f"### Dynamic Message [{idx}] ({msg.role})")
        lines.append("```xml")
        lines.append(msg.content)
        lines.append("```\n")

    lock = _get_debug_file_lock()
    async with lock:
        try:
            with open(debug_file, "a", encoding="utf-8") as df:
                df.write("\n".join(lines) + "\n")
        except (OSError, ValueError, TypeError) as exc:
            logger.warning("[LLMDebugLogger] Failed to write structured task prompt debug log: %s", exc)


async def write_llm_telemetry_log(
    execution_id: str,
    step_id: str,
    duration_ms: int,
    cache_hit: bool,
    tokens: int,
    trigger_reason: str,
) -> None:
    """Writes machine-readable telemetry data to a JSON Lines file after LLM execution asynchronously.

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

    lock = _get_debug_file_lock()
    async with lock:
        try:
            with open(telemetry_file, "a", encoding="utf-8") as tf:
                tf.write(json.dumps(data) + "\n")
        except (OSError, ValueError, TypeError) as exc:
            logger.warning("[LLMDebugLogger] Failed to write telemetry log: %s", exc)
