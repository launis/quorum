import subprocess

try:
    result = subprocess.run(
        ["uv", "run", "mypy", "backend", "--no-color-output"],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    with open("mypy_debug_utf8.txt", "w", encoding="utf-8") as f:
        f.write(result.stdout)
        f.write("\nSTDERR:\n")
        f.write(result.stderr)
    print("Done")
except Exception as e:
    print(e)
