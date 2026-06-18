import os

root_dir = r"c:\src\quorum\client_app_v2\lib"
task_file = r"c:\src\quorum\task.md"

leaf_dirs = []

for root, _dirs, files in os.walk(root_dir):
    # Only keep directories that have .dart files in them
    # But wait, a directory might have .dart files AND subdirectories
    # We should add any directory that contains purely .dart files?
    # Or just ANY directory that contains .dart files directly?
    # Let's say: any directory that contains at least one .dart file
    has_dart = any(f.endswith(".dart") for f in files)
    if has_dart:
        rel_path = os.path.relpath(root, root_dir)
        leaf_dirs.append(rel_path.replace("\\", "/"))

leaf_dirs.sort()

with open(task_file, "w", encoding="utf-8") as f:
    f.write("# Client App V2 Hardening Tasks\n\n")
    for d in leaf_dirs:
        # Handle the root directory itself if there are dart files in lib
        if d == ".":
            f.write("- [ ] client_app_v2/lib\n")
        else:
            f.write(f"- [ ] client_app_v2/lib/{d}\n")

print(f"Task list generated at: {task_file}")
