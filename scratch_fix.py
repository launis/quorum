import re

with open(r"c:\src\quorum\backend_v2\worker.py", encoding="utf-8") as f:
    content = f.read()

# Fix redefinition
content = content.replace(
    "messages: list[dict[str, Any]] = [",
    "strict_messages: list[dict[str, Any]] = [",
    1,  # but only the second occurrence! I will use regex
)
# Wait, I will just replace the exact lines
content = re.sub(
    r'(client = await LLMClient\.from_strategy\("strict", repository=repo\)\s+)messages: list\[dict\[str, Any\]\] = \[',
    r"\1strict_messages: list[dict[str, Any]] = [",
    content,
)
content = content.replace(
    "messages=messages,",
    "messages=strict_messages,",
    1,  # replace the second occurrence
)
content = re.sub(
    r"(t_row = tg\.create_task\(\s+client\.run_structured_task\(\s+)messages=messages,",
    r"\1messages=strict_messages,",
    content,
)

# Fix type ignore for section_syntheses
content = re.sub(
    r'sec_dict\[sec\.layout_id\] = \[\s+cb\.model_dump\(exclude_none=True\) if hasattr\(cb, "model_dump"\) else cb\s+for cb in sec\.content_blocks\s+\] if hasattr\(sec, "content_blocks"\) else \[\]  # type: ignore',
    r'sec_dict[sec.layout_id] = list([cb.model_dump(exclude_none=True) if hasattr(cb, "model_dump") else cb for cb in sec.content_blocks]) if hasattr(sec, "content_blocks") else []  # type: ignore',
    content,
    flags=re.MULTILINE | re.DOTALL,
)

# Fix type ignore for content_blocks
content = re.sub(
    r'content_blocks=\[\s+b\.model_dump\(exclude_none=True\) if hasattr\(b, "model_dump"\) else b\s+for b in synthesis_res\.content_blocks\s+\] if synthesis_res and hasattr\(synthesis_res, "content_blocks"\) and synthesis_res\.content_blocks else \[\],  # type: ignore',
    r'content_blocks=list([b.model_dump(exclude_none=True) if hasattr(b, "model_dump") else b for b in synthesis_res.content_blocks]) if synthesis_res and hasattr(synthesis_res, "content_blocks") and synthesis_res.content_blocks else [],  # type: ignore',
    content,
    flags=re.MULTILINE | re.DOTALL,
)

with open(r"c:\src\quorum\backend_v2\worker.py", "w", encoding="utf-8") as f:
    f.write(content)
