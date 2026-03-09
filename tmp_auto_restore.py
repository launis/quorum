import subprocess
import re
import os

print("Starting auto-restore script...")
while True:
    result = subprocess.run(["uv", "run", "python", "-c", "import backend_v2.run_worker"], capture_output=True, text=True, encoding="utf-8")
    if result.returncode == 0:
        print("Success! All imports fixed.")
        break
    
    match = re.search(r"ModuleNotFoundError: No module named '([^']+)'", result.stderr)
    if not match:
        print("Other error:", result.stderr)
        break
    
    module_name = match.group(1)
    print(f"Missing module: {module_name}")
    
    if not module_name.startswith("backend_v2."):
        print("Not a backend_v2 module, can't auto-restore.")
        break
    
    # Map backend_v2.foo.bar to backend/foo/bar.py
    rel_path = module_name.replace("backend_v2.", "").replace(".", "/") + ".py"
    git_path = f"backend/{rel_path}"
    dest_path = f"backend_v2/{rel_path}"
    
    print(f"Attempting to restore {git_path} to {dest_path}")
    
    # Create dir if not exists
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    # git show
    try:
        content = subprocess.check_output(["git", "show", f":{git_path}"], text=True, encoding="utf-8")
        actual_dest = dest_path
    except subprocess.CalledProcessError:
        print(f"Could not find {git_path} in Git.")
        # Try as __init__.py of a package
        init_path = module_name.replace("backend_v2.", "").replace(".", "/") + "/__init__.py"
        git_init = f"backend/{init_path}"
        try:
            content = subprocess.check_output(["git", "show", f":{git_init}"], text=True, encoding="utf-8")
            actual_dest = f"backend_v2/{init_path}"
            os.makedirs(os.path.dirname(actual_dest), exist_ok=True)
        except subprocess.CalledProcessError:
            print(f"Also could not find {git_init} in Git. Giving up.")
            break
            
    # Auto replace backend. with backend_v2.
    content = content.replace("from backend.", "from backend_v2.")
    content = content.replace("import backend.", "import backend_v2.")
    
    with open(actual_dest, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Restored and patched {actual_dest}")
