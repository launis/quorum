"""Rule Staleness Auditor Script.

Scans all `.agents/rules/*.md` files for code symbols referenced in `<banned_pattern>`
and `<mandatory_pattern>` XML blocks, and verifies whether each symbol still exists
in the active codebase (`backend_v2/` and `scripts/`).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Force UTF-8 encoding for stdout/stderr to support emojis on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass

# Curated exclusion set for common keywords, types, and Markdown noise
COMMON_RESERVED_SYMBOLS: set[str] = {
    "True",
    "False",
    "None",
    "dict",
    "list",
    "str",
    "int",
    "float",
    "set",
    "tuple",
    "bool",
    "Any",
    "Self",
    "Optional",
    "Union",
    "Field",
    "ConfigDict",
    "Annotated",
    "type",
    "class",
    "def",
    "async",
    "await",
    "return",
    "yield",
    "import",
    "from",
    "as",
    "try",
    "except",
    "finally",
    "raise",
    "with",
    "pass",
    "break",
    "continue",
    "if",
    "elif",
    "else",
    "for",
    "while",
    "in",
    "is",
    "not",
    "and",
    "or",
}


def extract_code_symbols_from_rules(rules_dir: Path) -> dict[str, set[str]]:
    """Extract backtick-enclosed code symbols from XML blocks in rule markdown files."""
    if not rules_dir.exists():
        return {}

    rule_symbols: dict[str, set[str]] = {}
    pattern_block_regex = re.compile(
        r"<(?:banned_pattern|mandatory_pattern)>([\s\S]*?)</(?:banned_pattern|mandatory_pattern)>",
        re.IGNORECASE,
    )
    symbol_regex = re.compile(r"[`']([a-zA-Z_][a-zA-Z0-9_]*)[`']")

    for rule_file in rules_dir.glob("*.md"):
        try:
            content = rule_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        file_symbols: set[str] = set()
        for block in pattern_block_regex.finditer(content):
            block_text = block.group(1)
            for match in symbol_regex.finditer(block_text):
                sym = match.group(1)
                if sym not in COMMON_RESERVED_SYMBOLS and len(sym) > 2:
                    file_symbols.add(sym)

        if file_symbols:
            rule_symbols[rule_file.name] = file_symbols

    return rule_symbols


def verify_symbols_exist(symbols: set[str], search_dirs: list[Path]) -> set[str]:
    """Check if symbols exist in any source file across target directories."""
    if not symbols:
        return set()

    found_symbols: set[str] = set()
    # Cache regex for all symbols
    symbol_patterns = {sym: re.compile(rf"\b{re.escape(sym)}\b") for sym in symbols}

    for directory in search_dirs:
        if not directory.exists():
            continue
        for ext in ("*.py", "*.dart", "*.json"):
            for source_file in directory.rglob(ext):
                try:
                    content = source_file.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue

                remaining = symbols - found_symbols
                if not remaining:
                    break
                for sym in remaining:
                    if symbol_patterns[sym].search(content):
                        found_symbols.add(sym)

    return symbols - found_symbols


def audit_rules_staleness(rules_dir: Path, search_dirs: list[Path]) -> tuple[dict[str, set[str]], int]:
    """Audit rule files and return orphaned symbols per rule file."""
    rule_symbols = extract_code_symbols_from_rules(rules_dir)
    all_symbols: set[str] = set()
    for s_set in rule_symbols.values():
        all_symbols.update(s_set)

    orphans = verify_symbols_exist(all_symbols, search_dirs)
    file_orphans: dict[str, set[str]] = {}

    for r_file, s_set in rule_symbols.items():
        file_orphaned = s_set & orphans
        if file_orphaned:
            file_orphans[r_file] = file_orphaned

    return file_orphans, len(all_symbols)


def main() -> None:
    """CLI Entrypoint for Rules Staleness Auditor."""
    parser = argparse.ArgumentParser(description="Audit .agents/rules for stale or non-existent code symbols.")
    parser.add_argument("--rules-dir", default=".agents/rules", help="Rules directory")
    parser.add_argument(
        "--search-dirs", nargs="+", default=["backend_v2", "scripts", "client_app_v2"], help="Search directories"
    )
    args = parser.parse_args()

    r_dir = Path(args.rules_dir).resolve()
    s_dirs = [Path(d).resolve() for d in args.search_dirs]

    print(f"\n🔍 Auditing Rule Staleness in {r_dir} against {len(s_dirs)} directories...")
    file_orphans, total_checked = audit_rules_staleness(r_dir, s_dirs)

    if not file_orphans:
        print(f"✅ Rules Staleness Audit Passed: All {total_checked} referenced symbols exist in codebase.")
    else:
        print(f"⚠️ Rules Staleness Warnings (Checked {total_checked} symbols):")
        for r_file, orphans in sorted(file_orphans.items()):
            print(f"  [{r_file}] Found {len(orphans)} unreferenced symbol(s):")
            for sym in sorted(orphans):
                print(f"    - [WARN] `{sym}`")

    # Informational audit tool, exits 0
    sys.exit(0)


if __name__ == "__main__":
    main()
