
import requests
import json

BASE_URL = "http://localhost:8000"

def cleanup():
    print("🧹 Cleaning up workflows...")
    
    # 1. Fetch All
    r = requests.get(f"{BASE_URL}/builder/workflows")
    if r.status_code != 200:
        print(f"❌ Failed to list workflows: {r.text}")
        return
        
    wfs = r.json()
    print(f"Found {len(wfs)} workflows.")
    
    original_id = "sequential_audit_chain"
    fused_candidates = []
    to_delete = []
    
    # 2. Analyze
    for wf in wfs:
        wid = wf['id']
        steps = wf.get('steps', [])
        
        # Check for Original
        if wid == original_id:
            print(f"✅ Keeping Original: {wf['name']} ({wid})")
            continue
            
        # Check for Fused (Has step_panel)
        if "step_panel" in steps:
            fused_candidates.append(wf)
        else:
            # Neither original nor fused -> potential garbage
            # But wait, maybe there are other legitimate ones? 
            # User said "leave only two".
            to_delete.append(wid)

    # 3. Select Best Fused
    fused_wf = None
    if fused_candidates:
        # Sort by creation time (desc) to get latest
        # ISO string sort works for same-length dates
        fused_candidates.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        fused_wf = fused_candidates[0]
        
        # Add others to delete
        for extra in fused_candidates[1:]:
            to_delete.append(extra['id'])
            
        print(f"✅ Keeping Fused: {fused_wf['name']} ({fused_wf['id']})")
        
        # Rename for clarity
        requests.put(f"{BASE_URL}/builder/workflows/{fused_wf['id']}", json={"name": "Courtroom (Fused Critics)"})
        print(f"   Renamed to 'Courtroom (Fused Critics)'")
    else:
        print("⚠️ No Fused workflow found! You might need to compile one again.")

    # 4. Delete
    print(f"🗑️ Deleting {len(to_delete)} workflows...")
    for wid in to_delete:
        res = requests.delete(f"{BASE_URL}/builder/workflows/{wid}")
        if res.status_code == 200:
            print(f"   Deleted {wid}")
        else:
            print(f"   ❌ Failed to delete {wid}: {res.text}")

    print("✨ Cleanup Complete.")

if __name__ == "__main__":
    cleanup()
