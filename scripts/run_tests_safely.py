import os
import subprocess
import sys


def run_tests():
    # Set env vars to skip arq worker
    env = os.environ.copy()
    env["TESTING"] = "true"

    cmd = ["uv", "run", "pytest", "-v", "--tb=short", "--color=no"]

    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")

        output = f"--- STDOUT ---\n{result.stdout}\n\n--- STDERR ---\n{result.stderr}"

        with open("tests/output/safe_log.txt", "w", encoding="utf-8") as f:
            f.write(output)

        print("Output written to tests/output/safe_log.txt")
        return result.returncode

    except Exception as e:
        print(f"Failed to run tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
