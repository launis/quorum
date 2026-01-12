"""Run pytests and capture output to file."""
import subprocess

with open("pytest_traceback.txt", "w", encoding="utf-8") as f:
    try:
        f.write("Running pytest via subprocess...\n")
        res = subprocess.run(["uv", "run", "pytest"], capture_output=True, text=True, encoding="utf-8")
        f.write("--- STDOUT ---\n")
        f.write(res.stdout)
        f.write("\n--- STDERR ---\n")
        f.write(res.stderr)
        f.write("\n--- END ---\n")
    except Exception as e:
        f.write(f"Error running pytest: {e}\n")
