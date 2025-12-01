import os
import requests
import subprocess
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
README_PATH = PROJECT_ROOT / "README.md"
OPENAPI_URL = "http://localhost:8000/openapi.json"
OPENAPI_OUTPUT = DOCS_DIR / "swagger" / "openapi.json"

IGNORE_DIRS = {
    ".git", "__pycache__", "venv", ".venv", "site", ".gemini", ".agent", ".idea", ".vscode", "node_modules"
}
IGNORE_FILES = {
    ".DS_Store", "Thumbs.db", "*.pyc"
}

def generate_tree(startpath):
    tree_str = ""
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        level = root.replace(str(startpath), '').count(os.sep)
        indent = ' ' * 4 * (level)
        subindent = ' ' * 4 * (level + 1)
        
        if level == 0:
            # tree_str += f"{os.path.basename(root)}/\n"
            pass
        else:
            tree_str += f"{indent}{os.path.basename(root)}/\n"
            
        for f in files:
            if f in IGNORE_FILES: continue
            if f.endswith(".pyc"): continue
            tree_str += f"{subindent}{f}\n"
            
    return tree_str

def generate_tree_simple(startpath):
    """
    Generates a simplified tree structure focusing on key directories.
    """
    tree_lines = []
    
    def add_to_tree(path, prefix=""):
        contents = sorted(list(path.iterdir()), key=lambda x: (not x.is_dir(), x.name.lower()))
        pointers = [("├── " if i < len(contents) - 1 else "└── ") for i in range(len(contents))]
        
        for pointer, item in zip(pointers, contents):
            if item.name in IGNORE_DIRS or item.name.startswith('.'):
                continue
            if item.is_file() and item.suffix == ".pyc":
                continue
                
            tree_lines.append(f"{prefix}{pointer}{item.name}{'/' if item.is_dir() else ''}")
            
            if item.is_dir():
                extension = "│   " if pointer == "├── " else "    "
                add_to_tree(item, prefix=prefix + extension)

    add_to_tree(startpath)
    return "\n".join(tree_lines)

def update_readme_tree():
    print("Updating Directory Tree in README.md...")
    if not README_PATH.exists():
        print("README.md not found!")
        return

    tree_content = generate_tree_simple(PROJECT_ROOT)
    
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    start_marker = "<!-- TREE_START -->"
    end_marker = "<!-- TREE_END -->"
    
    if start_marker in content and end_marker in content:
        start_idx = content.find(start_marker) + len(start_marker)
        end_idx = content.find(end_marker)
        
        new_content = content[:start_idx] + "\n" + tree_content + "\n" + content[end_idx:]
        
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("README.md updated successfully.")
    else:
        print("Markers not found in README.md. Skipping tree update.")

def update_api_docs():
    print(f"Fetching OpenAPI spec from {OPENAPI_URL}...")
    try:
        response = requests.get(OPENAPI_URL, timeout=5)
        if response.status_code == 200:
            with open(OPENAPI_OUTPUT, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"Saved OpenAPI spec to {OPENAPI_OUTPUT}")
        else:
            print(f"Failed to fetch OpenAPI spec: Status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("Could not connect to backend server. Is it running? Skipping API doc update.")
    except Exception as e:
        print(f"Error updating API docs: {e}")

def run_mkdocs():
    print("Running mkdocs build...")
    try:
        result = subprocess.run(["mkdocs", "build"], cwd=PROJECT_ROOT, capture_output=True, text=True)
        if result.returncode == 0:
            print("MkDocs build successful!")
            print(result.stdout)
        else:
            print("MkDocs build failed!")
            print(result.stderr)
    except FileNotFoundError:
        print("mkdocs command not found. Please ensure it is installed.")

def update_content_with_ai():
    """
    Iterates through documentation files and requests an AI update via the backend API.
    """
    print("--- Starting AI Content Update ---")
    files_to_update = [README_PATH] + list(DOCS_DIR.glob("*.md"))
    
    llm_url = "http://localhost:8000/llm/generate"
    
    for file_path in files_to_update:
        if file_path.name == "openapi.json": continue
        
        print(f"Processing {file_path.name}...")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                current_content = f.read()
            
            # Construct a prompt for the LLM
            # In a real scenario, we would also inject relevant code snippets or summaries here.
            prompt_text = f"""
            You are an expert technical writer. Your task is to review and update the following documentation file.
            
            FILENAME: {file_path.name}
            
            CURRENT CONTENT:
            {current_content[:10000]} # Truncate to avoid token limits for now
            
            INSTRUCTIONS:
            1. Fix any typos or grammatical errors.
            2. Ensure the tone is professional and consistent.
            3. If the content refers to "v1" architecture, update it to "v2" (Generic Engine, Data-Driven).
            4. Return ONLY the updated markdown content. Do not include explanations.
            """
            
            payload = {
                "prompts": [{"role": "user", "parts": [prompt_text]}],
                "model": "gemini-2.5-pro"
            }
            
            response = requests.post(llm_url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                # The response structure depends on LLMHandler. Assuming it returns text directly or nested.
                # Based on llm_router.py: return {"response": response}
                # And LLMHandler.call_llm returns a string.
                updated_content = result.get("response", "")
                
                if updated_content:
                    # Basic safety check: don't overwrite if empty
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(updated_content)
                    print(f"Updated {file_path.name}")
                else:
                    print(f"Received empty response for {file_path.name}")
            else:
                print(f"Failed to update {file_path.name}: Status {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("Backend not reachable. Skipping AI update.")
            break
        except Exception as e:
            print(f"Error updating {file_path.name}: {e}")

if __name__ == "__main__":
    import sys
    
    print("--- Starting Documentation Update ---")
    
    # Always run tree and API updates
    update_readme_tree()
    update_api_docs()
    
    # Run AI update only if requested
    if "--ai" in sys.argv:
        update_content_with_ai()
    else:
        print("Skipping AI content update. Use '--ai' flag to enable.")
        
    run_mkdocs()
    print("--- Update Complete ---")
