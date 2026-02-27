import subprocess
with open("test_results.txt", "w", encoding="utf-8") as f:
    subprocess.run(["pytest", "backend/tests/", "--lf", "--tb=short"], stdout=f)
