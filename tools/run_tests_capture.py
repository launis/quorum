
import subprocess
import os

def run_tests():
    env = os.environ.copy()
    env.update({
        "STORAGE_BACKEND": "TINYDB",
        "USE_MOCK_LLM": "true",
        "USE_MOCK_DB": "true"
    })
    
    with open("pytest_output.txt", "w") as f:
        subprocess.run(["uv", "run", "pytest"], env=env, stdout=f, stderr=subprocess.STDOUT)

if __name__ == "__main__":
    run_tests()
