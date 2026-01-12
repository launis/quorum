"""Script to debug Ruff failures."""

import subprocess


def check():
    """Run Ruff check on specific file."""
    res = subprocess.run(["uv", "run", "ruff", "check", "tests/test_live_llm.py"], capture_output=True, text=True)
    with open("ruff_debug.txt", "w") as f:
        f.write(res.stdout)
        f.write(res.stderr)


if __name__ == "__main__":
    check()
