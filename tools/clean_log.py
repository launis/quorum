"""Script to clean log files."""

import re


def clean():
    """Clean pytest output log."""
    with open("pytest_output.txt", "rb") as f:
        data = f.read().decode("utf-8", errors="ignore")

    # Remove ANSI codes
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    clean_data = ansi_escape.sub("", data)

    with open("pytest_clean.txt", "w", encoding="utf-8") as f:
        f.write(clean_data)


if __name__ == "__main__":
    clean()
