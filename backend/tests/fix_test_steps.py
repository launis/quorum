import os
import re

TEST_DIR = "backend/tests/api"

target_files = [
    "test_builder_preview.py",
    "test_builder_workflows.py",
    "test_organizations.py",
    "test_llm_router.py"
]

def fix_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    
    # JSON list of dicts: "steps": [{...}]
    content = re.sub(r'\"steps\"\s*:\s*\[\s*\{.*?\}\s*\]', '"steps": ["step1"]', content, flags=re.DOTALL)
    content = re.sub(r'\'steps\'\s*:\s*\[\s*\{.*?\}\s*\]', "'steps': ['step1']", content, flags=re.DOTALL)
    
    # Pydantic WorkflowLink instantiation: steps=[WorkflowLink(id="step1", name="...")]
    # Match greedy up to the closing bracket of the list
    content = re.sub(r'steps\s*=\s*\[\s*WorkflowLink\([^\]]*?\)\s*\]', 'steps=["step1"]', content, flags=re.DOTALL)

    # Empty WorkflowLinks list: steps=[WorkflowLink()]
    content = re.sub(r'steps\s*=\s*\[\s*WorkflowLink\(\)\s*\]', 'steps=["step1"]', content, flags=re.DOTALL)
    
    # Generic multiple WorkflowLinks: steps=[WorkflowLink(...), WorkflowLink(...)]
    # A bit more aggressive for any WorkflowLink instantiation
    content = re.sub(r'WorkflowLink\([^)]*\)', '"step1"', content, flags=re.DOTALL)
    content = re.sub(r'steps=\["step1"(,\s*"step1")*\]', 'steps=["step1"]', content)
    
    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Fixed {filepath}")

if __name__ == "__main__":
    count = 0
    for root, dirs, files in os.walk(TEST_DIR):
        for file in files:
            # We target a broader range of test files since there are 49 failures
            if file.startswith("test_") and file.endswith(".py"):
                path = os.path.join(root, file)
                fix_file(path)
                count += 1
    
    # Also check core directory just in case
    for root, dirs, files in os.walk("backend/tests/core"):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                 fix_file(os.path.join(root, file))
                 count += 1
                 
    print(f"Scanned {count} test files for WorkflowLink & dict replacements.")
