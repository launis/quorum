import json
import shutil
import os
from datetime import datetime

seed_path = r"c:\src\quorum\backend_v2\seed\seed_data.json"
backup_dir = r"c:\src\quorum\backend_v2\seed\backups"
os.makedirs(backup_dir, exist_ok=True)

# 1. Backup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = os.path.join(backup_dir, f"seed_data.json.{timestamp}.grid_test.bak")
shutil.copy2(seed_path, backup_path)
print(f"Backup created: {backup_path}")

# 2. Modify
with open(seed_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find 'workflow_courtroom_20_full_audit' in 'workflows'
for wf in data.get("workflows", []):
    if wf.get("id") == "workflow_courtroom_20_full_audit":
        renders = wf.get("render_blueprints", {}).get("default", {})
        # try legacy render_blueprint if render_blueprints doesn't exist
        if not renders:
            renders = wf.get("render_blueprint", {})
        
        if "components" in renders:
            comps = renders["components"]
            matrices = [c for c in comps if c.get("type") in ("2d_matrix", "3d_scatter")]
            other_comps = [c for c in comps if c.get("type") not in ("2d_matrix", "3d_scatter")]
            
            if matrices:
                grid = {
                    "type": "grid_row",
                    "columns": 2, # Setting to 2 as it might fit better on PDF
                    "children": matrices
                }
                
                new_comps = []
                # Inject grid right after the 1d gauge or header
                grid_injected = False
                for c in other_comps:
                    new_comps.append(c)
                    if c.get("type") == "1d_gauge" and not grid_injected:
                        new_comps.append(grid)
                        grid_injected = True
                
                if not grid_injected:
                    new_comps.insert(1, grid)
                        
                renders["components"] = new_comps
                print(f"Modification successful. Wrapped {len(matrices)} matrices into a single grid_row component.")
                print(f"Original component count: {len(comps)} -> New component count: {len(new_comps)}")

with open(seed_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
