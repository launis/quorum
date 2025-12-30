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

import json

def get_db_content():
    """
    Loads the seed data from data/seed_data.json to provide context for documentation.
    """
    seed_path = PROJECT_ROOT / "data" / "seed_data.json"
    try:
        if seed_path.exists():
            with open(seed_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Summarize data to avoid hitting token limits if too large
            # For now, we'll try to pass the structure of workflows and steps
            return json.dumps(data, indent=2)
    except Exception as e:
        print(f"Warning: Could not load seed data: {e}")
    return ""

def get_prompt_for_file(filename, content, db_context=""):
    """
    Returns a tailored prompt based on the filename.
    """
    base_instructions = """
    INSTRUCTIONS:
    1.  **Update & Correct**: Review the current content and update it to strictly match the current software state (Cognitive Quorum v2). Remove any obsolete "v1" or hardcoded logic references. The system is now a Generic Engine driven by data.
    2.  **Tone & Style**: Professional, concise, technical but accessible.
    3.  **Formatting**: Use clean Markdown.
    4.  **Output**: Return ONLY the updated markdown content.
    """

    if filename.lower() == "readme.md":
        return f"""
        You are an expert technical writer. Rewrite README.md to follow industry best practices.
        
        FILENAME: {filename}
        CURRENT CONTENT:
        {content[:20000]}
        
        SPECIFIC INSTRUCTIONS:
        1.  **Structure**: Title, Badges, TOC, Key Features, Architecture v2, Getting Started (Prereqs, Install), Usage (Backend, Frontend), Configuration, Development, License.
        2.  **Content**: Compelling summary, clear instructions.
        {base_instructions}
        """
    
    elif "structured_cognitive_architecture.md" in filename.lower():
        return f"""
        You are a Cognitive Systems Architect and Scientific Researcher. 
        Your task is to rewrite this document to be a functional and scientific explanation of the "Cognitive Quorum" workflow, based on the actual database configuration provided below.

        FILENAME: {filename}
        
        DATABASE CONTEXT (The actual "Mind" of the system):
        {db_context[:60000]} # Injecting DB content here. Truncate if absolutely necessary but try to keep steps.

        CURRENT CONTENT:
        {content[:15000]}
        
        SPECIFIC INSTRUCTIONS:
        1.  **Code-First / Data-Driven**: Explain that the system's behavior is defined by the data in `db.json` (Steps, Components).
        2.  **Workflow Breakdown**: detailed section for the "Cognitive Quorum Assessment" workflow found in the DB.
            -   Iterate through each **Step** defined in the DB.
            -   For each step, explain its **Purpose** (Scientific/Functional justification).
            -   Mention the **Components** used (Prompts, Rules, Mandates) and why they are selected.
            -   Reference external scientific concepts where applicable (e.g., "System 2 thinking", "Adversarial Review", "Chain of Thought").
        3.  **Architecture**: Keep the "Mind vs. Spine" concept but ground it in the actual JSON data structure shown above.
        4.  **Scientific Tone**: The document should read like a technical whitepaper justifying the design choices.
        {base_instructions}
        """

    elif "architecture" in filename.lower():
        return f"""
        You are a software architect. Update this architecture document to accurately describe the implemented v2 system.
        
        FILENAME: {filename}
        CURRENT CONTENT:
        {content[:15000]}
        
        SPECIFIC INSTRUCTIONS:
        1.  **Diagrams**: Ensure Mermaid diagrams reflect the actual v2 flow (Streamlit -> FastAPI -> Generic Engine -> Agents).
        2.  **Components**: Define the roles of Frontend, Backend, Engine, and Database clearly.
        3.  **Data Flow**: Explain the data-driven nature (Workflows defined in DB, not hardcoded).
        {base_instructions}
        """

    elif filename.lower() == "index.md":
        return f"""
        You are a technical librarian. Update this index page to be an accurate and up-to-date entry point.
        
        FILENAME: {filename}
        CURRENT CONTENT:
        {content[:10000]}
        
        SPECIFIC INSTRUCTIONS:
        1.  **Navigation**: Provide clear links to all other major documentation files.
        2.  **Overview**: Summarize the current "Cognitive Quorum v2" capabilities.
        {base_instructions}
        """

    else:
        return f"""
        You are an expert technical writer. Your task is to update this documentation file to accurately reflect the current software version.
        
        FILENAME: {filename}
        CURRENT CONTENT:
        {content[:15000]}
        
        SPECIFIC INSTRUCTIONS:
        1.  **Accuracy**: Correct any outdated information. The software is now a data-driven workflow engine.
        2.  **Clarity**: Improve sentence structure and readability.
        {base_instructions}
        """

def update_content_with_ai():
    """
    Iterates through documentation files and requests an AI update via the backend API.
    """
    print("--- Starting AI Content Update ---")
    files_to_update = [README_PATH] + list(DOCS_DIR.glob("*.md"))
    
    # Load DB context once
    db_context = get_db_content()
    if db_context:
        print(f"Loaded database context ({len(db_context)} chars).")
    else:
        print("Warning: No database context loaded.")

    llm_url = "http://localhost:8000/llm/generate"
    
    for file_path in files_to_update:
        if file_path.name == "openapi.json": continue
        
        print(f"\nProcessing {file_path.name}...")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                current_content = f.read()
            
            prompt_text = get_prompt_for_file(file_path.name, current_content, db_context)
            
            payload = {
                "prompts": [{"role": "user", "parts": [prompt_text]}],
                "model": "gemini-2.5-pro"
            }
            
            # Increased timeout for larger files
            response = requests.post(llm_url, json=payload, timeout=180)
            
            if response.status_code == 200:
                result = response.json()
                updated_content = result.get("response", "")
                
                if updated_content:
                    print(f"--- Proposed Update for {file_path.name} Generated ---")
                    # Universal confirmation for all files
                    user_response = input(f"Do you want to overwrite {file_path.name}? (y/N): ").strip().lower()
                    
                    if user_response == 'y':
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(updated_content)
                        print(f"Successfully updated {file_path.name}")
                    else:
                        print(f"Skipped update for {file_path.name}")
                else:
                    print(f"Received empty response for {file_path.name}")
            else:
                print(f"Failed to update {file_path.name}: Status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("Backend not reachable. Is the server running? Skipping AI update.")
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
