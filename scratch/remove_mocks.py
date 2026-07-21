import sys
import glob

files = [
    "backend_v2/tests/unit/llm/test_provider_toolcalls.py",
    "backend_v2/tests/unit/llm/test_provider_penalties.py",
    "backend_v2/tests/unit/llm/test_provider_httpx_client.py",
    "backend_v2/tests/unit/llm/test_provider.py",
    "backend_v2/tests/unit/llm/test_fallback_caching.py",
    "backend_v2/tests/unit/llm/test_adaptive_retry.py",
    "backend_v2/tests/test_provider_caching_scrub.py"
]

for file in files:
    try:
        with open(file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        new_lines = []
        skip_next = False
        for line in lines:
            if "apply_provider_pacing" in line:
                if line.strip().endswith("(") or line.strip().endswith(","):
                    skip_next = True
                continue
            if skip_next:
                if line.strip() == ")," or line.strip() == ")" or line.strip() == "":
                    skip_next = False
                    continue
            new_lines.append(line)
        
        with open(file, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"Processed {file}")
    except Exception as e:
        print(f"Failed {file}: {e}")
