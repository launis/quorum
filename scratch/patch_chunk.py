import sys

with open('backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py', 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

start_idx = -1
for i, line in enumerate(lines):
    if line == "        if effective_mcp_tools:":
        start_idx = i
        break

if start_idx == -1:
    print("Could not find start idx")
    sys.exit(1)

end_idx = -1
for i in range(start_idx, len(lines)):
    if lines[i] == "        return chunk_final, chunk_usage, chunk_traces, prompt_context":
        end_idx = i
        break

if end_idx == -1:
    print("Could not find end idx")
    sys.exit(1)

new_lines = lines[:start_idx]
new_lines.append("        try:")
for i in range(start_idx, end_idx + 1):
    if lines[i].strip() == "":
        new_lines.append("")
    else:
        new_lines.append("    " + lines[i])

new_lines.extend("""
        except (LLMSchemaValidationError, AppException, ExceptionGroup) as e:

            def _has_programmatic_errors(exc: BaseException) -> bool:
                if isinstance(exc, ExceptionGroup):
                    return any(_has_programmatic_errors(inner) for inner in exc.exceptions)
                return not isinstance(exc, (LLMSchemaValidationError, AppException))

            if _has_programmatic_errors(e):
                raise e

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
            chunk_final = {
                "_dlq_status": "FAILED/DLQ",
                "reason": fallback_reason,
            }
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

            return chunk_final, None, [], prompt_context
""".strip("\n").split("\n"))

new_lines.extend(lines[end_idx + 1:])

with open('backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines) + '\n')

print("Patched successfully")
