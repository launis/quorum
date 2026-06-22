import sys
import re

with open(r'c:\src\quorum\backend_v2\services\orchestrator\strategies\llm_execution\chunk_worker.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

out = []
for idx, line in enumerate(lines):
    if "class ChunkWorker:" in line:
        out.append('''def _is_transient_chunk_error(exc: BaseException) -> bool:
    """Classify whether a chunk-level error is transient (retryable) or structural (terminal)."""
    import litellm
    import asyncio

    TRANSIENT_TYPES = (
        asyncio.TimeoutError,
        ConnectionError,
        getattr(litellm, "APIConnectionError", type(None)),
        getattr(litellm, "RateLimitError", type(None)),
        getattr(litellm, "ServiceUnavailableError", type(None)),
        getattr(litellm, "Timeout", type(None)),
    )
    TRANSIENT_KEYWORDS = ("APIConnectionError", "ServiceUnavailable", "Timeout", "Resource exhausted")

    if isinstance(exc, ExceptionGroup):
        return all(_is_transient_chunk_error(inner) for inner in exc.exceptions)

    if isinstance(exc, TRANSIENT_TYPES):
        return True

    error_str = str(exc)
    return any(keyword in error_str for keyword in TRANSIENT_KEYWORDS)

''')
    out.append(line)

content = "".join(out)

# Find where try starts in process_chunk
try_idx = content.find("        try:\n            if effective_mcp_tools:")
except_idx = content.find("        except (LLMSchemaValidationError, AppException, ExceptionGroup) as e:")

if try_idx == -1 or except_idx == -1:
    print("Could not find try or except block!")
    sys.exit(1)

# Extract the inner part of the try block
try_block_inner = content[try_idx + 13 : except_idx]

# Replace `return chunk_final, chunk_usage, chunk_traces, prompt_context` with injection
try_block_inner = try_block_inner.replace(
    "            return chunk_final, chunk_usage, chunk_traces, prompt_context",
    "            if attempt > 0:\n                chunk_final[\"_dlq_retry_count\"] = attempt\n            return chunk_final, chunk_usage, chunk_traces, prompt_context"
)

# Indent it by 4 spaces
indented_inner = "\n".join("    " + line if line.strip() else line for line in try_block_inner.split('\n'))

new_try_block = f"""        MAX_CHUNK_RETRIES = 2
        attempt = 0

        while attempt <= MAX_CHUNK_RETRIES:
            try:
{indented_inner}"""

except_block_original = content[except_idx : content.find("            return chunk_final, None, [], prompt_context", except_idx) + len("            return chunk_final, None, [], prompt_context")]

new_except_block = """        except (LLMSchemaValidationError, AppException, ExceptionGroup, Exception) as e:

            def _is_structural(exc: BaseException) -> bool:
                if isinstance(exc, ExceptionGroup):
                    return any(_is_structural(inner) for inner in exc.exceptions)
                return isinstance(exc, (LLMSchemaValidationError, AppException)) or not _is_transient_chunk_error(exc)

            if attempt < MAX_CHUNK_RETRIES and _is_transient_chunk_error(e) and not _is_structural(e):
                attempt += 1
                backoff_seconds = min(10 * (2 ** (attempt - 1)), 60)
                logger.warning("[ChunkWorker] Transient error detected. Retrying chunk (attempt %d/%d)...", attempt, MAX_CHUNK_RETRIES)
                import asyncio
                await asyncio.sleep(backoff_seconds)
                continue

            if _is_structural(e) and not isinstance(e, ExceptionGroup):
                raise e

            if attempt > 0:
                chunk_final["_dlq_retry_count"] = attempt

            def _unwrap_error(exc: BaseException) -> str:
                if isinstance(exc, ExceptionGroup):
                    return " | ".join(_unwrap_error(inner) for inner in exc.exceptions)
                return str(exc)

            reason_str = _unwrap_error(e)

            logger.error(
                f"[ChunkWorker] Caught error: {reason_str}. Routing to DLQ.",
                extra={"error_code": "DLQ_ROUTING"},
                exc_info=True,
            )
            fallback_reason = f"Chunk Processing Failed: {reason_str}"
            chunk_final.update({
                "_dlq_status": "FAILED/DLQ",
                "reason": fallback_reason,
            })
            # Graceful DLQ Fallback: Map the failure to individual elements
            if has_shuffled_atoms and chunk is not None:
                chunk_final["evaluations"] = []
                for item in getattr(chunk, "items", []):
                    aid = item.get("atom_id") if isinstance(item, dict) else None
                    if aid:
                        chunk_final["evaluations"].append(
                            {
                                "atom_id": aid,
                                "status": "DLQ",
                                "exact_quote": None,
                                "contextual_override": False,
                                "semantic_reasoning": fallback_reason,
                            }
                        )
            else:
                for crit in chunk_criteria:
                    chunk_final[crit.id] = {
                        "status": "DLQ",
                        "exact_quote": None,
                        "contextual_override": False,
                        "semantic_reasoning": fallback_reason,
                    }

            return chunk_final, None, [], prompt_context"""

content = content.replace(content[try_idx:content.find("            return chunk_final, None, [], prompt_context", except_idx) + len("            return chunk_final, None, [], prompt_context")], new_try_block + new_except_block)

with open(r'c:\src\quorum\backend_v2\services\orchestrator\strategies\llm_execution\chunk_worker.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
