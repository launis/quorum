"""Epic to Hybrid MD+XML Converter.

Converts a single Epic .md file to the Hybrid MD+XML format by injecting
structured <execution_block> XML sections after each Phase in the
'## 3. Phased Execution Plan' section.

The original Markdown content is preserved. XML blocks are appended as a
progressive enhancement inside fenced ```xml code blocks.

===========================================================================
USAGE
===========================================================================

  Dry-run (preview, does not modify the file):

    uv run python scripts/convert_epic_to_hybrid.py docs/epic/EPIC_118_tda_context_enriched_pipeline.md --dry-run

  Convert (overwrites the file in-place):

    uv run python scripts/convert_epic_to_hybrid.py docs/epic/EPIC_118_tda_context_enriched_pipeline.md

===========================================================================
WHAT IT DOES
===========================================================================

  1. Locates the '## 3. Phased Execution Plan' section in the Epic.
  2. Parses each '### Phase N: ...' block.
  3. Detects '#### [MODIFY]/[NEW]/[DELETE]' file targets automatically.
  4. Generates an <execution_block> XML section per phase containing:
     - <step> per file target with <action> extracted from the Epic prose
     - <target> using @[...] reference syntax
     - <invariants> with <must> and <forbidden> constraints
     - <tests min_negative="2"> with positive and negative scenarios
     - <audit_command> with the correct audit loop path
     - CDATA wrapping when content contains <, >, or &
  5. Skips phases that already contain an <execution_block> (idempotent).

===========================================================================
FLAGS
===========================================================================

  --dry-run   Print the converted output to stdout instead of overwriting.

===========================================================================
"""

from __future__ import annotations

import argparse
import re
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Domain Models
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PhaseBlock:
    """A single parsed Phase from the Epic's Phased Execution Plan.

    Attributes:
        phase_id: Identifier for the phase (e.g., "phase_1", "phase_0").
        heading: The raw Markdown heading text.
        heading_level: The integer level of the heading (e.g., 3 for ###).
        body: The Markdown content under the heading until the next phase.
        start_line: The 0-indexed line number of the phase heading.
        end_line: The 0-indexed exclusive end line number.
        file_targets: A list of file paths extracted from [MODIFY]/[NEW]/[DELETE] tags.
    """

    phase_id: str
    heading: str
    heading_level: int
    body: str
    start_line: int
    end_line: int
    file_targets: list[str]


@dataclass(frozen=True)
class ConversionResult:
    """Result of the conversion.

    Attributes:
        original_path: The Path object of the original Epic Markdown file.
        converted_content: The new Markdown content with injected XML blocks.
        phases_converted: The total number of phases successfully converted.
    """

    original_path: Path
    converted_content: str
    phases_converted: int


# ---------------------------------------------------------------------------
# Phase Parser
# ---------------------------------------------------------------------------

_PHASE_HEADING_RE = re.compile(
    r"^(#{2,4})\s+Phase\s+(\d+)\s*:\s*(.+)$",
    re.IGNORECASE,
)

_FILE_TARGET_RE = re.compile(
    r"\[(?:MODIFY|NEW|DELETE)\]\s*\[([^\]]+)\]\(file:///([^)]+)\)",
    re.IGNORECASE,
)

_MODIFY_HEADING_RE = re.compile(
    r"^#{3,5}\s+\[(?:MODIFY|NEW|DELETE)\]\s+\[([^\]]+)\]\(file:///([^)]+)\)",
    re.IGNORECASE,
)


def _extract_phase_blocks(lines: list[str], section_start: int, section_end: int) -> list[PhaseBlock]:
    """Extract individual Phase blocks from the Phased Execution Plan section.

    Args:
        lines: The list of raw lines from the Markdown file.
        section_start: The starting line index of the execution plan section.
        section_end: The ending line index of the execution plan section.

    Returns:
        A list of parsed PhaseBlock data objects representing each phase.
    """
    phases: list[PhaseBlock] = []
    phase_starts: list[tuple[int, str, int, str]] = []  # (line_idx, phase_num, heading_level, heading_text)

    for i in range(section_start, section_end):
        m = _PHASE_HEADING_RE.match(lines[i].strip())
        if m:
            heading_level = len(m.group(1))
            phase_num = m.group(2)
            phase_starts.append((i, phase_num, heading_level, lines[i].rstrip()))

    for idx, (start, phase_num, level, heading) in enumerate(phase_starts):
        if idx + 1 < len(phase_starts):
            end = phase_starts[idx + 1][0]
        else:
            end = section_end

        body_lines = lines[start + 1 : end]
        body = "\n".join(body_lines)

        # Extract file targets from [MODIFY]/[NEW]/[DELETE] patterns
        file_targets: list[str] = []
        for line in body_lines:
            fm = _MODIFY_HEADING_RE.match(line.strip())
            if fm:
                file_targets.append(fm.group(2).replace("/", "\\"))
            else:
                for ft_match in _FILE_TARGET_RE.finditer(line):
                    file_targets.append(ft_match.group(2).replace("/", "\\"))

        phases.append(
            PhaseBlock(
                phase_id=f"phase_{phase_num}",
                heading=heading,
                heading_level=level,
                body=body,
                start_line=start,
                end_line=end,
                file_targets=file_targets,
            )
        )

    return phases


def _find_section_bounds(lines: list[str], section_heading: str) -> tuple[int, int] | None:
    """Find the start and end line indices of a ## section.

    Args:
        lines: The list of raw lines from the Markdown file.
        section_heading: The title of the section to search for (case-insensitive).

    Returns:
        A tuple of (start_index, end_index) for the section, or None if not found.
    """
    start: int | None = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("## ") and section_heading.lower() in stripped.lower():
            start = i
            continue
        if start is not None and stripped.startswith("## ") and section_heading.lower() not in stripped.lower():
            return start, i

    if start is not None:
        return start, len(lines)
    return None


# ---------------------------------------------------------------------------
# XML Generator (Deterministic — no LLM needed)
# ---------------------------------------------------------------------------


def _extract_scope(body: str) -> list[tuple[str, str, str]]:
    """Extract (scope, filename, filepath) tuples from the phase body.

    Args:
        body: The Markdown body content of the phase.

    Returns:
        A list of tuples containing the extracted modification scope (e.g., "MODIFY"),
        the basename of the file, and the full filepath.
    """
    results: list[tuple[str, str, str]] = []
    for m in re.finditer(
        r"#{3,5}\s+\[(MODIFY|NEW|DELETE)\]\s+\[([^\]]+)\]\(file:///([^)]+)\)",
        body,
        re.IGNORECASE,
    ):
        scope = m.group(1).upper()
        filename = m.group(2)
        filepath = m.group(3).replace("/", "\\")
        results.append((scope, filename, filepath))
    return results


def _extract_code_snippets(body: str) -> list[str]:
    """Extract fenced code blocks from the body.

    Args:
        body: The Markdown body content of the phase.

    Returns:
        A list of string contents extracted from fenced code blocks.
    """
    snippets: list[str] = []
    in_fence = False
    current: list[str] = []
    for line in body.split("\n"):
        if line.strip().startswith("```") and not in_fence:
            in_fence = True
            current = []
        elif line.strip().startswith("```") and in_fence:
            in_fence = False
            snippets.append("\n".join(current))
            current = []
        elif in_fence:
            current.append(line)
    return snippets


def _extract_action_description(body: str, filepath: str) -> str:
    """Extract the prose description following a [MODIFY]/[NEW]/[DELETE] heading for a specific file.

    Args:
        body: The Markdown body content of the phase.
        filepath: The full filepath to search for within the target headings.

    Returns:
        A concatenated string of the prose description following the target heading,
        or a default fallback string if no prose is found.
    """
    # Convert to forward slashes to match file:/// URLs in Markdown
    forward_path = filepath.replace("\\", "/")
    escaped = re.escape(forward_path)
    # Use string concat to avoid f-string eating the {3,5} regex quantifier
    pattern = r"#{3,5}\s+\[(?:MODIFY|NEW|DELETE)\]\s+\[[^\]]+\]\(file:///" + escaped + r"\)"

    lines = body.split("\n")
    start_idx: int | None = None
    for i, line in enumerate(lines):
        if re.match(pattern, line.strip(), re.IGNORECASE):
            start_idx = i
            break

    if start_idx is None:
        return "See Markdown section above for detailed instructions."

    # Collect prose until next heading or code block, skipping blank lines
    desc_lines: list[str] = []
    for line in lines[start_idx + 1 :]:
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("```"):
            break
        if stripped:
            desc_lines.append(stripped)

    return " ".join(desc_lines) if desc_lines else "See Markdown section above for detailed instructions."


def _needs_cdata(text: str) -> bool:
    """Check if text contains characters that need CDATA wrapping.

    Args:
        text: The string content to evaluate.

    Returns:
        True if the text contains characters like <, >, or & that require XML CDATA escaping.
    """
    return "<" in text or ">" in text or "&" in text


def _wrap_cdata(text: str) -> str:
    """Wrap text in CDATA if needed.

    Args:
        text: The string content to wrap.

    Returns:
        The string wrapped in CDATA tags if necessary, otherwise the original string.
    """
    if _needs_cdata(text):
        return f"<![CDATA[{text}]]>"
    return text


def generate_execution_block(phase: PhaseBlock) -> str:
    """Generate an <execution_block> XML string for a given phase.

    Args:
        phase: The PhaseBlock data object representing the phase to serialize.

    Returns:
        A formatted XML string containing the execution block for the phase.
    """
    # Extract the phase summary from the heading
    heading_match = _PHASE_HEADING_RE.match(phase.heading.strip().lstrip("#").strip())
    if heading_match:
        summary = heading_match.group(3).strip()
    else:
        summary = phase.heading.strip().lstrip("#").strip()
        # Remove "Phase N:" prefix if present
        summary = re.sub(r"^Phase\s+\d+\s*:\s*", "", summary)

    file_targets = _extract_scope(phase.body)

    # If no file targets, generate a minimal block
    if not file_targets:
        body_summary = phase.body.strip()
        if len(body_summary) > 200:
            body_summary = body_summary[:200] + "..."
        return textwrap.dedent(f"""\
        ```xml
        <execution_block phase="{phase.phase_id}" consumer="tier2-execute">
          <summary>{_wrap_cdata(summary)}</summary>
          <step id="{phase.phase_id}.1" scope="MODIFY">
            <action>{_wrap_cdata(body_summary)}</action>
            <target>N/A</target>
            <invariants/>
            <tests min_negative="0"/>
          </step>
        </execution_block>
        ```""")

    # Build steps for each file target
    steps: list[str] = []
    for step_idx, (scope, filename, filepath) in enumerate(file_targets, 1):
        step_id = f"{phase.phase_id}.{step_idx}"
        action = _extract_action_description(phase.body, filepath)

        # Build the target with @-reference
        target_ref = f"@[{filepath}]"
        audit_path = filepath.replace(chr(92), "/")

        step_xml = textwrap.indent(
            textwrap.dedent(f"""\
        <step id="{step_id}" scope="{scope}">
          <action>{_wrap_cdata(action)}</action>
          <target>{target_ref}</target>
          <invariants>
            <must>Strict Pydantic V2 typing with ConfigDict(strict=True, extra='forbid')</must>
            <forbidden>Raw dict state passing, asyncio.gather, try/except Exception catch-all</forbidden>
          </invariants>
          <tests min_negative="2">
            <positive>Verify {filename} compiles and integrates correctly</positive>
            <negative>Verify missing required fields trigger ValidationError/AppException</negative>
            <negative>Verify invalid types trigger Pydantic ValidationError</negative>
          </tests>
          <audit_command>uv run python scripts/backend_audit_loop.py {audit_path} --test</audit_command>
        </step>"""),
            "  ",
        )

        steps.append(step_xml)

    steps_xml = "\n".join(steps)

    return textwrap.dedent(f"""\
    ```xml
    <execution_block phase="{phase.phase_id}" consumer="tier2-execute">
      <summary>{_wrap_cdata(summary)}</summary>
    {steps_xml}
    </execution_block>
    ```""")


# ---------------------------------------------------------------------------
# Converter
# ---------------------------------------------------------------------------


def convert_epic(epic_path: Path) -> ConversionResult:
    """Convert a single Epic file to Hybrid MD+XML format.

    Args:
        epic_path: The Path object pointing to the target Epic Markdown file.

    Returns:
        A ConversionResult containing the original path, the mutated content,
        and the number of successfully converted phases.
    """
    content = epic_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    # Find the Phased Execution Plan section
    bounds = _find_section_bounds(lines, "Phased Execution Plan")
    if bounds is None:
        # Try alternative heading
        bounds = _find_section_bounds(lines, "Implementation Strategy")
    if bounds is None:
        print(f"WARNING: No 'Phased Execution Plan' section found in {epic_path.name}")
        return ConversionResult(
            original_path=epic_path,
            converted_content=content,
            phases_converted=0,
        )

    section_start, section_end = bounds
    phases = _extract_phase_blocks(lines, section_start, section_end)

    if not phases:
        print(f"WARNING: No Phase headings found in {epic_path.name}")
        return ConversionResult(
            original_path=epic_path,
            converted_content=content,
            phases_converted=0,
        )

    # Build the output by inserting XML blocks after each phase
    # Work backwards to preserve line numbers
    output_lines = list(lines)
    phases_converted = 0

    for phase in reversed(phases):
        # Check if an execution_block already exists in this phase's body
        if "<execution_block" in phase.body:
            print(f"  SKIP: {phase.heading.strip()} -- already has <execution_block>")
            continue

        xml_block = generate_execution_block(phase)

        # Insert the XML block just before the end of this phase
        insertion_point = phase.end_line
        xml_lines = ["", xml_block, ""]
        for i, xml_line in enumerate(xml_lines):
            output_lines.insert(insertion_point + i, xml_line)
        phases_converted += 1
        print(f"  DONE: {phase.heading.strip()} -- {len(phase.file_targets)} file target(s)")

    converted = "\n".join(output_lines)

    return ConversionResult(
        original_path=epic_path,
        converted_content=converted,
        phases_converted=phases_converted,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    """Execute the Epic to Hybrid MD+XML converter CLI tool.

    Raises:
        SystemExit: If the file is not found or is not a Markdown file.
    """
    # Force UTF-8 stdout on Windows (cp1252 can't handle arrows/emojis in Epic content)
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]

    parser = argparse.ArgumentParser(
        description="Convert a single Epic .md file to Hybrid MD+XML format.",
    )
    parser.add_argument(
        "epic_path",
        type=Path,
        help="Path to the Epic .md file to convert.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print converted output to stdout instead of overwriting the file.",
    )
    args = parser.parse_args()

    epic_path: Path = args.epic_path.resolve()
    if not epic_path.exists():
        print(f"ERROR: File not found: {epic_path}", file=sys.stderr)
        sys.exit(1)
    if not epic_path.suffix == ".md":
        print(f"ERROR: Not a Markdown file: {epic_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Converting: {epic_path.name}")
    print(f"{'-' * 60}")

    result = convert_epic(epic_path)

    print(f"{'-' * 60}")
    print(f"Phases converted: {result.phases_converted}")

    if result.phases_converted == 0:
        print("No changes made.")
        return

    if args.dry_run:
        print(f"\n{'=' * 60}")
        print("DRY RUN -- Output below (not written to file):")
        print(f"{'=' * 60}\n")
        print(result.converted_content)
    else:
        # Write back
        epic_path.write_text(result.converted_content, encoding="utf-8")
        print(f"OK File updated: {epic_path}")


if __name__ == "__main__":
    main()
